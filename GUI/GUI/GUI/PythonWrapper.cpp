// Import rand_s() WIN32 API.
#define _CRT_RAND_S
// Silence security warnings caused by importing stdlib.h before wx.
#define _CRT_SECURE_NO_WARNINGS

#include <stdlib.h>

#include "Logging.h"
#include "PythonWrapper.h"
#include "ScopeGuard.h"
#include "Util.h"
#include "Config.h"

#include <stdio.h>
#include <Windows.h>

#include <filesystem>
#include <fstream>
#include <sstream>

using ::Logging::Log;

namespace {
	constexpr const char kEmotesPickle[] = "Resources/Fonts/Bitmaps/emotes.map";
}  // namespace

class PythonProcess : public wxProcess {
public:
	PythonProcess(std::function<void(wxProcess* proc, int ret)>&& exit_callback) : exit_cb_(exit_callback) {
		Redirect();
	}

	virtual void OnTerminate(int pid, int status) wxOVERRIDE {
		exit_cb_(this, status);
	}

private:
	const std::function<void(wxProcess* proc, int ret)> exit_cb_;
};

wxProcess* PythonWrapper::InvokeAsyncWithArgs(std::vector<std::string>&& args,
	std::function<void(wxProcess* proc, int ret)>&& exit_callback) {
	std::ostringstream cmd_oss;
	cmd_oss << "Resources/Python/python.exe";
	for (const auto& arg : args) {
		cmd_oss << " " << arg;
	}

	auto *p = new PythonProcess(std::move(exit_callback));
	int pid = wxExecute(cmd_oss.str(), wxEXEC_ASYNC, p);

	if (!pid) {
		delete p;
		p = nullptr;
	}

	return p;
}

std::string GetWin32ErrMsg() {
	DWORD error = GetLastError();
	LPSTR err_msg = nullptr;
	FormatMessageA(
		FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
		NULL,
		error,
		MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
		(LPSTR)&err_msg,
		0,
		NULL
	);
	ScopeGuard err_msg_cleanup([&]() { LocalFree(err_msg); });
	return std::to_string(error) + ": " + err_msg;
}


std::string DrainWin32Pipe(const HANDLE pipe) {
	DWORD bytes_avail;
	std::ostringstream oss;
	if (PeekNamedPipe(
		pipe,
		nullptr,  // buffer to read into
		0,  // buffer size
		nullptr,  // bytes read
		&bytes_avail,
		nullptr  // bytes left in this message
	)) {
		DWORD cur_bytes_read = 0;
		DWORD sum_bytes_read = 0;
		std::vector<char> buf(4096, 0);
		while (sum_bytes_read < bytes_avail &&
			ReadFile(pipe, buf.data(), buf.size() - 1, &cur_bytes_read, NULL) &&
			cur_bytes_read > 0) {
			oss << std::string(buf.data(), cur_bytes_read);
			sum_bytes_read += cur_bytes_read;
		}
	}
	return oss.str();
}

