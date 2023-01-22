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

#if 0
	class Log {
	public:
		static Log& Get() {
			static Log l;
			return l;
		}

		bool Write(const std::string& text);

	private:
		Log() {}

		bool Open(const std::string& path);

		int fd_;
	};
#endif

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
		// Limit log to 10 MB to avoid runaway memory usage.
		const int max_frame_len_bytes = 10 * 1000 * 1000;
		if (frame->GetLastPosition() > max_frame_len_bytes) {
			frame->Remove(0, frame->GetLastPosition() - max_frame_len_bytes);
		}
	}
}

