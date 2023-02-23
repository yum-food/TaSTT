#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "oatpp/core/macro/codegen.hpp"
#include "oatpp/core/macro/component.hpp"
#include "oatpp/core/Types.hpp"
#include "oatpp/network/tcp/server/ConnectionProvider.hpp"
#include "oatpp/parser/json/mapping/ObjectMapper.hpp"
#include "oatpp/web/server/api/ApiController.hpp"
#include "oatpp/web/server/HttpConnectionHandler.hpp"
#include "oatpp/web/protocol/http/incoming/Request.hpp"

#include <stdint.h>

#include OATPP_CODEGEN_BEGIN(DTO)

class AppDto : public oatpp::DTO
{
    DTO_INIT(AppDto, DTO)

	DTO_FIELD(Int32, statusCode);
    DTO_FIELD(String, message);
};

#include OATPP_CODEGEN_END(DTO)

#include OATPP_CODEGEN_BEGIN(ApiController)

class AppController : public oatpp::web::server::api::ApiController
{
public:
    AppController(OATPP_COMPONENT(std::shared_ptr<ObjectMapper>, objectMapper))
        : oatpp::web::server::api::ApiController(objectMapper)
    {}
public:

    ENDPOINT("GET", "/", root) {
        auto dto = AppDto::createShared();
        dto->statusCode = 200;
        dto->message = "Hello World!";
        return createDtoResponse(Status::CODE_200, dto);
    }
};

#include OATPP_CODEGEN_END(ApiController)

class AppComponent
{
public:
    AppComponent(uint16_t port) : port_(port) {}

    // TODO(yum) make port configurable. oatpp examples show how to use a port
    // that's available at boot time. Plumbing this with port_ or port causes
    // oatpp to use a different port every time, which I think is caused by port_
    // being uninitialized.
	OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::network::ServerConnectionProvider>, serverConnectionProvider)([] {
        return oatpp::network::tcp::server::ConnectionProvider::createShared({ "0.0.0.0", 9517, oatpp::network::Address::IP_4 });
        }());

    OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::web::server::HttpRouter>, httpRouter)([] {
        return oatpp::web::server::HttpRouter::createShared();
        }());

    OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::network::ConnectionHandler>, serverConnectionHandler)([] {
        OATPP_COMPONENT(std::shared_ptr<oatpp::web::server::HttpRouter>, router); // get Router component
    return oatpp::web::server::HttpConnectionHandler::createShared(router);
        }());

    OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::data::mapping::ObjectMapper>, apiObjectMapper)([] {
        return oatpp::parser::json::mapping::ObjectMapper::createShared();
        }());

private:
    const uint16_t port_;
};

class BrowserSource
{
public:
	BrowserSource(uint16_t port, wxTextCtrl *out);

    void Run(volatile bool* run);

private:
	const uint16_t port_;
    wxTextCtrl* const out_;
};
