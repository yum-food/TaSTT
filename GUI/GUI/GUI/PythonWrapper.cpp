#include "Logging.h"
#include "PythonWrapper.h"

#include <stdio.h>

#include <filesystem>
#include <sstream>

using ::Logging::Log;

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

	wxString path;
	if (!wxGetEnv("PATH", &path)) {
		*py_stderr = "Failed to get PATH";
		return false;
	}
	if (!wxSetEnv("PATH", path + ";Resources/PortableGit/bin")) {
		*py_stderr = "Failed to append to PATH";
		return false;
	}

	wxArrayString cmd_stdout;
	wxArrayString cmd_stderr;
	long result = wxExecute(cmd_oss.str(), cmd_stdout, cmd_stderr, /*flags=*/0);
	std::ostringstream cmd_stdout_oss;
	for (const auto& line : cmd_stdout) {
		if (!cmd_stdout_oss.str().empty()) {
			cmd_stdout_oss << std::endl;
		}
		cmd_stdout_oss << line;
	}
	std::ostringstream cmd_stderr_oss;
	for (const auto& line : cmd_stderr) {
		if (!cmd_stderr_oss.str().empty()) {
			cmd_stderr_oss << std::endl;
		}
		cmd_stderr_oss << line;
	}
	if (result == -1) {
		std::ostringstream err_oss;
		err_oss << "Error while executing python command \"" << cmd_oss.str() << "\": Failed to launch process" << std::endl;
		err_oss << cmd_stdout_oss.str() << std::endl;
		err_oss << cmd_stderr_oss.str() << std::endl;
		if (py_stderr) {
			*py_stderr = err_oss.str();
		}
		return false;
	} else if (result) {
		if (py_stderr) {
			std::ostringstream err_oss;
			err_oss << "Error while executing python command \"" << cmd_oss.str() <<
				"\"" << std::endl <<
				"Process returned " << result << ": " << std::endl <<
				cmd_stdout_oss.str() << std::endl <<
				cmd_stderr_oss.str() << std::endl;
			*py_stderr = err_oss.str();
		}
		return false;
	}

	*py_stdout = cmd_stdout_oss.str();
	if (py_stderr) {
		*py_stderr = cmd_stderr_oss.str();
	}
	return true;
}

