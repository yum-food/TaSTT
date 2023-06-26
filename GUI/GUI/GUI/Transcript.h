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
	void Clear();

	std::vector<std::string> Get();

private:
	std::mutex mu_;
	std::vector<std::string> segments_;
};
