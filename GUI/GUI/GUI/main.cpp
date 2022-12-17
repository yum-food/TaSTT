// wxWidgets "Hello World" Program

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "ScopeGuard.h"

#include <filesystem>

class MyApp : public wxApp
{
public:
    virtual bool OnInit();
};

class MyFrame : public wxFrame
{
public:
    MyFrame();

private:
    wxPNGHandler png_handler_;

    void OnHello(wxCommandEvent& event);
    void OnExit(wxCommandEvent& event);
    void OnAbout(wxCommandEvent& event);
};

enum
{
    ID_Hello = 1
};

wxIMPLEMENT_APP(MyApp);

bool MyApp::OnInit()
{
    MyFrame* frame = new MyFrame();
    frame->Show(true);

    return true;
}

MyFrame::MyFrame()
    : wxFrame(nullptr, wxID_ANY, "TaSTT")
{
    Bind(wxEVT_MENU, &MyFrame::OnHello, this, ID_Hello);
    Bind(wxEVT_MENU, &MyFrame::OnAbout, this, wxID_ABOUT);
    Bind(wxEVT_MENU, &MyFrame::OnExit, this, wxID_EXIT);

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

void MyFrame::OnExit(wxCommandEvent& event)
{
    Close(true);
}

void MyFrame::OnAbout(wxCommandEvent& event)
{
    wxMessageBox("This is a wxWidgets Hello World example",
        "About Hello World", wxOK | wxICON_INFORMATION);
}

void MyFrame::OnHello(wxCommandEvent& event)
{
    //wxLogMessage("Hello world from wxWidgets!");
}

