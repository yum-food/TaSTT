#pragma once

#include <filesystem>

class TranscriptionAppConfig {
public:
	TranscriptionAppConfig();

	bool Serialize(const std::filesystem::path& path);

	bool Deserialize(const std::filesystem::path& path);

	// The default path at which configs are serialized.
	static constexpr char kConfigPath[] = "Resources/transcription_app_config.yml";

	std::string microphone;
	std::string language;
	std::string model;
	std::string chars_per_sync;
	std::string bytes_per_char;
	std::string rows;
	std::string cols;
	std::string window_duration;
	bool enable_local_beep;
	bool use_cpu;
};
