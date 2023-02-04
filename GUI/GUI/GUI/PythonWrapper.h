#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <wx/process.h>

#include "Config.h"

#include <filesystem>
#include <string>
#include <vector>

/*
 * This class wraps interactions with the embedded Python interpreter.
*/
namespace PythonWrapper
{
	// Invoke the interpreter asynchronously with the given arguments.
	// When the process exits, `exit_callback` runs.
	// The caller is responsible for deleting wxProcess.
	wxProcess* InvokeAsyncWithArgs(std::vector<std::string>&& args,
		std::function<void(wxProcess* proc, int ret)>&& exit_callback);

	// Invoke a command on the shell with arguments.
	// On error, sets `out` to an error message and returns false.
	bool InvokeCommandWithArgs(const std::string& cmd,
		std::vector<std::string>&& args,
		std::string* py_stdout,
		std::string* py_stderr = NULL);

	// Invoke the interpreter with arguments.
	// On error, sets `out` to an error message and returns false.
	bool InvokeWithArgs(std::vector<std::string>&& args, std::string* py_stdout,
		std::string* py_stderr = NULL);

	bool InvokeWithArgs(std::vector<std::string>&& args,
		const std::string&& err_msg, wxTextCtrl* out);

	// Execute python --version.
	std::string GetVersion();

	// Executes dump_mic_devices.py.
	std::string DumpMics();

	// Execute get-pip.py.
	bool InstallPip(std::string* out);

	// TODO(yum) both StartApp and GenerateAnimator should be
	// parameterized with config files instead of these ever-growing lists of
	// parameters. We could persist those files so settings would persist across
	// app restarts.
	wxProcess* StartApp(
		std::function<void(wxProcess* proc, int ret)>&& exit_callback,
		const TranscriptionAppConfig& config);

	bool GenerateAnimator(
		const UnityAppConfig& config,
		const std::string& unity_animator_generated_dir,
		const std::string& unity_animator_generated_name,
		const std::string& unity_parameters_generated_name,
		const std::string& unity_menu_generated_name,
		wxTextCtrl* out);
};

