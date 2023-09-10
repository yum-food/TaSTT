#pragma once

#include <wx/filepicker.h>
#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "Config.h"
#include "Transcript.h"

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

    wxTextCtrl* transcribe_out_;
    wxTextCtrl* unity_out_;
    wxTextCtrl* debug_out_;

    wxTextCtrl* unity_animator_generated_dir_;
    wxTextCtrl* unity_animator_generated_name_;
    wxTextCtrl* unity_parameters_generated_name_;
    wxTextCtrl* unity_menu_generated_name_;

    wxTextCtrl* py_app_rows_;
    wxTextCtrl* py_app_cols_;
    wxTextCtrl* py_app_gpu_idx_;
    wxTextCtrl* py_app_keybind_;
    wxTextCtrl* py_app_browser_src_port_;
    wxTextCtrl* py_app_commit_fuzz_threshold_;
    wxTextCtrl* unity_rows_;
    wxTextCtrl* unity_cols_;

    wxDirPickerCtrl* unity_assets_file_picker_;
    wxFilePickerCtrl* unity_animator_file_picker_;
    wxFilePickerCtrl* unity_parameters_file_picker_;
    wxFilePickerCtrl* unity_menu_file_picker_;

    wxChoice* py_app_mic_;
    wxChoice* py_app_lang_;
    wxChoice* py_app_translate_target_;
    wxChoice* py_app_model_;
    wxChoice* py_app_model_translation_;
    // TODO(yum) figure out how to deduplicate these objects
    wxChoice* py_app_chars_per_sync_;
    wxChoice* py_app_bytes_per_char_;
    wxChoice* py_app_button_;
    wxChoice* unity_chars_per_sync_;
    wxChoice* unity_bytes_per_char_;

    wxCheckBox* py_app_enable_local_beep_;
    wxCheckBox* py_app_enable_browser_src_;
    wxCheckBox* py_app_use_cpu_;
    wxCheckBox* py_app_use_builtin_;
    wxCheckBox* py_app_enable_uwu_filter_;
    wxCheckBox* py_app_remove_trailing_period_;
    wxCheckBox* py_app_enable_uppercase_filter_;
    wxCheckBox* py_app_enable_lowercase_filter_;
    wxCheckBox* py_app_enable_profanity_filter_;
    wxCheckBox* py_app_enable_debug_mode_;
    wxCheckBox* py_app_reset_on_toggle_;
    wxCheckBox* py_app_enable_previews_;
    wxCheckBox* unity_clear_osc_;
    wxCheckBox* unity_enable_phonemes_;

    std::future<bool> py_app_;
    std::future<bool> obs_app_;
    Transcript transcript_;
    bool run_py_app_;
    bool run_unity_auto_refresh_;
    std::future<bool> unity_app_;
    std::future<bool> unity_auto_refresh_;
    std::future<bool> dump_mics_;
    std::future<bool> env_proc_;
    std::future<void> reset_venv_proc_;

    wxTimer py_app_drain_;

    std::unique_ptr<AppConfig> app_c_;

    // Initialize GUI input fields using `app_c_`.
    void ApplyConfigToInputFields();
    // Ensure that virtual env is set up.
    void EnsureVirtualEnv(bool block, bool force = false);

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
    void OnUnityAutoRefresh(wxCommandEvent& event);
    void OnUnityAutoRefreshStop();
    void OnUnityAutoRefreshStop(wxCommandEvent& event);
    void OnUnityParamChangeImpl();
    void OnUnityParamChange(wxCommandEvent& event);
    void OnListPip(wxCommandEvent& event);
    void OnClearPip(wxCommandEvent& event);
    void OnResetVenv(wxCommandEvent& event);
    void OnClearOSC(wxCommandEvent& event);
    void OnBackupVenv(wxCommandEvent& event);
    void OnRestoreVenv(wxCommandEvent& event);
    void OnSetupVenv(wxCommandEvent& event);

    void LoadAndSetIcons();
    void Resize();
};

