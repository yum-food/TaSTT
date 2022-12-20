#include "Frame.h"
#include "PythonWrapper.h"

#include <filesystem>
#include <string>
#include <vector>
#include <wx/filepicker.h>

namespace {
    enum FrameIds {
		ID_MAIN_PANEL,
		ID_NAVBAR,
		ID_NAVBAR_BUTTON_TRANSCRIBE,
		ID_NAVBAR_BUTTON_UNITY,
        ID_PY_PANEL,
        ID_PY_CONFIG_PANEL,
        ID_PY_CONFIG_DROPDOWN_PANEL,
        ID_PY_SETUP_BUTTON,
        ID_PY_DUMP_MICS_BUTTON,
        ID_PY_APP_START_BUTTON,
        ID_PY_APP_STOP_BUTTON,
        ID_TRANSCRIBE_OUT,
        ID_PY_APP_MIC,
        ID_PY_APP_MIC_PANEL,
        ID_PY_APP_LANG,
        ID_PY_APP_LANG_PANEL,
        ID_PY_APP_MODEL,
        ID_PY_APP_MODEL_PANEL,
        ID_UNITY_PANEL,
        ID_UNITY_CONFIG_PANEL,
        ID_UNITY_OUT,
		ID_UNITY_ANIMATOR_FILE_PICKER,
		ID_UNITY_PARAMETERS_FILE_PICKER,
		ID_UNITY_MENU_FILE_PICKER,
		ID_UNITY_CONFIG_PANEL_PAIRS,
		ID_UNITY_ANIMATOR_GENERATED_DIR,
		ID_UNITY_ANIMATOR_GENERATED_NAME,
		ID_UNITY_PARAMETERS_GENERATED_NAME,
		ID_UNITY_MENU_GENERATED_NAME,
		ID_UNITY_BUTTON_GEN_ANIMATOR,
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
    auto* main_panel = new wxPanel(this, ID_MAIN_PANEL);
	main_panel_ = main_panel;
    {
        auto* navbar = new wxPanel(main_panel, ID_NAVBAR);
        {
			auto* navbar_button_transcribe = new wxButton(navbar, ID_NAVBAR_BUTTON_TRANSCRIBE, "Transcription");
			auto* navbar_button_unity = new wxButton(navbar, ID_NAVBAR_BUTTON_UNITY, "Unity");

			auto* sizer = new wxBoxSizer(wxVERTICAL);
			navbar->SetSizer(sizer);

			sizer->Add(navbar_button_transcribe, /*proportion=*/0, /*flags=*/wxEXPAND);
			sizer->Add(navbar_button_unity, /*proportion=*/0, /*flags=*/wxEXPAND);
        }

        auto* transcribe_panel = new wxPanel(main_panel, ID_PY_PANEL);
        transcribe_panel_ = transcribe_panel;
        {
            const auto transcribe_out_sz = wxSize(/*x_px=*/320, /*y_px=*/160);
            auto* transcribe_out = new wxTextCtrl(transcribe_panel, ID_TRANSCRIBE_OUT,
                wxEmptyString,
                wxDefaultPosition,
                transcribe_out_sz, wxTE_MULTILINE | wxTE_READONLY);
            transcribe_out->SetMinSize(transcribe_out_sz);
            transcribe_out_ = transcribe_out;

            transcribe_out_->AppendText(PythonWrapper::GetVersion() + "\n");

            auto* py_config_panel = new wxPanel(transcribe_panel, ID_PY_CONFIG_PANEL);
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

                    auto* sizer = new wxFlexGridSizer(/*cols=*/2);
                    py_config_dropdown_panel->SetSizer(sizer);

                    sizer->Add(new wxStaticText(py_config_dropdown_panel, wxID_ANY, /*label=*/"Microphone:"));
                    sizer->Add(py_app_mic, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_config_dropdown_panel, wxID_ANY, /*label=*/"Language:"));
                    sizer->Add(py_app_lang, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_config_dropdown_panel, wxID_ANY, /*label=*/"Model:"));
                    sizer->Add(py_app_model, /*proportion=*/0, /*flags=*/wxEXPAND);
                }

                auto* py_app_start_button = new wxButton(py_config_panel, ID_PY_APP_START_BUTTON, "Begin transcribing");
                auto* py_app_stop_button = new wxButton(py_config_panel, ID_PY_APP_STOP_BUTTON, "Stop transcribing");

