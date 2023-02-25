#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "HTTPParser.h"
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
			// TODO(yum) periodically cull connections_.
			wxTextCtrl* out = out_;
			const auto& dispatch_map = dispatch_map_;
			connections_.push_back(std::async(std::launch::async, [csock, peer_addr, out, run, dispatch_map]() -> void {
				ScopeGuard csock_cleanup([csock]() { closesocket(csock); });
				char peer_ip_str[INET_ADDRSTRLEN]{};
				inet_ntop(AF_INET, &peer_addr.sin_addr, peer_ip_str, sizeof(peer_ip_str));
				Log(out, "Connection get: peer: {}:{}\n", peer_ip_str, ntohs(peer_addr.sin_port));

				std::string buf(4096 * 16, 0);
				int cur_bytes_read = 0;
				int sum_bytes_read = 0;

				bool abort_client = false;
				while (*run) {
					cur_bytes_read = recv(csock, buf.data() + sum_bytes_read,
						buf.size() - (1 + sum_bytes_read), /*flags=*/0);
					if (cur_bytes_read == SOCKET_ERROR) {
						if (WSAGetLastError() == WSAEWOULDBLOCK) {
							// Client may try to keep the connection open,
							// so see if there's a complete request in the
							// buffer. If so, terminate the recv loop.
							HTTPParser p;
							std::string err;
							if (p.Parse(buf, err)) {
								// In general we should verify that we got a
								// full message, but since we only need to
								// support GET, this is unnecessary.
								cur_bytes_read = 0;
								break;
							}
							continue;
						}
						break;
					}
					sum_bytes_read += cur_bytes_read;
					if (cur_bytes_read == 0) {
						break;
					}
				}
				if (abort_client) {
					return;
				}
				if (cur_bytes_read == SOCKET_ERROR) {
					Log(out, "Failed to read client socket: {}\n", WSAGetLastError());
					return;
				}
				buf.resize(sum_bytes_read);

				HTTPParser p;
				std::string err;
				if (!p.Parse(buf, err)) {
					Log(out, "Failed to parse client request: {}\n", err);
					Log(out, "Offending request:\n{}\n", buf);
					return;
				}

				dispatch_key_t dispatch_key = GetDispatchKey(p.GetMethod(), p.GetPath());
				auto iter = dispatch_map.find(dispatch_key);
				if (iter == dispatch_map.end()) {
					Log(out, "No route defined for client request: {} {}\n",
						p.GetMethod(), p.GetPath());
					return;
				}

				// TODO(yum) send a response
			}));
		}
		return true;
	}
}
