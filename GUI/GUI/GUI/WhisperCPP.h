#pragma once

#include <wx/filepicker.h>
#include <wx/wxprec.h>
#include <wx/process.h>
#include <wx/thread.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <unknwn.h>
#include <wchar.h>
#include <winerror.h>

#include "whisperWindows.h"

#include "Config.h"

#include <filesystem>
#include <functional>
#include <string>
#include <vector>

class WhisperCPP {
public:
	WhisperCPP(wxTextCtrl* out);
	~WhisperCPP();

	bool Init();
	bool GetMics(std::vector<std::string>& mics);
	bool OpenMic(const int idx, Whisper::iAudioCapture*& stream);
	bool InstallDependencies(wxProcess*& proc);
	bool DownloadModel(const std::string& model_name,
		const std::filesystem::path& fs_path, wxProcess*& proc);
	bool LoadModel(const std::string& path, Whisper::iModel*& model);
	bool CreateContext(Whisper::iModel* model, Whisper::iContext*& context);

	void Start(const AppConfig& c);
	void Stop();

private:
	bool GetMicsImpl(std::vector<Whisper::sCaptureDevice>& mics);

	class AppThread : public wxThread {
	public:
		AppThread(const std::function<void(AppThread* thd)>&& cb, WhisperCPP* app);

		virtual ~AppThread();

		virtual void* Entry() wxOVERRIDE;

	private:
		const std::function<void(AppThread* thd)> cb_;
		WhisperCPP* app_;
	};

	wxTextCtrl* out_;
	Whisper::iMediaFoundation* f_;
	bool did_init_;
	AppThread* volatile proc_;
	volatile bool run_;
};
