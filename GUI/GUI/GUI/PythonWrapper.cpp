#include "PythonWrapper.h"

#include <stdio.h>

#include <sstream>

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
		wxLogFatalError("Failed to get python version: %s", result.c_str());
	}
	return result;
}

bool PythonWrapper::InstallPip(std::string* out) {
	std::string result;

	std::string pip_path = "Resources/Python/get-pip.py";
    return InvokeWithArgs({ pip_path }, out);
}
