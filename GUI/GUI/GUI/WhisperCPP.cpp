#include "BrowserSource.h"
#include "Logging.h"
#include "PythonWrapper.h"
#include "ScopeGuard.h"
#include "Util.h"
#include "WhisperCPP.h"

#include <unknwn.h>
#include <wchar.h>
#include <winerror.h>

#include "whisper/whisperWindows.h"

#include <charconv>
#include <codecvt>
#include <cwchar>
#include <fstream>
#include <future>
#include <locale>
#include <string>
#include <vector>

using namespace Whisper;
using ::Logging::DrainAsyncOutput;
using ::Logging::Log;

namespace {
	std::string wcharToAsciiString(const wchar_t* wc_str) {
		int len = wcslen(wc_str);
		if (len == 0) {
			return "";
		}

		std::string result(len + 1, 0);
		size_t len_out;
		wcstombs_s(&len_out, result.data(), len, wc_str, _TRUNCATE);

		return result;
	}

	std::string hresultToString(HRESULT err) {
		LPWSTR errorText = nullptr;

		// Call FormatMessage to retrieve the error message
		DWORD size = FormatMessage(
			FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
			nullptr,
			err,
			MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
			(LPWSTR)&errorText,
			0,
			nullptr);

		// Check if the error message was retrieved successfully
		if (size <= 0) {
			std::ostringstream oss;
			oss << "HRESULT:" << err;
			return oss.str();
		}
		std::wstring errorMessage(errorText, size);
		LocalFree(errorText);
		// Convert the wide string to a narrow string for printing
		return std::string(errorMessage.begin(), errorMessage.end());
	}
};

WhisperCPP::WhisperCPP(wxTextCtrl* out)
	: out_(out), f_(nullptr), did_init_(false), run_transcription_(false), run_browser_src_(false)
{
	// Initialize futures so that valid() returns true. We use this as a proxy
	// to tell whether they're still executing.
	{
		auto p = std::promise<void>();
		transcription_thd_ = p.get_future();
		p.set_value();
	}
	{
		auto p = std::promise<void>();
		browser_src_thd_ = p.get_future();
		p.set_value();
	}
	{
		auto p = std::promise<void>();
		custom_chatbox_thd_ = p.get_future();
		p.set_value();
	}
}

WhisperCPP::~WhisperCPP() {
	f_->Release();
}

bool WhisperCPP::Init() {
	if (did_init_) {
		return true;
	}

	iMediaFoundation* tmp_f = nullptr;
	HRESULT err = initMediaFoundation(&tmp_f);
	if (FAILED(err)) {
		Log(out_, "Failed to initialize media layer: {}", err);
		return false;
	}
	f_ = tmp_f;

	did_init_ = true;
	Log(out_, "Initialized successfully\n");
	return true;
}

bool WhisperCPP::GetMics(std::vector<std::string>& mics) {
	if (!did_init_) {
		return false;
	}

	std::vector<std::unique_ptr<sCaptureDevice>> mics_raw;
	if (!GetMicsImpl(mics_raw)) {
		return false;
	}

	mics.clear();
	for (const auto& raw_mic : mics_raw) {
		mics.push_back(wcharToAsciiString(raw_mic->displayName));
	}

	return true;
}

bool WhisperCPP::OpenMic(const int idx, Whisper::iAudioCapture*& stream) {
	if (!did_init_) {
		Log(out_, "Whisper not initialized\n");
		return false;
	}

	std::vector<std::unique_ptr<sCaptureDevice>> mics_raw;
	if (!GetMicsImpl(mics_raw)) {
		return false;
	}

	if (mics_raw.size() <= idx) {
		Log(out_, "Mic index out of range: {} vs. {}\n", idx, mics_raw.size());
		return false;
	}

	Whisper::sCaptureParams params{};
	params.dropStartSilence = 1.0;
	params.pauseDuration = 1.0;
	params.minDuration = 2.0;
	params.maxDuration = 3.0;
	params.retainDuration = 1.5;
	stream = nullptr;
	HRESULT err = f_->openCaptureDevice(mics_raw[idx]->endpoint, params,
		&stream);
	if (FAILED(err)) {
		Log(out_, "Failed to open mic with idx {} ({}): {}\n", idx,
			wcharToAsciiString(mics_raw[idx]->displayName),
			hresultToString(err));
		return false;
	}

	return true;
}

