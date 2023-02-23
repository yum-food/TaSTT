#include "BrowserSource.h"
#include "Logging.h"

#include "oatpp/network/Server.hpp"

BrowserSource::BrowserSource(uint16_t port, wxTextCtrl *out)
	: port_(port), out_(out)
{}

void BrowserSource::Run(volatile bool* run)
{
	AppComponent components;

	OATPP_COMPONENT(std::shared_ptr<oatpp::web::server::HttpRouter>, router);
	router->addController(std::make_shared<AppController>());

	OATPP_COMPONENT(std::shared_ptr<oatpp::network::ConnectionHandler>, connectionHandler);

	OATPP_COMPONENT(std::shared_ptr<oatpp::network::ServerConnectionProvider>, connectionProvider);

	oatpp::network::Server server(connectionProvider, connectionHandler);

	OATPP_LOGI("BrowserSource", "Server running on port %s",
		connectionProvider->getProperty("port").getData());

	server.run(std::function<bool()>([run]() { return *run == true; }));
}