bool PythonWrapper::InvokeCommandWithArgs(const std::string& cmd,
	std::vector<std::string>&& args,
	const std::function<void(const std::string& out, const std::string& err)>&& out_cb,
	const std::function<void(std::string& in)>&& in_cb,
	const std::function<bool()>&& run_cb) {
	std::ostringstream cmd_oss;
	cmd_oss << cmd;
	for (const auto& arg : args) {
		cmd_oss << " " << arg;
	}

	HANDLE stdout_read{};
	HANDLE stdout_write{};
	SECURITY_ATTRIBUTES stdout_sec_attr{};
	stdout_sec_attr.nLength = sizeof(stdout_sec_attr);
	stdout_sec_attr.bInheritHandle = TRUE;
	if (!CreatePipe(&stdout_read, &stdout_write, &stdout_sec_attr, 0)) {
		std::ostringstream err_oss;
		err_oss << "Error while executing python command \"" << cmd_oss.str()
			<< "\": Failed to create stdout pipe: " << GetWin32ErrMsg() << std::endl;
		out_cb("", err_oss.str());
		return false;
	}
	ScopeGuard stdout_cleanup([&]() {
		if (stdout_read) {
			CloseHandle(stdout_read);
		}
		if (stdout_write) {
			CloseHandle(stdout_write);
		}
		});
	SetHandleInformation(stdout_read, HANDLE_FLAG_INHERIT, 0);

	HANDLE stderr_read{};
	HANDLE stderr_write{};
	SECURITY_ATTRIBUTES stderr_sec_attr{};
	stderr_sec_attr.nLength = sizeof(stderr_sec_attr);
	stderr_sec_attr.bInheritHandle = TRUE;

	if (!CreatePipe(&stderr_read, &stderr_write, &stderr_sec_attr, 0)) {
		std::ostringstream err_oss;
		err_oss << "Error while executing python command \"" << cmd_oss.str()
			<< "\": Failed to create stderr pipe: " << GetWin32ErrMsg() << std::endl;
		out_cb("", err_oss.str());
		return false;
	}
	ScopeGuard stderr_cleanup([&]() {
		if (stderr_read) {
			CloseHandle(stderr_read);
		}
		if (stderr_write) {
			CloseHandle(stderr_write);
		}
		});
	SetHandleInformation(stderr_read, HANDLE_FLAG_INHERIT, 0);

	HANDLE stdin_read{};
	HANDLE stdin_write{};
	SECURITY_ATTRIBUTES stdin_sec_attr{};
	stdin_sec_attr.nLength = sizeof(stdin_sec_attr);
	stdin_sec_attr.bInheritHandle = TRUE;

	if (!CreatePipe(&stdin_read, &stdin_write, &stdin_sec_attr, 0)) {
		std::ostringstream err_oss;
		err_oss << "Error while executing python command \"" << cmd_oss.str()
			<< "\": Failed to create stdin pipe: " << GetWin32ErrMsg() << std::endl;
		out_cb("", err_oss.str());
		return false;
	}
	ScopeGuard stdin_cleanup([&]() {
		if (stdin_read) {
			CloseHandle(stdin_read);
		}
		if (stdin_write) {
			CloseHandle(stdin_write);
		}
		});
	SetHandleInformation(stdin_write, HANDLE_FLAG_INHERIT, 0);

	STARTUPINFOA si{};
	si.cb = sizeof(si);
	si.hStdOutput = stdout_write;
	si.hStdError = stderr_write;
	si.hStdInput = stdin_read;
	si.dwFlags |= STARTF_USESTDHANDLES;
	si.dwFlags |= STARTF_USESHOWWINDOW;
	si.wShowWindow = SW_HIDE;
	PROCESS_INFORMATION pi{};
	std::string env;

	{
		std::vector<char> buf(4096 * 8, 0);
		DWORD len = GetEnvironmentVariableA("PATH", buf.data(), buf.size() - 1);
		if (len > 0) {
			env = std::string("PATH=") + buf.data();
		}
		else {
			std::ostringstream err_oss;
			err_oss << "Error while executing python command \"" << cmd_oss.str()
				<< "\": Failed to get PATH env variable: " << GetWin32ErrMsg() << std::endl;
			out_cb("", err_oss.str());
			return false;
		}

		// Add git to PATH
		std::filesystem::path git_path =
			(std::filesystem::current_path() /
				"Resources/PortableGit/bin").lexically_normal();
		if (env.find(git_path.string()) == std::string::npos) {
			env += ";" + git_path.string();

			// Add updated PATH to current process's environment
			if (!SetEnvironmentVariableA("PATH", env.c_str())) {
				std::ostringstream err_oss;
				err_oss << "Error while executing python command \""
					<< cmd_oss.str()
					<< "\": Failed to add git to PATH: " << GetWin32ErrMsg()
					<< std::endl;
				out_cb("", err_oss.str());
				return false;
			}
		}

		// Add python scripts to PATH
		std::filesystem::path py_bin = (std::filesystem::current_path() /
			"Resources/Python/Scripts").lexically_normal();
		if (env.find(py_bin.string()) == std::string::npos) {
			env += ";" + py_bin.string();

			// Add updated PATH to current process's environment
			if (!SetEnvironmentVariableA("PATH", env.c_str())) {
				std::ostringstream err_oss;
				err_oss << "Error while executing python command \""
					<< cmd_oss.str()
					<< "\": Failed to add python scripts to PATH: "
					<< GetWin32ErrMsg() << std::endl;
				out_cb("", err_oss.str());
				return false;
			}
		}

		// Add scripts to PATH
		std::filesystem::path dll_bin = (std::filesystem::current_path() /
			"Resources/Scripts").lexically_normal();
		if (env.find(dll_bin.string()) == std::string::npos) {
			env += ";" + dll_bin.string();

			// Add updated PATH to current process's environment
			if (!SetEnvironmentVariableA("PATH", env.c_str())) {
				std::ostringstream err_oss;
				err_oss << "Error while executing python command \""
					<< cmd_oss.str()
					<< "\": Failed to add python scripts to PATH: "
					<< GetWin32ErrMsg() << std::endl;
				out_cb("", err_oss.str());
				return false;
			}
		}
	}

	std::string cmd_str = cmd_oss.str();
	if (!CreateProcessA(NULL,  // application name
		cmd_str.data(),
		NULL,  // process attributes
		NULL,  // thread attributes
		TRUE,  // whether to inherit parent's handles
		0,  // creation flags
		//env.data(),
		nullptr,  // environment variables
		std::filesystem::current_path().string().c_str(),  // current directory
		&si,
		&pi)) {
		std::ostringstream err_oss;
		err_oss << "Error while executing python command \"" << cmd_oss.str()
			<< "\": Failed to launch process: " << GetWin32ErrMsg();
		out_cb("", err_oss.str());
		return false;
	}
	ScopeGuard pi_cleanup([&] {
		CloseHandle(pi.hProcess);
		CloseHandle(pi.hThread);
		});

	// Set spawned process priority to low, to avoid lagging things like OBS.
	// TODO(yum) make a toggle for this.
#if 0
	if (!SetPriorityClass(pi.hProcess, BELOW_NORMAL_PRIORITY_CLASS)) {
		std::ostringstream err_oss;
		err_oss << "Error while executing python command \"" << cmd_oss.str()
			<< "\": Failed to reduce priority class: " << GetWin32ErrMsg();
		out_cb("", err_oss.str());
		return false;
	}
#endif

	// While the process is running, drain output and send input every 10 ms.
	DWORD timeout_ms = 10;
	DWORD ret = WAIT_TIMEOUT;
	while (run_cb() && ret == WAIT_TIMEOUT) {
		DWORD ret = WaitForSingleObject(pi.hProcess, timeout_ms);
		if (ret != WAIT_TIMEOUT) {
			break;
		}
		std::ostringstream stdout_oss, stderr_oss;
		stdout_oss << DrainWin32Pipe(stdout_read);
		stderr_oss << DrainWin32Pipe(stderr_read);
		out_cb(stdout_oss.str(), stderr_oss.str());

		std::string input;
		in_cb(input);
		if (input.size()) {
			DWORD cur_bytes_write = 0;
			DWORD sum_bytes_write = 0;
			std::vector<char> buf(4096, 0);
			while (sum_bytes_write < input.size() &&
				WriteFile(stdin_write, input.data() + sum_bytes_write,
					input.size() - sum_bytes_write, &cur_bytes_write, NULL)) {
				sum_bytes_write += cur_bytes_write;
			}
		}
	}
	if (!run_cb()) {
		DWORD timeout_ms = 1000 * 10;
		DWORD ret = WaitForSingleObject(pi.hProcess, timeout_ms);

		if (ret == WAIT_TIMEOUT) {
			std::ostringstream stderr_oss;
			stderr_oss << "Timed out waiting for graceful exit, killing process";
			out_cb("", stderr_oss.str());

			TerminateProcess(pi.hProcess, 0);
		}
	}

	std::ostringstream stdout_oss, stderr_oss;
	DWORD exit_code;
	if (!GetExitCodeProcess(pi.hProcess, &exit_code)) {
		stderr_oss << "Failed to get exit code: " << GetWin32ErrMsg();
	}
	if (exit_code != 0) {
		stderr_oss << "Command exited with code " << exit_code << ": "
			<< GetWin32ErrMsg();
	}

	// Close write ends of pipes. If we don't do this, the last read will block forever.
	CloseHandle(stdout_write);
	stdout_write = 0;
	CloseHandle(stderr_write);
	stderr_write = 0;

	stdout_oss << DrainWin32Pipe(stdout_read);
	stderr_oss << DrainWin32Pipe(stderr_read);
	out_cb(stdout_oss.str(), stderr_oss.str());

	return exit_code == 0;
}

