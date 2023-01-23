#include "Frame.h"
#include "Logging.h"
#include "PythonWrapper.h"

#include "Config.h"

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

using ::Logging::Log;

Frame::Frame()
    : wxFrame(nullptr, wxID_ANY, "TaSTT"),
    py_app_(nullptr),
    py_app_drain_(this, ID_PY_APP_DRAIN)
{
    TranscriptionAppConfig py_c;
    py_c.Deserialize(TranscriptionAppConfig::kConfigPath);

    UnityAppConfig unity_c;
    unity_c.Deserialize(UnityAppConfig::kConfigPath);

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
            const auto transcribe_out_sz = wxSize(/*x_px=*/480, /*y_px=*/160);
            auto* transcribe_out = new wxTextCtrl(transcribe_panel, ID_TRANSCRIBE_OUT,
                wxEmptyString,
                wxDefaultPosition,
                transcribe_out_sz, wxTE_MULTILINE | wxTE_READONLY);
            transcribe_out->SetMinSize(transcribe_out_sz);
            transcribe_out_ = transcribe_out;

            Log(transcribe_out_, "{}\n", PythonWrapper::GetVersion());

            auto* py_config_panel = new wxPanel(transcribe_panel, ID_PY_CONFIG_PANEL);
            {
                auto* py_setup_button = new wxButton(py_config_panel, ID_PY_SETUP_BUTTON, "Set up Python virtual environment");
                py_setup_button->SetToolTip(
                    "TaSTT uses the Python programming language to provide both "
                    "transcription services and to interface with Unity. "
                    "It installs its dependencies into an isolated folder "
                    "called a 'virtual environment'. Click this button to "
                    "install those dependencies. This only has to be done "
                    "once when you install a new version of TaSTT.");
                auto* py_dump_mics_button = new wxButton(py_config_panel, ID_PY_DUMP_MICS_BUTTON, "List input devices");
                py_dump_mics_button->SetToolTip(
                    "List the microphones (and input devices) attached to "
                    "your computer. To use a microphone, enter the number "
                    "to its left in the 'Microphone' dropdown.");
                auto* py_app_config_panel_pairs = new wxPanel(py_config_panel, ID_PY_APP_CONFIG_PANEL_PAIRS);
                {
                    auto* py_app_mic = new wxChoice(py_app_config_panel_pairs, ID_PY_APP_MIC, wxDefaultPosition,
                        wxDefaultSize, kNumMicChoices, kMicChoices);
                    int mic_idx = GetDropdownChoiceIndex(kMicChoices, kNumMicChoices, py_c.microphone, kMicDefault);
                    py_app_mic->SetSelection(mic_idx);
                    py_app_mic->SetToolTip(
                        "Select which microphone to listen to when "
                        "transcribing. To get list microphones and get their "
                        "numbers, click 'List input devices'.");
                    py_app_mic_ = py_app_mic;

                    auto* py_app_lang = new wxChoice(py_app_config_panel_pairs, ID_PY_APP_LANG, wxDefaultPosition,
                        wxDefaultSize, kNumLangChoices, kLangChoices);
                    int lang_idx = GetDropdownChoiceIndex(kLangChoices, kNumLangChoices, py_c.language, kLangDefault);
                    py_app_lang->SetSelection(lang_idx);
                    py_app_lang->SetToolTip("Select which language you will "
                        "speak in. It will be transcribed into that language. "
                        "If using a language with non-ASCII characters (i.e. "
                        "not English), make sure you have 'bytes per char' "
                        "set to 2. If using something other than English, "
                        "make sure you're not using a *.en model.");
                    py_app_lang_ = py_app_lang;

                    auto* py_app_model = new wxChoice(py_app_config_panel_pairs, ID_PY_APP_MODEL, wxDefaultPosition,
                        wxDefaultSize, kNumModelChoices, kModelChoices);
                    int model_idx = GetDropdownChoiceIndex(kModelChoices, kNumModelChoices, py_c.model, kModelDefault);
                    py_app_model->SetSelection(model_idx);
                    py_app_model->SetToolTip("Select which version of "
                        "the transcription model to use. 'base' is a good "
                        "choice for most users. 'small' is slightly more "
                        "accurate, slower, and uses more VRAM. The *.en "
                        "models are fine-tuned English language models, and "
                        "don't work for other languages.");
                    py_app_model_ = py_app_model;

                    auto* py_app_chars_per_sync = new wxChoice(py_app_config_panel_pairs,
                        ID_PY_APP_CHARS_PER_SYNC, wxDefaultPosition,
                        wxDefaultSize, kNumCharsPerSync, kCharsPerSync);
                    int chars_idx = GetDropdownChoiceIndex(kCharsPerSync, kNumCharsPerSync, py_c.chars_per_sync, kCharsDefault);
                    py_app_chars_per_sync->SetSelection(chars_idx);
                    py_app_chars_per_sync->SetToolTip(
                        "VRChat syncs avatar parameters roughly 5 times per "
                        "second. We use this to send text to the box. By "
                        "sending more characters per sync, the box will be "
                        "faster, but you'll use more avatar parameters.");
                    py_app_chars_per_sync_ = py_app_chars_per_sync;

                    auto* py_app_bytes_per_char = new wxChoice(py_app_config_panel_pairs,
                        ID_PY_APP_BYTES_PER_CHAR, wxDefaultPosition,
                        wxDefaultSize, kNumBytesPerChar, kBytesPerChar);
                    int bytes_idx = GetDropdownChoiceIndex(kBytesPerChar, kNumBytesPerChar, py_c.bytes_per_char, kBytesDefault);
                    py_app_bytes_per_char->SetSelection(bytes_idx);
					py_app_bytes_per_char->SetToolTip(
						"If you speak a language that uses non-ASCII "
						"characters (i.e. not English), set this to 2.");
                    py_app_bytes_per_char_ = py_app_bytes_per_char;

                    auto* py_app_rows = new wxTextCtrl(py_app_config_panel_pairs,
                        ID_PY_APP_ROWS, py_c.rows,
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
                    py_app_rows->SetToolTip(
                        "The number of rows on the text box.");
                    py_app_rows_ = py_app_rows;

                    auto* py_app_cols = new wxTextCtrl(py_app_config_panel_pairs,
                        ID_PY_APP_COLS, py_c.cols,
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
                    py_app_cols->SetToolTip(
                        "The number of columns on the text box.");
                    py_app_cols_ = py_app_cols;

                    auto* py_app_window_duration = new wxTextCtrl(py_app_config_panel_pairs,
                        ID_PY_APP_WINDOW_DURATION, py_c.window_duration,
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
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

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs, wxID_ANY, /*label=*/"Microphone:"));
                    sizer->Add(py_app_mic, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs, wxID_ANY, /*label=*/"Language:"));
                    sizer->Add(py_app_lang, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs, wxID_ANY, /*label=*/"Model:"));
                    sizer->Add(py_app_model, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs, wxID_ANY, /*label=*/"Characters per sync:"));
                    sizer->Add(py_app_chars_per_sync, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs, wxID_ANY, /*label=*/"Bytes per character:"));
                    sizer->Add(py_app_bytes_per_char, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs, wxID_ANY, /*label=*/"Text box rows:"));
                    sizer->Add(py_app_rows, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs, wxID_ANY, /*label=*/"Text box columns:"));
                    sizer->Add(py_app_cols, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs, wxID_ANY, /*label=*/"Window duration (s):"));
                    sizer->Add(py_app_window_duration, /*proportion=*/0, /*flags=*/wxEXPAND);
                }

                auto* py_app_enable_local_beep = new wxCheckBox(py_config_panel,
                    ID_PY_APP_ENABLE_LOCAL_BEEP, "Enable local beep");
                py_app_enable_local_beep->SetValue(py_c.enable_local_beep);
                py_app_enable_local_beep->SetToolTip(
                    "By default, TaSTT will play a sound (audible only to "
                    "you) when it begins transcription and when it stops. "
                    "Uncheck this to disable that behavior."
                );
                py_app_enable_local_beep_ = py_app_enable_local_beep;

                auto* py_app_use_cpu = new wxCheckBox(py_config_panel,
                    ID_PY_APP_USE_CPU, "Use CPU");
                py_app_use_cpu->SetValue(py_c.use_cpu);
                py_app_use_cpu->SetToolTip(
                    "If checked, the transcription engine will run on your "
                    "CPU instead of your GPU. This is typically much slower "
                    "and should only be used if you aren't able to use your "
                    "GPU."
                );
                py_app_use_cpu_ = py_app_use_cpu;

                auto* py_app_use_builtin = new wxCheckBox(py_config_panel,
                    ID_PY_APP_USE_CPU, "Use built-in chatbox");
                py_app_use_builtin->SetValue(py_c.use_builtin);
                py_app_use_builtin->SetToolTip(
                    "If checked, text will be sent to the built-in text box "
                    "instead of one attached to the current avatar."
                );
                py_app_use_builtin_ = py_app_use_builtin;

                auto* py_app_start_button = new wxButton(py_config_panel, ID_PY_APP_START_BUTTON, "Begin transcribing");
                auto* py_app_stop_button = new wxButton(py_config_panel, ID_PY_APP_STOP_BUTTON, "Stop transcribing");

                auto* sizer = new wxBoxSizer(wxVERTICAL);
                py_config_panel->SetSizer(sizer);
                sizer->Add(py_setup_button, /*proportion=*/0, /*flags=*/wxEXPAND);
                sizer->Add(py_dump_mics_button, /*proportion=*/0, /*flags=*/wxEXPAND);
                sizer->Add(py_app_config_panel_pairs, /*proportion=*/0, /*flags=*/wxEXPAND);
                sizer->Add(py_app_enable_local_beep, /*proportion=*/0, /*flags=*/wxEXPAND);
                sizer->Add(py_app_use_cpu, /*proportion=*/0, /*flags=*/wxEXPAND);
                sizer->Add(py_app_use_builtin, /*proportion=*/0, /*flags=*/wxEXPAND);
                sizer->Add(py_app_start_button, /*proportion=*/0, /*flags=*/wxEXPAND);
                sizer->Add(py_app_stop_button, /*proportion=*/0, /*flags=*/wxEXPAND);
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

            auto* unity_config_panel = new wxPanel(unity_panel, ID_UNITY_CONFIG_PANEL);
            {
				auto* unity_config_panel_pairs = new wxPanel(unity_config_panel, ID_UNITY_CONFIG_PANEL_PAIRS);
                {
                    auto* unity_assets_file_picker = new wxDirPickerCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_ASSETS_FILE_PICKER,
                        /*path=*/unity_c.assets_path,
                        /*message=*/"Unity Assets folder"
                        );
                    unity_assets_file_picker->SetToolTip(
                        "The path to the Assets folder for your avatar's "
                        "Unity project. Example:\n"
						"py_c:\\Users\\yum\\unity\\kumadan\\Assets");
                    unity_assets_file_picker_ = unity_assets_file_picker;

                    auto* unity_animator_file_picker = new wxFilePickerCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_ANIMATOR_FILE_PICKER,
                        /*path=*/unity_c.fx_path,
                        /*message=*/"FX controller path",
                        /*wildcard=*/wxFileSelectorDefaultWildcardStr,
                        /*pos=*/wxDefaultPosition,
                        /*size=*/wxDefaultSize
                        );
                    unity_animator_file_picker->SetToolTip(
                        "The path to your avatar's FX layer. You can find "
                        "this in your avatar descriptor. Example:\n"
						"py_c:\\Users\\yum\\unity\\kumadan\\Assets\\kumadan_fx.controller");
                    unity_animator_file_picker_ = unity_animator_file_picker;

                    auto* unity_parameters_file_picker = new wxFilePickerCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_PARAMETERS_FILE_PICKER,
                        /*path=*/unity_c.params_path,
                        /*message=*/"Avatar parameters path",
                        /*wildcard=*/wxFileSelectorDefaultWildcardStr,
                        /*pos=*/wxDefaultPosition,
                        /*size=*/wxDefaultSize
                        );
                    unity_parameters_file_picker->SetToolTip(
                        "The path to your avatar's parameters. You can find "
                        "this in your avatar descriptor. Example:\n"
						"py_c:\\Users\\yum\\unity\\kumadan\\Assets\\kumadan_parameters.asset");
                    unity_parameters_file_picker_ = unity_parameters_file_picker;

                    auto* unity_menu_file_picker = new wxFilePickerCtrl(
                        unity_config_panel_pairs,
                        ID_UNITY_MENU_FILE_PICKER,
                        /*path=*/unity_c.menu_path,
                        /*message=*/"Avatar menu path",
                        /*wildcard=*/wxFileSelectorDefaultWildcardStr,
                        /*pos=*/wxDefaultPosition,
                        /*size=*/wxDefaultSize
                        );
                    unity_menu_file_picker->SetToolTip(
                        "The path to your avatar's menu. You can find "
                        "this in your avatar descriptor. Example:\n"
						"py_c:\\Users\\yum\\unity\\kumadan\\Assets\\kumadan_menu.asset");
                    unity_menu_file_picker_ = unity_menu_file_picker;

					auto* unity_animator_generated_dir = new wxTextCtrl(unity_config_panel_pairs,
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
                    unity_animator_generated_dir_ = unity_animator_generated_dir;

					auto* unity_animator_generated_name = new wxTextCtrl(unity_config_panel_pairs,
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

					auto* unity_parameters_generated_name = new wxTextCtrl(unity_config_panel_pairs,
                        ID_UNITY_PARAMETERS_GENERATED_NAME,
						wxEmptyString, wxDefaultPosition, wxDefaultSize,
                        wxTE_READONLY);
                    unity_parameters_generated_name->AppendText("TaSTT_Parameters.asset");
                    unity_parameters_generated_name->SetToolTip(
                        "The name of the parameters file that TaSTT generates. "
                        "It will be placed inside the generated assets "
                        "folder. Put this on your avatar descriptor when "
                        "you're done!");
                    unity_parameters_generated_name_ = unity_parameters_generated_name;

					auto* unity_menu_generated_name = new wxTextCtrl(unity_config_panel_pairs,
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

                    auto* unity_chars_per_sync = new wxChoice(unity_config_panel_pairs,
                        ID_UNITY_CHARS_PER_SYNC, wxDefaultPosition,
                        wxDefaultSize, kNumCharsPerSync, kCharsPerSync);
                    int chars_idx = GetDropdownChoiceIndex(kCharsPerSync, kNumCharsPerSync,
                        std::to_string(unity_c.chars_per_sync), kCharsDefault);
                    unity_chars_per_sync->SetSelection(chars_idx);
					unity_chars_per_sync->SetToolTip(
						"VRChat syncs avatar parameters roughly 5 times per "
						"second. We use this to send text to the box. By "
						"sending more characters per sync, the box will be "
						"faster, but you'll use more avatar parameters.");
                    unity_chars_per_sync_ = unity_chars_per_sync;

                    auto* unity_bytes_per_char = new wxChoice(unity_config_panel_pairs,
                        ID_UNITY_BYTES_PER_CHAR, wxDefaultPosition,
                        wxDefaultSize, kNumBytesPerChar, kBytesPerChar);
					int bytes_idx = GetDropdownChoiceIndex(kBytesPerChar,
                        kNumBytesPerChar, std::to_string(unity_c.bytes_per_char), kBytesDefault);
                    unity_bytes_per_char->SetSelection(bytes_idx);
					unity_bytes_per_char->SetToolTip(
						"If you speak a language that uses non-ASCII "
						"characters (i.e. not English), set this to 2.");
                    unity_bytes_per_char_ = unity_bytes_per_char;

                    auto* unity_rows = new wxTextCtrl(unity_config_panel_pairs,
                        ID_UNITY_ROWS, std::to_string(unity_c.rows),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
                    unity_rows->SetToolTip(
                        "The number of rows on the text box.");
                    unity_rows_ = unity_rows;

                    auto* unity_cols = new wxTextCtrl(unity_config_panel_pairs,
                        ID_UNITY_COLS, std::to_string(unity_c.cols),
                        wxDefaultPosition, wxDefaultSize, /*style=*/0);
                    unity_cols->SetToolTip(
                        "The number of columns on the text box.");
                    unity_cols_ = unity_cols;

                    auto* sizer = new wxFlexGridSizer(/*cols=*/2);
                    unity_config_panel_pairs->SetSizer(sizer);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"Unity Assets folder:"));
                    sizer->Add(unity_assets_file_picker);

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

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"Characters per sync:"));
                    sizer->Add(unity_chars_per_sync, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"Bytes per character:"));
                    sizer->Add(unity_bytes_per_char, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"Text box rows:"));
                    sizer->Add(unity_rows, /*proportion=*/0, /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(unity_config_panel_pairs, wxID_ANY, /*label=*/"Text box columns:"));
                    sizer->Add(unity_cols, /*proportion=*/0, /*flags=*/wxEXPAND);
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
            sizer->Add(unity_config_panel, /*proportion=*/0, /*flags=*/wxEXPAND);
            sizer->Add(unity_out, /*proportion=*/1, /*flags=*/wxEXPAND);
        }
        unity_panel_->Hide();

		auto* sizer = new wxBoxSizer(wxHORIZONTAL);
		main_panel->SetSizer(sizer);
		sizer->Add(navbar, /*proportion=*/0, /*flags=*/wxEXPAND);
		sizer->Add(transcribe_panel, /*proportion=*/1, /*flags=*/wxEXPAND);
		sizer->Add(unity_panel, /*proportion=*/1, /*flags=*/wxEXPAND);
    }

	Bind(wxEVT_MENU, &Frame::OnExit, this, wxID_EXIT);
	Bind(wxEVT_BUTTON, &Frame::OnNavbarTranscribe, this, ID_NAVBAR_BUTTON_TRANSCRIBE);
	Bind(wxEVT_BUTTON, &Frame::OnNavbarUnity, this, ID_NAVBAR_BUTTON_UNITY);
	Bind(wxEVT_BUTTON, &Frame::OnAppStart, this, ID_PY_APP_START_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnAppStop, this, ID_PY_APP_STOP_BUTTON);
    Bind(wxEVT_TIMER,  &Frame::OnAppDrain, this, ID_PY_APP_DRAIN);
	Bind(wxEVT_BUTTON, &Frame::OnSetupPython, this, ID_PY_SETUP_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnDumpMics, this, ID_PY_DUMP_MICS_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnGenerateFX, this, ID_UNITY_BUTTON_GEN_ANIMATOR);
    Bind(wxEVT_CHOICE, &Frame::OnUnityParamChange, this, ID_UNITY_CHARS_PER_SYNC);
    Bind(wxEVT_CHOICE, &Frame::OnUnityParamChange, this, ID_UNITY_BYTES_PER_CHAR);

	// wx needs this to be able to load PNGs.
	wxImage::AddHandler(&png_handler_);
	LoadAndSetIcons();

    Resize();
	OnUnityParamChangeImpl();

    // Every 100 milliseconds we drain output from the Python app.
    py_app_drain_.Start(/*milliseconds=*/100);
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
    Log(transcribe_out_, "Setting up Python virtual environment\n");
    Log(transcribe_out_, "This could take several minutes, please be patient!\n");
    Log(transcribe_out_, "This will download ~5GB of dependencies.\n");

    {
        std::string transcribe_out;
        Log(transcribe_out_, "  Installing pip\n");
        if (!PythonWrapper::InstallPip(&transcribe_out)) {
			Log(transcribe_out_, "Failed to install pip: {}\n", transcribe_out);
        }
    }

    // TODO(yum) do this in a requirements.txt and run this command
    // asynchronously so the GUI doesn't hang
    const std::vector<std::string> pip_deps{
        "future==0.18.2",
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
		Log(transcribe_out_, "  Installing {}\n", pip_dep);
        std::string py_stdout, py_stderr;
        bool res = PythonWrapper::InvokeWithArgs({ "-m", "pip", "install", pip_dep }, &py_stdout, &py_stderr);
        if (!res) {
			Log(transcribe_out_, "Failed to install {}: {}\n", pip_dep, py_stderr);
            return;
        }
    }

	Log(transcribe_out_, "Python virtual environment successfully set up!\n");
}