bool WhisperCPP::InstallDependencies() {
	std::filesystem::path flag_file = "Resources/.whisper_deps_installed";
	flag_file = flag_file.lexically_normal();

	if (std::filesystem::exists(flag_file)) {
		return true;
	}

	auto out_cb = [&](const std::string& out, const std::string& err) -> void {
		Log(out_, out);
		Log(out_, err);
	};
	auto in_cb = [&](std::string& in) {};
	auto run_cb = [&]() -> bool {
		return run_transcription_;
	};
	bool ret = PythonWrapper::InvokeWithArgs({
		"-u",  // Unbuffered output
		"-m pip",
		"install",
		"-r Resources/Scripts/whisper_requirements.txt",
		}, std::move(out_cb), std::move(in_cb), std::move(run_cb));

	if (!ret) {
		Log(out_, "Failed to install dependencies!\n");
		return false;
	}

	// Create the flag file so subsequent calls don't reinstall.
	std::ofstream flagfile_ofs(flag_file);
	flagfile_ofs.close();

	return true;
}

bool WhisperCPP::DownloadModel(const std::string& model_name,
	const std::filesystem::path& fs_path) {
	std::ostringstream url_oss;
	url_oss << "https://huggingface.co/datasets/ggerganov/whisper.cpp/resolve/main/";
	url_oss << model_name;
	Log(out_, "Model will be saved to {}\n", fs_path.lexically_normal().string());
	auto out_cb = [&](const std::string& out, const std::string& err) {
		Log(out_, out);
		Log(out_, err);
	};
	auto in_cb = [&](std::string& in) {};
	auto run_cb = [&]() -> bool {
		return run_transcription_;
	};
	bool ret = PythonWrapper::InvokeWithArgs({
		"-u",  // Unbuffered output
		"-m wget",
		url_oss.str(),
		"-o", fs_path.string(),
		}, std::move(out_cb), std::move(in_cb), std::move(run_cb));
	if (!ret) {
		Log(out_, "Failed to download model!\n");
		return false;
	}

	return true;
}

std::wstring utf8ToUtf16(const std::string& utf8) {
	int wide_str_len = MultiByteToWideChar(CP_UTF8, 0, utf8.c_str(), -1, NULL, 0);
	std::wstring utf16(wide_str_len, 0);
	MultiByteToWideChar(CP_UTF8, 0, utf8.c_str(), -1, utf16.data(), wide_str_len);
	return utf16;
}

bool WhisperCPP::LoadModel(const std::string& path, Whisper::iModel*& model) {
	model = nullptr;
	HRESULT err = Whisper::loadModel(utf8ToUtf16(path).c_str(),
		eModelImplementation::GPU, /*flags=*/0, /*callbacks=*/nullptr, &model);
	if (FAILED(err)) {
		Log(out_, "Failed to load model: {}\n", hresultToString(err));
		return false;
	}

	return true;
}

bool WhisperCPP::CreateContext(Whisper::iModel* model, Whisper::iContext*& context) {
	context = nullptr;
	HRESULT err = model->createContext(&context);
	if (FAILED(err)) {
		Log(out_, "Failed to create context: {}\n", hresultToString(err));
		return false;
	}

	return true;
}

