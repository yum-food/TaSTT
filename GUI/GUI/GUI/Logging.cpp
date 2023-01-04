#include "Logging.h"

#include <regex>
#include <string>

std::string Logging::HidePII(const std::string&& str,
	const std::string& replacement) {
	try {
		std::regex c_users("(C:\\\\+Users\\\\+)[a-zA-Z0-9_ ]+");
		std::string real_replacement = "$1" + replacement;
		return std::regex_replace(str, c_users, real_replacement);
	}
	catch (const std::exception& e) {
		wxLogFatalError(e.what());
	}
	wxLogFatalError("Unhandled regex error (HidePII)");
	return "";  // Compiler thinks we can get here (we can't) and prints a warning.
}