bool PythonWrapper::InvokeCommandWithArgs(
	const std::string& cmd,
	std::vector<std::string>&& args,
	std::string* py_stdout, std::string* py_stderr) {

	std::ostringstream out_oss, err_oss;
	auto out_cb = [&](const std::string& out, const std::string& err) {
		out_oss << out;
		err_oss << err;
	};
	bool ret = InvokeCommandWithArgs(cmd, std::move(args), std::move(out_cb));
	if (py_stderr) {
		*py_stderr = err_oss.str();
	}
	*py_stdout = out_oss.str();
	return ret;
}

bool PythonWrapper::InvokeWithArgs(std::vector<std::string>&& args,
	std::string* py_stdout, std::string* py_stderr) {
	return InvokeCommandWithArgs("Resources/Python/python.exe",
		std::move(args), py_stdout, py_stderr);
}

bool PythonWrapper::InvokeWithArgs(std::vector<std::string>&& args,
	const std::string&& err_msg,
	wxTextCtrl* const out) {
	std::string py_stdout, py_stderr;
	if (InvokeWithArgs(std::move(args), &py_stdout, &py_stderr)) {
		Log(out, "success!\n");
		Log(out, py_stdout.c_str());
		if (!py_stdout.empty()) {
			Log(out, "\n");
		}
		Log(out, py_stderr.c_str());
		if (!py_stderr.empty()) {
			Log(out, "\n");
		}
		return true;
	}
	else {
		Log(out, "failed!\n");
		Log(out, "Error: {}: {}\n", err_msg, py_stderr);
		return false;
	}
}

