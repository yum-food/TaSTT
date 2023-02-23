#include "BrowserSource.h"

#include "oatpp/network/Server.hpp"

BrowserSource::BrowserSource(uint16_t port)
	: port_(port)
{
	AppComponent components;
	OATPP_COMPONENT(std::shared_ptr<oatpp::web::server::HttpRouter>, router);
	router->addController(std::make_shared<AppController>());

}
