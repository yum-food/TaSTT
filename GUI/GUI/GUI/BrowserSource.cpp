#include "BrowserSource.h"
#include "Logging.h"
#include "ScopeGuard.h"
#include "WebCommon.h"
#include "WebServer.h"

using ::Logging::Log;

BrowserSource::BrowserSource(uint16_t port, wxTextCtrl *out, Transcript *transcript)
	: port_(port), out_(out), transcript_(transcript)
{}

void BrowserSource::Run(volatile bool* run)
{
	WebServer::WebServer ws(out_, port_);

	ws.RegisterPathHandler("GET", "/",
		[&](int& status_code, std::string& payload,
			WebServer::ContentType& type) -> void {
			auto html_path = std::filesystem::path("Resources/BrowserSource/index.html");

			std::ifstream html_ifs(html_path);
			std::vector<char> resp(4096 * 16, 0);
			html_ifs.read(resp.data(), resp.size());

			std::string html(resp.data());
			resp.clear();

			size_t pos = 0;
			std::string key = "%PORT%";
			std::string value = std::to_string(port_);
			while ((pos = html.find("%PORT%", pos)) != std::string::npos) {
				html.replace(pos, key.size(), value);
				pos += value.size();
			}

			status_code = 200;
			payload = html;
			type = WebServer::HTML;
		});

	ws.RegisterPathHandler("GET", "/api/transcript",
		[&](int& status_code, std::string& payload,
			WebServer::ContentType& type) -> void {
			status_code = 200;
			
			std::ostringstream transcript_oss;
			std::vector<std::string> transcript = transcript_->Get();
			// Hack: escape transcription to work inside JSON blob.
			for (auto& segment : transcript) {
				size_t pos;
				while ((pos = segment.find('"')) != std::string::npos) {
					segment[pos] = '\'';
				}
				transcript_oss << segment;
			}

			std::ostringstream resp_oss;
			resp_oss << "{";
			resp_oss << "\"transcript\":\"" << transcript_oss.str() << "\"";
			resp_oss << "}";
			payload = resp_oss.str();
			type = WebServer::JSON;

			//Log(out_, "Serving transcript to port {}: {}\n", port_, transcript_oss.str());
		});

	if (!ws.Run(run)) {
		Log(out_, "Failed to launch browser source!\n");
	}
	return;
}
