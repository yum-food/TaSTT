#include "BrowserSource.h"
#include "Logging.h"
#include "ScopeGuard.h"

#include "oatpp/network/Server.hpp"

using ::Logging::Log;

BrowserSource::BrowserSource(uint16_t port, wxTextCtrl *out)
	: port_(port), out_(out)
{}

void BrowserSource::Run(volatile bool* run)
{
	oatpp::base::Environment::init();
	ScopeGuard oatpp_env_cleanup([]() { oatpp::base::Environment::destroy(); });

	AppComponent components(port_);

	OATPP_COMPONENT(std::shared_ptr<oatpp::web::server::HttpRouter>, router);
	router->addController(std::make_shared<AppController>());

	OATPP_COMPONENT(std::shared_ptr<oatpp::network::ConnectionHandler>, connectionHandler);

	OATPP_COMPONENT(std::shared_ptr<oatpp::network::ServerConnectionProvider>, connectionProvider);

	oatpp::network::Server server(connectionProvider, connectionHandler);

	Log(out_, "Server running on port {}\n",
		static_cast<const char*>(connectionProvider->getProperty("port").getData()));

	server.run(std::function<bool()>([run]() { return *run == true; }));
}
