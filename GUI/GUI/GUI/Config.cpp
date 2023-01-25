#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#define RYML_SINGLE_HDR_DEFINE_NOW
#include "ryml.h"

#include "Config.h"

#include <fstream>
#include <memory>
#include <string>

bool Config::Serialize(const std::filesystem::path& path,
	const ryml::Tree* const t) {

	// Write the config to a tmp file. If we crash in the middle of this, it
	// doesn't matter, since the next process will just overwrite it.
	std::filesystem::path tmp_path = path;
	tmp_path += ".tmp";
	FILE* fp = fopen(tmp_path.string().c_str(), "wb");
	if (!fp) {
		wxLogError("Failed to open %s: %s", path.string().c_str(), strerror(errno));
		return false;
	}
	ryml::emit_yaml(t, fp);  // For now we assume this didn't fail.
	fclose(fp);
	fp = nullptr;

	// If there's an old config, delete it.
	struct stat tmpstat;
	if (stat(path.string().c_str(), &tmpstat) == 0) {
		if (::_unlink(path.string().c_str())) {
			wxLogError("Failed to delete old config at %s: %s", path.string().c_str(),
				strerror(errno));
			return false;
		}
	}

	// File renames within the same filesystem are atomic, so there's no risk
	// of leaving a corrupt file on disk.
	if (rename(tmp_path.string().c_str(), path.string().c_str()) != 0) {
		wxLogError("Failed to save config to %s: %s", path.string().c_str(),
			strerror(errno));
		return false;
	}

	return true;
}

bool Config::Deserialize(const std::filesystem::path& path,
	ryml::Tree* t) {
	std::ifstream file(path, std::ios::binary | std::ios::ate);
	if (!file.is_open()) {
		return false;
	}
	std::streamsize size = file.tellg();
	file.seekg(0, std::ios::beg);
	std::vector<char> yaml_buf(size);
	if (!file.read(yaml_buf.data(), size)) {
		return false;
	}

	*t = ryml::parse_in_place(ryml::to_substr(yaml_buf.data()));
	return true;
}

TranscriptionAppConfig::TranscriptionAppConfig()
	: microphone("index"),
	language("english"),
	model("base.en"),
	chars_per_sync("20"),
	bytes_per_char("1"),
	button("left joystick"),
	rows("4"),
	cols("48"),
	window_duration("15"),
	enable_local_beep(true),
	use_cpu(false),
	use_builtin(false)
{}

bool TranscriptionAppConfig::Serialize(const std::filesystem::path& path) {
	ryml::Tree t;
	ryml::NodeRef root = t.rootref();
	root |= ryml::MAP;
	root["microphone"] << ryml::to_substr(microphone);
	root["language"] << ryml::to_substr(language);
	root["model"] << ryml::to_substr(model);
	root["chars_per_sync"] << ryml::to_substr(chars_per_sync);
	root["bytes_per_char"] << ryml::to_substr(bytes_per_char);
	root["button"] << ryml::to_substr(button);
	root["rows"] << ryml::to_substr(rows);
	root["cols"] << ryml::to_substr(cols);
	root["window_duration"] << ryml::to_substr(window_duration);
	root["enable_local_beep"] << enable_local_beep;
	root["use_cpu"] << use_cpu;
	root["use_builtin"] << use_builtin;
  return Config::Serialize(path, &t);
}

bool TranscriptionAppConfig::Deserialize(const std::filesystem::path& path) {
	std::error_code err;
	if (!std::filesystem::exists(path, err)) {
		*this = TranscriptionAppConfig();
		return true;
	}

	ryml::Tree t{};
	if (!Config::Deserialize(path, &t)) {
		wxLogError("Deserialization failed at %s", path.string());
		return false;
	}

	ryml::ConstNodeRef root = t.rootref();
	TranscriptionAppConfig c;
	root.get_if("microphone", &c.microphone);
	root.get_if("language", &c.language);
	root.get_if("model", &c.model);
	root.get_if("chars_per_sync", &c.chars_per_sync);
	root.get_if("bytes_per_char", &c.bytes_per_char);
	root.get_if("button", &c.button);
	root.get_if("rows", &c.rows);
	root.get_if("cols", &c.cols);
	root.get_if("window_duration", &c.window_duration);
	root.get_if("enable_local_beep", &c.enable_local_beep);
	root.get_if("use_cpu", &c.use_cpu);
	root.get_if("use_builtin", &c.use_builtin);

	*this = std::move(c);
	return true;
}

UnityAppConfig::UnityAppConfig()
	: assets_path(),
	fx_path(),
	params_path(),
	menu_path(),
	chars_per_sync(20),
	bytes_per_char(1),
	rows(4),
	cols(48)
{}

bool UnityAppConfig::Serialize(const std::filesystem::path& path) {
	ryml::Tree t;
	ryml::NodeRef root = t.rootref();
	root |= ryml::MAP;
	root["assets_path"] << ryml::to_substr(assets_path);
	root["fx_path"] << ryml::to_substr(fx_path);
	root["params_path"] << ryml::to_substr(params_path);
	root["menu_path"] << ryml::to_substr(menu_path);
	root["chars_per_sync"] << chars_per_sync;
	root["bytes_per_char"] << bytes_per_char;
	root["rows"] << rows;
	root["cols"] << cols;

	return Config::Serialize(path, &t);
}

bool UnityAppConfig::Deserialize(const std::filesystem::path& path) {
	std::error_code err;
	if (!std::filesystem::exists(path, err)) {
		*this = UnityAppConfig();
		return true;
	}

	ryml::Tree t;
	if (!Config::Deserialize(path, &t)) {
		return false;
	}

	ryml::ConstNodeRef root = t.rootref();
	UnityAppConfig c;

	root.get_if("chars_per_sync", &c.chars_per_sync);
	root.get_if("bytes_per_char", &c.bytes_per_char);
	root.get_if("rows", &c.rows);
	root.get_if("cols", &c.cols);

	root.get_if("assets_path", &c.assets_path);
	root.get_if("fx_path", &c.fx_path);
	root.get_if("params_path", &c.params_path);
	root.get_if("menu_path", &c.menu_path);

	*this = std::move(c);
	return true;
}

