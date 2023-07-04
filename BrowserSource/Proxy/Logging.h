#pragma once

#pragma once

#include <fmt/core.h>
#include <iostream>
#include <string>
#include <string_view>

namespace Logging {
	// Usage: Log("{}\n", "Hello, world!");
	template<typename... Args>
	void Log(std::string_view format, Args&&... args) {
		const std::string raw = fmt::vformat(format, fmt::make_format_args(args...));

    std::cout << raw;
	}
}

