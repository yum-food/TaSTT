#include "Frame.h"
#include "PythonWrapper.h"

#include <filesystem>
#include <string>
#include <vector>

namespace {
    enum FrameIds {
        ID_PY_PANEL,
        ID_PY_VERSION_BUTTON,
        ID_PY_SETUP_BUTTON,
        ID_PY_APP_START_BUTTON,
        ID_PY_APP_STOP_BUTTON,
        ID_PY_OUT,
        ID_PY_APP_MIC,
        ID_PY_APP_LANG,
    };

    const wxString kMicChoices[] = {
        "index",
        "focusrite",
        // ok now this is epic
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
    };
    const size_t kNumMicChoices = sizeof(kMicChoices) / sizeof(kMicChoices[0]);

    // lifted from whisper/tokenizer.py
	const wxString kLangChoices[] = {
	    "english",
		"chinese",
		"german",
		"spanish",
		"russian",
		"korean",
		"french",
		"japanese",
		"portuguese",
		"turkish",
		"polish",
		"catalan",
		"dutch",
		"arabic",
		"swedish",
		"italian",
		"indonesian",
		"hindi",
		"finnish",
		"vietnamese",
		"hebrew",
		"ukrainian",
		"greek",
		"malay",
		"czech",
		"romanian",
		"danish",
		"hungarian",
		"tamil",
		"norwegian",
		"thai",
		"urdu",
		"croatian",
		"bulgarian",
		"lithuanian",
		"latin",
		"maori",
		"malayalam",
		"welsh",
		"slovak",
		"telugu",
		"persian",
		"latvian",
		"bengali",
		"serbian",
		"azerbaijani",
		"slovenian",
		"kannada",
		"estonian",
		"macedonian",
		"breton",
		"basque",
		"icelandic",
		"armenian",
		"nepali",
		"mongolian",
		"bosnian",
		"kazakh",
		"albanian",
		"swahili",
		"galician",
		"marathi",
		"punjabi",
		"sinhala",
		"khmer",
		"shona",
		"yoruba",
		"somali",
		"afrikaans",
		"occitan",
		"georgian",
		"belarusian",
		"tajik",
		"sindhi",
		"gujarati",
		"amharic",
		"yiddish",
		"lao",
		"uzbek",
		"faroese",
		"haitian creole",
		"pashto",
		"turkmen",
		"nynorsk",
		"maltese",
		"sanskrit",
		"luxembourgish",
		"myanmar",
		"tibetan",
		"tagalog",
		"malagasy",
		"assamese",
		"tatar",
		"hawaiian",
		"lingala",
		"hausa",
		"bashkir",
		"javanese",
		"sundanese"
	};
    const size_t kNumLangChoices = sizeof(kLangChoices) / sizeof(kLangChoices[0]);
}  // namespace

Frame::Frame()
    : wxFrame(nullptr, wxID_ANY, "TaSTT"),
    py_panel_(this, ID_PY_PANEL),
    py_panel_sizer_(wxVERTICAL),
    py_version_button_(&py_panel_, ID_PY_VERSION_BUTTON, "Check embedded Python version"),
    py_setup_button_(&py_panel_, ID_PY_SETUP_BUTTON, "Set up Python virtual environment"),
    py_app_start_button_(&py_panel_, ID_PY_APP_START_BUTTON, "Begin transcribing"),
    py_app_stop_button_(&py_panel_, ID_PY_APP_STOP_BUTTON, "Stop transcribing"),
    py_out_(&py_panel_, ID_PY_OUT, wxEmptyString, wxDefaultPosition,
        wxSize(/*x_px=*/480, /*y_px=*/160), wxTE_MULTILINE),
    py_app_(nullptr),
    py_app_mic_(&py_panel_, ID_PY_APP_MIC, wxDefaultPosition, wxDefaultSize, kNumMicChoices, kMicChoices),
    py_app_lang_(&py_panel_, ID_PY_APP_LANG, wxDefaultPosition, wxDefaultSize, kNumLangChoices, kLangChoices)
{
	Bind(wxEVT_MENU, &Frame::OnExit, this, wxID_EXIT);
	Bind(wxEVT_BUTTON, &Frame::OnGetPythonVersion, this, ID_PY_VERSION_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnAppStart, this, ID_PY_APP_START_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnAppStop, this, ID_PY_APP_STOP_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnSetupPython, this, ID_PY_SETUP_BUTTON);

	// wx needs this to be able to load PNGs.
	wxImage::AddHandler(&png_handler_);
	const std::string icon_path = "Resources/logo.png";
	LoadAndSetIcon(icon_path);

    wxSize py_out_size(/*x=*/80, /*y=*/20);
    py_out_.SetSize(py_out_size);
    py_app_mic_.SetSelection(0);
    py_app_lang_.SetSelection(0);

	py_panel_.SetSizer(&py_panel_sizer_);
    py_panel_sizer_.Add(&py_version_button_);
    py_panel_sizer_.Add(&py_setup_button_);
    py_panel_sizer_.Add(&py_app_mic_);
    py_panel_sizer_.Add(&py_app_lang_);
    py_panel_sizer_.Add(&py_app_start_button_);
    py_panel_sizer_.Add(&py_app_stop_button_);
    py_panel_sizer_.Add(&py_out_);
}

