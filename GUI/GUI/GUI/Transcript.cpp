#include "Transcript.h"

void Transcript::Append(std::string&& segment) {
	std::scoped_lock l(mu_);
	segments_.push_back(std::move(segment));
}

void Transcript::Set(std::string&& segment) {
	std::scoped_lock l(mu_);
	segments_.clear();
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

void Transcript::SetFinalized(bool is_finalized) {
	// Accessing anything smaller than a word is always atomic.
	is_finalized_ = is_finalized;
}

bool Transcript::IsFinalized() {
	// Accessing anything smaller than a word is always atomic.
	return is_finalized_;
}
