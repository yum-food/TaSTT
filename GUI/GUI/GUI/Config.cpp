#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "Config.h"

#define RYML_SINGLE_HDR_DEFINE_NOW
#include "ryml.h"

#include <fstream>
#include <memory>
#include <string>

TranscriptionAppConfig::TranscriptionAppConfig()
	: microphone("index"),
	language("english"),
	model("base.en"),
	chars_per_sync("20"),
	bytes_per_char("1"),
	rows("4"),
	cols("48"),
	window_duration("15"),
	enable_local_beep(true),
	use_cpu(false)
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
	root["rows"] << ryml::to_substr(rows);
	root["cols"] << ryml::to_substr(cols);
	root["window_duration"] << ryml::to_substr(window_duration);
	root["enable_local_beep"] << enable_local_beep;
	root["use_cpu"] << use_cpu;

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

bool TranscriptionAppConfig::Deserialize(const std::filesystem::path& path) {
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

	ryml::Tree t = ryml::parse_in_place(ryml::to_substr(yaml_buf.data()));
	ryml::ConstNodeRef root = t.rootref();
	TranscriptionAppConfig c;
	root["microphone"] >> c.microphone;
	root["language"] >> c.language;
	root["model"] >> c.model;
	root["chars_per_sync"] >> c.chars_per_sync;
	root["bytes_per_char"] >> c.bytes_per_char;
	root["rows"] >> c.rows;
	root["cols"] >> c.cols;
	root["window_duration"] >> c.window_duration;
	root["enable_local_beep"] >> c.enable_local_beep;

	*this = std::move(c);
	return true;
}