void WhisperCPP::Start(const AppConfig& c) {
    Init();
	transcript_.Clear();

	if (!transcription_thd_.valid()) {
		Log(out_, "Transcription engine already running\n");
		return;
	}

	transcription_thd_ = std::async(std::launch::async, [&]() -> void {
		run_transcription_ = true;

		Whisper::iAudioCapture* mic_stream;
		if (!OpenMic(c.whisper_mic, mic_stream)) {
			return;
		}
		ScopeGuard mic_stream_cleanup([mic_stream]() { mic_stream->Release(); });

		{
			auto out_cb = [&](const std::string& out, const std::string& err) -> void {
				Log(out_, out);
				Log(out_, err);
			};
			auto in_cb = [&](std::string& in) {};
			auto run_cb = [&]() -> bool {
				return run_transcription_;
			};
			Log(out_, "Installing pip\n");
			if (!PythonWrapper::InstallPip(std::move(out_cb), std::move(in_cb),
				std::move(run_cb))) {
				Log(out_, "Failed to install pip!\n");
				return;
			}
		}
		Log(out_, "Installing Python dependencies\n");
		if (!InstallDependencies()) {
			return;
		}

		std::filesystem::path model_path = "Resources/Models";
		model_path /= c.whisper_model;
		if (std::filesystem::exists(model_path)) {
			Log(out_, "Model found at {}\n", model_path.string());
		}
		else {
			Log(out_, "Downloading model {}\n", c.whisper_model);
			if (!DownloadModel(c.whisper_model, model_path)) {
				return;
			}
		}

		Whisper::iModel* model;
		if (!LoadModel(model_path.string(), model)) {
			return;
		}
		ScopeGuard model_cleanup([model]() { model->Release(); });

		Whisper::iContext* context;
		if (!CreateContext(model, context)) {
			return;
		}
		ScopeGuard context_cleanup([context]() { context->Release(); });

		Whisper::sFullParams wparams{};
		context->fullDefaultParams(eSamplingStrategy::Greedy, &wparams);
		wparams.language = Whisper::makeLanguageKey("en");  // TODO(yum) use config
		// This must be set to keep memory usage from growing without bound.
		wparams.n_max_text_ctx = 100;

		wparams.new_segment_callback = [](iContext* context, uint32_t n_new, void* user_data) noexcept -> HRESULT {
			WhisperCPP* app = static_cast<WhisperCPP*>(user_data);
			iTranscribeResult* results = nullptr;
			HRESULT err = context->getResults(eResultFlags::Timestamps | eResultFlags::Tokens, &results);
			if (FAILED(err)) {
				Log(app->out_, "Failed to get transcription: {}\n", hresultToString(err));
				return S_OK;
			}
			ScopeGuard results_cleanup([results]() { results->Release(); });

			sTranscribeLength length;
			err = results->getSize(length);
			if (FAILED(err)) {
				Log(app->out_, "Failed to get transcription size: {}\n", hresultToString(err));
				return S_OK;
			}

			// Scanning a vector is faster than using a hashtable up to ~1k
			// entries (source: I heard it from someone once).
			static const std::vector<std::string> banned_words{
				" -",
				" (static)",
				" *no audio*",
			};

			const sSegment* const segments = results->getSegments();
			const sToken* const tokens = results->getTokens();
			const int s0 = length.countSegments - n_new;
			int n_tok = 0;
			for (int i = s0; i < length.countSegments; i++) {
				const sSegment& seg = segments[i];
				bool is_metadata = false;
				for (int j = 0; j < seg.countTokens; j++) {
					const sToken& tok = tokens[seg.firstToken + j];
					std::string_view tok_str(tok.text);
					if (tok_str.starts_with("[") ||
						tok_str.starts_with(" [")) {
						is_metadata = true;
					}
					if (is_metadata) {
						if (tok_str.ends_with("]") ||
							tok_str.ends_with(")")) {
							is_metadata = false;
						}
						continue;
					}
					std::vector<std::string>::const_iterator word_iter =
						std::find(banned_words.cbegin(), banned_words.cend(),
							tok_str);
					if (word_iter != banned_words.end()) {
						continue;
					}
					++n_tok;
					Log(app->out_, "{}", tok.text);
					app->transcript_.Append(tok.text);
				}
			}
			if (n_tok) {
				Log(app->out_, "\n");
			}

			return S_OK;
		};
		wparams.new_segment_callback_user_data = this;

		sCaptureCallbacks callbacks{};

		callbacks.shouldCancel = [](void* pv) noexcept -> HRESULT __stdcall {
			WhisperCPP* app = static_cast<WhisperCPP*>(pv);
			if (!app->run_transcription_) {
				Log(app->out_, "Exit transcription loop\n");
				return S_FALSE;
			}
			return S_OK;
		};
		callbacks.pv = this;

		// This will block.
		HRESULT err = context->runCapture(wparams, callbacks, mic_stream);
		if (FAILED(err)) {
			Log(out_, "Capture failed: {}\n", hresultToString(err));
			return;
		}

		Log(out_, "Exit transcription engine\n");
	});

	return;
}

void WhisperCPP::Stop() {
	Log(out_, "Stopping transcription engine...\n");
	run_transcription_ = false;
	transcription_thd_.wait();
	Log(out_, "Done!\n");
}

void WhisperCPP::StartBrowserSource(const AppConfig& c) {
	if (!browser_src_thd_.valid()) {
		Log(out_, "Browser source already running\n");
		return;
	}

	browser_src_thd_ = std::async(std::launch::async, [&]() -> void {
		run_browser_src_ = true;
		BrowserSource src(c.browser_src_port, out_, &transcript_);
		src.Run(&run_browser_src_);
		Log(out_, "Browser source thread exit\n");
	});
}

