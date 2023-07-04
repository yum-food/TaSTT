#include "HTTPParser.h"
#include "Logging.h"
#include "ScopeGuard.h"

#include <sstream>
#include <string.h>
#include <string_view>

using ::Logging::Log;

namespace WebServer {
	HTTPParser::HTTPParser() {}

	namespace {
		constexpr const char kLineDelim[] = "\r\n";
		constexpr const char kHeadersDelim[] = "\r\n\r\n";
		constexpr const char kRfcLWS[] = " \t\r\n";
	};

	bool HTTPParser::Parse(const std::string& raw_http, std::string& err) {
		std::ostringstream err_oss;
		ScopeGuard err_oss_flush([&]() { err += err_oss.str(); });

		ParserState state = PARSER_STATE_START_LINE;
		size_t pos = 0;
		while (pos < raw_http.length()) {
			size_t end;
			switch (state) {
			case PARSER_STATE_START_LINE:
				end = raw_http.find(kLineDelim, pos);
				break;
			case PARSER_STATE_HEADERS:
				end = raw_http.find(kHeadersDelim, pos);
				break;
			case PARSER_STATE_PAYLOAD:
				end = raw_http.length();
				break;
			}
			ScopeGuard advance_pos([&]() { pos = end + 1; });
			if (end == std::string::npos) {
				err_oss << "Failed to parse HTTP in state " << state << ": No delimiter!" << std::endl;
				return false;
			}
			std::string_view segment(raw_http.data() + pos, end - pos);
			if (!ParseSegment(segment, state, err)) {
				return false;
			}
		}
		return true;
	}

	const std::string& HTTPParser::GetMethod() const {
		return method_;
	}

	const std::string& HTTPParser::GetPath() const {
		return path_;
	}

	bool HTTPParser::GetHeader(const std::string& header, std::string& value) const {
		auto iter = headers_.find(header);
		if (iter == headers_.end()) {
			return false;
		}
		value = iter->second;
		return true;
	}

	const std::map<std::string, std::string>& HTTPParser::GetHeaders() const {
		return headers_;
	}

	const std::string& HTTPParser::GetPayload() const {
		return payload_;
	}

	bool HTTPParser::ParseSegment(
		const std::string_view segment,
		ParserState& state,
		std::string& err) {
		std::ostringstream err_oss;
		ScopeGuard err_oss_flush([&]() { err += err_oss.str(); });
		switch (state) {
		case PARSER_STATE_START_LINE:
			return ParseStartLine(segment, state, err);
		case PARSER_STATE_HEADERS:
			return ParseHeaders(segment, state, err);
		case PARSER_STATE_PAYLOAD:
			return ParsePayload(segment, state, err);
		}
	}

	enum StartLineParserState {
		START_LINE_PARSER_STATE_METHOD,
		START_LINE_PARSER_STATE_PATH,
		START_LINE_PARSER_STATE_VERSION,
		START_LINE_PARSER_STATE_END,
	};
	// Source: RFC 2616 section 5.1.1.
	bool HTTPParser::ParseStartLine(
		const std::string_view segment,
		ParserState& state,
		std::string& err) {
		std::ostringstream err_oss;
		ScopeGuard err_oss_flush([&]() { err += err_oss.str(); });

		// Request-Line = Method SP Request-URI SP HTTP-Version CRLF
		// SP == space.
		// Thus we expect to see exactly three space-delimited chunks.
		StartLineParserState cur_state = START_LINE_PARSER_STATE_METHOD;
		size_t pos = 0;
		while (pos < segment.length()) {
			size_t end = segment.find(' ', pos);
			if (end == std::string::npos) {
				end = segment.length();
			}
			ScopeGuard advance_pos([&]() { pos = end + 1; });

			std::string_view cur_segment(segment.data() + pos, end - pos);
			switch (cur_state) {
			case START_LINE_PARSER_STATE_METHOD:
				method_ = cur_segment;
				cur_state = START_LINE_PARSER_STATE_PATH;
				continue;
			case START_LINE_PARSER_STATE_PATH:
				path_ = cur_segment;
				cur_state = START_LINE_PARSER_STATE_VERSION;
				continue;
			case START_LINE_PARSER_STATE_VERSION:
				// TODO(yum) check this
				cur_state = START_LINE_PARSER_STATE_END;
				continue;
			case START_LINE_PARSER_STATE_END:
				err_oss << "Invalid start line: has too many parts: " << segment << std::endl;
				return false;
			}
		}
		if (cur_state != START_LINE_PARSER_STATE_END) {
			err_oss << "Invalid start line: missing parts: " << segment << std::endl;
			return false;
		}

		state = PARSER_STATE_HEADERS;
		return true;
	}

	// Source: RFC 2616 section 4.2.
	bool HTTPParser::ParseHeaders(
		const std::string_view segment,
		ParserState& state,
		std::string& err) {
		std::ostringstream err_oss;
		ScopeGuard err_oss_flush([&]() { err += err_oss.str(); });

		// From the RFC:
		//	message-header = field-name ":" [ field-value ]
		//	field-name = token
		//	field-value = *(field-content | LWS)
		//	field-content = <the OCTETs making up the field - value
		//		and consisting of either * TEXT or combinations
		//		of token, separators, and quoted-string>
		// Takewaways:
		//  * field-name is guaranteed to not be preceded by whitespace
		//  * field-name is guaranteed to be followed by ":"
		//  * field-value may be preceded by LWS
		//  * multi-line field-values are guaranteed to start with either ' '
		//    or '\t'
		size_t pos = 0;
		std::string key, value;
		while (pos < segment.length()) {
			// Divide into lines.
			size_t end = segment.find(kLineDelim, pos);
			if (end == std::string::npos) {
				end = segment.length();
			}
			ScopeGuard advance_pos([&]() { pos = end + 1; });

			std::string_view line = segment.substr(pos, end - pos);
			if (line.empty()) {
				continue;
			}

			// Lengthen the current line to cover multi-line header.
			while (end + 1 < segment.length() &&
				(segment[end + 1] == ' ' || segment[end + 1] == '\t')) {
				end = segment.find("\r\n", end + 1);
			}

			size_t sep = line.find(':');
			if (sep == std::string::npos) {
				err_oss << "Invalid header: No ':' delimiter: " << segment << std::endl;
				return false;
			}

			std::string_view key = line.substr(0, sep);
			size_t key_start = key.find_first_not_of(kRfcLWS);
			size_t key_end = key.find_last_not_of(kRfcLWS);
			key = key.substr(key_start, (key_end - key_start) + 1);
			// Value may contain interspersed LWS (linear whitespace).
			// Could scrub it out, but not necessary for our purposes.
			std::string_view value = line.substr(sep + 1);
			size_t value_start = value.find_first_not_of(kRfcLWS);
			size_t value_end = value.find_last_not_of(kRfcLWS);
			value = value.substr(value_start, (value_end - value_start) + 1);

			headers_[std::string(key)] = value;
		}

		state = PARSER_STATE_PAYLOAD;
		return true;
	}

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-parameter"
	bool HTTPParser::ParsePayload(
		const std::string_view segment,
		ParserState& state,
		std::string& err) {

    const char kScuffedHeadersDelim[] = "\n\r\n";
    if (!segment.starts_with(kScuffedHeadersDelim)) {
      return true;
    }

		payload_ = segment.substr(strlen(kScuffedHeadersDelim));
		return true;
	}
#pragma clang diagnostic pop
}
