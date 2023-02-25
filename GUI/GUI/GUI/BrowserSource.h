#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "Transcript.h"

#include <stdint.h>

#include <filesystem>
#include <fstream>

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