bool PythonWrapper::InvokeWithArgs(std::vector<std::string>&& args,
	const std::function<void(const std::string& out, const std::string& err)>&& out_cb,
	const std::function<void(std::string& in)>&& in_cb,
	const std::function<bool()>&& run_cb) {
	return InvokeCommandWithArgs("Resources/Python/python.exe",
		std::move(args), std::move(out_cb), std::move(in_cb), std::move(run_cb));
}


std::string PythonWrapper::GetVersion() {
	std::string py_stdout, py_stderr;
    bool ok = InvokeWithArgs({ "--version" }, &py_stdout, &py_stderr);
	if (!ok) {
		wxLogError("Failed to get python version: %s", py_stderr.c_str());
	}
	return py_stdout;
}

std::string PythonWrapper::DumpMics() {
	std::string py_stdout, py_stderr;
	const std::string dump_mics_path = "Resources/Scripts/dump_mic_devices.py";
	bool ok = InvokeWithArgs({ dump_mics_path }, &py_stdout, &py_stderr);
	if (!ok) {
		wxLogError("Failed to dump mic devices: %s", py_stderr.c_str());
	}
	return py_stdout;
}

bool PythonWrapper::InstallPip(std::string* out, std::string* err) {
	std::ostringstream out_oss, err_oss;
	auto out_cb = [&](const std::string& out, const std::string& err) {
		out_oss << out;
		err_oss << err;
	};
	bool ret = InstallPip(std::move(out_cb));
	*out = out_oss.str();
	if (err) {
		*err = err_oss.str();
	}
	return ret;
}

