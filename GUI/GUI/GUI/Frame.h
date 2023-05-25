#pragma once

#include <wx/filepicker.h>
#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "Config.h"

#include <future>
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
    wxTextCtrl* py_app_gpu_idx_;
    wxTextCtrl* py_app_keybind_;
    wxTextCtrl* unity_rows_;
    wxTextCtrl* unity_cols_;
    wxTextCtrl* whisper_rows_;
    wxTextCtrl* whisper_cols_;
    wxTextCtrl* whisper_browser_src_port_;
    wxTextCtrl* whisper_max_ctxt_;
    wxTextCtrl* whisper_beam_width_;
    wxTextCtrl* whisper_beam_n_best_;
    wxTextCtrl* whisper_vad_min_duration_;
    wxTextCtrl* whisper_vad_max_duration_;
    wxTextCtrl* whisper_vad_drop_start_silence_;
    wxTextCtrl* whisper_vad_pause_duration_;
    wxTextCtrl* whisper_vad_retain_duration_;

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
    wxChoice* whisper_decode_method_;

    wxCheckBox* py_app_enable_local_beep_;
    wxCheckBox* py_app_use_cpu_;
    wxCheckBox* py_app_use_builtin_;
    wxCheckBox* py_app_enable_uwu_filter_;
    wxCheckBox* unity_clear_osc_;
    wxCheckBox* whisper_enable_local_beep_;
    wxCheckBox* whisper_use_cpu_;
    wxCheckBox* whisper_enable_builtin_;
    wxCheckBox* whisper_enable_custom_;
    wxCheckBox* whisper_enable_browser_src_;

    std::future<bool> py_app_;
    bool run_py_app_;
    std::future<bool> unity_app_;
    std::future<bool> dump_mics_;
    std::future<bool> env_proc_;
    std::future<void> reset_venv_proc_;

    wxTimer py_app_drain_;

    std::unique_ptr<AppConfig> app_c_;

    // Initialize GUI input fields using `app_c_`.
    void ApplyConfigToInputFields();
    // Ensure that virtual env is set up.
    void EnsureVirtualEnv(bool block);

    void OnExit(wxCloseEvent& event);
    void OnNavbarTranscribe(wxCommandEvent& event);
    void OnNavbarUnity(wxCommandEvent& event);
    void OnNavbarDebug(wxCommandEvent& event);
    void OnDumpMics(wxCommandEvent& event);
    void OnAppStart(wxCommandEvent& event);
    void OnAppStop();
    void OnAppStop(wxCommandEvent& event);
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