                auto* sizer = new wxBoxSizer(wxVERTICAL);
                py_config_panel->SetSizer(sizer);
                sizer->Add(py_setup_button, /*proportion=*/0, /*flags=*/wxEXPAND);
                sizer->Add(py_dump_mics_button, /*proportion=*/0, /*flags=*/wxEXPAND);
                sizer->Add(py_config_dropdown_panel, /*proportion=*/0, /*flags=*/wxEXPAND);
                sizer->Add(py_app_start_button, /*proportion=*/0, /*flags=*/wxEXPAND);
                sizer->Add(py_app_stop_button, /*proportion=*/0, /*flags=*/wxEXPAND);
            }

            auto* sizer = new wxBoxSizer(wxHORIZONTAL);
            transcribe_panel->SetSizer(sizer);
            sizer->Add(py_config_panel);
            sizer->Add(transcribe_out);
        }

        auto* unity_panel = new wxPanel(main_panel, ID_UNITY_PANEL);
        unity_panel_ = unity_panel;
        {
            const auto unity_out_sz = wxSize(/*x_px=*/320, /*y_px=*/160);
            auto* unity_out = new wxTextCtrl(unity_panel, ID_UNITY_OUT,
                wxEmptyString,
                wxDefaultPosition,
                unity_out_sz, wxTE_MULTILINE | wxTE_READONLY);
            unity_out->SetMinSize(unity_out_sz);
            unity_out_ = unity_out;

            auto* unity_config_panel = new wxPanel(unity_panel, ID_UNITY_CONFIG_PANEL);
            {
				auto* unity_config_panel_pairs = new wxPanel(unity_config_panel, ID_UNITY_CONFIG_PANEL_PAIRS);
                {
                    auto* unity_animator_file_picker = new wxFilePickerCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_ANIMATOR_FILE_PICKER,
                        /*path=*/wxEmptyString,
                        /*message=*/"FX controller path",
                        /*wildcard=*/wxFileSelectorDefaultWildcardStr,
                        /*pos=*/wxDefaultPosition,
                        /*size=*/wxDefaultSize
                        );
                    unity_animator_file_picker_ = unity_animator_file_picker;

                    auto* unity_parameters_file_picker = new wxFilePickerCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_PARAMETERS_FILE_PICKER,
                        /*path=*/wxEmptyString,
                        /*message=*/"Avatar parameters path",
                        /*wildcard=*/wxFileSelectorDefaultWildcardStr,
                        /*pos=*/wxDefaultPosition,
                        /*size=*/wxDefaultSize
                        );
                    unity_parameters_file_picker_ = unity_parameters_file_picker;

                    auto* unity_menu_file_picker = new wxFilePickerCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_MENU_FILE_PICKER,
                        /*path=*/wxEmptyString,
                        /*message=*/"Avatar menu path",
                        /*wildcard=*/wxFileSelectorDefaultWildcardStr,
                        /*pos=*/wxDefaultPosition,
                        /*size=*/wxDefaultSize
                        );
                    unity_parameters_file_picker_ = unity_parameters_file_picker;

					auto* unity_animator_generated_dir = new wxTextCtrl(unity_config_panel_pairs,
                        ID_UNITY_ANIMATOR_GENERATED_DIR,
						wxEmptyString,
						wxDefaultPosition);
                    unity_animator_generated_dir->AppendText("TaSTT_Generated");
                    unity_animator_generated_dir_ = unity_animator_generated_dir;

					auto* unity_animator_generated_name = new wxTextCtrl(unity_config_panel_pairs,
                        ID_UNITY_ANIMATOR_GENERATED_NAME);
                    unity_animator_generated_name->AppendText("TaSTT.controller");
                    unity_animator_generated_name_ = unity_animator_generated_name;

					auto* unity_parameters_generated_name = new wxTextCtrl(unity_config_panel_pairs,
                        ID_UNITY_PARAMETERS_GENERATED_NAME);
                    unity_parameters_generated_name->AppendText("TaSTT_Menu.asset");
                    unity_parameters_generated_name_ = unity_parameters_generated_name;

					auto* unity_menu_generated_name = new wxTextCtrl(unity_config_panel_pairs,
                        ID_UNITY_MENU_GENERATED_NAME);
                    unity_menu_generated_name->AppendText("TaSTT_Parameters.asset");
                    unity_menu_generated_name_ = unity_menu_generated_name;

                    auto* sizer = new wxFlexGridSizer(/*cols=*/2);
                    unity_config_panel_pairs->SetSizer(sizer);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"FX controller:"));
                    sizer->Add(unity_animator_file_picker);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"Avatar parameters:"));
                    sizer->Add(unity_parameters_file_picker);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"Avatar menu:"));
                    sizer->Add(unity_menu_file_picker);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"Generated assets folder:"));
                    sizer->Add(unity_animator_generated_dir);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"Generated FX controller:"));
                    sizer->Add(unity_animator_generated_name);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"Generated parameters:"));
                    sizer->Add(unity_parameters_generated_name);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"Generated menu:"));
                    sizer->Add(unity_menu_generated_name);
                }

				auto* unity_button_gen_fx = new wxButton(unity_config_panel, ID_UNITY_BUTTON_GEN_ANIMATOR, "Generate avatar assets");
                unity_button_gen_fx->SetWindowStyleFlag(wxBU_EXACTFIT);

				auto* sizer = new wxBoxSizer(wxVERTICAL);
				unity_config_panel->SetSizer(sizer);
				sizer->Add(unity_config_panel_pairs);
				sizer->Add(unity_button_gen_fx, /*proportion=*/0, /*flags=*/wxEXPAND);
            }

            auto* sizer = new wxBoxSizer(wxHORIZONTAL);
            unity_panel->SetSizer(sizer);
            sizer->Add(unity_config_panel);
            sizer->Add(unity_out);
        }
        unity_panel_->Hide();

		auto* sizer = new wxBoxSizer(wxHORIZONTAL);
		main_panel->SetSizer(sizer);
		sizer->Add(navbar);
		sizer->Add(transcribe_panel);
		sizer->Add(unity_panel);
    }

	Bind(wxEVT_MENU, &Frame::OnExit, this, wxID_EXIT);
	Bind(wxEVT_BUTTON, &Frame::OnNavbarTranscribe, this, ID_NAVBAR_BUTTON_TRANSCRIBE);
	Bind(wxEVT_BUTTON, &Frame::OnNavbarUnity, this, ID_NAVBAR_BUTTON_UNITY);
	Bind(wxEVT_BUTTON, &Frame::OnAppStart, this, ID_PY_APP_START_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnAppStop, this, ID_PY_APP_STOP_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnSetupPython, this, ID_PY_SETUP_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnDumpMics, this, ID_PY_DUMP_MICS_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnGenerateFX, this, ID_UNITY_BUTTON_GEN_ANIMATOR);

	// wx needs this to be able to load PNGs.
	wxImage::AddHandler(&png_handler_);
	LoadAndSetIcons();

    Resize();
}

