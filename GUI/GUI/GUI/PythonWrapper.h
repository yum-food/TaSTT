#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <wx/process.h>

#include <string>
#include <vector>

/*
 * This class wraps interactions with the embedded Python interpreter.
*/
class PythonWrapper
{
public:

	// Invoke the interpreter asynchronously with the given arguments.
	// When the process exits, `exit_callback` runs.
	// The caller is responsible for deleting wxProcess.
	wxProcess* InvokeAsyncWithArgs(std::vector<std::string>&& args,
		std::function<void(wxProcess* proc, int ret)>&& exit_callback);

	// Invoke the interpreter with arguments.
	// On error, sets `out` to an error message and returns false.
	bool InvokeWithArgs(std::vector<std::string>&& args, std::string* out);

	// Execute python --version.
	std::string GetVersion();

	// Execute get-pip.py.
	bool InstallPip(std::string* out);

	wxProcess* StartApp(
		std::function<void(wxProcess* proc, int ret)>&& exit_callback,
		const std::string& mic, const std::string& lang);
};

