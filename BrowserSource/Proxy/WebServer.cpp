#include "HTTPMapper.h"
#include "HTTPParser.h"
#include "Logging.h"
#include "ScopeGuard.h"
#include "WebServer.h"

#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>

using ::Logging::Log;

namespace WebServer {
	WebServer::WebServer(uint16_t port)
		: port_(port)
	{
		default_handler_ =
			[](int& status_code, std::string& payload,
			ContentType& type) -> void {
			status_code = 404;
			payload = "404: No route to URI";
			type = HTML;
		};
	}

	bool WebServer::RegisterPathHandler(const std::string& method,
		const std::string& path, handler_t&& handler) {
		dispatch_key_t key = GetDispatchKey(method, path);
		if (dispatch_map_.contains(key)) {
			Log("Failed to register path handler at {} {}: "
				"Handler already exists!\n", method, path);
			return false;
		}

		dispatch_map_[key] = std::move(handler);
		return true;
	}

	void WebServer::RegisterDefaultHandler(handler_t&& handler) {
		default_handler_ = std::move(handler);
	}

	bool WebServer::Run(volatile bool* run) {
		int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
		if (sock == -1) {
			Log("Failed to create socket: {}\n", strerror(errno));
			return false;
		}
		ScopeGuard sock_cleanup([sock]() { close(sock); });

		sockaddr_in saddr;
		saddr.sin_family = AF_INET;
		saddr.sin_addr.s_addr = INADDR_ANY;
		saddr.sin_port = htons(port_);
		if (bind(sock, (sockaddr*)&saddr, sizeof(saddr)) == -1) {
			Log("Failed to bind to port {}: {}\n", port_, strerror(errno));
			return false;
		}

		// enable non-blocking mode
		int flags = fcntl(sock, F_GETFL, 0);
		if (flags == -1) {
			Log("Failed to get socket flags for port {}: {}\n", port_, strerror(errno));
			return false;
		}
		if (fcntl(sock, F_SETFL, flags | O_NONBLOCK) == -1) {
			Log("Failed to enable non-blocking mode on socket {}: {}\n", port_, strerror(errno));
			return false;
		}

		if (listen(sock, SOMAXCONN) == -1) {
			Log("Failed to listen on port {}: {}\n", port_, strerror(errno));
			return false;
		}

    struct sockaddr_in bound_addr;
    socklen_t len = sizeof(bound_addr);
    if (getsockname(sock, (struct sockaddr *)&bound_addr, &len) == -1) {
        Log("Failed to get socket name: {}\n", strerror(errno));
        return false;
    }
    char ipstr[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &bound_addr.sin_addr, ipstr, sizeof(ipstr));

		Log("Server running on IP {} port {}\n", ipstr, port_);

		sockaddr_in peer_addr;
		int accept_cnt = 0;
		while (*run) {
			socklen_t peer_addr_sz = sizeof(peer_addr);
			int csock = accept(sock, (sockaddr*)&peer_addr, &peer_addr_sz);
			if (csock == -1) {
				if (errno == EWOULDBLOCK) {
					std::this_thread::sleep_for(std::chrono::milliseconds(10));
					continue;
				}
				Log("Accept failed: {}\n", strerror(errno));
				return false;
			}

      // enable non-blocking mode
      int flags = fcntl(csock, F_GETFL, 0);
      if (flags == -1) {
        Log("Failed to get socket flags for client on port {}: {}\n", port_, strerror(errno));
        return false;
      }
      if (fcntl(csock, F_SETFL, flags | O_NONBLOCK) == -1) {
        Log("Failed to enable non-blocking mode on client socket {}: {}\n", port_, strerror(errno));
        return false;
      }

			// Periodically cull dead connections to prevent runaway memory usage.
			++accept_cnt;
			if (accept_cnt % 10 == 0) {
				std::vector<std::future<void>> alive_conn;
				for (size_t i = 0; i < connections_.size(); i++) {
					if (connections_[i].valid()) {
						continue;
					}
					alive_conn.push_back(std::move(connections_[i]));
				}
				//Log("Culled {} dead connections\n", connections_.size() - alive_conn.size());
				connections_ = std::move(alive_conn);
				accept_cnt = 0;  // Prevent overflow
			}

			const auto& dispatch_map = dispatch_map_;
			const auto& default_handler = default_handler_;
			connections_.push_back(std::async(std::launch::async,
				[csock, peer_addr, run, dispatch_map, default_handler]() -> void {
				ScopeGuard csock_cleanup([csock]() { close(csock); });
				char peer_ip_str[INET_ADDRSTRLEN]{};
				inet_ntop(AF_INET, &peer_addr.sin_addr, peer_ip_str, sizeof(peer_ip_str));

				std::string buf(4096 * 16, 0);
				int cur_bytes_read = 0;
				int sum_bytes_read = 0;

				// Drain socket until we see a valid HTTP message.
				while (*run) {
					cur_bytes_read = recv(csock, buf.data() + sum_bytes_read,
						buf.size() - (1 + sum_bytes_read), /*flags=*/0);
					if (cur_bytes_read == -1) {
						if (errno == EWOULDBLOCK || errno == EAGAIN) {
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
							std::this_thread::sleep_for(std::chrono::milliseconds(10));
							continue;
						}
						break;
					}
					sum_bytes_read += cur_bytes_read;
					if (cur_bytes_read == 0) {
						break;
					}
				}
				if (cur_bytes_read == -1) {
					Log("Failed to read client socket: {}\n", strerror(errno));
					return;
				}
				// Edge case: Server was stopped in the middle of serving a request.
				if (!*run) {
          Log("Server stop requested, bail out!\n");
					return;
				}
				buf.resize(sum_bytes_read);

				// Parse HTTP. Expect this to succeed, since we only exit the loop once the
				// request parses.
				// TODO(yum) this repeats work! The loop already parsed the request.
				HTTPParser p;
				std::string err;
				if (!p.Parse(buf, err)) {
					Log("Failed to parse client request: {}\n", err);
					Log("Offending request:\n{}\n", buf);
					return;
				}

				// Find the dispatch handler for the requested method and path.
				dispatch_key_t dispatch_key = GetDispatchKey(p.GetMethod(), p.GetPath());
				auto iter = dispatch_map.find(dispatch_key);
				handler_t handler;
				if (iter == dispatch_map.end()) {
					handler = default_handler;
				} else {
					handler = iter->second;
				}

				// Generate a response.
				int status_code;
				std::string payload = p.GetPayload();
				ContentType type;
				handler(status_code, payload, type);
				std::string response = HTTPMapper().Map(status_code, payload, type);

				// Send the response.
				if (send(csock, response.data(), response.size(), /*flags=*/0) == -1) {
					Log("Failed to send response to client: {}\n", strerror(errno));
					return;
				}

				// Implicitly close the connection by exiting scope. We
				// completely ignore keep-alive requests for now. Browsers
				// should handle this well, there are many reasons why
				// keep-alive requests may be ignored, such as transient
				// network failures.
			}));
		}
		return true;
	}
}
