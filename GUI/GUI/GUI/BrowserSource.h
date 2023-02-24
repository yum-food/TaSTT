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

#include "Transcript.h"

#include <stdint.h>

#include <filesystem>
#include <fstream>

#include OATPP_CODEGEN_BEGIN(DTO)

class AppDto : public oatpp::DTO
{
    DTO_INIT(AppDto, DTO)

	DTO_FIELD(Int32, statusCode);
    DTO_FIELD(String, transcript);
};

#include OATPP_CODEGEN_END(DTO)

#include OATPP_CODEGEN_BEGIN(ApiController)

class AppController : public oatpp::web::server::api::ApiController
{
public:
    AppController(std::shared_ptr<ObjectMapper> objectMapper, Transcript* transcript)
        : oatpp::web::server::api::ApiController(objectMapper), transcript_(transcript)
    {}

    ENDPOINT("GET", "/api/transcript", transcription) {
        auto dto = AppDto::createShared();
        dto->statusCode = 200;

        std::ostringstream oss;
        std::vector<std::string> segments = transcript_->Get();
        for (const auto& seg : segments) {
            oss << seg;
        }
        dto->transcript = oss.str();

        return createDtoResponse(Status::CODE_200, dto);
    }

    ENDPOINT("GET", "/", root) {
        auto html_path = std::filesystem::path("Resources/BrowserSource/index.html");
        std::ifstream html_ifs(html_path);
        std::vector<char> resp(4096 * 16, 0);
        html_ifs.read(resp.data(), resp.size());
        return createResponse(Status::CODE_200, resp.data());
    }

private:
    Transcript* const transcript_;
};

#include OATPP_CODEGEN_END(ApiController)

class BrowserSource
{
public:
	BrowserSource(uint16_t port, wxTextCtrl *out, Transcript *transcript);

    void Run(volatile bool* run);

private:
	const uint16_t port_;
    wxTextCtrl* const out_;
    Transcript* const transcript_;
};

