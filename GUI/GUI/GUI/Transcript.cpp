#include "Transcript.h"

void Transcript::Append(std::string&& segment) {
	std::scoped_lock l(mu_);
	segments_.push_back(std::move(segment));
}

void Transcript::Clear() {
	std::scoped_lock l(mu_);
	segments_.clear();
}

std::vector<std::string> Transcript::Get() {
	std::scoped_lock l(mu_);
	return segments_;
}
