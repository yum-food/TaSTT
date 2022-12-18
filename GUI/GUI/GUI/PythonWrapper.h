#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <string>
#include <vector>

/*
 * This class wraps interactions with the embedded Python interpreter.
*/
class PythonWrapper
{
public:
	// Invoke the interpreter with arguments.
	// On error, sets `out` to an error message and returns false.
	bool InvokeWithArgs(std::vector<std::string>&& args, std::string* out);

	// Execute python --version.
	std::string GetVersion();

	// Execute get-pip.py.
	bool InstallPip(std::string* out);
};

