#include "Frame.h"
#include "PythonWrapper.h"

#include <filesystem>
#include <string>
#include <vector>

namespace {
    enum FrameIds {
        ID_PY_PANEL,
        ID_PY_CONFIG_PANEL,
        ID_PY_CONFIG_DROPDOWN_PANEL,
        ID_PY_SETUP_BUTTON,
        ID_PY_DUMP_MICS_BUTTON,
        ID_PY_APP_START_BUTTON,
        ID_PY_APP_STOP_BUTTON,
        ID_PY_OUT,
        ID_PY_APP_MIC,
        ID_PY_APP_MIC_PANEL,
        ID_PY_APP_LANG,
        ID_PY_APP_LANG_PANEL,
        ID_PY_APP_MODEL,
        ID_PY_APP_MODEL_PANEL,
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
    constexpr int kMicDefault = 0;  // index

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
    constexpr int kLangDefault = 0;  // english

    // lifted from whisper/__init__.py
    const wxString kModelChoices[] = {
        "tiny.en",
        "tiny",
        "base.en",
        "base",
        "small.en",
        "small",
        "medium.en",
        "medium",
    };
    const size_t kNumModelChoices = sizeof(kModelChoices) / sizeof(kModelChoices[0]);
    constexpr int kModelDefault = 2;  // base.en
}  // namespace

Frame::Frame()
    : wxFrame(nullptr, wxID_ANY, "TaSTT"),
    py_app_(nullptr)
{
    auto* py_panel = new wxPanel(this, ID_PY_PANEL);
    {
        const auto py_out_sz = wxSize(/*x_px=*/320, /*y_px=*/160);
		auto* py_out = new wxTextCtrl(py_panel, ID_PY_OUT,
            wxEmptyString,
            wxDefaultPosition,
			py_out_sz, wxTE_MULTILINE | wxTE_READONLY);
        py_out->SetMinSize(py_out_sz);
        py_out_ = py_out;

        py_out_->AppendText(PythonWrapper::GetVersion() + "\n");

		auto* py_config_panel = new wxPanel(py_panel, ID_PY_CONFIG_PANEL);
        {
            auto* py_setup_button = new wxButton(py_config_panel, ID_PY_SETUP_BUTTON, "Set up Python virtual environment");
            auto* py_dump_mics_button = new wxButton(py_config_panel, ID_PY_DUMP_MICS_BUTTON, "List input devices");

            auto* py_config_dropdown_panel = new wxPanel(py_config_panel, ID_PY_CONFIG_DROPDOWN_PANEL);
            {
                auto* py_app_mic = new wxChoice(py_config_dropdown_panel, ID_PY_APP_MIC, wxDefaultPosition,
                    wxDefaultSize, kNumMicChoices, kMicChoices);
				py_app_mic->SetSelection(kMicDefault);
				py_app_mic_ = py_app_mic;

                auto* py_app_lang = new wxChoice(py_config_dropdown_panel, ID_PY_APP_LANG, wxDefaultPosition,
                    wxDefaultSize, kNumLangChoices, kLangChoices);
                py_app_lang->SetSelection(kLangDefault);
				py_app_lang_ = py_app_lang;

                auto* py_app_model = new wxChoice(py_config_dropdown_panel, ID_PY_APP_MODEL, wxDefaultPosition,
                    wxDefaultSize, kNumModelChoices, kModelChoices);
                py_app_model->SetSelection(kModelDefault);
                py_app_model_ = py_app_model;

                auto* sizer = new wxGridSizer(/*cols=*/2);
                py_config_dropdown_panel->SetSizer(sizer);

				sizer->Add(new wxStaticText(py_config_dropdown_panel, wxID_ANY, /*label=*/"Microphone:"));
                sizer->Add(py_app_mic);

				sizer->Add(new wxStaticText(py_config_dropdown_panel, wxID_ANY, /*label=*/"Language:"));
                sizer->Add(py_app_lang);

				sizer->Add(new wxStaticText(py_config_dropdown_panel, wxID_ANY, /*label=*/"Model:"));
                sizer->Add(py_app_model);
            }

            auto* py_app_start_button = new wxButton(py_config_panel, ID_PY_APP_START_BUTTON, "Begin transcribing");
            auto* py_app_stop_button = new wxButton(py_config_panel, ID_PY_APP_STOP_BUTTON, "Stop transcribing");

            auto* sizer = new wxBoxSizer(wxVERTICAL);
			py_config_panel->SetSizer(sizer);
			sizer->Add(py_setup_button);
			sizer->Add(py_dump_mics_button);
			sizer->Add(py_config_dropdown_panel);
			sizer->Add(py_app_start_button);
			sizer->Add(py_app_stop_button);
        }

		auto* sizer = new wxBoxSizer(wxHORIZONTAL);
        py_panel->SetSizer(sizer);
        sizer->Add(py_config_panel);
        sizer->Add(py_out);
    }

	Bind(wxEVT_MENU, &Frame::OnExit, this, wxID_EXIT);
	Bind(wxEVT_BUTTON, &Frame::OnAppStart, this, ID_PY_APP_START_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnAppStop, this, ID_PY_APP_STOP_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnSetupPython, this, ID_PY_SETUP_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnDumpMics, this, ID_PY_DUMP_MICS_BUTTON);

	// wx needs this to be able to load PNGs.
	wxImage::AddHandler(&png_handler_);
	LoadAndSetIcons();

	{
        auto frame_sz = GetBestSize();
		auto panel_sz = py_panel->GetBestSize();

        auto ideal_sz = panel_sz;
        ideal_sz.y += frame_sz.y;

        this->SetSize(ideal_sz);
	}
}

void Frame::OnExit(wxCommandEvent& event)
{
    OnAppStop(event);
    Close(true);
}

void Frame::OnSetupPython(wxCommandEvent& event)
{
    py_out_->AppendText("Setting up Python virtual environment\n");
    py_out_->AppendText("This could take several minutes, please be patient!\n");
    py_out_->AppendText("This will download ~5GB of dependencies.\n");

    {
        std::string py_out;
        std::ostringstream py_out_oss;
        py_out_oss << "  Installing pip" << std::endl;
        py_out_->AppendText(py_out_oss.str());
        if (!PythonWrapper::InstallPip(&py_out)) {
            std::ostringstream py_out_oss;
            py_out_oss << "Failed to install pip: " << py_out;
            py_out_->AppendText(py_out_oss.str());
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
            py_out_->AppendText(py_out_oss.str());
        }
        std::string py_out;
        bool res = PythonWrapper::InvokeWithArgs({ "-m", "pip", "install", pip_dep }, &py_out);
        if (!res) {
            std::ostringstream py_out_oss;
            py_out_oss << "Failed to install " << pip_dep << ": " << py_out << std::endl;
            py_out_->AppendText(py_out_oss.str());
            return;
        }
    }

    py_out_->AppendText("Python virtual environment successfully set up!\n");
}

void Frame::OnDumpMics(wxCommandEvent& event)
{
    py_out_->AppendText(PythonWrapper::DumpMics());
}

void Frame::OnAppStart(wxCommandEvent& event) {
    if (py_app_) {
        if (wxProcess::Exists(py_app_->GetPid())) {
            py_out_->AppendText("Transcription engine already running\n");
            return;
        }
        delete py_app_;
        py_app_ = nullptr;
    }

	py_out_->AppendText("Launching transcription engine\n");

    auto cb = [&](wxProcess* proc, int ret) -> void {
		std::ostringstream py_out_oss;
        py_out_oss << "Transcription engine exited with code " << ret << std::endl;

		py_out_->AppendText(py_out_oss.str());
		return;
    };

    int which_mic = py_app_mic_->GetSelection();
    if (which_mic == wxNOT_FOUND) {
        which_mic = kMicDefault;
    }
    int which_lang = py_app_lang_->GetSelection();
    if (which_lang == wxNOT_FOUND) {
        which_lang = kLangDefault;
    }
    int which_model = py_app_model_->GetSelection();
    if (which_model == wxNOT_FOUND) {
        which_model = kModelDefault;
    }

    wxProcess* p = PythonWrapper::StartApp(std::move(cb),
        kMicChoices[which_mic].ToStdString(),
        kLangChoices[which_lang].ToStdString(),
        kModelChoices[which_model].ToStdString());
    if (!p) {
        py_out_->AppendText("Failed to launch transcription engine\n");
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
				py_out_->AppendText("Timed out trying to stop transcription engine "
					"cleanly, sending SIGKILL\n");
			}
			else if (++loop_cnt % 100 == 0) {
                    py_out_->AppendText("Waiting for transcription engine to exit");
			}
			wxProcess::Kill(pid, wxSIGKILL);
			wxMilliSleep(10);
        }

        // Since we don't process the termination event, py_app_ deletes itself!
        py_app_ = nullptr;
        py_out_->AppendText("Stopped transcription engine\n");
    }
    else {
        py_out_->AppendText("Transcription engine already stopped\n");
    }
}

void Frame::LoadAndSetIcons() {
    const char* icons[] = {
        "Resources/Images/logo.png",
        "Resources/Images/logo_16x16.png",
        "Resources/Images/logo_32x32.png",
    };
    wxIconBundle icon_bundle;
    for (const auto& icon_path : icons) {
        if (!std::filesystem::exists(icon_path)) {
            wxLogFatalError("Logo is missing from %s", icon_path);
        }
        icon_bundle.AddIcon(icon_path, wxBITMAP_TYPE_PNG);
    }
    SetIcons(icon_bundle);
}

