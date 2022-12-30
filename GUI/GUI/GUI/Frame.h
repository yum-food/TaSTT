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
    // TODO(yum) figure out how to deduplicate these objects
    wxChoice* py_app_chars_per_sync_;
    wxChoice* py_app_bytes_per_char_;
    wxChoice* unity_chars_per_sync_;
    wxChoice* unity_bytes_per_char_;

    wxCheckBox* py_app_enable_local_beep_;

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
    void OnUnityParamChangeImpl();
    void OnUnityParamChange(wxCommandEvent& event);

    void LoadAndSetIcons();
    void Resize();
};

