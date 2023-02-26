#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <stdint.h>

#include <functional>
#include <future>
#include <map>
#include <mutex>
#include <string>
#include <vector>

#include "Logging.h"
#include "WebCommon.h"

namespace WebServer {
	class WebServer {
	public:
		WebServer(wxTextCtrl *out, std::uint16_t port);

		typedef std::function<void(
			int& status_code,
			std::string& payload,
			ContentType& type)> handler_t;

		bool RegisterPathHandler(const std::string& method,
			const std::string& path, handler_t&& handler);
		void RegisterDefaultHandler(handler_t&& handler);

		bool Run(volatile bool* run);

	private:
		// Dispatch requests by mapping from (method, path) to handler.
		// Dispatch key is (method, path) in that order.
		typedef std::tuple<std::string, std::string> dispatch_key_t;
		static inline dispatch_key_t GetDispatchKey(const std::string& method, const std::string& path)
		{
			return dispatch_key_t(method, path);
		}

		typedef std::map<dispatch_key_t, handler_t> dispatch_map_t;
		dispatch_map_t dispatch_map_;
		handler_t default_handler_;

		wxTextCtrl* const out_;
		const uint16_t port_;

		std::vector<std::future<void>> connections_;
	};
}

