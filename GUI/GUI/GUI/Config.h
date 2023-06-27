#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "ConfigMarshal.h"

#include <filesystem>

// Represents a disk-backed configuration. Knows how to save to disk
// (Serialize) and restore from disk (Deserialize).
class Config {
public:
	Config(wxTextCtrl* out) : out_(out) {}

	virtual ~Config() {}

	virtual bool Serialize(const std::filesystem::path& path) = 0;

	virtual bool Deserialize(const std::filesystem::path& path) = 0;

protected:
	virtual bool Serialize(const std::filesystem::path& path,
		const ConfigMarshal& cm);

	virtual bool Deserialize(const std::filesystem::path& path,
		ConfigMarshal& cm);

	wxTextCtrl* out_;
};

// Represents the configurable fields for the GUI. Used by both the
// Transcription panel and the Unity panel.
class AppConfig : public Config {
public:
	virtual ~AppConfig() {}

	AppConfig(wxTextCtrl* out);

	bool Serialize(const std::filesystem::path& path) override;

	bool Deserialize(const std::filesystem::path& path) override;

	// The default path at which configs are serialized.
	static constexpr char kConfigPath[] = "Resources/app_config.yml";

	// Transcription-specific settings.
	std::string microphone;
	std::string language;
	std::string language_target;
	std::string model;
	std::string model_translation;
	std::string button;

	bool enable_local_beep;
	bool enable_browser_src;
	int browser_src_port;
	bool use_cpu;
	bool use_builtin;
	bool enable_uwu_filter;
	bool remove_trailing_period;
	bool enable_uppercase_filter;
	bool enable_lowercase_filter;
	int gpu_idx;
	std::string keybind;

	// Unity and transcription shared settings.
	int chars_per_sync;
	int bytes_per_char;
	int rows;
	int cols;

	// Unity-specific settings.
	std::string assets_path;
	std::string fx_path;
	std::string params_path;
	std::string menu_path;
	bool clear_osc;

	// WhisperCPP-specific settings.
	std::string whisper_model;
	int whisper_mic;
	std::string whisper_decode_method;
	int whisper_max_ctxt;
	int whisper_beam_width;
	int whisper_beam_n_best;
	float whisper_vad_min_duration;
	float whisper_vad_max_duration;
	float whisper_vad_drop_start_silence;
	float whisper_vad_pause_duration;
	float whisper_vad_retain_duration;

	// Browser source-specific settings.
	bool whisper_enable_builtin;
	bool whisper_enable_custom;
	bool whisper_enable_browser_src;
};

