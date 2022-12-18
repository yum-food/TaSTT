#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

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
    wxTextCtrl py_out_;

    void OnExit(wxCommandEvent& event);
    void OnGetPythonVersion(wxCommandEvent& event);
    void OnSetupPython(wxCommandEvent& event);

    void LoadAndSetIcon(const std::string& icon_path);
};
