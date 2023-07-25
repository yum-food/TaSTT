#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "Config.h"
#include "ConfigMarshal.h"
#include "Logging.h"

#include <fstream>
#include <memory>
#include <string>

using ::Logging::Log;

bool Config::Serialize(const std::filesystem::path& path,
	const ConfigMarshal& cm) {
	// If there's an old config, delete it.
	struct stat tmpstat;
	if (stat(path.string().c_str(), &tmpstat) == 0) {
		if (::_unlink(path.string().c_str())) {
			Log(out_, "Failed to delete old config at {}: {}\n",
				path.string().c_str(), strerror(errno));
			return false;
		}
	}

	// Write the config to a tmp file. If we crash in the middle of this, it
	// doesn't matter, since the next process will just overwrite it.
	std::filesystem::path tmp_path = path;

	if (stat(tmp_path.string().c_str(), &tmpstat) == 0) {
		if (::_unlink(tmp_path.string().c_str())) {
			Log(out_, "Failed to delete old tmp config at {}: {}\n",
				tmp_path.string().c_str(), strerror(errno));
			return false;
		}
	}

	if (!cm.Save(tmp_path)) {
		Log(out_, "Failed to save config to {}\n", tmp_path.string());
		return false;
	}

	// File renames within the same filesystem are atomic, so there's no risk
	// of leaving a corrupt file on disk.
	if (rename(tmp_path.string().c_str(), path.string().c_str()) != 0) {
		Log(out_, "Failed to save config to {}: {}\n", path.string().c_str(),
			strerror(errno));
		return false;
	}

	return true;
}

bool Config::Deserialize(const std::filesystem::path& path,
	ConfigMarshal& cm) {
	return cm.Load(path);
}

AppConfig::AppConfig(wxTextCtrl* out)
	: Config(out),

	microphone("index"),
	language("english"),
	language_target("Do not translate"),
	model("base.en"),
	model_translation("nllb-200-distilled-600M"),
	button("left joystick"),

	enable_local_beep(true),
	enable_browser_src(false),
	browser_src_port(8097),
	commit_fuzz_threshold(8),
	use_cpu(false),
	use_builtin(false),
	enable_uwu_filter(false),
	remove_trailing_period(false),
	enable_uppercase_filter(false),
	enable_lowercase_filter(false),
	enable_profanity_filter(false),
	enable_debug_mode(false),
	reset_on_toggle(true),
	gpu_idx(0),
	keybind("ctrl+x"),

	chars_per_sync(8),
	bytes_per_char(1),
	rows(4),
	cols(48),

	assets_path(),
	fx_path(),
	params_path(),
	menu_path(),
	unity_generated_dir("TaSTT_Generated"),
	clear_osc(true),

	whisper_model("ggml-medium.bin"),
	whisper_mic(0),
	whisper_decode_method("greedy"),
	whisper_max_ctxt(100),
	whisper_beam_width(5),
	whisper_beam_n_best(5),
	whisper_vad_min_duration(0.5),
	whisper_vad_max_duration(5.0),
	whisper_vad_drop_start_silence(0.5),
	whisper_vad_pause_duration(0.2),
	whisper_vad_retain_duration(0.2),

	whisper_enable_builtin(false),
	whisper_enable_custom(false),
	whisper_enable_browser_src(true)
{}

bool AppConfig::Serialize(const std::filesystem::path& path) {
	ConfigMarshal cm(out_);

	cm.Set("microphone", microphone);
	cm.Set("language", language);
	cm.Set("language_target", language_target);
	cm.Set("model", model);
	cm.Set("model_translation", model_translation);
	cm.Set("button", button);

	cm.Set("enable_local_beep", enable_local_beep);
	cm.Set("enable_browser_src", enable_browser_src);
	cm.Set("browser_src_port", browser_src_port);
	cm.Set("commit_fuzz_threshold", commit_fuzz_threshold);
	cm.Set("use_cpu", use_cpu);
	cm.Set("use_builtin", use_builtin);
	cm.Set("enable_uwu_filter", enable_uwu_filter);
	cm.Set("remove_trailing_period", remove_trailing_period);
	cm.Set("enable_uppercase_filter", enable_uppercase_filter);
	cm.Set("enable_lowercase_filter", enable_lowercase_filter);
	cm.Set("enable_profanity_filter", enable_profanity_filter);
	cm.Set("enable_debug_mode", enable_debug_mode);
	cm.Set("reset_on_toggle", reset_on_toggle);
	cm.Set("gpu_idx", gpu_idx);
	cm.Set("keybind", keybind);

	cm.Set("chars_per_sync", chars_per_sync);
	cm.Set("bytes_per_char", bytes_per_char);
	cm.Set("rows", rows);
	cm.Set("cols", cols);

	cm.Set("assets_path", assets_path);
	cm.Set("fx_path", fx_path);
	cm.Set("params_path", params_path);
	cm.Set("menu_path", menu_path);
	cm.Set("unity_generated_dir", unity_generated_dir);
	cm.Set("clear_osc", clear_osc);

	cm.Set("whisper_model", whisper_model);
	cm.Set("whisper_mic", whisper_mic);
	cm.Set("whisper_decode_method", whisper_decode_method);
	cm.Set("whisper_max_ctxt", whisper_max_ctxt);
	cm.Set("whisper_beam_width", whisper_beam_width);
	cm.Set("whisper_beam_n_best", whisper_beam_n_best);
	cm.Set("whisper_vad_min_duration", whisper_vad_min_duration);
	cm.Set("whisper_vad_max_duration", whisper_vad_max_duration);
	cm.Set("whisper_vad_drop_start_silence", whisper_vad_drop_start_silence);
	cm.Set("whisper_vad_pause_duration", whisper_vad_pause_duration);
	cm.Set("whisper_vad_retain_duration", whisper_vad_retain_duration);

	cm.Set("whisper_enable_builtin", whisper_enable_builtin);
	cm.Set("whisper_enable_custom", whisper_enable_custom);
	cm.Set("whisper_enable_browser_src", whisper_enable_browser_src);

	return Config::Serialize(path, cm);
}