void WhisperCPP::StopBrowserSource() {
	Log(out_, "Stopping browser source...\n");
	run_browser_src_ = false;
	browser_src_thd_.wait();
	Log(out_, "Done!\n");
}

// TODO(yum) we should have a thread which simply tells us when to
// start/stop transcription.
void WhisperCPP::StartCustomChatbox(const AppConfig& c) {
	if (!custom_chatbox_thd_.valid()) {
		Log(out_, "Custom chatbox already running\n");
		return;
	}

	custom_chatbox_thd_ = std::async(std::launch::async, [&]() -> void {
		run_custom_chatbox_ = true;
		Log(out_, "Launching custom chatbox OSC layer\n");

		while (run_custom_chatbox_) {
			bool send_transcript = false;
			auto out_cb = [&](const std::string& out, const std::string& err) {
				std::string delim = "\r\n";
				size_t begin = 0;
				size_t end = out.size();
				while (begin < out.size()) {
					end = out.find(delim, begin);
					if (end == std::string::npos) {
						end = out.size();
					}
					ScopeGuard advance_begin([&]() { begin = end + delim.size(); });
					std::string line = out.substr(begin, end - begin);
					if (line == "1") {
						Log(out_, "Control message get: send transcript\n");
						transcript_.Clear();
						send_transcript = true;
					}
					else if (line == "0") {
						// TODO pause transcription loop?
						Log(out_, "Control message get: stop transcript\n");
						send_transcript = false;
					}
					else {
						Log(out_, "  custom chatbox: Unrecognized control sequence: {}\n", line);
					}
				}

				begin = 0;
				end = err.size();
				while (begin < err.size()) {
					end = err.find(delim, begin);
					if (end == std::string::npos) {
						end = err.size();
					}
					ScopeGuard advance_begin([&]() { begin = end + delim.size(); });
					std::string line = err.substr(begin, end - begin);
					Log(out_, "  {}\n", line);
				}
			};
			auto in_cb = [&](std::string& in) {
				if (!send_transcript) {
					return;
				}
				// TODO(yum) use a streaming interface for this. As written, we
				// have to copy a ton of redundant text every time.
				const std::vector<std::string> segments = transcript_.Get();
				std::ostringstream oss;
				for (const auto& segment : segments) {
					oss << segment;
				}
				oss << std::endl;
				in = oss.str();
			};
			auto run_cb = [&]() {
				return run_custom_chatbox_;
			};
			if (!PythonWrapper::InvokeWithArgs({
				"Resources/Scripts/cpp_transcribe.py",
				"--bytes_per_char", std::to_string(c.bytes_per_char),
				"--chars_per_sync", std::to_string(c.chars_per_sync),
				"--rows", std::to_string(c.rows),
				"--cols", std::to_string(c.cols),
				"--button", Quote(c.button),
				"--enable_local_beep", c.enable_local_beep ? "1" : "0",
				"--use_builtin", "0",
				}, out_cb, in_cb, run_cb)) {
				Log(out_, "Failed to launch custom chatbox OSC layer!\n");
				break;
			}
		}

		Log(out_, "Custom chatbox thread exit\n");
	});
}

void WhisperCPP::StopCustomChatbox() {
	Log(out_, "Stopping custom chatbox...\n");
	run_custom_chatbox_ = false;
	custom_chatbox_thd_.wait();
	Log(out_, "Done!\n");
}

bool WhisperCPP::GetMicsImpl(std::vector<std::unique_ptr<sCaptureDevice>>& mics) {
	pfnFoundCaptureDevices dev_cb = [](int len, const sCaptureDevice* buf, void* pv)->HRESULT __stdcall {
		auto mics = static_cast<std::vector<std::unique_ptr<sCaptureDevice>>*>(pv);
		for (int i = 0; i < len; i++) {
			mics->push_back(std::make_unique<sCaptureDevice>(buf[i]));
		}
		return S_OK;
	};
	mics.clear();
	HRESULT err = f_->listCaptureDevices(dev_cb, &mics);
	if (FAILED(err)) {
		Log(out_, "Failed to get microphones: {}\n", err);
		return false;
	}

	return true;
}
