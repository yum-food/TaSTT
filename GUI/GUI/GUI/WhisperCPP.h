#pragma once

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <unknwn.h>
#include <wchar.h>
#include <winerror.h>

#include "whisper/whisperWindows.h"

#include "Config.h"

#include <filesystem>
#include <functional>
#include <future>
#include <string>
#include <vector>

class WhisperCPP {
public:
	WhisperCPP(wxTextCtrl* out);
	~WhisperCPP();

	bool Init();
	bool GetMics(std::vector<std::string>& mics);
	bool OpenMic(const int idx, Whisper::iAudioCapture*& stream);
	bool InstallDependencies();
	bool DownloadModel(const std::string& model_name,
		const std::filesystem::path& fs_path);
	bool LoadModel(const std::string& path, Whisper::iModel*& model);
	bool CreateContext(Whisper::iModel* model, Whisper::iContext*& context);

	void Start(const AppConfig& c);
	void Stop();

	void StartBrowserSource(const AppConfig& c);
	void StopBrowserSource();

private:
	bool GetMicsImpl(std::vector<Whisper::sCaptureDevice>& mics);

	wxTextCtrl* out_;
	Whisper::iMediaFoundation* f_;
	bool did_init_;

	std::future<void> transcription_thd_;
	volatile bool run_transcription_;

	std::future<void> browser_src_thd_;
	volatile bool run_browser_src_;
};
