#include "PythonWrapper.h"

#include <stdio.h>

#include <filesystem>
#include <sstream>

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

bool PythonWrapper::InvokeWithArgs(std::vector<std::string>&& args,
	std::string* py_stdout, std::string* py_stderr) {
	std::ostringstream cmd_oss;
	cmd_oss << "Resources/Python/python.exe";
	for (const auto& arg : args) {
		cmd_oss << " " << arg;
	}

	wxArrayString cmd_stdout;
	wxArrayString cmd_stderr;
	long result = wxExecute(cmd_oss.str(), cmd_stdout, cmd_stderr);
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
		err_oss << "Error while executing python command \"" << cmd_oss.str() << "\": Failed to launch process";
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
	const std::string& mic, const std::string& lang, const std::string& model) {
	return InvokeAsyncWithArgs({
		"-u",
		"Resources/Scripts/transcribe.py",
		"--mic", mic,
		"--lang", lang,
		"--model", model,
		},
		std::move(exit_callback));
}

bool PythonWrapper::GenerateAnimator(
	const std::string& unity_assets_path,
	const std::string& unity_animator_path,
	const std::string& unity_parameters_path,
	const std::string& unity_menu_path,
	const std::string& unity_animator_generated_dir,
	const std::string& unity_animator_generated_name,
	const std::string& unity_parameters_generated_name,
	const std::string& unity_menu_generated_name,
	wxTextCtrl* out) {
	// Python script locations
	std::string libunity_path = "Resources/Scripts/libunity.py";
	std::string libtastt_path = "Resources/Scripts/libtastt.py";

	// Generated directory locations
	std::filesystem::path tastt_generated_dir_path =
		std::filesystem::path(unity_assets_path) / unity_animator_generated_dir;
	std::filesystem::path guid_map_path =
		tastt_generated_dir_path / "guid.map";
	std::filesystem::path tastt_animations_path =
		tastt_generated_dir_path / "Animations";
	std::filesystem::path tastt_animator_path =
		tastt_generated_dir_path / unity_animator_generated_name;
	std::filesystem::path tastt_params_path =
		tastt_generated_dir_path / unity_parameters_generated_name;
	std::filesystem::path tastt_menu_path =
		tastt_generated_dir_path / unity_menu_generated_name;

	{
		out->AppendText("Generating guid.map... ");
		std::string py_stdout, py_stderr;
		if (InvokeWithArgs({ libunity_path, "guid_map",
			"--project_root", unity_assets_path,
			"--save_to", guid_map_path.string() },
			&py_stdout, &py_stderr)) {
			out->AppendText("success!\n");
			out->AppendText(py_stdout.c_str());
			out->AppendText(py_stderr.c_str());
		}
		else {
			wxLogError("Failed to generate guid.map: %s", py_stderr.c_str());
			out->AppendText("failed!\n");
		}
	}
	{
		out->AppendText("Generating animations... ");
		std::string py_stdout, py_stderr;
		if (InvokeWithArgs({ libtastt_path, "gen_anims",
			"--gen_anim_dir", tastt_animations_path.string(),
			"--guid_map", guid_map_path.string() },
			&py_stdout, &py_stderr)) {
			out->AppendText("success!\n");
			out->AppendText(py_stdout.c_str());
			out->AppendText(py_stderr.c_str());
		}
		else {
			wxLogError("Failed to generate animations: %s", py_stderr.c_str());
			out->AppendText("failed!\n");
		}
	}

	return true;
}

