#pragma once

#include "WebCommon.h"

#include <string>

namespace WebServer {

	class HTTPMapper {
	public:
		HTTPMapper() {}
		virtual ~HTTPMapper() {}

		std::string Map(int status_code,
			const std::string& payload, ContentType type);
	};

	class HTTPMapperHTML : public HTTPMapper {
	public:
		HTTPMapperHTML() {}
		virtual ~HTTPMapperHTML() {}

		std::string Map(int status_code,
			const std::string& payload);
	};

	class HTTPMapperJSON : public HTTPMapper {
	public:
		HTTPMapperJSON() {}
		virtual ~HTTPMapperJSON() {}

		std::string Map(int status_code,
			const std::string& payload);
	};
}
