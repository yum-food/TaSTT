#pragma once

#include <filesystem>
#include <string>

// Wrap the filesystem path in quotes, escaping intermediate quotes with \\.
inline std::string Quote(const std::filesystem::path& p) {
	std::ostringstream oss;
	oss << std::quoted(p.string());
	return oss.str();
}

inline std::string Unquote(const std::string& s) {
	std::istringstream iss(s);

	std::string result;
	iss >> quoted(result);

	return result;
}
