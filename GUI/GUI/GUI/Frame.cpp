#include "Frame.h"
#include "Logging.h"
#include "PythonWrapper.h"
#include "ScopeGuard.h"
#include "Util.h"

#include <filesystem>
#include <string>
#include <vector>
#include <wx/filepicker.h>
#include <wx/txtstrm.h>

namespace {
    enum FrameIds {
		ID_MAIN_PANEL,
		ID_NAVBAR,
		ID_NAVBAR_BUTTON_TRANSCRIBE,
		ID_NAVBAR_BUTTON_UNITY,
		ID_NAVBAR_BUTTON_DEBUG,
		ID_NAVBAR_BUTTON_WHISPER,
        ID_PY_PANEL,
        ID_PY_CONFIG_PANEL,
        ID_PY_APP_CONFIG_PANEL_PAIRS,
        ID_PY_SETUP_BUTTON,
        ID_PY_DUMP_MICS_BUTTON,
        ID_PY_APP_DRAIN,
        ID_PY_APP_START_BUTTON,
        ID_PY_APP_STOP_BUTTON,
        ID_TRANSCRIBE_OUT,
        ID_PY_APP_MIC,
        ID_PY_APP_MIC_PANEL,
        ID_PY_APP_LANG,
        ID_PY_APP_LANG_PANEL,
        ID_PY_APP_MODEL,
        ID_PY_APP_CHARS_PER_SYNC,
        ID_PY_APP_BYTES_PER_CHAR,
        ID_PY_APP_BUTTON,
        ID_PY_APP_MODEL_PANEL,
        ID_PY_APP_ENABLE_LOCAL_BEEP,
        ID_PY_APP_USE_CPU,
        ID_PY_APP_USE_BUILTIN,
        ID_PY_APP_ROWS,
        ID_PY_APP_COLS,
        ID_PY_APP_WINDOW_DURATION,
        ID_UNITY_PANEL,
        ID_UNITY_CONFIG_PANEL,
        ID_UNITY_OUT,
		ID_UNITY_ASSETS_FILE_PICKER,
		ID_UNITY_ANIMATOR_FILE_PICKER,
		ID_UNITY_PARAMETERS_FILE_PICKER,
		ID_UNITY_MENU_FILE_PICKER,
		ID_UNITY_CONFIG_PANEL_PAIRS,
		ID_UNITY_ANIMATOR_GENERATED_DIR,
		ID_UNITY_ANIMATOR_GENERATED_NAME,
		ID_UNITY_PARAMETERS_GENERATED_NAME,
		ID_UNITY_MENU_GENERATED_NAME,
		ID_UNITY_BUTTON_GEN_ANIMATOR,
        ID_UNITY_CHARS_PER_SYNC,
        ID_UNITY_BYTES_PER_CHAR,
        ID_UNITY_ROWS,
        ID_UNITY_COLS,
        ID_UNITY_CLEAR_OSC,
		ID_DEBUG_PANEL,
		ID_DEBUG_OUT,
		ID_DEBUG_CONFIG_PANEL,
		ID_DEBUG_BUTTON_CLEAR_PIP,
		ID_DEBUG_BUTTON_LIST_PIP,
		ID_DEBUG_BUTTON_RESET_VENV,
		ID_DEBUG_BUTTON_CLEAR_OSC,
		ID_DEBUG_BUTTON_BACKUP_VENV,
		ID_DEBUG_BUTTON_RESTORE_VENV,
		ID_WHISPER_PANEL,
		ID_WHISPER_OUT,
		ID_WHISPER_CONFIG_PANEL,
		ID_WHISPER_SETUP_BUTTON,
		//ID_WHISPER_DUMP_MICS_BUTTON,
		ID_WHISPER_CONFIG_PANEL_PAIRS,
		ID_WHISPER_MIC,
		ID_WHISPER_LANG,
		ID_WHISPER_MODEL,
		ID_WHISPER_CHARS_PER_SYNC,
		ID_WHISPER_BYTES_PER_CHAR,
		ID_WHISPER_BUTTON,
		ID_WHISPER_ROWS,
		ID_WHISPER_COLS,
		ID_WHISPER_BROWSER_SRC_PORT,
		ID_WHISPER_ENABLE_LOCAL_BEEP,
		ID_WHISPER_USE_CPU,
		ID_WHISPER_DECODE_METHOD,
		ID_WHISPER_MAX_CTXT,
		ID_WHISPER_BEAM_WIDTH,
		ID_WHISPER_BEAM_N_BEST,
		ID_WHISPER_VAD_MIN_DURATION,
		ID_WHISPER_VAD_MAX_DURATION,
		ID_WHISPER_VAD_DROP_START_SILENCE,
		ID_WHISPER_VAD_PAUSE_DURATION,
		ID_WHISPER_VAD_RETAIN_DURATION,
		ID_WHISPER_ENABLE_BUILTIN,
		ID_WHISPER_ENABLE_CUSTOM,
		ID_WHISPER_ENABLE_BROWSER_SRC,
		ID_WHISPER_START_BUTTON,
		ID_WHISPER_STOP_BUTTON,
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

