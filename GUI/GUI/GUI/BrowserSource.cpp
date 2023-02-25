#include "BrowserSource.h"
#include "Logging.h"
#include "ScopeGuard.h"
#include "WebServer.h"

using ::Logging::Log;
//using ::WebServer::WebServer;

BrowserSource::BrowserSource(uint16_t port, wxTextCtrl *out, Transcript *transcript)
	: port_(port), out_(out), transcript_(transcript)
{}

void BrowserSource::Run(volatile bool* run)
{
	WebServer::WebServer ws(out_, port_);
	if (!ws.Run(run)) {
		Log(out_, "Failed to launch browser source!\n");
	}
	return;
}
