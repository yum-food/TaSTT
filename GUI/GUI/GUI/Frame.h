#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <memory>

class Frame : public wxFrame
{
public:
    Frame();

private:
    wxPNGHandler png_handler_;
    wxPanel py_panel_;
    wxBoxSizer py_panel_sizer_;
    wxButton py_version_button_;
    wxButton py_setup_button_;
    wxButton py_app_start_button_;
    wxButton py_app_stop_button_;
    wxTextCtrl py_out_;
    wxChoice py_app_mic_;
    wxChoice py_app_lang_;

    wxProcess* py_app_;

    void OnExit(wxCommandEvent& event);
    void OnGetPythonVersion(wxCommandEvent& event);
    void OnSetupPython(wxCommandEvent& event);
    void OnAppStart(wxCommandEvent& event);
    void OnAppStop(wxCommandEvent& event);

    void LoadAndSetIcon(const std::string& icon_path);
};