bool PythonWrapper::InstallPip(
	const std::function<void(const std::string& out, const std::string& err)>&& out_cb,
	const std::function<void(std::string& in)>&& in_cb,
	const std::function<bool()>&& run_cb) {
	std::filesystem::path pip_flag = "Resources/Python/.pip_installed";
	if (std::filesystem::exists(pip_flag)) {
		out_cb("Pip flag exists, already installed\n", "");
		return true;
	}

	std::string pip_path = "Resources/Python/get-pip.py";
	if (!InvokeWithArgs({ pip_path }, std::move(out_cb), std::move(in_cb),
		std::move(run_cb))) {
		return false;
	}

	// Create the flag file so subsstd::chrono::milliseconds(100));equent calls don't reinstall.
	std::ofstream flag_ofs(pip_path);
	flag_ofs.close();

	return true;
}

std::future<bool> PythonWrapper::StartApp(
		const std::string& config_path,
		wxTextCtrl *out,
		const std::function<void(const std::string& out, const std::string& err)>&& out_cb,
		const std::function<void(std::string& in)>&& in_cb,
		const std::function<bool()>&& run_cb,
		const std::function<void()>&& prestart_cb) {

	return std::move(std::async(std::launch::async,
		[](
			const std::string config_path,
			wxTextCtrl *out,
			const std::function<void(const std::string& out, const std::string& err)>&& out_cb,
			const std::function<void(std::string& in)>&& in_cb,
			const std::function<bool()>&& run_cb,
			const std::function<void()>&& prestart_cb) -> bool {
				prestart_cb();

				Log(out, "DEBUG::{}:: config_path: {}\n", __func__, config_path);

				return InvokeWithArgs({
					"-u",  // Unbuffered output
					"Resources/Scripts/transcribe_v2.py",
					"--config", config_path,
					},
					std::move(out_cb),
					std::move(in_cb),
					std::move(run_cb));
		}, config_path, out, std::move(out_cb), std::move(in_cb),
			std::move(run_cb), std::move(prestart_cb)));
}