void Frame::OnExit(wxCommandEvent& event)
{
    Close(true);
}

void Frame::OnGetPythonVersion(wxCommandEvent& event)
{
    PythonWrapper py;
    std::string py_version = py.GetVersion();
    py_out_.AppendText(py_version + "\n");
}

void Frame::OnSetupPython(wxCommandEvent& event)
{
    PythonWrapper py;

    py_out_.AppendText("Setting up Python virtual environment\n");
    py_out_.AppendText("This could take several minutes, please be patient!\n");
    py_out_.AppendText("This will download ~5GB of dependencies.\n");
    py_out_.AppendText("Dependencies are installed in the GUI's folder, "
        "so deleting the folder is all that's needed to uninstall.\n");

    {
        std::string py_out;
        std::ostringstream py_out_oss;
        py_out_oss << "  Installing pip" << std::endl;
        py_out_.AppendText(py_out_oss.str());
        if (!py.InstallPip(&py_out)) {
            std::ostringstream py_out_oss;
            py_out_oss << "Failed to install pip: " << py_out;
            py_out_.AppendText(py_out_oss.str());
        }
    }

    const std::vector<std::string> pip_deps{
        "openvr",
        "pillow",
        "pyaudio",
        "python-osc",
        "playsound==1.2.2",
        "torch --extra-index-url https://download.pytorch.org/whl/cu116",
        "git+https://github.com/openai/whisper.git",
        "editdistance",
    };

    for (const auto& pip_dep : pip_deps) {
        {
            std::ostringstream py_out_oss;
            py_out_oss << "  Installing " << pip_dep << std::endl;
            py_out_.AppendText(py_out_oss.str());
        }
        std::string py_out;
        bool res = py.InvokeWithArgs({ "-m", "pip", "install", pip_dep }, &py_out);
        if (!res) {
            std::ostringstream py_out_oss;
            py_out_oss << "Failed to install " << pip_dep << ": " << py_out << std::endl;
            py_out_.AppendText(py_out_oss.str());
            return;
        }
    }

    py_out_.AppendText("Python virtual environment successfully set up!\n");
}

void Frame::OnAppStart(wxCommandEvent& event) {
    if (py_app_) {
        if (wxProcess::Exists(py_app_->GetPid())) {
            py_out_.AppendText("Transcription engine already running\n");
            return;
        }
        delete py_app_;
        py_app_ = nullptr;
    }

	py_out_.AppendText("Launching transcription engine\n");

    PythonWrapper py;
    auto cb = [&](wxProcess* proc, int ret) -> void {
		std::ostringstream py_out_oss;
        py_out_oss << "Transcription engine exited with code " << ret << std::endl;

		py_out_.AppendText(py_out_oss.str());
		return;
    };

    int which_mic = py_app_mic_.GetSelection();
    if (which_mic == wxNOT_FOUND) {
        which_mic = 0;
    }
    int which_lang = py_app_lang_.GetSelection();
    if (which_lang == wxNOT_FOUND) {
        which_lang = 0;
    }

    wxProcess* p = py.StartApp(std::move(cb),
        kMicChoices[which_mic].ToStdString(),
        kLangChoices[which_lang].ToStdString());
    if (!p) {
        py_out_.AppendText("Failed to launch transcription engine\n");
        return;
    }

    py_app_ = p;
}

void Frame::OnAppStop(wxCommandEvent& event) {
    if (py_app_) {
        const long pid = py_app_->GetPid();

        // Try to kill it politely.
        wxProcess::Kill(pid);
        for (int i = 0; i < 10; i++) {
            if (!wxProcess::Exists(pid)) {
                break;
            }
            wxMilliSleep(10);
        }

        // If it doesn't accept its fate, murder it with an axe.
		bool first = true;
        int loop_cnt = 0;
		while (wxProcess::Exists(pid)) {
			if (first) {
				first = false;
				py_out_.AppendText("Timed out trying to stop transcription engine "
					"cleanly, sending SIGKILL\n");
			}
			else if (++loop_cnt % 100 == 0) {
                    py_out_.AppendText("Waiting for transcription engine to exit");
			}
			wxProcess::Kill(pid, wxSIGKILL);
			wxMilliSleep(10);
        }

        // Since we don't process the termination event, py_app_ deletes itself!
        py_app_ = nullptr;
        py_out_.AppendText("Stopped transcription engine\n");
    }
    else {
        py_out_.AppendText("Transcription engine already stopped\n");
    }
}

void Frame::LoadAndSetIcon(const std::string& icon_path) {
    if (!std::filesystem::exists(icon_path)) {
        wxLogFatalError("Logo is missing from %s", icon_path.c_str());
    }
    wxBitmap icon_img(icon_path, wxBITMAP_TYPE_PNG);
    wxIcon icon;
    icon.CopyFromBitmap(icon_img);
    SetIcon(icon);
}