void Frame::OnDumpMics(wxCommandEvent& event)
{
    Log(transcribe_out_, "{}\n", PythonWrapper::DumpMics());
}

bool GetUserPath(const std::string& raw, std::filesystem::path& clean, const std::string& err_prefix = "", bool must_exist = true) {
    clean = raw;
    if (must_exist && !std::filesystem::exists(clean)) {
        std::ostringstream oss;
        oss << err_prefix << ": User-provided path does not exist at " << clean << std::endl;
        wxLogError(oss.str().c_str());
        return false;
    }
    return true;
}

void Frame::OnGenerateFX(wxCommandEvent& event)
{
    std::filesystem::path unity_assets_path;
    if (!GetUserPath(unity_assets_file_picker_->GetPath().ToStdString(), unity_assets_path,
        "Cannot generate FX layer: Failed to validate assets directory")) {
        return;
    }
    std::filesystem::path unity_animator_path;
    if (!GetUserPath(unity_animator_file_picker_->GetPath().ToStdString(), unity_animator_path,
        "Cannot generate FX layer: Failed to validate animator directory")) {
        return;
    }
    std::filesystem::path unity_parameters_path;
    if (!GetUserPath(unity_parameters_file_picker_->GetPath().ToStdString(), unity_parameters_path,
        "Cannot generate FX layer: Failed to validate parameters directory")) {
        return;
    }
    std::filesystem::path unity_menu_path;
    if (!GetUserPath(unity_menu_file_picker_->GetPath().ToStdString(), unity_menu_path,
        "Cannot generate FX layer: Failed to validate menu directory")) {
        return;
    }

    std::string unity_animator_generated_dir = unity_animator_generated_dir_->GetLineText(0).ToStdString();
    std::string unity_animator_generated_name = unity_animator_generated_name_->GetLineText(0).ToStdString();
    std::string unity_parameters_generated_name = unity_parameters_generated_name_->GetLineText(0).ToStdString();
    std::string unity_menu_generated_name = unity_menu_generated_name_->GetLineText(0).ToStdString();

    int chars_per_sync_idx = unity_chars_per_sync_->GetSelection();
    if (chars_per_sync_idx == wxNOT_FOUND) {
        chars_per_sync_idx = kCharsDefault;
    }
    std::string chars_per_sync_str = kCharsPerSync[chars_per_sync_idx].ToStdString();
    int bytes_per_char_idx = unity_bytes_per_char_->GetSelection();
    if (bytes_per_char_idx == wxNOT_FOUND) {
        bytes_per_char_idx = kBytesDefault;
    }
    std::string bytes_per_char_str = kBytesPerChar[bytes_per_char_idx].ToStdString();

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
        return;
    }
    catch (const std::out_of_range&) {
		Log(unity_out_, "Rows \"{}\" or cols \"{}\" are out of range\n", rows_str, cols_str);
        return;
    }

    UnityAppConfig unity_c;
    unity_c.assets_path = unity_assets_path.string();
    unity_c.fx_path = unity_animator_path.string();
    unity_c.params_path = unity_parameters_path.string();
    unity_c.menu_path = unity_menu_path.string();
    unity_c.bytes_per_char = bytes_per_char;
    unity_c.chars_per_sync = chars_per_sync;
    unity_c.rows = rows;
    unity_c.cols = cols;
    unity_c.Serialize(UnityAppConfig::kConfigPath);

    std::string out;
    if (!PythonWrapper::GenerateAnimator(
        unity_c,
        unity_animator_generated_dir,
        unity_animator_generated_name,
        unity_parameters_generated_name,
        unity_menu_generated_name,
        unity_out_)) {
        wxLogError("Failed to generate animator:\n%s\n", out.c_str());
    }
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
    if (py_app_) {
        if (wxProcess::Exists(py_app_->GetPid())) {
            Log(transcribe_out_, "Transcription engine already running\n");
            return;
        }
        delete py_app_;
        py_app_ = nullptr;
    }

	Log(transcribe_out_, "Launching transcription engine\n");

    auto cb = [&](wxProcess* proc, int ret) -> void {
        Log(transcribe_out_, "Transcription engine exited with code {}\n", ret);
        DrainApp(proc, transcribe_out_);
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
    int chars_per_sync_idx = py_app_chars_per_sync_->GetSelection();
    if (chars_per_sync_idx == wxNOT_FOUND) {
        chars_per_sync_idx = kCharsDefault;
    }
    int bytes_per_char_idx = py_app_bytes_per_char_->GetSelection();
    if (bytes_per_char_idx == wxNOT_FOUND) {
        bytes_per_char_idx = kBytesDefault;
    }
    const bool enable_local_beep = py_app_enable_local_beep_->GetValue();
    const bool use_cpu = py_app_use_cpu_->GetValue();
    const bool use_builtin = py_app_use_builtin_->GetValue();
    std::string rows_str = py_app_rows_->GetValue().ToStdString();
    std::string cols_str = py_app_cols_->GetValue().ToStdString();
    std::string window_duration_str = py_app_window_duration_->GetValue().ToStdString();
    int rows, cols, window_duration;
    try {
        rows = std::stoi(rows_str);
        cols = std::stoi(cols_str);
        window_duration = std::stoi(window_duration_str);
    }
    catch (const std::invalid_argument&) {
		Log(transcribe_out_, "Could not parse rows \"{}\", cols \"{}\", or window duration \"{}\" as an integer\n", rows_str, cols_str);
        return;
    }
    catch (const std::out_of_range&) {
		Log(transcribe_out_, "Rows \"{}\", cols \"{}\", or window duration \"{}\" are out of range\n", rows_str, cols_str, window_duration);
        return;
    }
    const int max_rows = 10;
    const int max_cols = 240;
    const int min_window_duration_s = 10;
    const int max_window_duration_s = 28;
    if (rows < 0 || rows > max_rows ||
        cols < 0 || cols > max_cols ||
        window_duration < min_window_duration_s || window_duration > max_window_duration_s) {
        Log(transcribe_out_, "Rows not on [{},{}] or cols not on [{},{}] or "
            "window_duration not on [{},{}]\n",
            0, max_rows,
            0, max_cols,
            min_window_duration_s, max_window_duration_s);
        return;
    }

    TranscriptionAppConfig py_c;
    py_c.microphone = kMicChoices[which_mic].ToStdString();
    py_c.language = kLangChoices[which_lang].ToStdString();
    py_c.model = kModelChoices[which_model].ToStdString();
    py_c.chars_per_sync = kCharsPerSync[chars_per_sync_idx].ToStdString();
    py_c.bytes_per_char = kBytesPerChar[bytes_per_char_idx].ToStdString();
    py_c.rows = std::to_string(rows);
    py_c.cols = std::to_string(cols);
    py_c.window_duration = std::to_string(window_duration);
    py_c.enable_local_beep = enable_local_beep;
    py_c.use_cpu = use_cpu;
    py_c.use_builtin = use_builtin;
    py_c.Serialize(TranscriptionAppConfig::kConfigPath);

    wxProcess* p = PythonWrapper::StartApp(std::move(cb), py_c);
    if (!p) {
        Log(transcribe_out_, "Failed to launch transcription engine\n");
        return;
    }

    py_app_ = p;
}

