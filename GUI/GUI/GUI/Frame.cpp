#include "Frame.h"

#include <filesystem>

Frame::Frame()
    : wxFrame(nullptr, wxID_ANY, "TaSTT")
{
    Bind(wxEVT_MENU, &Frame::OnExit, this, wxID_EXIT);

    // wx needs this to be able to load PNGs.
    wxImage::AddHandler(&png_handler_);

    const std::string logo_path = "Resources/logo.png";
    if (!std::filesystem::exists(logo_path)) {
        wxLogFatalError("Logo is missing from %s", logo_path.c_str());
    }
    wxBitmap icon_img("Resources/logo.png", wxBITMAP_TYPE_PNG);
    wxIcon icon;
    icon.CopyFromBitmap(icon_img);
    SetIcon(icon);
}

void Frame::OnExit(wxCommandEvent& event)
{
    Close(true);
}