void Frame::OnExit(wxCommandEvent& event)
{
    OnAppStop(event);
    Close(true);
}

void Frame::OnNavbarTranscribe(wxCommandEvent& event)
{
    transcribe_panel_->Show();
    unity_panel_->Hide();
    Resize();
}

void Frame::OnNavbarUnity(wxCommandEvent& event)
{
    transcribe_panel_->Hide();
    unity_panel_->Show();
    Resize();
}

void Frame::OnSetupPython(wxCommandEvent& event)
{
    transcribe_out_->AppendText("Setting up Python virtual environment\n");
    transcribe_out_->AppendText("This could take several minutes, please be patient!\n");
    transcribe_out_->AppendText("This will download ~5GB of dependencies.\n");

    {
        std::string transcribe_out;
        std::ostringstream transcribe_out_oss;
        transcribe_out_oss << "  Installing pip" << std::endl;
        transcribe_out_->AppendText(transcribe_out_oss.str());
        if (!PythonWrapper::InstallPip(&transcribe_out)) {
            std::ostringstream transcribe_out_oss;
            transcribe_out_oss << "Failed to install pip: " << transcribe_out;
            transcribe_out_->AppendText(transcribe_out_oss.str());
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
            std::ostringstream transcribe_out_oss;
            transcribe_out_oss << "  Installing " << pip_dep << std::endl;
            transcribe_out_->AppendText(transcribe_out_oss.str());
        }
        std::string transcribe_out;
        bool res = PythonWrapper::InvokeWithArgs({ "-m", "pip", "install", pip_dep }, &transcribe_out);
        if (!res) {
            std::ostringstream transcribe_out_oss;
            transcribe_out_oss << "Failed to install " << pip_dep << ": " << transcribe_out << std::endl;
            transcribe_out_->AppendText(transcribe_out_oss.str());
            return;
        }
    }

    transcribe_out_->AppendText("Python virtual environment successfully set up!\n");
}

void Frame::OnDumpMics(wxCommandEvent& event)
{
    transcribe_out_->AppendText(PythonWrapper::DumpMics());
}

void Frame::OnGenerateFX(wxCommandEvent& event)
{
}

void Frame::OnAppStart(wxCommandEvent& event) {
    if (py_app_) {
        if (wxProcess::Exists(py_app_->GetPid())) {
            transcribe_out_->AppendText("Transcription engine already running\n");
            return;
        }
        delete py_app_;
        py_app_ = nullptr;
    }

	transcribe_out_->AppendText("Launching transcription engine\n");

    auto cb = [&](wxProcess* proc, int ret) -> void {
		std::ostringstream transcribe_out_oss;
        transcribe_out_oss << "Transcription engine exited with code " << ret << std::endl;

		transcribe_out_->AppendText(transcribe_out_oss.str());
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
        transcribe_out_->AppendText("Failed to launch transcription engine\n");
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
				transcribe_out_->AppendText("Timed out trying to stop transcription engine "
					"cleanly, sending SIGKILL\n");
			}
			else if (++loop_cnt % 100 == 0) {
                    transcribe_out_->AppendText("Waiting for transcription engine to exit");
			}
			wxProcess::Kill(pid, wxSIGKILL);
			wxMilliSleep(10);
        }

        // Since we don't process the termination event, py_app_ deletes itself!
        py_app_ = nullptr;
        transcribe_out_->AppendText("Stopped transcription engine\n");
    }
    else {
        transcribe_out_->AppendText("Transcription engine already stopped\n");
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

void Frame::Resize()
{
	auto frame_sz = GetBestSize();
	auto panel_sz = main_panel_->GetBestSize();

	auto ideal_sz = panel_sz;
	ideal_sz.x += frame_sz.x;
	ideal_sz.y += frame_sz.y;

	this->SetSize(ideal_sz);
}

