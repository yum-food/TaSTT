#pragma once

#include <functional>
#include <utility>

class ScopeGuard {
public:
	ScopeGuard(std::function<void()>&& cb) : cb_(std::move(cb)), active_(true) {}
	~ScopeGuard() {
		Invoke();
	}

	ScopeGuard() = delete;
	ScopeGuard(ScopeGuard&) = delete;
	ScopeGuard(const ScopeGuard&) = delete;
	ScopeGuard(ScopeGuard&&) = delete;
	ScopeGuard& operator=(ScopeGuard&) = delete;
	ScopeGuard& operator=(const ScopeGuard&) = delete;

	void Cancel() { active_ = false; }

	void Invoke() {
		if (active_) {
			cb_();
			active_ = false;
		}
	}

private:
	const std::function<void()> cb_;
	bool active_;
};
