#pragma once

#include <string>
#include <map>

namespace WebServer {

	// A simple HTTP/1.1 message parser based on RFC 2616.
	class HTTPParser
	{
	public:
		HTTPParser();

		bool Parse(const std::string& raw_http, std::string& err);

		const std::string& GetMethod() const;
		const std::string& GetPath() const;
		bool GetHeader(const std::string& header, std::string& value) const;
		const std::map<std::string, std::string>& GetHeaders() const;
		const std::string& GetPayload() const;

	private:
		enum ParserState {
			PARSER_STATE_START_LINE,
			PARSER_STATE_HEADERS,
			PARSER_STATE_PAYLOAD,
		};

		bool ParseSegment(
			const std::string_view segment,
			ParserState& state,
			std::string& err);
		bool ParseStartLine(
			const std::string_view segment,
			ParserState& state,
			std::string& err);
		bool ParseHeaders(
			const std::string_view segment,
			ParserState& state,
			std::string& err);
		bool ParsePayload(
			const std::string_view segment,
			ParserState& state,
			std::string& err);

		std::string method_;
		std::string path_;
		std::map<std::string, std::string> headers_;
		std::string payload_;
	};
}
