#pragma once

#include <wx/filepicker.h>
#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "Config.h"
#include "WhisperCPP.h"

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
    wxPanel* debug_panel_;
    wxPanel* whisper_panel_;

    wxTextCtrl* transcribe_out_;
    wxTextCtrl* unity_out_;
    wxTextCtrl* debug_out_;
    wxTextCtrl* whisper_out_;

    wxTextCtrl* unity_animator_generated_dir_;
    wxTextCtrl* unity_animator_generated_name_;
    wxTextCtrl* unity_parameters_generated_name_;
    wxTextCtrl* unity_menu_generated_name_;

    wxTextCtrl* py_app_rows_;
    wxTextCtrl* py_app_cols_;
    wxTextCtrl* py_app_window_duration_;
    wxTextCtrl* unity_rows_;
    wxTextCtrl* unity_cols_;
    wxTextCtrl* whisper_rows_;
    wxTextCtrl* whisper_cols_;
    wxTextCtrl* whisper_window_duration_;
    wxTextCtrl* whisper_browser_src_port_;

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
    wxChoice* py_app_button_;
    wxChoice* unity_chars_per_sync_;
    wxChoice* unity_bytes_per_char_;
    wxChoice* whisper_mic_;
    wxChoice* whisper_lang_;
    wxChoice* whisper_model_;
    wxChoice* whisper_chars_per_sync_;
    wxChoice* whisper_bytes_per_char_;
    wxChoice* whisper_button_;

    wxCheckBox* py_app_enable_local_beep_;
    wxCheckBox* py_app_use_cpu_;
    wxCheckBox* py_app_use_builtin_;
    wxCheckBox* unity_clear_osc_;
    wxCheckBox* whisper_enable_local_beep_;
    wxCheckBox* whisper_use_cpu_;
    wxCheckBox* whisper_enable_builtin_;
    wxCheckBox* whisper_enable_custom_;
    wxCheckBox* whisper_enable_browser_src_;

    wxProcess* py_app_;
    wxProcess* env_proc_;
    wxTimer py_app_drain_;

    wxProcess* whisper_app_;
    wxTimer whisper_app_drain_;

    AppConfig app_c_;

    std::unique_ptr<WhisperCPP> whisper_;

    // Initialize GUI input fields using `app_c_`.
    void ApplyConfigToInputFields();
    // Populate dynamically-generated input fields, such as microphone lists.
    void PopulateDynamicInputFields();

    void OnExit(wxCommandEvent& event);
    void OnNavbarTranscribe(wxCommandEvent& event);
    void OnNavbarUnity(wxCommandEvent& event);
    void OnNavbarDebug(wxCommandEvent& event);
    void OnNavbarWhisper(wxCommandEvent& event);
    void OnSetupPython(wxCommandEvent& event);
    void OnDumpMics(wxCommandEvent& event);
    void OnAppStart(wxCommandEvent& event);
    void OnAppStop(wxCommandEvent& event);
    void OnWhisperStart(wxCommandEvent& event);
    void OnWhisperStop(wxCommandEvent& event);
    void OnAppDrain(wxTimerEvent& event);
    void OnGenerateFX(wxCommandEvent& event);
    void OnUnityParamChangeImpl();
    void OnUnityParamChange(wxCommandEvent& event);
    void OnListPip(wxCommandEvent& event);
    void OnClearPip(wxCommandEvent& event);
    void OnResetVenv(wxCommandEvent& event);
    void OnClearOSC(wxCommandEvent& event);
    void OnBackupVenv(wxCommandEvent& event);
    void OnRestoreVenv(wxCommandEvent& event);

    void LoadAndSetIcons();
    void Resize();
};

