#include "Logging.h"
#include "Utils.h"
#include "WebServer.h"

#include <chrono>
#include <iostream>
#include <mutex>
#include <set>
#include <sstream>
#include <unordered_map>

using ::Logging::Log;

class Sessions {
  public:
    struct SessionInfo {
      std::chrono::time_point<std::chrono::steady_clock> creation_time;
      std::string transcript;
    };

    // Create a new session and return its identifier.
    std::string CreateSession()
    {
      // Each char in RandomString has 5.9 bits of entropy, so 16 chars gives
      // us 94 bits of entropy - unlikely to ever collide or be guessed.
      std::string id = RandomString(16);

      SessionInfo info;
      info.creation_time = std::chrono::steady_clock::now();

      std::scoped_lock l(mu_);
      sessions_[id] = info;

      return id;
    }

    // Look up a session by ID. The session info is copied into `info`.
    bool GetSession(const std::string& id, SessionInfo& info)
    {
      std::scoped_lock l(mu_);
      auto session_iter = sessions_.find(id);
      if (session_iter == sessions_.end()) {
        return false;
      }
      info = session_iter->second;
      return true;
    }

    void SetSession(const std::string& id, SessionInfo&& info)
    {
      std::scoped_lock l(mu_);
      sessions_[id] = std::move(info);
    }

    void PruneSessions(std::chrono::duration<double> max_age)
    {
      auto now = std::chrono::steady_clock::now();
      std::set<std::string> pruned_sessions;
      {
        std::scoped_lock l(mu_);
        auto session_iter = sessions_.begin();
        while (session_iter != sessions_.end()) {
          std::chrono::duration<double> age = now - session_iter->second.creation_time;
          if (age > max_age) {
            pruned_sessions.insert(session_iter->first);
            sessions_.erase(session_iter++);
          } else {
            ++session_iter;
          }
        }
      }
      if (!pruned_sessions.empty()) {
        std::ostringstream sessions_oss;
        for (auto& session : pruned_sessions) {
          sessions_oss << ' ' << session;
        }
        Log("Pruned sessions{}\n", sessions_oss.str());
      }
    }

  private:

    std::mutex mu_;
    std::unordered_map<std::string, SessionInfo> sessions_;
};

int main () {
  WebServer::WebServer ws(8080);
  Sessions s;

  // TODO rm
  {
    Sessions::SessionInfo info;
    info.creation_time = std::chrono::steady_clock::now();
    s.SetSession("test_session", std::move(info));
  }

	ws.RegisterDefaultHandler(
		[&](int& status_code, std::string& payload,
			WebServer::ContentType& type) -> void {

			std::string resp = "Hello, world!\n";

			status_code = 200;
			payload = resp;
			type = WebServer::HTML;
		});

	ws.RegisterPathHandler("GET", "/api/v0/create_session",
		[&](int& status_code, std::string& payload,
			WebServer::ContentType& type) -> void {

      std::string id = s.CreateSession();
      // Each char in RandomString has 5.9 bits of entropy, so 16 chars gives
      // us 94 bits of entropy - unlikely to ever collide or be guessed.
			std::string resp = "{session_id:" + id + "}";

      Log("Created session {}\n", id);

			status_code = 200;
			payload = resp;
			type = WebServer::JSON;
		});

	ws.RegisterPathHandler("POST", "/api/v0/set_transcript",
		[&](int& status_code, std::string& payload,
			WebServer::ContentType& type) -> void {

      // Payload must look like "$session_id $transcript"
      size_t space_pos = payload.find(' ');
      std::string session_id;
      std::string transcript;
      if (space_pos == std::string::npos) {
        session_id = payload;
      } else {
        session_id = payload.substr(0, space_pos);
        transcript = payload.substr(space_pos + 1);
      }

      Log("Updating session {}\n", session_id);

      Sessions::SessionInfo info;
      if (!s.GetSession(session_id, info)) {
        status_code = 404;
        payload = "Failed to find session " + session_id;
        type = WebServer::HTML;
        return;
      }

      info.transcript = transcript;
      s.SetSession(session_id, std::move(info));

      Log("Updated transcript of session {}: {}\n", session_id, transcript);

			status_code = 200;
			payload.clear();
			type = WebServer::HTML;
		});

	ws.RegisterPathHandler("GET", "/api/v0/get_transcript",
		[&](int& status_code, std::string& payload,
			WebServer::ContentType& type) -> void {

      // Payload must look like "$session_id $transcript"
      std::string session_id = payload;

      Sessions::SessionInfo info;
      if (!s.GetSession(session_id, info)) {
        status_code = 404;
        payload = "Failed to find session " + session_id;
        type = WebServer::HTML;
        return;
      }

			status_code = 200;
			payload = info.transcript;
			type = WebServer::HTML;
		});

  bool run = true;
  auto server_thd = std::async(std::launch::async, [&]() -> void {
      ws.Run(&run);
      });
  auto prune_thd = std::async(std::launch::async, [&]() -> void {
      while (run) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        s.PruneSessions(std::chrono::days(1));
      }
      });

  Log("Started webserver. Press enter to exit.\n");
  std::string line;
  while (std::getline(std::cin, line)) {
    break;
  }
  run = false;

  // Wait for server to exit.
  Log("Joining server thread...\n");
  server_thd.get();
  Log("Done!\n");

  return 0;
}
