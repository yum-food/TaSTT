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
		std::string result(len, 0);

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

	std::vector<sCaptureDevice> mics_raw;
	if (!GetMicsImpl(mics_raw)) {
		return false;
	}

	mics.clear();
	for (const auto& raw_mic : mics_raw) {
		mics.push_back(wcharToAsciiString(raw_mic.displayName));
	}

	return true;
}

bool WhisperCPP::OpenMic(const int idx, Whisper::iAudioCapture*& stream) {
	if (!did_init_) {
		Log(out_, "Whisper not initialized\n");
		return false;
	}

	std::vector<sCaptureDevice> mics_raw;
	if (!GetMicsImpl(mics_raw)) {
		return false;
	}

	if (mics_raw.size() <= idx) {
		Log(out_, "Mic index out of range: {} vs. {}\n", idx, mics_raw.size());
		return false;
	}

	Whisper::sCaptureParams params{};
	stream = nullptr;
	HRESULT err = f_->openCaptureDevice(mics_raw[idx].endpoint, params,
		&stream);
	if (FAILED(err)) {
		Log(out_, "Failed to open mic with idx {} ({}): {}\n", idx,
			wcharToAsciiString(mics_raw[idx].displayName),
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

	std::function<void(const std::string&, const std::string& out_cb)> out_cb =
		[&](const std::string& out, const std::string& err) -> void {
		Log(out_, out);
		Log(out_, err);
	};
	bool ret = PythonWrapper::InvokeWithArgs({
		"-u",  // Unbuffered output
		"-m pip",
		"install",
		"-r Resources/Scripts/whisper_requirements.txt",
		}, std::move(out_cb));

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
	std::string py_stdout, py_stderr;
	bool ret = PythonWrapper::InvokeWithArgs({
		"-u",  // Unbuffered output
		"-m wget",
		url_oss.str(),
		"-o", fs_path.string(),
		}, &py_stdout, &py_stderr);
	Log(out_, py_stdout);
	Log(out_, py_stderr);
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
			std::function<void(const std::string&, const std::string& out_cb)> out_cb =
				[&](const std::string& out, const std::string& err) -> void {
				Log(out_, out);
				Log(out_, err);
			};
			Log(out_, "Installing pip\n");
			if (!PythonWrapper::InstallPip(std::move(out_cb))) {
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
		context->fullDefaultParams(eSamplingStrategy::BeamSearch, &wparams);
		wparams.language = Whisper::makeLanguageKey("en");  // TODO(yum) use config
		// This must be set to keep memory usage from growing without bound.
		wparams.n_max_text_ctx = 100;

		wparams.new_segment_callback = [](iContext* context, uint32_t n_new, void* user_data) noexcept -> HRESULT {
			wxTextCtrl* out = static_cast<wxTextCtrl*>(user_data);
			iTranscribeResult* results = nullptr;
			HRESULT err = context->getResults(eResultFlags::Timestamps | eResultFlags::Tokens, &results);
			if (FAILED(err)) {
				Log(out, "Failed to get transcription: {}\n", hresultToString(err));
				return S_OK;
			}
			ScopeGuard results_cleanup([results]() { results->Release(); });

			sTranscribeLength length;
			err = results->getSize(length);
			if (FAILED(err)) {
				Log(out, "Failed to get transcription size: {}\n", hresultToString(err));
				return S_OK;
			}

			const sSegment* const segments = results->getSegments();
			const sToken* const tokens = results->getTokens();
			const int s0 = length.countSegments - n_new;
			for (int i = s0; i < length.countSegments; i++) {
				const sSegment& seg = segments[i];
				bool is_metadata = false;
				for (int j = 0; j < seg.countTokens; j++) {
					const sToken& tok = tokens[seg.firstToken + j];
					std::string_view tok_str(tok.text);
					if (tok_str.starts_with("[") ||
						tok_str.starts_with(" [") ||
						tok_str.starts_with(" (")) {
						if (tok_str.ends_with("]") ||
							tok_str.ends_with(")")) {
							continue;
						}
						is_metadata = true;
						continue;
					}
					if (is_metadata) {
						if (tok_str.ends_with("]") ||
							tok_str.ends_with(")")) {
							is_metadata = false;
						}
						continue;
					}
					if (tok_str.ends_with("BLANK_AUDIO")) {
						continue;
					}
					Log(out, "{}", tok.text);
				}
			}
			if (n_new) {
				Log(out, "\n");
			}

			return S_OK;
		};
		wparams.new_segment_callback_user_data = out_;

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

	Log(out_, "Success!\n");
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
		BrowserSource src(c.browser_src_port, out_);
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

bool WhisperCPP::GetMicsImpl(std::vector<sCaptureDevice>& mics) {
	pfnFoundCaptureDevices dev_cb = [](int len, const sCaptureDevice* buf, void* pv)->HRESULT __stdcall {
		std::vector<sCaptureDevice>* mics = static_cast<std::vector<sCaptureDevice>*>(pv);
		for (int i = 0; i < len; i++) {
			mics->push_back(buf[i]);
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
