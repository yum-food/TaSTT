#pragma once

#include <wx/filepicker.h>
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

    wxPanel* main_panel_;
    wxPanel* transcribe_panel_;
    wxPanel* unity_panel_;

    wxTextCtrl* transcribe_out_;
    wxTextCtrl* unity_out_;

    wxTextCtrl* unity_animator_generated_dir_;
    wxTextCtrl* unity_animator_generated_name_;
    wxTextCtrl* unity_parameters_generated_name_;
    wxTextCtrl* unity_menu_generated_name_;

    wxDirPickerCtrl* unity_assets_file_picker_;
    wxFilePickerCtrl* unity_animator_file_picker_;
    wxFilePickerCtrl* unity_parameters_file_picker_;
    wxFilePickerCtrl* unity_menu_file_picker_;

    wxChoice* py_app_mic_;
    wxChoice* py_app_lang_;
    wxChoice* py_app_model_;

    wxProcess* py_app_;
    wxTimer py_app_drain_;

    void OnExit(wxCommandEvent& event);
    void OnNavbarTranscribe(wxCommandEvent& event);
    void OnNavbarUnity(wxCommandEvent& event);
    void OnSetupPython(wxCommandEvent& event);
    void OnDumpMics(wxCommandEvent& event);
    void OnAppStart(wxCommandEvent& event);
    void OnAppStop(wxCommandEvent& event);
    void OnAppDrain(wxTimerEvent& event);
    void DrainApp(wxProcess* proc, wxTextCtrl *frame);
    void OnGenerateFX(wxCommandEvent& event);

    void LoadAndSetIcons();
    void Resize();
};

