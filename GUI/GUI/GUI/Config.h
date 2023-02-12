#pragma once

#include "ryml.h"

#include <filesystem>

// Represents a disk-backed configuration. Knows how to save to disk
// (Serialize) and restore from disk (Deserialize).
class Config {
public:
	virtual ~Config() {}

	virtual bool Serialize(const std::filesystem::path& path) = 0;

	virtual bool Deserialize(const std::filesystem::path& path) = 0;

protected:
	virtual bool Serialize(const std::filesystem::path& path,
		const ryml::Tree* t);

	virtual bool Deserialize(const std::filesystem::path& path,
		ryml::Tree* t);
};

// Represents the configurable fields for the transcription app.
class TranscriptionAppConfig : public Config {
public:
	virtual ~TranscriptionAppConfig() {}

	TranscriptionAppConfig();

	bool Serialize(const std::filesystem::path& path) override;

	bool Deserialize(const std::filesystem::path& path) override;

	// The default path at which configs are serialized.
	static constexpr char kConfigPath[] = "Resources/transcription_app_config.yml";

	std::string microphone;
	std::string language;
	std::string model;
	std::string chars_per_sync;
	std::string bytes_per_char;
	std::string button;
	std::string rows;
	std::string cols;
	std::string window_duration;
	bool enable_local_beep;
	bool use_cpu;
	bool use_builtin;
};

// Represents the configurable fields for the Unity app.
class UnityAppConfig : public Config {
public:
	virtual ~UnityAppConfig() {}

	UnityAppConfig();

	bool Serialize(const std::filesystem::path& path) override;

	bool Deserialize(const std::filesystem::path& path) override;

	// The default path at which configs are serialized.
	static constexpr char kConfigPath[] = "Resources/unity_app_config.yml";

	std::string assets_path;
	std::string fx_path;
	std::string params_path;
	std::string menu_path;
	int chars_per_sync;
	int bytes_per_char;
	int rows;
	int cols;
	bool clear_osc;
};
