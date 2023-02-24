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
	// TODO(yum) oatpp::base::Environment::destroy() accesses invalid memory if
	// it's called after serving a connection. Probably a bug in my code. Fix it
	// and then use a pattern like
	//	init();
	//	ScopeGuard cleanup([]() { destroy(); });
	static bool did_init = false;
	if (!did_init) {
		oatpp::base::Environment::init();
	}
	//ScopeGuard oatpp_env_cleanup([]() { oatpp::base::Environment::destroy(); });

	OATPP_CREATE_COMPONENT(
		std::shared_ptr<oatpp::network::ServerConnectionProvider>,
		serverConnectionProvider)([&] {
			return oatpp::network::tcp::server::ConnectionProvider::createShared(
				{ "0.0.0.0", port_, oatpp::network::Address::IP_4 });
		}());

    OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::data::mapping::ObjectMapper>, apiObjectMapper)([] {
        return oatpp::parser::json::mapping::ObjectMapper::createShared();
	}());

    OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::web::server::HttpRouter>, httpRouter)([] {
        return oatpp::web::server::HttpRouter::createShared();
	}());
	httpRouter.getObject()->addController(std::make_shared<AppController>(apiObjectMapper.getObject()));

    OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::network::ConnectionHandler>, serverConnectionHandler)([&] {
		return oatpp::web::server::HttpConnectionHandler::createShared(httpRouter.getObject());
	}());

	oatpp::network::Server server(serverConnectionProvider.getObject(), serverConnectionHandler.getObject());
	Log(out_, "Server running on port {}\n",
		static_cast<const char*>(serverConnectionProvider.getObject()->getProperty("port").getData()));

	server.run(std::function<bool()>([run]() { return *run == true; }));
}
