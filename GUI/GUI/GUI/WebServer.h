#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <stdint.h>

#include <functional>
#include <map>
#include <string>

#include "Logging.h"
#include "WebCommon.h"

namespace WebServer {
	class WebServer {
	public:
		WebServer(wxTextCtrl *out, std::uint16_t port);

		typedef std::function<void(
			const std::string& method,
			const std::string& path,
			std::string& payload,
			ContentType& type)> handler_t;

		bool RegisterPathHandler(const std::string& method,
			const std::string& path, handler_t&& handler);

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

		wxTextCtrl* const out_;
		const uint16_t port_;
	};
}

