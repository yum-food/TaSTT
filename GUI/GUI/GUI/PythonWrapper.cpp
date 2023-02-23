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
	// TODO(yum) we should hide the console & stream output to a friendlier interface
	int pid = wxExecute(cmd_oss.str(), wxEXEC_ASYNC, p);

	if (!pid) {
		delete p;
		p = nullptr;
	}

	return p;
}

bool PythonWrapper::InvokeCommandWithArgs(
	const std::string& cmd,
	std::vector<std::string>&& args,
	std::string* py_stdout, std::string* py_stderr) {
	std::ostringstream cmd_oss;
	cmd_oss << cmd;
	for (const auto& arg : args) {
		cmd_oss << " " << arg;
	}

	HANDLE stdout_read{};
	HANDLE stdout_write{};
	SECURITY_ATTRIBUTES sec_attr{};
	sec_attr.nLength = sizeof(sec_attr);
	sec_attr.bInheritHandle = TRUE;
	if (!CreatePipe(&stdout_read, &stdout_write, &sec_attr, 0)) {
		if (py_stderr) {
			std::ostringstream err_oss;
			err_oss << "Error while executing python command \"" << cmd_oss.str()
				<< "\": Failed to create stdout pipe" << std::endl;
			*py_stderr = err_oss.str();
		}
		return false;
	}
	ScopeGuard stdout_cleanup([&]() {
		CloseHandle(stdout_read);
		CloseHandle(stdout_write);
		});

	HANDLE stderr_read{};
	HANDLE stderr_write{};
	if (!CreatePipe(&stderr_read, &stderr_write, &sec_attr, 0)) {
		if (py_stderr) {
			std::ostringstream err_oss;
			err_oss << "Error while executing python command \"" << cmd_oss.str()
				<< "\": Failed to create stderr pipe" << std::endl;
			*py_stderr = err_oss.str();
		}
		return false;
	}
	ScopeGuard stderr_cleanup([&]() {
		CloseHandle(stderr_read);
		CloseHandle(stderr_write);
		});

	STARTUPINFOA si{};
	si.cb = sizeof(si);
	si.hStdOutput = stdout_write;
	si.hStdError = stderr_write;
	PROCESS_INFORMATION pi{};
	std::string path = "Resources/PortableGit/bin";
	std::string env = "PATH=" + path;
	//std::string env;

	//std::string tmp_cmd = "Get-ChildItem";

	std::string cmd_str = cmd_oss.str();
	if (!CreateProcessA(NULL,  // application name
		cmd_str.data(),
		//tmp_cmd.data(),
		NULL,  // process attributes
		NULL,  // thread attributes
		FALSE,  // whether to inherit parent's handles
		0,  // creation flags
		env.data(),
		NULL,  // current directory (use parent's)
		&si,
		&pi)) {
		if (py_stderr) {
			std::ostringstream err_oss;
			err_oss << "Error while executing python command \"" << cmd_oss.str()
				<< "\": Failed to launch process" << std::endl;
			*py_stderr = err_oss.str();
		}
		return false;
	}
	ScopeGuard pi_cleanup([&] {
		CloseHandle(pi.hProcess);
		CloseHandle(pi.hThread);
		});

	std::ostringstream stdout_oss, stderr_oss;
	std::vector<char> buf(4096, 0);
	DWORD bytes_read = 0;
	while (ReadFile(si.hStdOutput, buf.data(), buf.size(), &bytes_read, NULL) && bytes_read > 0) {
		stdout_oss << std::string(buf.data(), bytes_read);
	}
	bytes_read = 0;
	while (ReadFile(si.hStdError, buf.data(), buf.size(), &bytes_read, NULL) && bytes_read > 0) {
		stderr_oss << std::string(buf.data(), bytes_read);
	}

	WaitForSingleObject(pi.hProcess, INFINITE);

	// TODO(yum) retrieve exit code

	*py_stdout = stdout_oss.str();
	if (py_stderr) {
		*py_stderr = stderr_oss.str();
	}
	return true;
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
		wxLogError("%s: %s", err_msg, py_stderr.c_str());
		Log(out, "failed!\n");
		return false;
	}
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
	std::string result;

	std::filesystem::path pip_flag = "Resources/Python/.pip_installed";
	if (std::filesystem::exists(pip_flag)) {
		return true;
	}

	std::string pip_path = "Resources/Python/get-pip.py";
	if (!InvokeWithArgs({ pip_path }, out, err)) {
		return false;
	}

	// Create the flag file so subsstd::chrono::milliseconds(100));equent calls don't reinstall.
	std::ofstream flag_ofs(pip_path);
	flag_ofs.close();

	return true;
}

wxProcess* PythonWrapper::StartApp(
	std::function<void(wxProcess* proc, int ret)>&& exit_callback,
	const AppConfig& config) {
	return InvokeAsyncWithArgs({
		"-u",  // Unbuffered output
		"Resources/Scripts/transcribe.py",
		"--mic", config.microphone,
		"--lang", config.language,
		"--model", config.model,
		"--chars_per_sync", std::to_string(config.chars_per_sync),
		"--bytes_per_char", std::to_string(config.bytes_per_char),
		"--button", Quote(config.button),
		"--enable_local_beep", config.enable_local_beep ? "1" : "0",
		"--rows", std::to_string(config.rows),
		"--cols", std::to_string(config.cols),
		"--window_duration_s", config.window_duration,
		"--cpu", config.use_cpu ? "1" : "0",
		"--use_builtin", config.use_builtin ? "1" : "0",
		"--emotes_pickle", kEmotesPickle,
		},
		std::move(exit_callback));
}

