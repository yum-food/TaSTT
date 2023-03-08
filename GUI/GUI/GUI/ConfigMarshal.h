#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include "Logging.h"

#include <filesystem>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <type_traits>

class ConfigMarshal
{
public:
	ConfigMarshal(wxTextCtrl* const out)
		: out_(out)
	{}

	bool Save(const std::filesystem::path& path) const {
		std::ostringstream oss;
		for (const auto& [k, v] : kv_str_) {
			oss << k << ": " << v << std::endl;
		}
		for (const auto& [k, v] : kv_int_) {
			oss << k << ": " << std::to_string(v) << std::endl;
		}
		for (const auto& [k, v] : kv_float_) {
			oss << k << ": " << std::to_string(v) << std::endl;
		}

		std::ofstream ofs(path.string());
		ofs << oss.str();
		ofs.close();

		return true;
	}

	bool Load(const std::filesystem::path& path) {
		std::ifstream ifs(path.string());
		std::string line;
		while (std::getline(ifs, line)) {
			int n_words = 0;

			std::string delim = ": ";
			size_t delim_pos = line.find(delim, 0);
			if (delim_pos == std::string::npos) {
				Logging::Log(out_, "Invalid config file: line {} has no delimiter\n", line);
				return false;
			}
			std::string key = line.substr(0, delim_pos);
			std::string val = line.substr(delim_pos + delim.length());

			try {
				size_t pos;
				int val_i = std::stoi(val, &pos);
				if (pos == val.length()) {
					// The entire value is an int -> interpret as an int. Corollary: users
					// can't store ints as strings!
					kv_int_[key] = val_i;
					continue;
				}
			}
			catch (const std::invalid_argument&) {}
			catch (const std::out_of_range&) {}

			try {
				size_t pos;
				float val_f = std::stof(val, &pos);
				if (pos == val.length()) {
					// The entire value is a float -> interpret as a float. Corollary: users
					// can't store floats as strings!
					kv_float_[key] = val_f;
					continue;
				}
			}
			catch (const std::invalid_argument&) {}
			catch (const std::out_of_range&) {}

			kv_str_[key] = val;
		}
		return true;
	}

	template <typename T>
	bool Set(const std::string& key, const T& value) {
		if constexpr (std::is_same_v<T, std::string>) {
			kv_str_[key] = value;
			return true;
		}
		if constexpr (std::is_same_v<T, int> || std::is_same_v<T, bool>) {
			kv_int_[key] = static_cast<int>(value);
			return true;
		}
		if constexpr (std::is_same_v<T, float>) {
			kv_float_[key] = value;
			return true;
		}
		Logging::Log(out_, "ConfigMarshal unsupported type: {}\n", typeid(T).name());
		return false;
	}

	template <typename T>
	bool Get(const std::string& key, T& value) const {
		if constexpr (std::is_same_v<T, std::string>) {
			auto iter = kv_str_.find(key);
			if (iter == kv_str_.end()) {
				// Edge case: string may be represented entirely as an int, so
				// it was parsed out as an int.
				auto iter = kv_int_.find(key);
				if (iter == kv_int_.end()) {
					Logging::Log(out_, "Config contains no field named `{}`\n", key);
					return false;
				}
				value = std::to_string(iter->second);
				return true;
			}
			value = iter->second;
			return true;
		}
		if constexpr (std::is_same_v<T, float>) {
			auto iter = kv_float_.find(key);
			if (iter == kv_float_.end()) {
				Logging::Log(out_, "Config contains no field named `{}`\n", key);
				return false;
			}
			value = iter->second;
			return true;
		}
		if constexpr (std::is_same_v<T, int> || std::is_same_v<T, bool>) {
			auto iter = kv_int_.find(key);
			if (iter == kv_int_.end()) {
				Logging::Log(out_, "Config contains no field named `{}`\n", key);
				return false;
			}
			if constexpr (std::is_same_v<T, bool>) {
				if (iter->second < 0 || iter->second > 1) {
					Logging::Log(out_, "Config field {} is out of boolean range: {}\n", key, iter->second);
					return false;
				}
			}
			value = static_cast<T>(iter->second);
			return true;
		}
		Logging::Log(out_, "ConfigMarshal unsupported type: {}\n", typeid(T).name());
		return false;
	}


private:
	wxTextCtrl* out_;

	std::map<std::string, std::string> kv_str_;
	std::map<std::string, int> kv_int_;
	std::map<std::string, float> kv_float_;
};
