#include "HTTPMapper.h"

#include <sstream>
#include <map>

namespace {
	// Source: RFC 2616 section 6.1.1
	const std::map<int, std::string> kStatusCodeToString{
		{100, "Continue" },
		{101, "Switching Protocols"},
		{200, "OK"},
		{201, "Created"},
		{202, "Accepted"},
		{203, "Non-Authoritative Information"},
		{204, "No Content"},
		{205, "Reset Content"},
		{206, "Partial Content"},
		{300, "Multiple Choices"},
		{301, "Moved Permanently"},
		{302, "Found"},
		{303, "See Other"},
		{304, "Not Modified"},
		{305, "Use Proxy"},
		{307, "Temporary Redirect"},
		{400, "Bad Request"},
		{401, "Unauthorized"},
		{402, "Payment Required"},
		{403, "Forbidden"},
		{404, "Not Found"},
		{405, "Method Not Allowed"},
		{406, "Not Acceptable"},
	};
}

namespace WebServer {
	std::string HTTPMapper::Map(const int status_code,
		const std::string& payload, const ContentType type) {
		switch (type) {
		case HTML:
			return HTTPMapperHTML().Map(status_code, payload);
		case JSON:
			return HTTPMapperJSON().Map(status_code, payload);
		}
	}

	std::string HTTPMapperHTML::Map(const int status_code,
		const std::string& payload) {
		std::ostringstream oss;
		// This might throw and crash the app, but that's ok, just don't use an unsupported code.
		oss << "HTTP/1.1 " << status_code << " " << kStatusCodeToString.at(status_code) << "\r\n";
		oss << "Content-Type: text/html\r\n";
		oss << "Content-Length: " << std::to_string(payload.size()) << "\r\n";
		oss << "\r\n";
		oss << payload;
		return oss.str();
	}

	std::string HTTPMapperJSON::Map(const int status_code,
		const std::string& payload) {
		std::ostringstream oss;
		// This might throw and crash the app, but that's ok, just don't use an unsupported code.
		oss << "HTTP/1.1 " << status_code << " " << kStatusCodeToString.at(status_code) << "\r\n";
		oss << "Content-Type: application/json\r\n";
		oss << "Content-Length: " << std::to_string(payload.size()) << "\r\n";
		oss << "\r\n";
		oss << payload;
		return oss.str();
	}
}