    wxString kWhisperMicChoices[] = {
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
    const size_t kNumWhisperMicChoices = sizeof(kWhisperMicChoices) / sizeof(kWhisperMicChoices[0]);
    constexpr int kWhisperMicDefault = 0;  // index

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

    // Source: https://huggingface.co/datasets/ggerganov/whisper.cpp/tree/main
    const wxString kWhisperModelChoices[] = {
        "ggml-tiny.bin",
        "ggml-tiny.en.bin",
        "ggml-base.bin",
        "ggml-base.en.bin",
        "ggml-small.bin",
        "ggml-small.en.bin",
        "ggml-medium.bin",
        "ggml-medium.en.bin",
        "ggml-large.bin",
    };
    const size_t kNumWhisperModelChoices = sizeof(kWhisperModelChoices) /
        sizeof(kWhisperModelChoices[0]);
    constexpr int kWhisperModelDefault = 6;  // medium.bin

    const wxString kCharsPerSync[] = {
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
    };
    const size_t kNumCharsPerSync = sizeof(kCharsPerSync) / sizeof(kCharsPerSync[0]);
    // 20 chars per sync is a good balance between parameter space and speed:
    //   20 * 8 + 25 = 185 bits, leaving 71 bits for other systems.
    constexpr int kCharsDefault = kNumCharsPerSync - 5;

    const wxString kBytesPerChar[] = {
        "1",
        "2",
    };
    const size_t kNumBytesPerChar = sizeof(kBytesPerChar) / sizeof(kBytesPerChar[0]);
    // Sorry international users. Optimize for English speakers, by default.
    constexpr int kBytesDefault = 0;

    const wxString kButton[] = {
        "left joystick",
        "left a",
        "left b",
        "right joystick",
        "right a",
        "right b",
    };
    const size_t kNumButtons = sizeof(kButton) / sizeof(kButton[0]);
    constexpr int kButtonDefault = 0;

    const wxString kDecodeMethods[] = {
        "greedy",
        "beam",
    };
    const size_t kNumDecodeMethods = sizeof(kDecodeMethods) / sizeof(kDecodeMethods[0]);
    constexpr int kDecodeMethodDefault = 0;

    // Given the string value of a dropdown menu's entry, find its index. If no
    // entry matches, return `default_index`.
	int GetDropdownChoiceIndex(const wxString menu[],
        const size_t num_menu_entries, const std::string& entry,
		const int default_index) {
		for (int i = 0; i < num_menu_entries; i++) {
			if (entry == menu[i]) {
				return i;
			}
		}
		return default_index;
	}

}  // namespace

using ::Logging::DrainAsyncOutput;
using ::Logging::Log;

Frame::Frame()
    : wxFrame(nullptr, wxID_ANY, "TaSTT"),
    run_py_app_(false),
    py_app_drain_(this, ID_PY_APP_DRAIN)
{
    app_c_ = std::make_unique<AppConfig>(nullptr);

	// Initialize futures so that valid() returns true. We use this as a proxy
	// to tell whether they're still executing.
	{
		auto p = std::promise<bool>();
		py_app_ = p.get_future();
		p.set_value(true);
	}
	{
		auto p = std::promise<bool>();
		unity_app_ = p.get_future();
		p.set_value(true);
	}
	{
		auto p = std::promise<bool>();
		dump_mics_ = p.get_future();
		p.set_value(true);
	}
	{
		auto p = std::promise<bool>();
		env_proc_ = p.get_future();
		p.set_value(true);
	}

    auto* main_panel = new wxPanel(this, ID_MAIN_PANEL);
	main_panel_ = main_panel;
    {
        auto* navbar = new wxPanel(main_panel, ID_NAVBAR);
        {
			auto* navbar_button_transcribe = new wxButton(navbar,
                ID_NAVBAR_BUTTON_TRANSCRIBE, "Transcription (PY)");
			auto* navbar_button_whisper = new wxButton(navbar,
                ID_NAVBAR_BUTTON_WHISPER, "Transcription (CPP)");
			auto* navbar_button_unity = new wxButton(navbar,
                ID_NAVBAR_BUTTON_UNITY, "Unity");
			auto* navbar_button_debug = new wxButton(navbar,
                ID_NAVBAR_BUTTON_DEBUG, "Debug");

			auto* sizer = new wxBoxSizer(wxVERTICAL);
			navbar->SetSizer(sizer);

			sizer->Add(navbar_button_transcribe, /*proportion=*/0,
                /*flags=*/wxEXPAND);
			sizer->Add(navbar_button_whisper, /*proportion=*/0,
                /*flags=*/wxEXPAND);
			sizer->Add(navbar_button_unity, /*proportion=*/0,
                /*flags=*/wxEXPAND);
			sizer->Add(navbar_button_debug, /*proportion=*/0,
                /*flags=*/wxEXPAND);
        }

        auto* transcribe_panel = new wxPanel(main_panel, ID_PY_PANEL);
        transcribe_panel_ = transcribe_panel;
        {
            const auto transcribe_out_sz = wxSize(/*x_px=*/480, /*y_px=*/160);
            auto* transcribe_out = new wxTextCtrl(transcribe_panel,
                ID_TRANSCRIBE_OUT, wxEmptyString, wxDefaultPosition,
                transcribe_out_sz, wxTE_MULTILINE | wxTE_READONLY);
            transcribe_out->SetMinSize(transcribe_out_sz);
            transcribe_out_ = transcribe_out;

            Log(transcribe_out_, "{}\n", PythonWrapper::GetVersion());

            auto* py_config_panel = new wxPanel(transcribe_panel,
                ID_PY_CONFIG_PANEL);
            {
                auto* py_setup_button = new wxButton(py_config_panel,
                    ID_PY_SETUP_BUTTON, "Set up Python virtual environment");
                py_setup_button->SetToolTip(
                    "TaSTT uses the Python programming language to provide both "
                    "transcription services and to interface with Unity. "
                    "It installs its dependencies into an isolated folder "
                    "called a 'virtual environment'. Click this button to "
                    "install those dependencies. This only has to be done "
                    "once when you install a new version of TaSTT.");
                auto* py_dump_mics_button = new wxButton(py_config_panel,
                    ID_PY_DUMP_MICS_BUTTON, "List input devices");
                py_dump_mics_button->SetToolTip(
                    "List the microphones (and input devices) attached to "
                    "your computer. To use a microphone, enter the number "
                    "to its left in the 'Microphone' dropdown.");
                auto* py_app_config_panel_pairs = new wxPanel(py_config_panel,
                    ID_PY_APP_CONFIG_PANEL_PAIRS);
                {
                    auto* py_app_mic = new wxChoice(py_app_config_panel_pairs,
                        ID_PY_APP_MIC, wxDefaultPosition,
                        wxDefaultSize, kNumMicChoices, kMicChoices);
                    py_app_mic->SetToolTip(
                        "Select which microphone to listen to when "
                        "transcribing. To get list microphones and get their "
                        "numbers, click 'List input devices'.");
                    py_app_mic_ = py_app_mic;

                    auto* py_app_lang = new wxChoice(py_app_config_panel_pairs,
                        ID_PY_APP_LANG, wxDefaultPosition, wxDefaultSize,
                        kNumLangChoices, kLangChoices);
                    py_app_lang->SetToolTip("Select which language you will "
                        "speak in. It will be transcribed into that language. "
                        "If using a language with non-ASCII characters (i.e. "
                        "not English), make sure you have 'bytes per char' "
                        "set to 2. If using something other than English, "
                        "make sure you're not using a *.en model.");
                    py_app_lang_ = py_app_lang;

                    auto* py_app_model = new wxChoice(
                        py_app_config_panel_pairs, ID_PY_APP_MODEL,
                        wxDefaultPosition, wxDefaultSize, kNumModelChoices,
                        kModelChoices);
                    py_app_model->SetToolTip("Select which version of "
                        "the transcription model to use. 'base' is a good "
                        "choice for most users. 'small' is slightly more "
                        "accurate, slower, and uses more VRAM. The *.en "
                        "models are fine-tuned English language models, and "
                        "don't work for other languages.");
                    py_app_model_ = py_app_model;

                    auto* py_app_chars_per_sync = new wxChoice(
                        py_app_config_panel_pairs, ID_PY_APP_CHARS_PER_SYNC,
                        wxDefaultPosition, wxDefaultSize, kNumCharsPerSync,
                        kCharsPerSync);
                    py_app_chars_per_sync->SetToolTip(
                        "VRChat syncs avatar parameters roughly 5 times per "
                        "second. We use this to send text to the box. By "
                        "sending more characters per sync, the box will be "
                        "faster, but you'll use more avatar parameters.");
                    py_app_chars_per_sync_ = py_app_chars_per_sync;

                    auto* py_app_bytes_per_char = new wxChoice(
                        py_app_config_panel_pairs, ID_PY_APP_BYTES_PER_CHAR,
                        wxDefaultPosition, wxDefaultSize, kNumBytesPerChar,
                        kBytesPerChar);
					py_app_bytes_per_char->SetToolTip(
						"If you speak a language that uses non-ASCII "
						"characters (i.e. not English), set this to 2.");
                    py_app_bytes_per_char_ = py_app_bytes_per_char;

                    auto* py_app_button = new wxChoice(py_app_config_panel_pairs,
                        ID_PY_APP_BUTTON, wxDefaultPosition,
                        wxDefaultSize, kNumButtons, kButton);
                    py_app_button->SetToolTip(
                        "You will use this button in game to start and stop "
                        "transcription. Set it to a button you're not using "
                        "for anything else!");
                    py_app_button_ = py_app_button;

                    auto* py_app_rows = new wxTextCtrl(py_app_config_panel_pairs,
                        ID_PY_APP_ROWS, std::to_string(app_c_->rows),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
                    py_app_rows->SetToolTip(
                        "The number of rows on the text box.");
                    py_app_rows_ = py_app_rows;

                    auto* py_app_cols = new wxTextCtrl(py_app_config_panel_pairs,
                        ID_PY_APP_COLS, std::to_string(app_c_->cols),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
                    py_app_cols->SetToolTip(
                        "The number of columns on the text box.");
                    py_app_cols_ = py_app_cols;

                    auto* py_app_window_duration = new wxTextCtrl(
                        py_app_config_panel_pairs, ID_PY_APP_WINDOW_DURATION,
                        app_c_->window_duration, wxDefaultPosition,
                        wxDefaultSize, /*style=*/0);
                    py_app_window_duration->SetToolTip(
                        "This controls how long the slice of audio that "
                        "we feed the transcription algorithm is, in seconds. "
                        "Shorter values (as low as 10 seconds) can be transcribed "
                        "more quickly, but are less accurate. Longer values "
                        "(as high as 28 seconds) take longer to transcribe, "
                        "but are far more accurate.");
                    py_app_window_duration_ = py_app_window_duration;

                    auto* sizer = new wxFlexGridSizer(/*cols=*/2);
                    py_app_config_panel_pairs->SetSizer(sizer);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Microphone:"));
                    sizer->Add(py_app_mic, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Language:"));
                    sizer->Add(py_app_lang, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Model:"));
                    sizer->Add(py_app_model, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Characters per sync:"));
                    sizer->Add(py_app_chars_per_sync, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Bytes per character:"));
                    sizer->Add(py_app_bytes_per_char, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Button:"));
                    sizer->Add(py_app_button, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Text box rows:"));
                    sizer->Add(py_app_rows, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Text box columns:"));
                    sizer->Add(py_app_cols, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Window duration (s):"));
                    sizer->Add(py_app_window_duration, /*proportion=*/0,
                        /*flags=*/wxEXPAND);
                }

                auto* py_app_enable_local_beep = new wxCheckBox(py_config_panel,
                    ID_PY_APP_ENABLE_LOCAL_BEEP, "Enable local beep");
                py_app_enable_local_beep->SetValue(app_c_->enable_local_beep);
                py_app_enable_local_beep->SetToolTip(
                    "By default, TaSTT will play a sound (audible only to "
                    "you) when it begins transcription and when it stops. "
                    "Uncheck this to disable that behavior."
                );
                py_app_enable_local_beep_ = py_app_enable_local_beep;

                auto* py_app_use_cpu = new wxCheckBox(py_config_panel,
                    ID_PY_APP_USE_CPU, "Use CPU");
                py_app_use_cpu->SetValue(app_c_->use_cpu);
                py_app_use_cpu->SetToolTip(
                    "If checked, the transcription engine will run on your "
                    "CPU instead of your GPU. This is typically much slower "
                    "and should only be used if you aren't able to use your "
                    "GPU."
                );
                py_app_use_cpu_ = py_app_use_cpu;

                auto* py_app_use_builtin = new wxCheckBox(py_config_panel,
                    ID_PY_APP_USE_BUILTIN, "Use built-in chatbox");
                py_app_use_builtin->SetValue(app_c_->use_builtin);
                py_app_use_builtin->SetToolTip(
                    "If checked, text will be sent to the built-in text box "
                    "instead of one attached to the current avatar."
                );
                py_app_use_builtin_ = py_app_use_builtin;

                // Hack: Add newlines before and after the button text to make
                // the buttons bigger, and easier to click from inside VR.
                auto* py_app_start_button = new wxButton(py_config_panel,
                    ID_PY_APP_START_BUTTON, "\nBegin transcribing\n\n");
                auto* py_app_stop_button = new wxButton(py_config_panel,
                    ID_PY_APP_STOP_BUTTON, "\nStop transcribing\n\n");

                auto* sizer = new wxBoxSizer(wxVERTICAL);
                py_config_panel->SetSizer(sizer);
                sizer->Add(py_setup_button, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_dump_mics_button, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_config_panel_pairs, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_enable_local_beep, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_use_cpu, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_use_builtin, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_start_button, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_stop_button, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
            }

            auto* sizer = new wxBoxSizer(wxHORIZONTAL);
            transcribe_panel->SetSizer(sizer);
            sizer->Add(py_config_panel, /*proportion=*/0, /*flags=*/wxEXPAND);
            sizer->Add(transcribe_out, /*proportion=*/1, /*flags=*/wxEXPAND);
        }

        auto* unity_panel = new wxPanel(main_panel, ID_UNITY_PANEL);
        unity_panel_ = unity_panel;
        {
            const auto unity_out_sz = wxSize(/*x_px=*/480, /*y_px=*/160);
            auto* unity_out = new wxTextCtrl(unity_panel, ID_UNITY_OUT,
                wxEmptyString,
                wxDefaultPosition,
                unity_out_sz, wxTE_MULTILINE | wxTE_READONLY);
            unity_out->SetMinSize(unity_out_sz);
            unity_out_ = unity_out;

            auto* unity_config_panel = new wxPanel(unity_panel,
                ID_UNITY_CONFIG_PANEL);
            {
				auto* unity_config_panel_pairs = new wxPanel(unity_config_panel,
                    ID_UNITY_CONFIG_PANEL_PAIRS);
                {
                    auto* unity_assets_file_picker = new wxDirPickerCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_ASSETS_FILE_PICKER,
                        /*path=*/app_c_->assets_path,
                        /*message=*/"Unity Assets folder"
                        );
                    unity_assets_file_picker->SetToolTip(
                        "The path to the Assets folder for your avatar's "
                        "Unity project. Example:\n"
						"C:\\Users\\yum\\unity\\kumadan\\Assets");
                    unity_assets_file_picker_ = unity_assets_file_picker;

                    auto* unity_animator_file_picker = new wxFilePickerCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_ANIMATOR_FILE_PICKER,
                        /*path=*/app_c_->fx_path,
                        /*message=*/"FX controller path",
                        /*wildcard=*/wxFileSelectorDefaultWildcardStr,
                        /*pos=*/wxDefaultPosition,
                        /*size=*/wxDefaultSize
                        );
                    unity_animator_file_picker->SetToolTip(
                        "The path to your avatar's FX layer. You can find "
                        "this in your avatar descriptor. Example:\n"
						"C:\\Users\\yum\\unity\\kumadan\\Assets\\kumadan_fx.controller");
                    unity_animator_file_picker_ = unity_animator_file_picker;

                    auto* unity_parameters_file_picker = new wxFilePickerCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_PARAMETERS_FILE_PICKER,
                        /*path=*/app_c_->params_path,
                        /*message=*/"Avatar parameters path",
                        /*wildcard=*/wxFileSelectorDefaultWildcardStr,
                        /*pos=*/wxDefaultPosition,
                        /*size=*/wxDefaultSize
                        );
                    unity_parameters_file_picker->SetToolTip(
                        "The path to your avatar's parameters. You can find "
                        "this in your avatar descriptor. Example:\n"
						"C:\\Users\\yum\\unity\\kumadan\\Assets\\kumadan_parameters.asset");
                    unity_parameters_file_picker_ =
                        unity_parameters_file_picker;

                    auto* unity_menu_file_picker = new wxFilePickerCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_MENU_FILE_PICKER,
                        /*path=*/app_c_->menu_path,
                        /*message=*/"Avatar menu path",
                        /*wildcard=*/wxFileSelectorDefaultWildcardStr,
                        /*pos=*/wxDefaultPosition,
                        /*size=*/wxDefaultSize
                        );
                    unity_menu_file_picker->SetToolTip(
                        "The path to your avatar's menu. You can find "
                        "this in your avatar descriptor. Example:\n"
						"C:\\Users\\yum\\unity\\kumadan\\Assets\\kumadan_menu.asset");
                    unity_menu_file_picker_ = unity_menu_file_picker;

					auto* unity_animator_generated_dir = new wxTextCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_ANIMATOR_GENERATED_DIR,
						wxEmptyString, wxDefaultPosition, wxDefaultSize,
                        wxTE_READONLY);
                    unity_animator_generated_dir->AppendText("TaSTT_Generated");
                    unity_animator_generated_dir->SetToolTip(
                        "TaSTT will create a bunch of files "
                        "(animations, shaders, etc.) to drive the text box. "
                        "It places them in this folder, which it creates "
                        "under your Unity project's Assets folder. Any data "
                        "inside this folder may be overwritten!");
                    unity_animator_generated_dir_ =
                        unity_animator_generated_dir;

					auto* unity_animator_generated_name = new wxTextCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_ANIMATOR_GENERATED_NAME,
						wxEmptyString, wxDefaultPosition, wxDefaultSize,
                        wxTE_READONLY);
                    unity_animator_generated_name->AppendText("TaSTT.controller");
                    unity_animator_generated_name->SetToolTip(
                        "The name of the FX layer that TaSTT generates. "
                        "It will be placed inside the generated assets "
                        "folder. Put this on your avatar descriptor when "
                        "you're done!");
                    unity_animator_generated_name_ = unity_animator_generated_name;

					auto* unity_parameters_generated_name = new wxTextCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_PARAMETERS_GENERATED_NAME,
						wxEmptyString, wxDefaultPosition, wxDefaultSize,
                        wxTE_READONLY);
                    unity_parameters_generated_name->AppendText(
                        "TaSTT_Parameters.asset");
                    unity_parameters_generated_name->SetToolTip(
                        "The name of the parameters file that TaSTT generates. "
                        "It will be placed inside the generated assets "
                        "folder. Put this on your avatar descriptor when "
                        "you're done!");
                    unity_parameters_generated_name_ =
                        unity_parameters_generated_name;

					auto* unity_menu_generated_name = new wxTextCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_MENU_GENERATED_NAME,
						wxEmptyString, wxDefaultPosition, wxDefaultSize,
                        wxTE_READONLY);
                    unity_menu_generated_name->AppendText("TaSTT_Menu.asset");
                    unity_menu_generated_name->SetToolTip(
                        "The name of the menu file that TaSTT generates. "
                        "It will be placed inside the generated assets "
                        "folder. Put this on your avatar descriptor when "
                        "you're done!");
                    unity_menu_generated_name_ = unity_menu_generated_name;

                    auto* unity_chars_per_sync = new wxChoice(
                        unity_config_panel_pairs,
                        ID_UNITY_CHARS_PER_SYNC, wxDefaultPosition,
                        wxDefaultSize, kNumCharsPerSync, kCharsPerSync);
					unity_chars_per_sync->SetToolTip(
						"VRChat syncs avatar parameters roughly 5 times per "
						"second. We use this to send text to the box. By "
						"sending more characters per sync, the box will be "
						"faster, but you'll use more avatar parameters.");
                    unity_chars_per_sync_ = unity_chars_per_sync;

                    auto* unity_bytes_per_char = new wxChoice(
                        unity_config_panel_pairs,
                        ID_UNITY_BYTES_PER_CHAR, wxDefaultPosition,
                        wxDefaultSize, kNumBytesPerChar, kBytesPerChar);
					unity_bytes_per_char->SetToolTip(
						"If you speak a language that uses non-ASCII "
						"characters (i.e. not English), set this to 2.");
                    unity_bytes_per_char_ = unity_bytes_per_char;

                    auto* unity_rows = new wxTextCtrl(unity_config_panel_pairs,
                        ID_UNITY_ROWS, std::to_string(app_c_->rows),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
                    unity_rows->SetToolTip(
                        "The number of rows on the text box.");
                    unity_rows_ = unity_rows;

                    auto* unity_cols = new wxTextCtrl(unity_config_panel_pairs,
                        ID_UNITY_COLS, std::to_string(app_c_->cols),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
                    unity_cols->SetToolTip(
                        "The number of columns on the text box.");
                    unity_cols_ = unity_cols;

                    auto* sizer = new wxFlexGridSizer(/*cols=*/2);
                    unity_config_panel_pairs->SetSizer(sizer);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"Unity Assets folder:"));
                    sizer->Add(unity_assets_file_picker);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"FX controller:"));
                    sizer->Add(unity_animator_file_picker);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"Avatar parameters:"));
                    sizer->Add(unity_parameters_file_picker);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"Avatar menu:"));
                    sizer->Add(unity_menu_file_picker);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"Generated assets folder:"));
                    sizer->Add(unity_animator_generated_dir);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"Generated FX controller:"));
                    sizer->Add(unity_animator_generated_name);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"Generated parameters:"));
                    sizer->Add(unity_parameters_generated_name);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"Generated menu:"));
                    sizer->Add(unity_menu_generated_name);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"Characters per sync:"));
                    sizer->Add(unity_chars_per_sync, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"Bytes per character:"));
                    sizer->Add(unity_bytes_per_char, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"Text box rows:"));
                    sizer->Add(unity_rows, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs,
                        wxID_ANY, /*label=*/"Text box columns:"));
                    sizer->Add(unity_cols, /*proportion=*/0,
                        /*flags=*/wxEXPAND);
                }

				auto* clear_osc = new wxCheckBox(unity_config_panel,
					ID_UNITY_CLEAR_OSC, "Clear OSC configs");
				clear_osc->SetValue(app_c_->clear_osc);
				clear_osc->SetToolTip(
					"If checked, VRChat's OSC configs will be cleared. "
					"VRC SDK has a bug where parameters added to an "
					"existing avatar are not added to the avatar's OSC "
					"config. By clearing configs, VRC SDK is forced to "
					"regenerate them. The regenerated config will include "
					"the STT parameters. Check this if you are updating "
					"an existing avatar.");
                unity_clear_osc_ = clear_osc;

				auto* unity_button_gen_fx = new wxButton(unity_config_panel,
                    ID_UNITY_BUTTON_GEN_ANIMATOR, "Generate avatar assets");
                unity_button_gen_fx->SetWindowStyleFlag(wxBU_EXACTFIT);

				auto* sizer = new wxBoxSizer(wxVERTICAL);
				unity_config_panel->SetSizer(sizer);
				sizer->Add(unity_config_panel_pairs);
                sizer->Add(clear_osc);
				sizer->Add(unity_button_gen_fx, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
            }

            auto* sizer = new wxBoxSizer(wxHORIZONTAL);
            unity_panel->SetSizer(sizer);
            sizer->Add(unity_config_panel, /*proportion=*/0,
                /*flags=*/wxEXPAND);
            sizer->Add(unity_out, /*proportion=*/1, /*flags=*/wxEXPAND);
        }
        unity_panel_->Hide();

        auto* whisper_panel = new wxPanel(main_panel, ID_WHISPER_PANEL);
        whisper_panel_ = whisper_panel;
        {
            const auto whisper_out_sz = wxSize(/*x_px=*/480, /*y_px=*/160);
            auto* whisper_out = new wxTextCtrl(whisper_panel,
                ID_WHISPER_OUT, wxEmptyString, wxDefaultPosition,
                whisper_out_sz, wxTE_MULTILINE | wxTE_READONLY);
            whisper_out->SetMinSize(whisper_out_sz);
            whisper_out_ = whisper_out;

            auto* whisper_config_panel = new wxPanel(whisper_panel,
                ID_WHISPER_CONFIG_PANEL);
            {
                auto* whisper_config_panel_pairs = new wxPanel(whisper_config_panel,
                    ID_WHISPER_CONFIG_PANEL_PAIRS);
                {
                    auto* whisper_mic = new wxChoice(whisper_config_panel_pairs,
                        ID_WHISPER_MIC, wxDefaultPosition,
                        wxDefaultSize, kNumWhisperMicChoices, kWhisperMicChoices);
                    whisper_mic->SetToolTip(
                        "Select which microphone to listen to when "
                        "transcribing. To get list microphones and get their "
                        "numbers, click 'List input devices'.");
                    whisper_mic_ = whisper_mic;

                    auto* whisper_lang = new wxChoice(whisper_config_panel_pairs,
                        ID_WHISPER_LANG, wxDefaultPosition, wxDefaultSize,
                        kNumLangChoices, kLangChoices);
                    whisper_lang->SetToolTip("Select which language you will "
                        "speak in. It will be whisperd into that language. "
                        "If using a language with non-ASCII characters (i.e. "
                        "not English), make sure you have 'bytes per char' "
                        "set to 2. If using something other than English, "
                        "make sure you're not using a *.en model.");
                    whisper_lang_ = whisper_lang;

                    auto* whisper_model = new wxChoice(
                        whisper_config_panel_pairs, ID_WHISPER_MODEL,
                        wxDefaultPosition, wxDefaultSize, kNumWhisperModelChoices,
                        kWhisperModelChoices);
                    whisper_model->SetToolTip("Select which version of "
                        "the transcription model to use. 'base' is a good "
                        "choice for most users. 'small' is slightly more "
                        "accurate, slower, and uses more VRAM. The *.en "
                        "models are fine-tuned English language models, and "
                        "don't work for other languages.");
                    whisper_model_ = whisper_model;

                    auto* whisper_chars_per_sync = new wxChoice(
                        whisper_config_panel_pairs, ID_WHISPER_CHARS_PER_SYNC,
                        wxDefaultPosition, wxDefaultSize, kNumCharsPerSync,
                        kCharsPerSync);
                    whisper_chars_per_sync->SetToolTip(
                        "VRChat syncs avatar parameters roughly 5 times per "
                        "second. We use this to send text to the box. By "
                        "sending more characters per sync, the box will be "
                        "faster, but you'll use more avatar parameters.");
                    whisper_chars_per_sync_ = whisper_chars_per_sync;

                    auto* whisper_bytes_per_char = new wxChoice(
                        whisper_config_panel_pairs, ID_WHISPER_BYTES_PER_CHAR,
                        wxDefaultPosition, wxDefaultSize, kNumBytesPerChar,
                        kBytesPerChar);
					whisper_bytes_per_char->SetToolTip(
						"If you speak a language that uses non-ASCII "
						"characters (i.e. not English), set this to 2.");
                    whisper_bytes_per_char_ = whisper_bytes_per_char;

                    auto* whisper_button = new wxChoice(whisper_config_panel_pairs,
                        ID_WHISPER_BUTTON, wxDefaultPosition,
                        wxDefaultSize, kNumButtons, kButton);
                    whisper_button->SetToolTip(
                        "You will use this button in game to start and stop "
                        "transcription. Set it to a button you're not using "
                        "for anything else!");
                    whisper_button_ = whisper_button;

                    auto* whisper_rows = new wxTextCtrl(whisper_config_panel_pairs,
                        ID_WHISPER_ROWS, std::to_string(app_c_->rows),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
                    whisper_rows->SetToolTip(
                        "The number of rows on the text box.");
                    whisper_rows_ = whisper_rows;

                    auto* whisper_cols = new wxTextCtrl(whisper_config_panel_pairs,
                        ID_WHISPER_COLS, std::to_string(app_c_->cols),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
                    whisper_cols->SetToolTip(
                        "The number of columns on the text box.");
                    whisper_cols_ = whisper_cols;

                    auto* whisper_browser_src_port = new wxTextCtrl(
                        whisper_config_panel_pairs, ID_WHISPER_BROWSER_SRC_PORT,
                        std::to_string(app_c_->browser_src_port), wxDefaultPosition,
                        wxDefaultSize, /*style=*/0);
                    whisper_browser_src_port->SetToolTip(
                        "This is the port that the browser source is hosted "
                        "on. If you aren't using TaSTT to stream, you can "
                        "ignore this option.");
                    whisper_browser_src_port_ = whisper_browser_src_port;

					auto* whisper_decode_method = new wxChoice(
                        whisper_config_panel_pairs,
						ID_WHISPER_DECODE_METHOD, wxDefaultPosition,
						wxDefaultSize, kNumDecodeMethods, kDecodeMethods);
					whisper_decode_method->SetToolTip(
						"Decoding method to use with whisper. Greedy is faster "
						"and slightly less accurate.");
					whisper_decode_method_ = whisper_decode_method;

					auto* whisper_max_ctxt = new wxTextCtrl(
						whisper_config_panel_pairs, ID_WHISPER_MAX_CTXT,
						std::to_string(app_c_->whisper_max_ctxt),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
					whisper_max_ctxt->SetToolTip("TODO");
					whisper_max_ctxt_ = whisper_max_ctxt;

					auto* whisper_beam_width = new wxTextCtrl(
						whisper_config_panel_pairs, ID_WHISPER_BEAM_WIDTH,
						std::to_string(app_c_->whisper_beam_width),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
					whisper_beam_width->SetToolTip("TODO");
					whisper_beam_width_ = whisper_beam_width;

					auto* whisper_beam_n_best = new wxTextCtrl(
						whisper_config_panel_pairs, ID_WHISPER_BEAM_N_BEST,
						std::to_string(app_c_->whisper_beam_n_best),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
					whisper_beam_n_best->SetToolTip("TODO");
					whisper_beam_n_best_ = whisper_beam_n_best;

					auto* whisper_vad_min_duration = new wxTextCtrl(
						whisper_config_panel_pairs, ID_WHISPER_VAD_MIN_DURATION,
						std::to_string(app_c_->whisper_vad_min_duration),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
					whisper_vad_min_duration->SetToolTip("TODO");
					whisper_vad_min_duration_ = whisper_vad_min_duration;

					auto* whisper_vad_max_duration = new wxTextCtrl(
						whisper_config_panel_pairs, ID_WHISPER_VAD_MAX_DURATION,
						std::to_string(app_c_->whisper_vad_max_duration),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
					whisper_vad_max_duration->SetToolTip("TODO");
					whisper_vad_max_duration_ = whisper_vad_max_duration;

					auto* whisper_vad_drop_start_silence = new wxTextCtrl(
						whisper_config_panel_pairs,
                        ID_WHISPER_VAD_DROP_START_SILENCE,
						std::to_string(app_c_->whisper_vad_drop_start_silence),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
					whisper_vad_drop_start_silence->SetToolTip("TODO");
					whisper_vad_drop_start_silence_ = whisper_vad_drop_start_silence;

					auto* whisper_vad_pause_duration = new wxTextCtrl(
						whisper_config_panel_pairs,
                        ID_WHISPER_VAD_PAUSE_DURATION,
						std::to_string(app_c_->whisper_vad_pause_duration),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
					whisper_vad_pause_duration->SetToolTip("TODO");
					whisper_vad_pause_duration_ = whisper_vad_pause_duration;

					auto* whisper_vad_retain_duration = new wxTextCtrl(
						whisper_config_panel_pairs,
                        ID_WHISPER_VAD_RETAIN_DURATION,
						std::to_string(app_c_->whisper_vad_retain_duration),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
					whisper_vad_retain_duration->SetToolTip("TODO");
					whisper_vad_retain_duration_ = whisper_vad_retain_duration;

                    auto* sizer = new wxFlexGridSizer(/*cols=*/2);
                    whisper_config_panel_pairs->SetSizer(sizer);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Microphone:"));
                    sizer->Add(whisper_mic, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Language:"));
                    sizer->Add(whisper_lang, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Model:"));
                    sizer->Add(whisper_model, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Decode method:"));
                    sizer->Add(whisper_decode_method, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Max audio contexts:"));
                    sizer->Add(whisper_max_ctxt, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Beam width:"));
                    sizer->Add(whisper_beam_width, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Beam n best:"));
                    sizer->Add(whisper_beam_n_best, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"VAD min duration:"));
                    sizer->Add(whisper_vad_min_duration, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"VAD max duration:"));
                    sizer->Add(whisper_vad_max_duration, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"VAD drop start silence:"));
                    sizer->Add(whisper_vad_drop_start_silence, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"VAD pause duration:"));
                    sizer->Add(whisper_vad_pause_duration, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"VAD retain duration:"));
                    sizer->Add(whisper_vad_retain_duration, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

#if 0
                    // Not implemented.
                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Characters per sync:"));
                    sizer->Add(whisper_chars_per_sync, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Bytes per character:"));
                    sizer->Add(whisper_bytes_per_char, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Button:"));
                    sizer->Add(whisper_button, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Text box rows:"));
                    sizer->Add(whisper_rows, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Text box columns:"));
                    sizer->Add(whisper_cols, /*proportion=*/0,
                        /*flags=*/wxEXPAND);
#else
                    whisper_chars_per_sync->Hide();
                    whisper_bytes_per_char->Hide();
                    whisper_button->Hide();
                    whisper_rows->Hide();
                    whisper_cols->Hide();
#endif

                    sizer->Add(new wxStaticText(whisper_config_panel_pairs,
                        wxID_ANY, /*label=*/"Browser source port:"));
                    sizer->Add(whisper_browser_src_port, /*proportion=*/0,
                        /*flags=*/wxEXPAND);
                }

                auto* whisper_enable_local_beep = new wxCheckBox(whisper_config_panel,
                    ID_WHISPER_ENABLE_LOCAL_BEEP, "Enable local beep");
                whisper_enable_local_beep->SetValue(app_c_->enable_local_beep);
                whisper_enable_local_beep->SetToolTip(
                    "By default, TaSTT will play a sound (audible only to "
                    "you) when it begins transcription and when it stops. "
                    "Uncheck this to disable that behavior."
                );
                whisper_enable_local_beep_ = whisper_enable_local_beep;

                auto* whisper_use_cpu = new wxCheckBox(whisper_config_panel,
                    ID_WHISPER_USE_CPU, "Use CPU");
                whisper_use_cpu->SetValue(app_c_->use_cpu);
                whisper_use_cpu->SetToolTip(
                    "If checked, the transcription engine will run on your "
                    "CPU instead of your GPU. This is typically much slower "
                    "and should only be used if you aren't able to use your "
                    "GPU."
                );
                whisper_use_cpu_ = whisper_use_cpu;

                auto* whisper_enable_builtin = new wxCheckBox(whisper_config_panel,
                    ID_WHISPER_ENABLE_BUILTIN, "Send to built-in chatbox");
                whisper_enable_builtin->SetValue(app_c_->whisper_enable_builtin);
                whisper_enable_builtin->SetToolTip(
                    "If checked, text will be sent to the built-in text box."
                );
                whisper_enable_builtin_ = whisper_enable_builtin;

                auto* whisper_enable_custom = new wxCheckBox(whisper_config_panel,
                    ID_WHISPER_ENABLE_CUSTOM, "Send to custom chatbox");
                whisper_enable_custom->SetValue(app_c_->whisper_enable_custom);
                whisper_enable_custom->SetToolTip(
                    "If checked, text will be sent to the custom text box."
                );
                whisper_enable_custom_ = whisper_enable_custom;

                auto* whisper_enable_browser_src = new wxCheckBox(whisper_config_panel,
                    ID_WHISPER_ENABLE_BROWSER_SRC, "Send to browser source");
                whisper_enable_browser_src->SetValue(app_c_->whisper_enable_browser_src);
                whisper_enable_browser_src->SetToolTip(
                    "If checked, text will be sent to a browser source. If "
                    "you're not using TaSTT to stream, you can ignore this option.");
                whisper_enable_browser_src_ = whisper_enable_browser_src;

                // Hack: Add newlines before and after the button text to make
                // the buttons bigger, and easier to click from inside VR.
                auto* whisper_start_button = new wxButton(whisper_config_panel,
                    ID_WHISPER_START_BUTTON, "\nBegin transcribing\n\n");
                auto* whisper_stop_button = new wxButton(whisper_config_panel,
                    ID_WHISPER_STOP_BUTTON, "\nStop transcribing\n\n");

                auto* sizer = new wxBoxSizer(wxVERTICAL);
                whisper_config_panel->SetSizer(sizer);
                sizer->Add(whisper_config_panel_pairs, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
#if 0
                sizer->Add(whisper_enable_local_beep, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                // Not yet implemented.
                sizer->Add(whisper_use_cpu, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(whisper_enable_builtin, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(whisper_enable_custom, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
#else
                whisper_enable_local_beep->Hide();
                whisper_use_cpu->Hide();
                whisper_enable_builtin->Hide();
                whisper_enable_custom->Hide();
#endif
                sizer->Add(whisper_enable_browser_src, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(whisper_start_button, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(whisper_stop_button, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
            }

            auto* sizer = new wxBoxSizer(wxHORIZONTAL);
            whisper_panel->SetSizer(sizer);
            sizer->Add(whisper_config_panel, /*proportion=*/0, /*flags=*/wxEXPAND);
            sizer->Add(whisper_out, /*proportion=*/1, /*flags=*/wxEXPAND);
        }
        whisper_ = std::make_unique<WhisperCPP>(whisper_out_);
        whisper_panel_->Hide();

        auto* debug_panel = new wxPanel(main_panel, ID_DEBUG_PANEL);
        debug_panel_ = debug_panel;
        {
            const auto debug_out_sz = wxSize(/*x_px=*/480, /*y_px=*/160);
            auto* debug_out = new wxTextCtrl(debug_panel, ID_DEBUG_OUT,
                wxEmptyString,
                wxDefaultPosition,
                debug_out_sz, wxTE_MULTILINE | wxTE_READONLY);
            debug_out->SetMinSize(debug_out_sz);
            debug_out_ = debug_out;

            auto* debug_config_panel = new wxPanel(debug_panel,
                ID_DEBUG_CONFIG_PANEL);
			{
				auto* debug_button_list_pip = new wxButton(debug_config_panel,
                    ID_DEBUG_BUTTON_LIST_PIP, "List pip packages");
                debug_button_list_pip->SetToolTip(
					"List the packages (and versions) installed in the "
                    "virtual environment by pip. Also list the contents "
                    "of the pip cache.");
				debug_button_list_pip->SetWindowStyleFlag(wxBU_EXACTFIT);

				auto* debug_button_clear_pip = new wxButton(debug_config_panel,
                    ID_DEBUG_BUTTON_CLEAR_PIP, "Clear pip cache");
                // The real explanation: we install a special version of torch
                // using --extra-index-url, and I'm like 99% sure that pip
                // doesn't correctly detect that we want this version instead
                // of the normal version.
                debug_button_clear_pip->SetToolTip(
					"TaSTT uses a piece of software called pip to install "
                    "Python dependencies. To enable reusing packages across "
                    "different Python projects, pip installs packages in a "
                    "system-wide cache. Sometimes the contents of this cache "
                    "can get stale (it's complicated) and clearing the cache "
                    "can fix issues.");
				debug_button_clear_pip->SetWindowStyleFlag(wxBU_EXACTFIT);

				auto* debug_button_reset_venv = new wxButton(
                    debug_config_panel, ID_DEBUG_BUTTON_RESET_VENV,
                    "Reset python virtual environment");
                debug_button_reset_venv->SetToolTip(
                    "Uninstall all Python packages installed into the virtual "
                    "environment. Do this after clearing pip!");
				debug_button_reset_venv->SetWindowStyleFlag(wxBU_EXACTFIT);

				auto* debug_button_clear_osc = new wxButton(debug_config_panel,
                    ID_DEBUG_BUTTON_CLEAR_OSC, "Clear OSC configs");
                debug_button_clear_osc->SetToolTip(
					"No idea if this actually does anything valuable yet. I "
                    "think making certain animator changes (s.a. turning on "
                    "multi-byte character encoding) require you to reset "
                    "(i.e. delete) your OSC config. This button deletes all "
                    "your OSC configs.");
				debug_button_clear_osc->SetWindowStyleFlag(wxBU_EXACTFIT);

				auto* debug_button_backup_venv = new wxButton(
                    debug_config_panel, ID_DEBUG_BUTTON_BACKUP_VENV,
                    "Back up virtual env");
                debug_button_backup_venv->SetToolTip(
                    "Back up the virtual environment to "
                    "~/Downloads/TaSTT_venv");
				debug_button_backup_venv->SetWindowStyleFlag(wxBU_EXACTFIT);

				auto* debug_button_restore_venv = new wxButton(
                    debug_config_panel, ID_DEBUG_BUTTON_RESTORE_VENV,
                    "Restore virtual env");
                debug_button_restore_venv->SetToolTip(
                    "Restore the virtual environment from "
                    "~/Downloads/TaSTT_venv");
				debug_button_restore_venv->SetWindowStyleFlag(wxBU_EXACTFIT);

				auto* sizer = new wxBoxSizer(wxVERTICAL);
				debug_config_panel->SetSizer(sizer);
				sizer->Add(debug_button_list_pip, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
				sizer->Add(debug_button_clear_pip, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
				sizer->Add(debug_button_reset_venv, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
				sizer->Add(debug_button_clear_osc, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
				sizer->Add(debug_button_backup_venv, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
				sizer->Add(debug_button_restore_venv, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
			}

            auto* sizer = new wxBoxSizer(wxHORIZONTAL);
            debug_panel->SetSizer(sizer);
            sizer->Add(debug_config_panel, /*proportion=*/0,
                /*flags=*/wxEXPAND);
            sizer->Add(debug_out, /*proportion=*/1, /*flags=*/wxEXPAND);
        }
        debug_panel_->Hide();

		auto* sizer = new wxBoxSizer(wxHORIZONTAL);
		main_panel->SetSizer(sizer);
		sizer->Add(navbar, /*proportion=*/0, /*flags=*/wxEXPAND);
		sizer->Add(transcribe_panel, /*proportion=*/1, /*flags=*/wxEXPAND);
		sizer->Add(unity_panel, /*proportion=*/1, /*flags=*/wxEXPAND);
		sizer->Add(debug_panel, /*proportion=*/1, /*flags=*/wxEXPAND);
		sizer->Add(whisper_panel, /*proportion=*/1, /*flags=*/wxEXPAND);
    }

    // Now that transcribe_out_ has been created, we can deserialize.
    app_c_ = std::make_unique<AppConfig>(transcribe_out_);
    app_c_->Deserialize(AppConfig::kConfigPath);

	Bind(wxEVT_CLOSE_WINDOW, &Frame::OnExit, this, wxID_EXIT);
	Bind(wxEVT_BUTTON, &Frame::OnNavbarTranscribe, this,
        ID_NAVBAR_BUTTON_TRANSCRIBE);
	Bind(wxEVT_BUTTON, &Frame::OnNavbarUnity, this, ID_NAVBAR_BUTTON_UNITY);
	Bind(wxEVT_BUTTON, &Frame::OnNavbarDebug, this, ID_NAVBAR_BUTTON_DEBUG);
	Bind(wxEVT_BUTTON, &Frame::OnNavbarWhisper, this, ID_NAVBAR_BUTTON_WHISPER);
	Bind(wxEVT_BUTTON, &Frame::OnAppStart, this, ID_PY_APP_START_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnAppStop, this, ID_PY_APP_STOP_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnWhisperStart, this, ID_WHISPER_START_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnWhisperStop, this, ID_WHISPER_STOP_BUTTON);
    Bind(wxEVT_TIMER,  &Frame::OnAppDrain, this, ID_PY_APP_DRAIN);
	Bind(wxEVT_BUTTON, &Frame::OnSetupPython, this, ID_PY_SETUP_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnDumpMics, this, ID_PY_DUMP_MICS_BUTTON);
	//Bind(wxEVT_BUTTON, &Frame::OnWhisperDumpMics, this, ID_WHISPER_DUMP_MICS_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnGenerateFX, this,
        ID_UNITY_BUTTON_GEN_ANIMATOR);
	Bind(wxEVT_BUTTON, &Frame::OnListPip, this, ID_DEBUG_BUTTON_LIST_PIP);
	Bind(wxEVT_BUTTON, &Frame::OnClearPip, this, ID_DEBUG_BUTTON_CLEAR_PIP);
	Bind(wxEVT_BUTTON, &Frame::OnListPip, this, ID_DEBUG_BUTTON_LIST_PIP);
	Bind(wxEVT_BUTTON, &Frame::OnResetVenv, this, ID_DEBUG_BUTTON_RESET_VENV);
	Bind(wxEVT_BUTTON, &Frame::OnClearOSC, this, ID_DEBUG_BUTTON_CLEAR_OSC);
	Bind(wxEVT_BUTTON, &Frame::OnBackupVenv, this, ID_DEBUG_BUTTON_BACKUP_VENV);
	Bind(wxEVT_BUTTON, &Frame::OnRestoreVenv, this,
        ID_DEBUG_BUTTON_RESTORE_VENV);
    Bind(wxEVT_CHOICE, &Frame::OnUnityParamChange, this,
        ID_UNITY_CHARS_PER_SYNC);
    Bind(wxEVT_CHOICE, &Frame::OnUnityParamChange, this,
        ID_UNITY_BYTES_PER_CHAR);

	// wx needs this to be able to load PNGs.
	wxImage::AddHandler(&png_handler_);
	LoadAndSetIcons();

    // Make tooltips show up for longer.
    wxToolTip::SetAutoPop(/*milliseconds=*/ 10 * 1000);

    // Initialize input fields using AppConfig.
    ApplyConfigToInputFields();
    PopulateDynamicInputFields();

    Resize();
	OnUnityParamChangeImpl();

    // Every 100 milliseconds we drain output from the Python app.
    py_app_drain_.Start(/*milliseconds=*/100);
}

void Frame::ApplyConfigToInputFields()
{
    // Transcription panel
    auto* py_app_mic = static_cast<wxChoice*>(FindWindowById(ID_PY_APP_MIC));
	int mic_idx = GetDropdownChoiceIndex(kMicChoices,
		kNumMicChoices, app_c_->microphone, kMicDefault);
	py_app_mic->SetSelection(mic_idx);

    auto* py_app_lang = static_cast<wxChoice*>(FindWindowById(ID_PY_APP_LANG));
	int lang_idx = GetDropdownChoiceIndex(kLangChoices,
		kNumLangChoices, app_c_->language, kLangDefault);
	py_app_lang->SetSelection(lang_idx);

    auto* py_app_model = static_cast<wxChoice*>(FindWindowById(ID_PY_APP_MODEL));
	int model_idx = GetDropdownChoiceIndex(kModelChoices,
		kNumModelChoices, app_c_->model, kModelDefault);
	py_app_model->SetSelection(model_idx);

    auto* py_app_button = static_cast<wxChoice*>(FindWindowById(ID_PY_APP_BUTTON));
	int button_idx = GetDropdownChoiceIndex(kButton,
		kNumButtons, app_c_->button, kButtonDefault);
	py_app_button->SetSelection(button_idx);

    auto* py_app_chars_per_sync = static_cast<wxChoice*>(FindWindowById(ID_PY_APP_CHARS_PER_SYNC));
	int chars_idx = GetDropdownChoiceIndex(kCharsPerSync,
		kNumCharsPerSync, std::to_string(app_c_->chars_per_sync),
		kCharsDefault);
	py_app_chars_per_sync->SetSelection(chars_idx);

    auto* py_app_bytes_per_char = static_cast<wxChoice*>(FindWindowById(ID_PY_APP_BYTES_PER_CHAR));
	int bytes_idx = GetDropdownChoiceIndex(kBytesPerChar,
		kNumBytesPerChar, std::to_string(app_c_->bytes_per_char),
		kBytesDefault);
	py_app_bytes_per_char->SetSelection(bytes_idx);

    auto* py_app_rows = static_cast<wxTextCtrl*>(FindWindowById(ID_PY_APP_ROWS));
    py_app_rows->Clear();
    py_app_rows->AppendText(std::to_string(app_c_->rows));

    auto* py_app_cols = static_cast<wxTextCtrl*>(FindWindowById(ID_PY_APP_COLS));
    py_app_cols->Clear();
    py_app_cols->AppendText(std::to_string(app_c_->cols));

    // Whisper panel
    auto* whisper_mic = static_cast<wxChoice*>(FindWindowById(ID_WHISPER_MIC));
    int whisper_mic_idx = app_c_->whisper_mic;
	whisper_mic->SetSelection(whisper_mic_idx);

    auto* whisper_lang = static_cast<wxChoice*>(FindWindowById(ID_WHISPER_LANG));
	whisper_lang->SetSelection(lang_idx);

    auto* whisper_model = static_cast<wxChoice*>(FindWindowById(ID_WHISPER_MODEL));
	int whisper_model_idx = GetDropdownChoiceIndex(kWhisperModelChoices,
		kNumWhisperModelChoices, app_c_->whisper_model, kWhisperModelDefault);
	whisper_model->SetSelection(whisper_model_idx);

    auto* whisper_button = static_cast<wxChoice*>(FindWindowById(ID_WHISPER_BUTTON));
	whisper_button->SetSelection(button_idx);

#if 0
    auto* whisper_chars_per_sync = static_cast<wxChoice*>(FindWindowById(ID_WHISPER_CHARS_PER_SYNC));
	whisper_chars_per_sync->SetSelection(chars_idx);

    auto* whisper_bytes_per_char = static_cast<wxChoice*>(FindWindowById(ID_WHISPER_BYTES_PER_CHAR));
	whisper_bytes_per_char->SetSelection(bytes_idx);

    auto* whisper_rows = static_cast<wxTextCtrl*>(FindWindowById(ID_WHISPER_ROWS));
    whisper_rows->Clear();
    whisper_rows->AppendText(std::to_string(app_c_->rows));

    auto* whisper_cols = static_cast<wxTextCtrl*>(FindWindowById(ID_WHISPER_COLS));
    whisper_cols->Clear();
    whisper_cols->AppendText(std::to_string(app_c_->cols));
#endif

    auto* whisper_browser_src_port = static_cast<wxTextCtrl*>(FindWindowById(ID_WHISPER_BROWSER_SRC_PORT));
    whisper_browser_src_port->Clear();
    whisper_browser_src_port->AppendText(std::to_string(app_c_->browser_src_port));

	auto* whisper_enable_local_beep = static_cast<wxCheckBox*>(FindWindowById(ID_WHISPER_ENABLE_LOCAL_BEEP));
    whisper_enable_local_beep->SetValue(app_c_->enable_local_beep);

	auto* whisper_use_cpu = static_cast<wxCheckBox*>(FindWindowById(ID_WHISPER_USE_CPU));
    whisper_use_cpu->SetValue(app_c_->use_cpu);

    auto* whisper_enable_builtin = static_cast<wxCheckBox*>(FindWindowById(ID_WHISPER_ENABLE_BUILTIN));
    whisper_enable_builtin->SetValue(app_c_->whisper_enable_builtin);

    auto* whisper_enable_custom = static_cast<wxCheckBox*>(FindWindowById(ID_WHISPER_ENABLE_CUSTOM));
    whisper_enable_custom->SetValue(app_c_->whisper_enable_custom);

    auto* whisper_enable_browser_src = static_cast<wxCheckBox*>(FindWindowById(ID_WHISPER_ENABLE_BROWSER_SRC));
    whisper_enable_browser_src->SetValue(app_c_->whisper_enable_browser_src);

    auto* whisper_decode_method = static_cast<wxChoice*>(FindWindowById(ID_WHISPER_DECODE_METHOD));
    int whisper_decode_method_idx = GetDropdownChoiceIndex(kDecodeMethods,
        kNumDecodeMethods, app_c_->whisper_decode_method, kDecodeMethodDefault);
    whisper_decode_method->SetSelection(whisper_decode_method_idx);

    auto* whisper_max_ctxt = static_cast<wxTextCtrl*>(FindWindowById(ID_WHISPER_MAX_CTXT));
    whisper_max_ctxt->SetValue(std::to_string(app_c_->whisper_max_ctxt));

    auto* whisper_beam_width = static_cast<wxTextCtrl*>(FindWindowById(ID_WHISPER_BEAM_WIDTH));
    whisper_beam_width->SetValue(std::to_string(app_c_->whisper_beam_width));

    auto* whisper_beam_n_best = static_cast<wxTextCtrl*>(FindWindowById(ID_WHISPER_BEAM_N_BEST));
    whisper_beam_n_best->SetValue(std::to_string(app_c_->whisper_beam_n_best));

    auto* whisper_vad_min_duration = static_cast<wxTextCtrl*>(FindWindowById(ID_WHISPER_VAD_MIN_DURATION));
    whisper_vad_min_duration->SetValue(std::to_string(app_c_->whisper_vad_min_duration));

    auto* whisper_vad_max_duration = static_cast<wxTextCtrl*>(FindWindowById(ID_WHISPER_VAD_MAX_DURATION));
    whisper_vad_max_duration->SetValue(std::to_string(app_c_->whisper_vad_max_duration));

    auto* whisper_vad_drop_start_silence = static_cast<wxTextCtrl*>(FindWindowById(ID_WHISPER_VAD_DROP_START_SILENCE));
    whisper_vad_drop_start_silence->SetValue(std::to_string(app_c_->whisper_vad_drop_start_silence));

    auto* whisper_vad_pause_duration = static_cast<wxTextCtrl*>(FindWindowById(ID_WHISPER_VAD_PAUSE_DURATION));
    whisper_vad_pause_duration->SetValue(std::to_string(app_c_->whisper_vad_pause_duration));

    auto* whisper_vad_retain_duration = static_cast<wxTextCtrl*>(FindWindowById(ID_WHISPER_VAD_RETAIN_DURATION));
    whisper_vad_retain_duration->SetValue(std::to_string(app_c_->whisper_vad_retain_duration));

    // Unity panel
    auto* unity_chars_per_sync = static_cast<wxChoice*>(FindWindowById(ID_UNITY_CHARS_PER_SYNC));
	unity_chars_per_sync->SetSelection(chars_idx);

    auto* unity_bytes_per_char = static_cast<wxChoice*>(FindWindowById(ID_UNITY_BYTES_PER_CHAR));
	unity_bytes_per_char->SetSelection(bytes_idx);

    auto* unity_rows = static_cast<wxTextCtrl*>(FindWindowById(ID_UNITY_ROWS));
    unity_rows->Clear();
    unity_rows->AppendText(std::to_string(app_c_->rows));

    auto* unity_cols = static_cast<wxTextCtrl*>(FindWindowById(ID_UNITY_COLS));
    unity_cols->Clear();
    unity_cols->AppendText(std::to_string(app_c_->cols));
}

void Frame::PopulateDynamicInputFields()
{
	Whisper::iMediaFoundation* f = nullptr;
	if (!whisper_->GetMediaFoundation(f)) {
		return;
	}
    ScopeGuard f_cleanup([f]() { f->Release(); });

	std::vector<std::string> mics;
	if (whisper_->GetMics(f, mics)) {
		std::vector<wxString> contents(mics.size());
		auto* whisper_mic = static_cast<wxChoice*>(FindWindowById(ID_WHISPER_MIC));
		for (int i = 0; i < std::min(mics.size(), kNumWhisperMicChoices); i++) {
			contents[i] = mics[i];
		}
		int mic_idx = whisper_mic->GetSelection();
		whisper_mic->Set(contents);
		if (mic_idx < contents.size()) {
			whisper_mic->SetSelection(mic_idx);
		}
	}
}

void Frame::OnExit(wxCloseEvent& event)
{
    OnAppStop();
    OnWhisperStop();
}

void Frame::OnNavbarTranscribe(wxCommandEvent& event)
{
    transcribe_panel_->Hide();
    unity_panel_->Hide();
    debug_panel_->Hide();
    whisper_panel_->Hide();

    // Initialize input fields using AppConfig.
    ApplyConfigToInputFields();
    PopulateDynamicInputFields();

    transcribe_panel_->Show();
    Resize();
}

void Frame::OnNavbarUnity(wxCommandEvent& event)
{
    transcribe_panel_->Hide();
    unity_panel_->Hide();
    debug_panel_->Hide();
    whisper_panel_->Hide();

    // Initialize input fields using AppConfig.
    ApplyConfigToInputFields();
    PopulateDynamicInputFields();

    unity_panel_->Show();
    Resize();
}

void Frame::OnNavbarDebug(wxCommandEvent& event)
{
    transcribe_panel_->Hide();
    unity_panel_->Hide();
    debug_panel_->Hide();
    whisper_panel_->Hide();

    // Initialize input fields using AppConfig.
    ApplyConfigToInputFields();
    PopulateDynamicInputFields();

    debug_panel_->Show();
    Resize();
}

void Frame::OnNavbarWhisper(wxCommandEvent& event)
{
    transcribe_panel_->Hide();
    unity_panel_->Hide();
    debug_panel_->Hide();
    whisper_panel_->Hide();

    // Initialize input fields using AppConfig.
    ApplyConfigToInputFields();
    PopulateDynamicInputFields();

    whisper_panel_->Show();
    Resize();
}

void Frame::OnSetupPython(wxCommandEvent& event)
{
    auto status = env_proc_.wait_for(std::chrono::seconds(0));
    if (status != std::future_status::ready) {
		Log(transcribe_out_, "Virtual environment setup already running\n");
		return;
	}

    env_proc_ = std::move(std::async(std::launch::async, [&]() {
        Log(transcribe_out_, "Setting up Python virtual environment\n");
		Log(transcribe_out_, "This could take several minutes, please be "
			"patient!\n");
		Log(transcribe_out_, "This will download ~5GB of dependencies.\n");

		{
			Log(transcribe_out_, "  Installing pip\n");
			auto out_cb = [&](const std::string& out, const std::string& err) {
				Log(transcribe_out_, "{}", out);
				Log(transcribe_out_, "{}", err);
			};
			if (!PythonWrapper::InstallPip(std::move(out_cb))) {
                Log(transcribe_out_, "Failed to install pip!\n");
                return false;
			}
		}

		{
			Log(transcribe_out_, "  DEBUG: check sys.path\n");
			auto out_cb = [&](const std::string& out, const std::string& err) {
				Log(transcribe_out_, "{}", out);
				Log(transcribe_out_, "{}", err);
			};
			if (!PythonWrapper::InvokeWithArgs({
				"Resources/Scripts/tst.py",
				}, std::move(out_cb))) {
				Log(transcribe_out_, "Failed to check sys.path!\n");
				return false;
			}
		}

		Log(transcribe_out_, "  Installing dependencies\n");
		auto out_cb = [&](const std::string& out, const std::string& err) {
			Log(transcribe_out_, "{}", out);
			Log(transcribe_out_, "{}", err);
		};
		if (!PythonWrapper::InvokeWithArgs({
			"-u",  // Unbuffered output
			"-m pip",
			"install",
			"-r Resources/Scripts/requirements.txt",
			}, std::move(out_cb))) {
			Log(transcribe_out_, "Failed to launch environment setup thread!\n");
			return false;
		}
        Log(transcribe_out_, "Successfully set up virtual environment!\n");
		return true;
	}));
}

void Frame::OnDumpMics(wxCommandEvent& event)
{
    auto status = dump_mics_.wait_for(std::chrono::seconds(0));
    if (status != std::future_status::ready) {
		Log(transcribe_out_, "Mic dump already running\n");
		return;
	}
    dump_mics_ = std::move(std::async(std::launch::async, [&]() {
        Log(transcribe_out_, "Getting mics...\n");
        Log(transcribe_out_, "{}\n", PythonWrapper::DumpMics());
		return true;
	}));
}

bool GetUserPath(wxTextCtrl* out,
    const std::string& raw, std::filesystem::path& clean,
    const std::string& err_prefix = "", bool must_exist = true) {
    clean = raw;
    if (must_exist && !std::filesystem::exists(clean)) {
        std::ostringstream oss;
        oss << err_prefix << ": User-provided path does not exist at "
            << clean << std::endl;
        Log(out, oss.str().c_str());
        return false;
    }
    return true;
}

void Frame::OnGenerateFX(wxCommandEvent& event)
{
    auto status = unity_app_.wait_for(std::chrono::seconds(0));
    if (status != std::future_status::ready) {
		Log(unity_out_, "Unity process already running\n");
		return;
	}

	unity_app_ = std::move(std::async(std::launch::async, [&]() {
		Log(unity_out_, "Generating animator\n");

		std::filesystem::path unity_assets_path;
		if (!GetUserPath(unity_out_,
            unity_assets_file_picker_->GetPath().ToStdString(),
			unity_assets_path,
			"Cannot generate FX layer: Failed to validate assets directory")) {
			return false;
		}
		std::filesystem::path unity_animator_path;
		if (!GetUserPath(unity_out_,
            unity_animator_file_picker_->GetPath().ToStdString(),
			unity_animator_path,
			"Cannot generate FX layer: Failed to validate animator directory")) {
			return false;
		}
		std::filesystem::path unity_parameters_path;
		if (!GetUserPath(unity_out_,
            unity_parameters_file_picker_->GetPath().ToStdString(),
			unity_parameters_path,
			"Cannot generate FX layer: Failed to validate parameters directory")) {
			return false;
		}
		std::filesystem::path unity_menu_path;
		if (!GetUserPath(unity_out_, unity_menu_file_picker_->GetPath().ToStdString(),
			unity_menu_path,
			"Cannot generate FX layer: Failed to validate menu directory")) {
			return false;
		}

		std::string unity_animator_generated_dir =
			unity_animator_generated_dir_->GetLineText(0).ToStdString();
		std::string unity_animator_generated_name =
			unity_animator_generated_name_->GetLineText(0).ToStdString();
		std::string unity_parameters_generated_name =
			unity_parameters_generated_name_->GetLineText(0).ToStdString();
		std::string unity_menu_generated_name =
			unity_menu_generated_name_->GetLineText(0).ToStdString();

		int chars_per_sync_idx = unity_chars_per_sync_->GetSelection();
		if (chars_per_sync_idx == wxNOT_FOUND) {
			chars_per_sync_idx = kCharsDefault;
		}
		std::string chars_per_sync_str =
			kCharsPerSync[chars_per_sync_idx].ToStdString();
		int bytes_per_char_idx = unity_bytes_per_char_->GetSelection();
		if (bytes_per_char_idx == wxNOT_FOUND) {
			bytes_per_char_idx = kBytesDefault;
		}
		std::string bytes_per_char_str =
			kBytesPerChar[bytes_per_char_idx].ToStdString();

		std::string rows_str = unity_rows_->GetValue().ToStdString();
		std::string cols_str = unity_cols_->GetValue().ToStdString();
		int rows, cols, bytes_per_char, chars_per_sync;
		try {
			rows = std::stoi(rows_str);
			cols = std::stoi(cols_str);
			bytes_per_char = std::stoi(bytes_per_char_str);
			chars_per_sync = std::stoi(chars_per_sync_str);
		}
		catch (const std::invalid_argument&) {
			Log(unity_out_, "Could not parse rows \"{}\", cols \"{}\", bytes per "
				"char \"{}\", or chars per sync \"{}\" as an integer\n",
				rows_str, cols_str, bytes_per_char_str, chars_per_sync_str);
			return false;
		}
		catch (const std::out_of_range&) {
			Log(unity_out_, "Rows \"{}\" or cols \"{}\" are out of range\n",
				rows_str, cols_str);
			return false;
		}

		app_c_->assets_path = unity_assets_path.string();
		app_c_->fx_path = unity_animator_path.string();
		app_c_->params_path = unity_parameters_path.string();
		app_c_->menu_path = unity_menu_path.string();
		app_c_->bytes_per_char = bytes_per_char;
		app_c_->chars_per_sync = chars_per_sync;
		app_c_->rows = rows;
		app_c_->cols = cols;
		app_c_->clear_osc = unity_clear_osc_->GetValue();
		app_c_->Serialize(AppConfig::kConfigPath);

		std::string out;
		if (!PythonWrapper::GenerateAnimator(
			*app_c_,
			unity_animator_generated_dir,
			unity_animator_generated_name,
			unity_parameters_generated_name,
			unity_menu_generated_name,
			unity_out_)) {
			Log(unity_out_, "Failed to generate animator:\n%s\n", out.c_str());
		}
		return true;
	}));
}

void Frame::OnListPip(wxCommandEvent& event)
{
    Log(debug_out_, "Listing pip packages... ");
    PythonWrapper::InvokeWithArgs({
        "-m pip",
        "list",
        }, "Failed to list pip packages", debug_out_);

    Log(debug_out_, "Listing pip cache... ");
    PythonWrapper::InvokeWithArgs({
        "-m pip",
        "cache",
        "list",
        }, "Failed to list pip cache", debug_out_);
}

void Frame::OnClearPip(wxCommandEvent& event)
{
    Log(debug_out_, "Clearing pip cache... ");
    PythonWrapper::InvokeWithArgs({
        "-m pip",
        "cache",
        "purge",
        }, "Failed to clear pip cache", debug_out_);
}

void Frame::OnResetVenv(wxCommandEvent& event)
{
	Log(debug_out_, "Resetting virtual environment... ");

	const std::string py_dir = "Resources/Python/Lib/site-packages";

    if (!std::filesystem::is_directory(py_dir)) {
		Log(debug_out_, "Python package directory not exist at {}, assuming "
            "already deleted!\n", py_dir);
        return;
    }

	std::error_code err;
	if (std::filesystem::remove_all(py_dir, err)) {
		Log(debug_out_, "success!\n");
	}
	else {
		wxLogError("Failed to reset virtual environment: %s", err.message());
		Log(debug_out_, "failed!\n");
	}
}

void Frame::OnClearOSC(wxCommandEvent& event)
{
    std::filesystem::path osc_path = "C:/Users";
    osc_path /= wxGetUserName().ToStdString();
    osc_path /= "AppData/LocalLow/VRChat/vrchat/OSC";
    osc_path = osc_path.lexically_normal();
    Log(debug_out_, "OSC configs are stored at {}\n", osc_path.string());

    if (!std::filesystem::is_directory(osc_path)) {
		Log(debug_out_, "OSC configs do not exist at {}, assuming already "
            "deleted!\n", osc_path.string());
        return;
    }

    Log(debug_out_, "Deleting OSC configs... ");
	std::error_code err;
	if (std::filesystem::remove_all(osc_path, err)) {
		Log(debug_out_, "success!\n");
	}
	else {
		wxLogError("Failed to delete OSC configs: %s", err.message());
		Log(debug_out_, "failed!\n");
	}
}

void Frame::OnBackupVenv(wxCommandEvent& event)
{
    std::filesystem::path venv_path = "C:/Users";
    venv_path /= wxGetUserName().ToStdString();
    venv_path /= "Downloads/TaSTT_venv";
    venv_path = venv_path.lexically_normal();
    Log(debug_out_, "Backing up virtual environment to {}\n",
        venv_path.string());

    if (std::filesystem::is_directory(venv_path)) {
        Log(debug_out_, "Old backup found, removing... ");
        std::error_code err;
        if (!std::filesystem::remove_all(venv_path, err)) {
            wxLogError("Failed to remove old virtual environment backup: %s",
                err.message());
            Log(debug_out_, "failed!\n");
            return;
        }
		Log(debug_out_, "success!\n");
    }

	Log(debug_out_, "Copying venv... ");
	auto opts = std::filesystem::copy_options();
	opts |= std::filesystem::copy_options::overwrite_existing;
	opts |= std::filesystem::copy_options::recursive;
	std::error_code error;
	std::filesystem::copy("Resources/Python", venv_path, opts, error);
	if (error.value()) {
		wxLogError("Failed to back up virtual environment: %s (%d)",
            error.message(), error.value());
		Log(debug_out_, "failed!\n");
        return;
	}
	Log(debug_out_, "success!\n");
}

void Frame::OnRestoreVenv(wxCommandEvent& event)
{
    std::filesystem::path venv_path = "C:/Users";
    venv_path /= wxGetUserName().ToStdString();
    venv_path /= "Downloads/TaSTT_venv";
    venv_path = venv_path.lexically_normal();
    Log(debug_out_, "Restoring virtual environment from {}\n",
        venv_path.string());

    if (!std::filesystem::is_directory(venv_path)) {
        wxLogError("Virtual environment backup does not exist at %s",
            venv_path.string());
        Log(debug_out_, "Failed!\n");
    }

    if (std::filesystem::is_directory("Resources/Python")) {
        Log(debug_out_, "Removing active virtual environment... ");
        std::error_code err;
        if (!std::filesystem::remove_all("Resources/Python", err)) {
            wxLogError("Failed to remove active virtual environment: %s",
                err.message());
            Log(debug_out_, "failed!\n");
            return;
        }
		Log(debug_out_, "success!\n");
    }

	Log(debug_out_, "Copying venv... ");
	auto opts = std::filesystem::copy_options();
	opts |= std::filesystem::copy_options::overwrite_existing;
	opts |= std::filesystem::copy_options::recursive;
	std::error_code error;
	std::filesystem::copy(venv_path, "Resources/Python", opts, error);
	if (error.value()) {
		wxLogError("Failed to copy venv: %s (%d)", error.message(),
            error.value());
		Log(debug_out_, "failed!\n");
        return;
	}
	Log(debug_out_, "success!\n");

	Log(debug_out_, "Setting up virtual env to ensure consistency. Most "
		"packages should not be re-acquired. Output is printed to the "
        "transcription panel.\n");
    OnSetupPython(event);
}

void Frame::OnUnityParamChangeImpl() {
    int chars_per_sync_idx = unity_chars_per_sync_->GetSelection();
    if (chars_per_sync_idx == wxNOT_FOUND) {
        chars_per_sync_idx = kCharsDefault;
    }
    std::string chars_per_sync_str = kCharsPerSync[chars_per_sync_idx].ToStdString();
    int chars_per_sync = std::stoi(chars_per_sync_str);
    int bytes_per_char_idx = unity_bytes_per_char_->GetSelection();
    if (bytes_per_char_idx == wxNOT_FOUND) {
        bytes_per_char_idx = kBytesDefault;
    }
    std::string bytes_per_char_str = kBytesPerChar[bytes_per_char_idx].ToStdString();
    int bytes_per_char = std::stoi(bytes_per_char_str);

    // Used to select which region is being updated.
    int select_bits = 8;
    // Used to update the active region.
    int layer_bits = (chars_per_sync * bytes_per_char) * 8;
    // Used to control the size of the board.
    int scale_bits = 8;
    // These are all the misc bits we use:
    //   1. dummy (we should get rid of this one)
    //   2. show
    //   3. disable
    //   4. lock
    //   5. clear
    //   6. audio indicator enable
    //   7. audio indicator toggle
    //   8. visual indicator 1
    //   9. visual indicator 2
    int misc_bits = 9;
    int total_bits = select_bits + layer_bits + scale_bits + misc_bits;
    Log(unity_out_, "This configuration will use {} bits of avatar parameter space:\n", total_bits);
    Log(unity_out_, "  {} bits coming from ({} characters per sync) * ({} bytes per character)\n", layer_bits, chars_per_sync, bytes_per_char);
    Log(unity_out_, "  {} bits coming from fixed overheads\n", select_bits + scale_bits + misc_bits);
}

void Frame::OnUnityParamChange(wxCommandEvent& event) {
	OnUnityParamChangeImpl();
}

void Frame::OnAppStart(wxCommandEvent& event) {
    auto status = py_app_.wait_for(std::chrono::seconds(0));
    if (status != std::future_status::ready) {
		Log(transcribe_out_, "Transcription engine already running\n");
		return;
	}

	Log(transcribe_out_, "Launching transcription engine\n");

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
    int chars_per_sync_idx = py_app_chars_per_sync_->GetSelection();
    if (chars_per_sync_idx == wxNOT_FOUND) {
        chars_per_sync_idx = kCharsDefault;
    }
    int bytes_per_char_idx = py_app_bytes_per_char_->GetSelection();
    if (bytes_per_char_idx == wxNOT_FOUND) {
        bytes_per_char_idx = kBytesDefault;
    }
    int button_idx = py_app_button_->GetSelection();
    if (button_idx == wxNOT_FOUND) {
        button_idx = kBytesDefault;
    }
    const bool enable_local_beep = py_app_enable_local_beep_->GetValue();
    const bool use_cpu = py_app_use_cpu_->GetValue();
    const bool use_builtin = py_app_use_builtin_->GetValue();
    std::string rows_str = py_app_rows_->GetValue().ToStdString();
    std::string cols_str = py_app_cols_->GetValue().ToStdString();
    std::string chars_per_sync_str =
        kCharsPerSync[chars_per_sync_idx].ToStdString();
    std::string bytes_per_char_str =
        kBytesPerChar[bytes_per_char_idx].ToStdString();
    std::string window_duration_str =
        py_app_window_duration_->GetValue().ToStdString();
    int rows, cols, chars_per_sync, bytes_per_char, window_duration;
    try {
        rows = std::stoi(rows_str);
        cols = std::stoi(cols_str);
        chars_per_sync = std::stoi(chars_per_sync_str);
        bytes_per_char = std::stoi(bytes_per_char_str);
        window_duration = std::stoi(window_duration_str);
    }
    catch (const std::invalid_argument&) {
		Log(transcribe_out_, "Could not parse rows \"{}\", cols \"{}\", chars "
            "per sync \"{}\", bytes per char \"{}\" or window duration \"{}\" "
            "as an integer\n", rows_str, cols_str, chars_per_sync_str,
            bytes_per_char_str, window_duration_str);
        return;
    }
    catch (const std::out_of_range&) {
		Log(transcribe_out_, "Rows \"{}\", cols \"{}\", chars per sync "
            "\"{}\", bytes per char \"{}\" or window duration \"{}\" are out "
            "of range\n", rows_str, cols_str, chars_per_sync_str,
            bytes_per_char_str, window_duration_str);
        return;
    }
    const int max_rows = 10;
    const int max_cols = 240;
    const int min_window_duration_s = 10;
    const int max_window_duration_s = 28;
    if (rows < 0 || rows > max_rows ||
        cols < 0 || cols > max_cols ||
        window_duration < min_window_duration_s ||
        window_duration > max_window_duration_s) {
        Log(transcribe_out_, "Rows not on [{},{}] or cols not on [{},{}] or "
            "window_duration not on [{},{}]\n",
            0, max_rows,
            0, max_cols,
            min_window_duration_s, max_window_duration_s);
        return;
    }

    app_c_->microphone = kMicChoices[which_mic].ToStdString();
    app_c_->language = kLangChoices[which_lang].ToStdString();
    app_c_->model = kModelChoices[which_model].ToStdString();
    app_c_->chars_per_sync = chars_per_sync;
    app_c_->bytes_per_char = bytes_per_char;
    app_c_->button = kButton[button_idx].ToStdString();
    app_c_->rows = rows;
    app_c_->cols = cols;
    app_c_->window_duration = std::to_string(window_duration);
    app_c_->enable_local_beep = enable_local_beep;
    app_c_->use_cpu = use_cpu;
    app_c_->use_builtin = use_builtin;
    app_c_->Serialize(AppConfig::kConfigPath);

    auto out_cb = [&](const std::string& out, const std::string& err) {
        Log(transcribe_out_, "{}", out);
        Log(transcribe_out_, "{}", err);
    };
    auto in_cb = [&](std::string& in) {};
    auto run_cb = [&]() {
        return run_py_app_;
    };
    run_py_app_ = true;
    py_app_ = std::move(PythonWrapper::StartApp(*app_c_, std::move(out_cb), std::move(in_cb), std::move(run_cb)));
    Log(transcribe_out_, "py app valid: {}\n", py_app_.valid());
}

void Frame::OnAppStop() {
    auto status = py_app_.wait_for(std::chrono::seconds(0));
    if (status == std::future_status::ready) {
		Log(transcribe_out_, "Transcription engine already stopped\n");
        return;
    }
    run_py_app_ = false;
    py_app_.wait();
	Log(transcribe_out_, "Stopped transcription engine\n");
}

void Frame::OnAppStop(wxCommandEvent& event) {
    OnAppStop();
}

void Frame::OnWhisperStart(wxCommandEvent& event) {
	Log(whisper_out_, "Launching transcription engine\n");

    int which_mic = whisper_mic_->GetSelection();
    if (which_mic == wxNOT_FOUND) {
        which_mic = kMicDefault;
    }
    int which_lang = whisper_lang_->GetSelection();
    if (which_lang == wxNOT_FOUND) {
        which_lang = kLangDefault;
    }
    int which_model = whisper_model_->GetSelection();
    if (which_model == wxNOT_FOUND) {
        which_model = kWhisperModelDefault;
    }
    int chars_per_sync_idx = whisper_chars_per_sync_->GetSelection();
    if (chars_per_sync_idx == wxNOT_FOUND) {
        chars_per_sync_idx = kCharsDefault;
    }
    int bytes_per_char_idx = whisper_bytes_per_char_->GetSelection();
    if (bytes_per_char_idx == wxNOT_FOUND) {
        bytes_per_char_idx = kBytesDefault;
    }
    int button_idx = whisper_button_->GetSelection();
    if (button_idx == wxNOT_FOUND) {
        button_idx = kBytesDefault;
    }
    int decode_method_idx = whisper_decode_method_->GetSelection();
    if (decode_method_idx == wxNOT_FOUND) {
        decode_method_idx = kDecodeMethodDefault;
    }
    const bool enable_local_beep = whisper_enable_local_beep_->GetValue();
    const bool use_cpu = whisper_use_cpu_->GetValue();
    std::string rows_str = whisper_rows_->GetValue().ToStdString();
    std::string cols_str = whisper_cols_->GetValue().ToStdString();
    std::string chars_per_sync_str =
        kCharsPerSync[chars_per_sync_idx].ToStdString();
    std::string bytes_per_char_str =
        kBytesPerChar[bytes_per_char_idx].ToStdString();
    std::string browser_src_port_str =
        whisper_browser_src_port_->GetValue().ToStdString();
    int rows, cols, chars_per_sync, bytes_per_char, browser_src_port;
    try {
        rows = std::stoi(rows_str);
        cols = std::stoi(cols_str);
        chars_per_sync = std::stoi(chars_per_sync_str);
        bytes_per_char = std::stoi(bytes_per_char_str);
        browser_src_port = std::stoi(browser_src_port_str);
    }
    catch (const std::invalid_argument&) {
		Log(whisper_out_, "Could not parse rows \"{}\", cols \"{}\", chars "
            "per sync \"{}\", or bytes per char \"{}\" "
            "as an integer\n", rows_str, cols_str, chars_per_sync_str,
            bytes_per_char_str);
        return;
    }
    catch (const std::out_of_range&) {
		Log(whisper_out_, "Rows \"{}\", cols \"{}\", chars per sync "
            "\"{}\", or bytes per char \"{}\" are out "
            "of range\n", rows_str, cols_str, chars_per_sync_str,
            bytes_per_char_str);
        return;
    }
    const int max_rows = 10;
    const int max_cols = 240;
    if (rows < 0 || rows > max_rows ||
        cols < 0 || cols > max_cols) {
        Log(whisper_out_, "Rows not on [{},{}] or cols not on [{},{}]\n",
            0, max_rows,
            0, max_cols);
        return;
    }

    std::string max_ctxt_str = whisper_max_ctxt_->GetValue().ToStdString();
    std::string beam_sz_str = whisper_beam_width_->GetValue().ToStdString();
    std::string beam_wd_str = whisper_beam_n_best_->GetValue().ToStdString();
    int max_ctxt, beam_sz, beam_wd;
    Log(whisper_out_, "here {}\n", __LINE__);
    try {
        Log(whisper_out_, "whisper max ctxt str: {}\n", max_ctxt_str);
        max_ctxt = std::stoi(max_ctxt_str);
        Log(whisper_out_, "whisper max ctxt: {}\n", max_ctxt);
        beam_sz = std::stoi(beam_sz_str);
        beam_wd = std::stoi(beam_wd_str);
    }
    catch (const std::invalid_argument&) {
        Log(whisper_out_, "Could not parse max_ctxt '{}' beam_sz '{}' or beam_wd '{}' as an integer",
            max_ctxt_str, beam_sz_str, beam_wd_str);
        return;
    }
    catch (const std::out_of_range&) {
        Log(whisper_out_, "Could not parse max_ctxt '{}', beam_sz '{}' or beam_wd '{}' as an integer: out of range",
            max_ctxt_str, beam_sz_str, beam_wd_str);
        return;
    }

    std::string vad_min_dur_str = whisper_vad_min_duration_->GetValue().ToStdString();
    std::string vad_max_dur_str = whisper_vad_max_duration_->GetValue().ToStdString();
    std::string vad_drop_si_dur_str = whisper_vad_drop_start_silence_->GetValue().ToStdString();
    std::string vad_pause_dur_str = whisper_vad_pause_duration_->GetValue().ToStdString();
    std::string vad_ret_dur_str = whisper_vad_retain_duration_->GetValue().ToStdString();
    float vad_min_dur, vad_max_dur, vad_drop_silence_dur, vad_pause_dur, vad_retain_dur;
    try {
        vad_min_dur = std::stof(vad_min_dur_str);
        vad_max_dur = std::stof(vad_max_dur_str);
        vad_drop_silence_dur = std::stof(vad_drop_si_dur_str);
        vad_pause_dur = std::stof(vad_pause_dur_str);
        vad_retain_dur = std::stof(vad_ret_dur_str);
    }
    catch (const std::invalid_argument&) {
        // TODO update error msg
        Log(whisper_out_, "Could not parse beam_sz '{}' or beam_wd '{}' as an integer",
            beam_sz, beam_wd);
        return;
    }
    catch (const std::out_of_range&) {
        // TODO update error msg
        Log(whisper_out_, "Could not parse beam_sz '{}' or beam_wd '{}' as an integer: out of range",
            beam_sz, beam_wd);
        return;
    }

    const int min_port = 1024;
    const int max_port = 65535;
    if (browser_src_port < min_port || browser_src_port > max_port) {
        Log(whisper_out_, "Browser source port not on [{},{}]\n",
            min_port, max_port);
        return;
    }

    app_c_->whisper_mic = which_mic;
    app_c_->language = kLangChoices[which_lang].ToStdString();
    app_c_->whisper_model = kWhisperModelChoices[which_model].ToStdString();
    app_c_->chars_per_sync = chars_per_sync;
    app_c_->bytes_per_char = bytes_per_char;
    app_c_->button = kButton[button_idx].ToStdString();
    app_c_->rows = rows;
    app_c_->cols = cols;
    app_c_->enable_local_beep = enable_local_beep;
    app_c_->use_cpu = use_cpu;
    app_c_->browser_src_port = browser_src_port;
    app_c_->whisper_enable_browser_src = whisper_enable_browser_src_->GetValue();
    app_c_->whisper_enable_builtin = whisper_enable_builtin_->GetValue();
    app_c_->whisper_enable_custom = whisper_enable_custom_->GetValue();
    app_c_->whisper_decode_method = kDecodeMethods[decode_method_idx].ToStdString();
    app_c_->whisper_max_ctxt = max_ctxt;
    app_c_->whisper_beam_width = beam_sz;
    app_c_->whisper_beam_n_best = beam_wd;
    app_c_->whisper_vad_min_duration = vad_min_dur;
    app_c_->whisper_vad_max_duration = vad_max_dur;
    app_c_->whisper_vad_drop_start_silence = vad_drop_silence_dur;
    app_c_->whisper_vad_pause_duration = vad_pause_dur;
    app_c_->whisper_vad_retain_duration = vad_retain_dur;
    app_c_->Serialize(AppConfig::kConfigPath);

    whisper_->Start(*app_c_);
    if (whisper_enable_browser_src_->GetValue()) {
        whisper_->StartBrowserSource(*app_c_);
    }
    if (whisper_enable_custom_->GetValue()) {
        whisper_->StartCustomChatbox(*app_c_);
    }
}

void Frame::OnWhisperStop() {
    whisper_->Stop();
    if (whisper_enable_browser_src_->GetValue()) {
        whisper_->StopBrowserSource();
    }
    if (whisper_enable_custom_->GetValue()) {
        whisper_->StopCustomChatbox();
    }
}

void Frame::OnWhisperStop(wxCommandEvent& event) {
    OnWhisperStop();
}

void Frame::OnAppDrain(wxTimerEvent& event) {
    Logging::kThreadLogger.Drain();
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

	//auto ideal_sz = panel_sz;
	//ideal_sz.x += frame_sz.x;
	//ideal_sz.y += frame_sz.y;

	this->SetSize(panel_sz);
}