void Frame::OnAppStop(wxCommandEvent& event) {
    if (py_app_) {
        const long pid = py_app_->GetPid();

        Log(transcribe_out_, "Stopping transcription engine...\n");

        // Closing stdout causes the app to exit. It takes it quite a while
        // to exit gracefully; be patient.
        py_app_->CloseOutput();

        int timeout_s = 10;
        for (int i = 0; i < 100 * timeout_s; i++) {
			if (!wxProcess::Exists(pid)) {
				break;
			}
            wxMilliSleep(10);
        }

		DrainApp(py_app_, transcribe_out_);

        // Now shut it down.
		bool first = true;
        int loop_cnt = 0;
		while (wxProcess::Exists(pid)) {
			wxProcess::Kill(pid, wxSIGKILL);
			if (++loop_cnt % 100 == 0) {
                Log(transcribe_out_, "Waiting for transcription engine to exit\n");
			}
			wxMilliSleep(10);
        }

        // Since we don't process the termination event, py_app_ deletes itself!
        py_app_ = nullptr;
        Log(transcribe_out_, "Stopped transcription engine\n");
    }
    else {
        Log(transcribe_out_, "Transcription engine already stopped\n");
    }
}

void Frame::OnAppDrain(wxTimerEvent& event) {
	DrainApp(py_app_, transcribe_out_);
}

void Frame::DrainApp(wxProcess* proc, wxTextCtrl* frame) {
    if (!proc) {
        return;
    }

    while (proc->IsInputAvailable()) {
		wxTextInputStream iss(*(proc->GetInputStream()));
        Log(frame, "  {}\n", iss.ReadLine());
	}

    while (proc->IsErrorAvailable()) {
        wxTextInputStream iss(*(proc->GetErrorStream()));
        Log(frame, "  {}\n", iss.ReadLine());
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

