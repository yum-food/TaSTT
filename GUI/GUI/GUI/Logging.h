#pragma once

#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <format>
#include <string>
#include <string_view>

namespace Logging {
	// Remove personally identifying information (PII) from str.
	//
	// For example, this translates "C:/Users/foo/Desktop" to "C:/Users/*****/Desktop".
	std::string HidePII(const std::string&& str, const std::string& replacement = "*****");

	// Provides a simple Python format()-like interface to wxTextCtrl.
	// Ex: Log(my_textctrl_, "{}\n", "Hello, world!");
	template<typename... Args>
	void Log(wxTextCtrl* frame, std::string_view format, Args&&... args) {
		const std::string raw = std::vformat(format, std::make_format_args(args...));
		const std::string masked = HidePII(std::move(raw));
		frame->AppendText(masked);
	}
}

