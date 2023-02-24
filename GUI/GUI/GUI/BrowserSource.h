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
    AppController(std::shared_ptr<ObjectMapper> objectMapper)
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

class BrowserSource
{
public:
	BrowserSource(uint16_t port, wxTextCtrl *out);

    void Run(volatile bool* run);

private:
	const uint16_t port_;
    wxTextCtrl* const out_;
};
