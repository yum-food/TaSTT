#include "PythonWrapper.h"

#include <stdio.h>

#include <sstream>

class PythonProcess : public wxProcess {
public:
	PythonProcess(std::function<void(wxProcess* proc, int ret)>&& exit_callback) : exit_cb_(exit_callback) {}

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

bool PythonWrapper::InvokeWithArgs(std::vector<std::string>&& args, std::string* out) {
	std::ostringstream cmd_oss;
	cmd_oss << "Resources/Python/python.exe";
	for (const auto& arg : args) {
		cmd_oss << " " << arg;
	}

	wxArrayString cmd_output_ary;
	long result = wxExecute(cmd_oss.str(), cmd_output_ary);
	std::ostringstream cmd_out_oss;
	for (const auto& line : cmd_output_ary) {
		if (!cmd_out_oss.str().empty()) {
			cmd_out_oss << std::endl;
		}
		cmd_out_oss << line;
	}
	if (result == -1) {
		std::ostringstream err_oss;
		err_oss << "Error while executing python command \"" << cmd_oss.str() << "\": Failed to launch process";
		*out = err_oss.str();
		return false;
	} else if (result) {
		std::ostringstream err_oss;
		err_oss << "Error while executing python command \"" << cmd_oss.str() << "\": Process returned " << result << ": " << cmd_out_oss.str();
		*out = err_oss.str();
		return false;
	}

	*out = cmd_out_oss.str();
	return true;
}


std::string PythonWrapper::GetVersion() {
	std::string result;
    bool ok = InvokeWithArgs({ "--version" }, &result);
	if (!ok) {
		wxLogError("Failed to get python version: %s", result.c_str());
		result = "";
	}
	return result;
}

std::string PythonWrapper::DumpMics() {
	std::string result;
	const std::string dump_mics_path = "Resources/Scripts/dump_mic_devices.py";
	bool ok = InvokeWithArgs({ dump_mics_path }, &result);
	if (!ok) {
		wxLogError("Failed to dump mic devices: %s", result.c_str());
		result = "";
	}
	return result;
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
		"Resources/Scripts/transcribe.py",
		"--mic", mic,
		"--lang", lang,
		"--model", model,
		},
		std::move(exit_callback));
}