bool PythonWrapper::InvokeWithArgs(std::vector<std::string>&& args,
	std::string* py_stdout, std::string* py_stderr) {
	return InvokeCommandWithArgs("Resources/Python/python.exe",
		std::move(args), py_stdout, py_stderr);
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

bool PythonWrapper::InstallPip(std::string* out) {
	std::string result;

	std::string pip_path = "Resources/Python/get-pip.py";
    return InvokeWithArgs({ pip_path }, out);
}

wxProcess* PythonWrapper::StartApp(
	std::function<void(wxProcess* proc, int ret)>&& exit_callback,
	const std::string& mic, const std::string& lang, const std::string& model,
	const std::string& chars_per_sync, const std::string& bytes_per_char,
	int rows, int cols, int window_duration_s, bool enable_local_beep,
	bool use_cpu) {
	return InvokeAsyncWithArgs({
		"-u",
		"Resources/Scripts/transcribe.py",
		"--mic", mic,
		"--lang", lang,
		"--model", model,
		"--chars_per_sync", chars_per_sync,
		"--bytes_per_char", bytes_per_char,
		"--enable_local_beep", enable_local_beep ? "1" : "0",
		"--rows", std::to_string(rows),
		"--cols", std::to_string(cols),
		"--window_duration_s", std::to_string(window_duration_s),
		"--cpu", use_cpu ? "1" : "0",
		},
		std::move(exit_callback));
}

// Wrap the filesystem path in quotes, escaping intermediate quotes with \\.
std::string Quote(const std::filesystem::path& p) {
	std::ostringstream oss;
	oss << std::quoted(p.string());
	return oss.str();
}

bool PythonWrapper::GenerateAnimator(
	const std::filesystem::path& unity_assets_path,
	const std::filesystem::path& unity_animator_path,
	const std::filesystem::path& unity_parameters_path,
	const std::filesystem::path& unity_menu_path,
	const std::string& unity_animator_generated_dir,
	const std::string& unity_animator_generated_name,
	const std::string& unity_parameters_generated_name,
	const std::string& unity_menu_generated_name,
	const std::string& chars_per_sync,
	const std::string& bytes_per_char,
	const int rows,
	const int cols,
	wxTextCtrl* out) {
	// Python script locations
	std::string libunity_path = "Resources/Scripts/libunity.py";
	std::string libtastt_path = "Resources/Scripts/libtastt.py";
	std::string generate_params_path = "Resources/Scripts/generate_params.py";
	std::string generate_menu_path = "Resources/Scripts/generate_menu.py";
	std::string generate_shader_path = "Resources/Scripts/generate_shader.py";
	std::string shader_template_path = "Resources/Shaders/TaSTT_template.shader";
	std::string shader_path = "Resources/Shaders/TaSTT.shader";

	// Generated directory locations
	std::filesystem::path tastt_generated_dir_path =
		std::filesystem::path(unity_assets_path) / unity_animator_generated_dir;
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
		Log(out, "Generating shader for {}x{} board...", rows, cols);

		std::string py_stdout, py_stderr;
		if (InvokeWithArgs({ generate_shader_path,
			"--bytes_per_char", bytes_per_char,
			"--rows", std::to_string(rows),
			"--cols", std::to_string(cols),
			"--shader_template", shader_template_path,
			"--shader_path", shader_path },
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
			wxLogError("Failed to generate shader: %s", py_stderr.c_str());
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
		std::string py_stdout, py_stderr;
		if (PythonWrapper::InvokeWithArgs({ libunity_path, "guid_map",
			"--project_root", Quote(unity_assets_path),
			"--save_to", Quote(guid_map_path), },
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
			wxLogError("Failed to generate guid.map: %s", py_stderr.c_str());
			Log(out, "failed!\n");
			return false;
		}
	}
	{
		Log(out, "Generating animations... ");
		std::string py_stdout, py_stderr;
		if (InvokeWithArgs({ libtastt_path, "gen_anims",
			"--gen_anim_dir", Quote(tastt_animations_path),
			"--guid_map", Quote(guid_map_path),
			"--chars_per_sync", chars_per_sync,
			"--bytes_per_char", bytes_per_char,
			"--rows", std::to_string(rows),
			"--cols", std::to_string(cols)},
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
			wxLogError("Failed to generate animations: %s", py_stderr.c_str());
			Log(out, "failed!\n");
			return false;
		}
	}
	{
		Log(out, "Generating FX layer... ");
		std::string py_stdout, py_stderr;
		if (InvokeWithArgs({ libtastt_path, "gen_fx",
			"--fx_dest", Quote(tastt_fx0_path),
			"--gen_anim_dir", Quote(tastt_animations_path),
			"--guid_map", Quote(guid_map_path),
			"--chars_per_sync", chars_per_sync,
			"--bytes_per_char", bytes_per_char,
			"--rows", std::to_string(rows),
			"--cols", std::to_string(cols)},
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
			wxLogError("Failed to generate FX layer: %s", py_stderr.c_str());
			Log(out, "failed!\n");
			return false;
		}
	}
	{
		Log(out, "Adding enable/disable toggle... ");
		std::string py_stdout, py_stderr;
		if (InvokeWithArgs({ libunity_path, "add_toggle",
			"--fx0", Quote(tastt_fx0_path),
			"--fx_dest", Quote(tastt_fx1_path),
			"--gen_anim_dir", Quote(tastt_animations_path),
			"--guid_map", Quote(guid_map_path), },
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
			wxLogError("Failed to add enable/disable toggle: %s", py_stderr.c_str());
			Log(out, "failed!\n");
			return false;
		}
	}
	{
		Log(out, "Merging with user animator... ");
		std::string py_stdout, py_stderr;
		if (InvokeWithArgs({ libunity_path, "merge",
			"--fx0", Quote(unity_animator_path),
			"--fx1", Quote(tastt_fx1_path),
			"--fx_dest", Quote(tastt_fx2_path), },
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
			wxLogError("Failed to merge animators: %s", py_stderr.c_str());
			Log(out, "failed!\n");
			return false;
		}
	}
	{
		Log(out, "Setting noop animations... ");
		std::string py_stdout, py_stderr;
		if (InvokeWithArgs({ libunity_path, "set_noop_anim",
			"--fx0", Quote(tastt_fx2_path),
			"--fx_dest", Quote(tastt_animator_path),
			"--gen_anim_dir", Quote(tastt_animations_path),
			"--guid_map", Quote(guid_map_path), },
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
			wxLogError("Failed to set noop animations: %s", py_stderr.c_str());
			Log(out, "failed!\n");
			return false;
		}
	}
	{
		Log(out, "Generating avatar parameters... ");
		std::string py_stdout, py_stderr;
		if (InvokeWithArgs({ generate_params_path,
			"--old_params", Quote(unity_parameters_path),
			"--new_params", Quote(tastt_params_path),
			"--chars_per_sync", chars_per_sync,
			"--bytes_per_char", bytes_per_char },
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
			wxLogError("Failed to generate avatar parameters: %s", py_stderr.c_str());
			Log(out, "failed!\n");
			return false;
		}
	}
	{
		Log(out, "Generating avatar menu... ");
		std::string py_stdout, py_stderr;
		// No idea why, but inlining this into `InvokeWithArgs` confuses the compiler.
		std::vector<std::string> args = { generate_menu_path,
			"--old_menu", Quote(unity_menu_path),
			"--new_menu", Quote(tastt_menu_path), };
		if (InvokeWithArgs( std::move(args),
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
			wxLogError("Failed to generate avatar menu: %s", py_stderr.c_str());
			Log(out, "failed!\n");
			return false;
		}
	}

	Log(out, "Done!\n");
	return true;
}

