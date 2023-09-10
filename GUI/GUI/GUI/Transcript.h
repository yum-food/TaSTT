#pragma once

#include <mutex>
#include <string>
#include <vector>

// Simple thread-safe class to share transcription data between layers.
class Transcript {
public:
	Transcript() = default;

	void Append(std::string&& segment);
	void Set(std::string&& segment);
	void SetPreview(std::string&& segment);
	void Clear();

	// Indicate whether the transcript is "finalized", i.e. the transcription
	// engine has committed the entirety of the transcript and will no longer
	// change it.
	void SetFinalized(bool is_finalized);

	std::vector<std::string> Get();
	std::vector<std::string> GetPreview();
	bool IsFinalized();

private:
	std::mutex mu_;
	std::vector<std::string> segments_;
	std::vector<std::string> previews_;
	bool is_finalized_{ false };
};
