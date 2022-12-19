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

    wxTextCtrl* py_out_;
    wxChoice* py_app_mic_;
    wxChoice* py_app_lang_;
    wxChoice* py_app_model_;
    wxProcess* py_app_;

    void OnExit(wxCommandEvent& event);
    void OnGetPythonVersion(wxCommandEvent& event);
    void OnSetupPython(wxCommandEvent& event);
    void OnDumpMics(wxCommandEvent& event);
    void OnAppStart(wxCommandEvent& event);
    void OnAppStop(wxCommandEvent& event);

    void LoadAndSetIcons();
};
