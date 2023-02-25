#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "ScopeGuard.h"
#include "WebServer.h"

#include <stdint.h>
#include <WinSock2.h>
#include <ws2tcpip.h>

using ::Logging::Log;

namespace WebServer {
	WebServer::WebServer(wxTextCtrl* out, uint16_t port)
		: out_(out), port_(port)
	{}

	bool WebServer::RegisterPathHandler(const std::string& method,
		const std::string& path, handler_t&& handler) {
		dispatch_key_t key = GetDispatchKey(method, path);
		if (dispatch_map_.contains(key)) {
			Log(out_, "Failed to register path handler at {} {}: "
				"Handler already exists!\n", method, path);
			return false;
		}

		dispatch_map_[key] = std::move(handler);
		return true;
	}

	bool WebServer::Run(volatile bool* run) {
		WSADATA wsaData;
		int result = WSAStartup(/*version=*/MAKEWORD(2, 2), &wsaData);
		if (result) {
			Log(out_, "Failed to start winsock: {}\n", result);
			return false;
		}
		ScopeGuard wsa_cleanup([]() { WSACleanup(); });

		SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
		if (sock == INVALID_SOCKET) {
			Log(out_, "Failed to create socket: {}\n", WSAGetLastError());
			return false;
		}
		ScopeGuard sock_cleanup([sock]() { closesocket(sock); });

		sockaddr_in saddr;
		saddr.sin_family = AF_INET;
		saddr.sin_addr.s_addr = INADDR_ANY;  // TODO(yum) loopback?
		saddr.sin_port = htons(port_);
		if (bind(sock, (sockaddr*)&saddr, sizeof(saddr)) == SOCKET_ERROR) {
			Log(out_, "Failed to bind to port {}: {}\n", port_, WSAGetLastError());
			return false;
		}

		u_long enable_nonblock = 1;
		if (ioctlsocket(sock, FIONBIO, &enable_nonblock) == SOCKET_ERROR) {
			Log(out_, "Failed to enable non-blocking socket: {}\n", WSAGetLastError());
			return false;
		}

		if (listen(sock, SOMAXCONN) == SOCKET_ERROR) {
			Log(out_, "Failed to listen on port {}: {}\n", port_, WSAGetLastError());
			return false;
		}

		Log(out_, "Server running on port {}\n", port_);

		sockaddr_in peer_addr;
		while (*run) {
			int peer_addr_sz = sizeof(peer_addr);
			SOCKET csock = accept(sock, (sockaddr*)&peer_addr, &peer_addr_sz);
			if (csock == INVALID_SOCKET) {
				int err = WSAGetLastError();
				if (err == WSAEWOULDBLOCK) {
					std::this_thread::sleep_for(std::chrono::milliseconds(10));
					continue;
				}
				Log(out_, "Accept failed: {}\n", WSAGetLastError());
				return false;
			}
			ScopeGuard csock_cleanup([csock]() { closesocket(csock); });
			char peer_ip_str[INET_ADDRSTRLEN]{};
			inet_ntop(AF_INET, &peer_addr.sin_addr, peer_ip_str, sizeof(peer_ip_str));
			Log(out_, "Connection get: peer: {}:{}\n", peer_ip_str, ntohs(peer_addr.sin_port));
			// TODO(yum) parse and send a response
		}

		return true;
	}
}