bool AppConfig::Deserialize(const std::filesystem::path& path) {
	std::error_code err;
	if (!std::filesystem::exists(path, err)) {
		*this = AppConfig(out_);
		return true;
	}

	ConfigMarshal cm(out_);
	if (!Config::Deserialize(path, cm)) {
		Log(out_, "Deserialization failed at {}\n", path.string());
		return false;
	}

	AppConfig c(out_);
	cm.Get("microphone", c.microphone);
	cm.Get("language", c.language);
	cm.Get("language_target", c.language_target);
	cm.Get("model", c.model);
	cm.Get("model_translation", c.model_translation);
	cm.Get("button", c.button);

	cm.Get("enable_local_beep", c.enable_local_beep);
	cm.Get("enable_browser_src", c.enable_browser_src);
	cm.Get("browser_src_port", c.browser_src_port);
	cm.Get("commit_fuzz_threshold", c.commit_fuzz_threshold);
	cm.Get("use_cpu", c.use_cpu);
	cm.Get("use_builtin", c.use_builtin);
	cm.Get("enable_uwu_filter", c.enable_uwu_filter);
	cm.Get("remove_trailing_period", c.remove_trailing_period);
	cm.Get("enable_uppercase_filter", c.enable_uppercase_filter);
	cm.Get("enable_lowercase_filter", c.enable_lowercase_filter);
	cm.Get("enable_profanity_filter", c.enable_profanity_filter);
	cm.Get("enable_debug_mode", c.enable_debug_mode);
	cm.Get("reset_on_toggle", c.reset_on_toggle);
	cm.Get("gpu_idx", c.gpu_idx);
	cm.Get("keybind", c.keybind);

	cm.Get("chars_per_sync", c.chars_per_sync);
	cm.Get("bytes_per_char", c.bytes_per_char);
	cm.Get("rows", c.rows);
	cm.Get("cols", c.cols);

	cm.Get("assets_path", c.assets_path);
	cm.Get("fx_path", c.fx_path);
	cm.Get("params_path", c.params_path);
	cm.Get("menu_path", c.menu_path);
	cm.Get("unity_generated_dir", c.unity_generated_dir);
	cm.Get("clear_osc", c.clear_osc);

	cm.Get("whisper_model", c.whisper_model);
	cm.Get("whisper_mic", c.whisper_mic);
	cm.Get("whisper_decode_method", c.whisper_decode_method);
	cm.Get("whisper_max_ctxt", c.whisper_max_ctxt);
	cm.Get("whisper_beam_width", c.whisper_beam_width);
	cm.Get("whisper_beam_n_best", c.whisper_beam_n_best);
	cm.Get("whisper_vad_min_duration", c.whisper_vad_min_duration);
	cm.Get("whisper_vad_max_duration", c.whisper_vad_max_duration);
	cm.Get("whisper_vad_drop_start_silence", c.whisper_vad_drop_start_silence);
	cm.Get("whisper_vad_pause_duration", c.whisper_vad_pause_duration);
	cm.Get("whisper_vad_retain_duration", c.whisper_vad_retain_duration);

	cm.Get("whisper_enable_builtin", c.whisper_enable_builtin);
	cm.Get("whisper_enable_custom", c.whisper_enable_custom);
	cm.Get("whisper_enable_browser_src", c.whisper_enable_browser_src);

	*this = std::move(c);
	return true;
}