bool PythonWrapper::GenerateAnimator(
	const AppConfig& config,
	const std::string& config_path,
	const std::string& unity_animator_generated_dir,
	const std::string& unity_animator_generated_name,
	const std::string& unity_parameters_generated_name,
	const std::string& unity_menu_generated_name,
	wxTextCtrl* out) {
	// Python script locations
	std::string remove_audio_srcs_path = "Resources/Scripts/remove_audio_sources.py";
	std::string set_texture_sz_path = "Resources/Scripts/set_texture_sz.py";
	std::string libunity_path = "Resources/Scripts/libunity.py";
	std::string libtastt_path = "Resources/Scripts/libtastt.py";
	std::string generate_emotes_path = "Resources/Scripts/emotes_v2.py";
	std::string generate_params_path = "Resources/Scripts/generate_params.py";
	std::string generate_menu_path = "Resources/Scripts/generate_menu.py";
	std::string generate_shader_path = "Resources/Scripts/generate_shader.py";
	std::string shader_template_path = "Resources/Shaders/TaSTT_template.shader";
	std::string shader_lighting_template_path = "Resources/Shaders/STT_generated_template.cginc";
	std::string shader_path = "Resources/Shaders/TaSTT.shader";
	std::string shader_lighting_path = "Resources/Shaders/STT_generated.cginc";

	// Generated directory locations
	std::filesystem::path tastt_generated_dir_path =
		std::filesystem::path(config.assets_path) / unity_animator_generated_dir;
	std::filesystem::path guid_map_path =
		tastt_generated_dir_path / "guid.map";
	std::filesystem::path tastt_animations_path =
		tastt_generated_dir_path / "Animations";
	std::filesystem::path tastt_assets_path =
		tastt_generated_dir_path / "UnityAssets";
	std::filesystem::path tastt_sounds_path =
		tastt_generated_dir_path / "Sounds";
	std::filesystem::path tastt_shaders_path =
		tastt_generated_dir_path / "Shaders";
	std::filesystem::path tastt_fonts_path =
		tastt_generated_dir_path / "Fonts";
	std::filesystem::path tastt_params_path =
		tastt_generated_dir_path / unity_parameters_generated_name;
	std::filesystem::path tastt_menu_path =
		tastt_generated_dir_path / unity_menu_generated_name;
	// These are intermediate animators. We apply several transformations before
	// arriving at the final animator.
	std::filesystem::path tastt_fx0_path =
		tastt_generated_dir_path / "FX0.controller";
	std::filesystem::path tastt_fx1_path =
		tastt_generated_dir_path / "FX1.controller";
	// This is the final animator.
	std::filesystem::path tastt_animator_path =
		tastt_generated_dir_path / unity_animator_generated_name;

	const int texture_rows = (config.bytes_per_char == 1 ? 8 : 64);
	const int texture_cols = (config.bytes_per_char == 1 ? 16 : 128);
	{
		Log(out, "Generating shader for {}x{} board (pass 0)...", config.rows, config.cols);
		if (!InvokeWithArgs({ generate_shader_path,
			"--bytes_per_char", std::to_string(config.bytes_per_char),
			"--board_rows", std::to_string(config.rows),
			"--board_cols", std::to_string(config.cols),
			"--texture_rows", std::to_string(texture_rows),
			"--texture_cols", std::to_string(texture_cols),
			"--shader_template", shader_template_path,
			"--shader_path", shader_path },
			"Failed to generate shader", out)) {
			return false;
		}
	}
	{
		Log(out, "Generating shader for {}x{} board (pass 1)...", config.rows, config.cols);

		std::string py_stdout, py_stderr;
		if (!InvokeWithArgs({ generate_shader_path,
			"--bytes_per_char", std::to_string(config.bytes_per_char),
			"--board_rows", std::to_string(config.rows),
			"--board_cols", std::to_string(config.cols),
			"--texture_rows", std::to_string(texture_rows),
			"--texture_cols", std::to_string(texture_cols),
			"--shader_template", shader_lighting_template_path,
			"--shader_path", shader_lighting_path },
			"Failed to generate shader", out)) {
			return false;
		}
	}
#if 0
	{
		Log(out, "Generating emotes... ");

		std::string py_stdout, py_stderr;
		if (InvokeWithArgs({ generate_emotes_path,
			"Resources/Fonts/Emotes/",
			/*board_aspect_ratio=*/ std::to_string(6),
			/*texture_aspect_ratio=*/ std::to_string(2),
			"Resources/Fonts/Bitmaps/emotes.png",
			kEmotesPickle
			},
			&py_stdout, &py_stderr)) {
			Log(out, "success!\n");
			Log(out, py_stdout.c_str());
			if (!py_stdout.empty()) {
				Log(out, "\n");
			}
			Log(out, py_stderr.c_str());
			if (!py_stderr.empty()) {
				Log(out, "\n");
			}
		}
		else {
			Log(out, "failed!\n");
			Log(out, "stdout: {}\n", py_stdout.c_str());
			Log(out, "stderr: {}\n", py_stderr.c_str());
			return false;
		}
	}
#endif
	{
		Log(out, "Creating {}\n", tastt_generated_dir_path.string());
		std::filesystem::create_directories(tastt_generated_dir_path);
	}
	{
		Log(out, "Copying canned animations... ");
		auto opts = std::filesystem::copy_options();
		opts |= std::filesystem::copy_options::overwrite_existing;
		opts |= std::filesystem::copy_options::recursive;
		std::error_code error;
		std::filesystem::copy("Resources/Animations", tastt_animations_path, opts, error);
		if (error.value()) {
			Log(out, "failed!\n");
			Log(out, "Error: {} ({})\n", error.message(), error.value());
			return false;
		}
		Log(out, "success!\n");
	}
	{
		Log(out, "Copying canned assets... ");
		auto opts = std::filesystem::copy_options();
		opts |= std::filesystem::copy_options::overwrite_existing;
		opts |= std::filesystem::copy_options::recursive;
		std::error_code error;
		std::filesystem::copy("Resources/UnityAssets", tastt_assets_path, opts, error);
		if (error.value()) {
			Log(out, "failed!\n");
			Log(out, "Error: {} ({})\n", error.message(), error.value());
			return false;
		}
		Log(out, "success!\n");
	}
	if (!config.enable_phonemes) {
		std::string prefab_path = (std::filesystem::path(tastt_assets_path) / "World Constraint.prefab").string();
		Log(out, "Remove audio sources from prefab at {}\n", prefab_path);
		Log(out, "Removing audio sources from prefab... ");
		if (!InvokeWithArgs({ remove_audio_srcs_path,
			"--prefab", Quote(prefab_path)
			},
			"Failed to remove audio sources", out)) {
			return false;
		}
		Log(out, "succes!\n");
	}
	{
		Log(out, "Copying canned sounds... ");
		auto opts = std::filesystem::copy_options();
		opts |= std::filesystem::copy_options::overwrite_existing;
		opts |= std::filesystem::copy_options::recursive;
		std::error_code error;
		std::filesystem::copy("Resources/Sounds", tastt_sounds_path, opts, error);
		if (error.value()) {
			Log(out, "failed!\n");
			Log(out, "Error: {} ({})\n", error.message(), error.value());
			return false;
		}
		Log(out, "success!\n");
	}
	{
		Log(out, "Copying canned shaders... ");
		auto opts = std::filesystem::copy_options();
		opts |= std::filesystem::copy_options::overwrite_existing;
		opts |= std::filesystem::copy_options::recursive;
		std::error_code error;
		std::filesystem::copy("Resources/Shaders", tastt_shaders_path, opts, error);
		if (error.value()) {
			Log(out, "failed!\n");
			Log(out, "Error: {} ({})\n", error.message(), error.value());
			return false;
		}
		Log(out, "success!\n");
	}
	{
		Log(out, "Deleting shader templates... ");
		try {
			if (std::filesystem::exists(tastt_shaders_path) && std::filesystem::is_directory(tastt_shaders_path)) {
				for (const auto& entry : std::filesystem::directory_iterator(tastt_shaders_path)) {
					if (entry.is_regular_file()) {
						if (entry.path().stem().string().ends_with("_template")) {
							std::filesystem::remove(entry.path());
						}
					}
				}
			}
		}
		catch (const std::exception& e) {
			Log(out, "failed!\n");
			Log(out, "Error: {}\n", e.what());
		}
		Log(out, "success!\n");
	}
	{
		Log(out, "Copying canned fonts... ");
		auto opts = std::filesystem::copy_options();
		opts |= std::filesystem::copy_options::overwrite_existing;
		opts |= std::filesystem::copy_options::recursive;
		std::error_code error;
		std::filesystem::copy("Resources/Fonts", tastt_fonts_path, opts, error);
		if (error.value()) {
			Log(out, "failed!\n");
			Log(out, "Error: {} ({})\n", error.message(), error.value());
			return false;
		}
		Log(out, "success!\n");
	}
	if (config.bytes_per_char == 1) {
		Log(out, "Applying texture memory optimization for English speakers... ");
		std::error_code err;
		for (int i = 0; i < 8; i++) {
			std::filesystem::remove(tastt_fonts_path / ("Bitmaps/font-" + std::to_string(i) + ".png"), err);
			if (err.value()) {
				Log(out, "failed!\n");
				Log(out, "Error removing unicode texture: {} ({})\n", err.message(), err.value());
				return false;
			}
			std::filesystem::remove(tastt_fonts_path / ("Bitmaps/font-" + std::to_string(i) + ".png.meta"), err);
			if (err.value()) {
				Log(out, "failed!\n");
				Log(out, "Error removing unicode texture: {} ({})\n", err.message(), err.value());
				return false;
			}
		}
		std::filesystem::remove(tastt_fonts_path / "Bitmaps/emotes.png", err);
		if (err.value()) {
			Log(out, "failed!\n");
			Log(out, "Error removing emotes texture: {} ({})\n", err.message(), err.value());
			return false;
		}

		Log(out, "success!\n");
	}
	else {
		std::error_code err;
		std::filesystem::remove(tastt_fonts_path / ("Bitmaps/font-ascii.png"), err);
		if (err.value()) {
			Log(out, "failed!\n");
			Log(out, "Error removing unicode texture: {} ({})\n", err.message(), err.value());
			return false;
		}
		std::filesystem::remove(tastt_fonts_path / ("Bitmaps/font-ascii.png.meta"), err);
		if (err.value()) {
			Log(out, "failed!\n");
			Log(out, "Error removing unicode texture: {} ({})\n", err.message(), err.value());
			return false;
		}
	}
	{
		Log(out, "Setting texture sizes... ");
		std::filesystem::path fonts_dir = tastt_fonts_path / "Bitmaps";
		for (const auto& entry : std::filesystem::recursive_directory_iterator(fonts_dir)) {
			Log(out, "Entry get {}\n", entry.path().string());
			Log(out, "Setting size to {}\n", config.texture_sz);
			if (entry.is_regular_file() && entry.path().extension() == ".meta") {
				if (!InvokeWithArgs({ set_texture_sz_path,
					"--meta", Quote(entry.path().string()),
					"--size", std::to_string(config.texture_sz)},
					"Failed to set texture size", out)) {
					return false;
				}
			}
		}
		Log(out, "succes!\n");
	}
	{
		Log(out, "Generating guid.map... ");
		if (!InvokeWithArgs({ libunity_path, "guid_map",
			"--project_root", Quote(config.assets_path),
			"--save_to", Quote(guid_map_path), },
			"Failed to generate guid.map", out)) {
			return false;
		}
	}
	{
		Log(out, "Generating animations... ");
		if (!InvokeWithArgs({ libtastt_path, "gen_anims",
			"--gen_anim_dir", Quote(tastt_animations_path),
			"--guid_map", Quote(guid_map_path),
			"--config", Quote(config_path) },
			"Failed to generate animations", out)) {
			return false;
		}
	}
	{
		Log(out, "Generating FX layer... ");
		if (!InvokeWithArgs({ libtastt_path, "gen_fx",
			"--fx_dest", Quote(tastt_fx0_path),
			"--gen_anim_dir", Quote(tastt_animations_path),
			"--guid_map", Quote(guid_map_path),
			"--config", Quote(config_path) },
			"Failed to generate FX layer", out)) {
			return false;
		}
	}
	{
		Log(out, "Merging with user animator... ");
		if (!InvokeWithArgs({ libunity_path, "merge",
			"--fx0", Quote(config.fx_path),
			"--fx1", Quote(tastt_fx0_path),
			"--fx_dest", Quote(tastt_fx1_path), },
			"Failed to merge animators", out)) {
			return false;
		}
	}
	{
		Log(out, "Setting noop animations... ");
		if (!InvokeWithArgs({ libunity_path, "set_noop_anim",
			"--fx0", Quote(tastt_fx1_path),
			"--fx_dest", Quote(tastt_animator_path),
			"--gen_anim_dir", Quote(tastt_animations_path),
			"--guid_map", Quote(guid_map_path), },
			"Failed to set noop animations", out)) {
			return false;
		}
	}
	{
		Log(out, "Generating avatar parameters... ");
		if (!InvokeWithArgs({ generate_params_path,
			"--old_params", Quote(config.params_path),
			"--new_params", Quote(tastt_params_path),
			"--config", Quote(config_path) },
			"Failed to generate avatar parameters", out)) {
			return false;
		}
	}
	{
		Log(out, "Generating avatar menu... ");
		if (!InvokeWithArgs({ generate_menu_path,
			"--old_menu", Quote(config.menu_path),
			"--new_menu", Quote(tastt_menu_path) },
			"Failed to generate avatar menu", out)) {
			return false;
		}
	}
	if (config.clear_osc) {
		std::filesystem::path osc_path = "C:/Users";
		osc_path /= wxGetUserName().ToStdString();
		osc_path /= "AppData/LocalLow/VRChat/vrchat/OSC";
		osc_path = osc_path.lexically_normal();
		Log(out, "OSC configs are stored at {}\n", osc_path.string());
		Log(out, "Clearing OSC configs... ");

		if (std::filesystem::is_directory(osc_path)) {
			std::error_code err;
			if (std::filesystem::remove_all(osc_path, err)) {
				Log(out, "success!\n");
			}
			else {
				Log(out, "failed!\n");
				Log(out, "Error: {} ({})\n", err.message(), err.value());
			}
		}
		else {
			Log(out, "OSC configs do not exist at {}, assuming already "
				"cleared!\n", osc_path.string());
		}
	}

	Log(out, "Done!\n");
	return true;
}