bool PythonWrapper::GenerateAnimator(
	const AppConfig& config,
	const std::string& unity_animator_generated_dir,
	const std::string& unity_animator_generated_name,
	const std::string& unity_parameters_generated_name,
	const std::string& unity_menu_generated_name,
	wxTextCtrl* out) {
	// Python script locations
	std::string libunity_path = "Resources/Scripts/libunity.py";
	std::string libtastt_path = "Resources/Scripts/libtastt.py";
	std::string generate_emotes_path = "Resources/Scripts/emotes_v2.py";
	std::string generate_params_path = "Resources/Scripts/generate_params.py";
	std::string generate_menu_path = "Resources/Scripts/generate_menu.py";
	std::string generate_shader_path = "Resources/Scripts/generate_shader.py";
	std::string shader_template_path = "Resources/Shaders/TaSTT_template.shader";
	std::string shader_lighting_template_path = "Resources/Shaders/TaSTT_lighting_template.cginc";
	std::string shader_path = "Resources/Shaders/TaSTT.shader";
	std::string shader_lighting_path = "Resources/Shaders/TaSTT_lighting.cginc";

	// Generated directory locations
	std::filesystem::path tastt_generated_dir_path =
		std::filesystem::path(config.assets_path) / unity_animator_generated_dir;
	std::filesystem::path guid_map_path =
		tastt_generated_dir_path / "guid.map";
	std::filesystem::path tastt_animations_path =
		tastt_generated_dir_path / "Animations";
	std::filesystem::path tastt_assets_path =
		tastt_generated_dir_path / "UnityAssets";
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
	std::filesystem::path tastt_fx2_path =
		tastt_generated_dir_path / "FX2.controller";
	// This is the final animator.
	std::filesystem::path tastt_animator_path =
		tastt_generated_dir_path / unity_animator_generated_name;

	{
		Log(out, "Generating shader for {}x{} board (pass 0)...", config.rows, config.cols);
		if (!InvokeWithArgs({ generate_shader_path,
			"--bytes_per_char", std::to_string(config.bytes_per_char),
			"--rows", std::to_string(config.rows),
			"--cols", std::to_string(config.cols),
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
			"--rows", std::to_string(config.rows),
			"--cols", std::to_string(config.cols),
			"--shader_template", shader_lighting_template_path,
			"--shader_path", shader_lighting_path },
			"Failed to generate shader", out)) {
			return false;
		}
	}
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
			wxLogError("Failed to generate emotes: %s", py_stderr.c_str());
			Log(out, "failed!\n");
			return false;
		}
	}
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
			wxLogError("Failed to copy animations: %s (%d)", error.message(), error.value());
			Log(out, "failed!\n");
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
			wxLogError("Failed to copy animations: %s (%d)", error.message(), error.value());
			Log(out, "failed!\n");
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
			wxLogError("Failed to copy animations: %s (%d)", error.message(), error.value());
			Log(out, "failed!\n");
			return false;
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
			wxLogError("Failed to copy animations: %s (%d)", error.message(), error.value());
			Log(out, "failed!\n");
			return false;
		}
		Log(out, "success!\n");
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
			"--chars_per_sync", std::to_string(config.chars_per_sync),
			"--bytes_per_char", std::to_string(config.bytes_per_char),
			"--rows", std::to_string(config.rows),
			"--cols", std::to_string(config.cols)},
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
			"--chars_per_sync", std::to_string(config.chars_per_sync),
			"--bytes_per_char", std::to_string(config.bytes_per_char),
			"--rows", std::to_string(config.rows),
			"--cols", std::to_string(config.cols) },
			"Failed to generate FX layer", out)) {
			return false;
		}
	}
	{
		Log(out, "Adding enable/disable toggle... ");
		if (!InvokeWithArgs({ libunity_path, "add_toggle",
			"--fx0", Quote(tastt_fx0_path),
			"--fx_dest", Quote(tastt_fx1_path),
			"--gen_anim_dir", Quote(tastt_animations_path),
			"--guid_map", Quote(guid_map_path), },
			"Failed to add enable/disable toggle", out)) {
			return false;
		}
	}
	{
		Log(out, "Merging with user animator... ");
		if (!InvokeWithArgs({ libunity_path, "merge",
			"--fx0", Quote(config.fx_path),
			"--fx1", Quote(tastt_fx1_path),
			"--fx_dest", Quote(tastt_fx2_path), },
			"Failed to merge animators", out)) {
			return false;
		}
	}
	{
		Log(out, "Setting noop animations... ");
		if (!InvokeWithArgs({ libunity_path, "set_noop_anim",
			"--fx0", Quote(tastt_fx2_path),
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
			"--chars_per_sync", std::to_string(config.chars_per_sync),
			"--bytes_per_char", std::to_string(config.bytes_per_char) },
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
				wxLogError("Failed to delete OSC configs: %s", err.message());
				Log(out, "failed!\n");
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

