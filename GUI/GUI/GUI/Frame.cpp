#include "BrowserSource.h"
#include "Frame.h"
#include "Logging.h"
#include "PythonWrapper.h"
#include "ScopeGuard.h"
#include "Util.h"

#include <filesystem>
#include <fstream>
#include <numeric>
#include <regex>
#include <sstream>
#include <string>
#include <vector>
#include <wx/filepicker.h>
#include <wx/txtstrm.h>

// Does `lhs_type lhs = rhs`, where rhs returns `std::optional<lhs_type>`.
// If the optional doesn't return a value, this returns.
// TODO(yum) do this without creating a named temporary.
// Example:
//  ASSIGN_OR_RETURN(int, foo, 1)
#define ASSIGN_OR_RETURN_VOID(lhs_type, lhs, rhs) \
    std::optional<lhs_type> lhs ## _tmp = rhs; \
    if (!lhs ## _tmp.has_value()) return; \
    lhs_type lhs = std::move(lhs ## _tmp).value()

#define ASSIGN_OR_RETURN_BOOL(lhs_type, lhs, rhs) \
    std::optional<lhs_type> lhs ## _tmp = rhs; \
    if (!lhs ## _tmp.has_value()) return false; \
    lhs_type lhs = std::move(lhs ## _tmp).value()

using ::Logging::DrainAsyncOutput;
using ::Logging::Log;

namespace {
    enum FrameIds {
		ID_MAIN_PANEL,
		ID_NAVBAR,
		ID_NAVBAR_BUTTON_TRANSCRIBE,
		ID_NAVBAR_BUTTON_UNITY,
		ID_NAVBAR_BUTTON_DEBUG,
        ID_PY_PANEL,
        ID_PY_CONFIG_PANEL,
        ID_PY_APP_CONFIG_PANEL_PAIRS,
        ID_PY_DUMP_MICS_BUTTON,
        ID_PY_APP_DRAIN,
        ID_PY_APP_START_BUTTON,
        ID_PY_APP_STOP_BUTTON,
        ID_TRANSCRIBE_OUT,
        ID_PY_APP_MIC,
        ID_PY_APP_MIC_PANEL,
        ID_PY_APP_LANG,
        ID_PY_APP_TRANSLATE_TARGET,
        ID_PY_APP_LANG_PANEL,
        ID_PY_APP_MODEL,
        ID_PY_APP_MODEL_TRANSLATION,
        ID_PY_APP_CHARS_PER_SYNC,
        ID_PY_APP_BYTES_PER_CHAR,
        ID_PY_APP_BUTTON,
        ID_PY_APP_MODEL_PANEL,
        ID_PY_APP_ENABLE_LOCAL_BEEP,
        ID_PY_APP_ENABLE_BROWSER_SRC,
        ID_PY_APP_USE_CPU,
        ID_PY_APP_USE_BUILTIN,
        ID_PY_APP_ENABLE_UWU_FILTER,
        ID_PY_APP_REMOVE_TRAILING_PERIOD,
        ID_PY_APP_ENABLE_UPPERCASE_FILTER,
        ID_PY_APP_ENABLE_LOWERCASE_FILTER,
        ID_PY_APP_ENABLE_PROFANITY_FILTER,
        ID_PY_APP_ENABLE_DEBUG_MODE,
        ID_PY_APP_RESET_ON_TOGGLE,
        ID_PY_APP_ENABLE_PREVIEWS,
        ID_PY_APP_ENABLE_LOCK_AT_SPAWN,
        ID_PY_APP_ROWS,
        ID_PY_APP_COLS,
        ID_PY_APP_GPU_IDX,
        ID_PY_APP_KEYBIND,
        ID_PY_APP_BROWSER_SRC_PORT,
        ID_PY_APP_COMMIT_FUZZ_THRESHOLD,
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
		ID_UNITY_BUTTON_AUTO_REFRESH,
		ID_UNITY_BUTTON_AUTO_REFRESH_STOP,
        ID_UNITY_CHARS_PER_SYNC,
        ID_UNITY_BYTES_PER_CHAR,
        ID_UNITY_ROWS,
        ID_UNITY_COLS,
        ID_UNITY_CLEAR_OSC,
        ID_UNITY_ENABLE_PHONEMES,
		ID_DEBUG_PANEL,
		ID_DEBUG_OUT,
		ID_DEBUG_CONFIG_PANEL,
		ID_DEBUG_BUTTON_CLEAR_PIP,
		ID_DEBUG_BUTTON_LIST_PIP,
		ID_DEBUG_BUTTON_RESET_VENV,
		ID_DEBUG_BUTTON_CLEAR_OSC,
		ID_DEBUG_BUTTON_BACKUP_VENV,
		ID_DEBUG_BUTTON_RESTORE_VENV,
		ID_DEBUG_BUTTON_SETUP_VENV,
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
      "afrikaans",
      "albanian",
      "amharic",
      "arabic",
      "armenian",
      "assamese",
      "azerbaijani",
      "bashkir",
      "basque",
      "belarusian",
      "bengali",
      "bosnian",
      "breton",
      "bulgarian",
      "catalan",
      "chinese",
      "croatian",
      "czech",
      "danish",
      "dutch",
      "estonian",
      "faroese",
      "finnish",
      "french",
      "galician",
      "georgian",
      "german",
      "greek",
      "gujarati",
      "haitian creole",
      "hausa",
      "hawaiian",
      "hebrew",
      "hindi",
      "hungarian",
      "icelandic",
      "indonesian",
      "italian",
      "japanese",
      "javanese",
      "kannada",
      "kazakh",
      "khmer",
      "korean",
      "lao",
      "latin",
      "latvian",
      "lingala",
      "lithuanian",
      "luxembourgish",
      "macedonian",
      "malagasy",
      "malay",
      "malayalam",
      "maltese",
      "maori",
      "marathi",
      "mongolian",
      "myanmar",
      "nepali",
      "norwegian",
      "nynorsk",
      "occitan",
      "pashto",
      "persian",
      "polish",
      "portuguese",
      "punjabi",
      "romanian",
      "russian",
      "sanskrit",
      "serbian",
      "shona",
      "sindhi",
      "sinhala",
      "slovak",
      "slovenian",
      "somali",
      "spanish",
      "sundanese"
        "swahili",
      "swedish",
      "tagalog",
      "tajik",
      "tamil",
      "tatar",
      "telugu",
      "thai",
      "tibetan",
      "turkish",
      "turkmen",
      "ukrainian",
      "urdu",
      "uzbek",
      "vietnamese",
      "welsh",
      "yiddish",
      "yoruba",
    };
    const size_t kNumLangChoices = sizeof(kLangChoices) / sizeof(kLangChoices[0]);
    constexpr int kLangDefault = 0;  // english

    const wxString kLangTargetChoices[] = {
	  "Do not translate",
			"Acehnese(Arabic script) | ace_Arab",
			"Acehnese(Latin script) | ace_Latn",
			"Afrikaans | afr_Latn",
			"Akan | aka_Latn",
			"Amharic | amh_Ethi",
			"Armenian | hye_Armn",
			"Assamese | asm_Beng",
			"Asturian | ast_Latn",
			"Awadhi | awa_Deva",
			"Ayacucho Quechua | quy_Latn",
			"Balinese | ban_Latn",
			"Bambara | bam_Latn",
			"Banjar(Arabic script) | bjn_Arab",
			"Banjar(Latin script) | bjn_Latn",
			"Bashkir | bak_Cyrl",
			"Basque | eus_Latn",
			"Belarusian | bel_Cyrl",
			"Bemba | bem_Latn",
			"Bengali | ben_Beng",
			"Bhojpuri | bho_Deva",
			"Bosnian | bos_Latn",
			"Buginese | bug_Latn",
			"Bulgarian | bul_Cyrl",
			"Burmese | mya_Mymr",
			"Catalan | cat_Latn",
			"Cebuano | ceb_Latn",
			"Central Atlas Tamazight | tzm_Tfng",
			"Central Aymara | ayr_Latn",
			"Central Kanuri(Arabic script) | knc_Arab",
			"Central Kanuri(Latin script) | knc_Latn",
			"Central Kurdish | ckb_Arab",
			"Chhattisgarhi | hne_Deva",
			"Chinese(Simplified) | zho_Hans",
			"Chinese(Traditional) | zho_Hant",
			"Chokwe | cjk_Latn",
			"Crimean Tatar | crh_Latn",
			"Croatian | hrv_Latn",
			"Czech | ces_Latn",
			"Danish | dan_Latn",
			"Dari | prs_Arab",
			"Dutch | nld_Latn",
			"Dyula | dyu_Latn",
			"Dzongkha | dzo_Tibt",
			"Eastern Panjabi | pan_Guru",
			"Eastern Yiddish | ydd_Hebr",
			"Egyptian Arabic | arz_Arab",
			"English | eng_Latn",
			"Esperanto | epo_Latn",
			"Estonian | est_Latn",
			"Ewe | ewe_Latn",
			"Faroese | fao_Latn",
			"Fijian | fij_Latn",
			"Finnish | fin_Latn",
			"Fon | fon_Latn",
			"French | fra_Latn",
			"Friulian | fur_Latn",
			"Galician | glg_Latn",
			"Ganda | lug_Latn",
			"Georgian | kat_Geor",
			"German | deu_Latn",
			"Greek | ell_Grek",
			"Guarani | grn_Latn",
			"Gujarati | guj_Gujr",
			"Haitian Creole | hat_Latn",
			"Halh Mongolian | khk_Cyrl",
			"Hausa | hau_Latn",
			"Hebrew | heb_Hebr",
			"Hindi | hin_Deva",
			"Hungarian | hun_Latn",
			"Icelandic | isl_Latn",
			"Igbo | ibo_Latn",
			"Ilocano | ilo_Latn",
			"Indonesian | ind_Latn",
			"Irish | gle_Latn",
			"Italian | ita_Latn",
			"Japanese | jpn_Jpan",
			"Javanese | jav_Latn",
			"Jingpho | kac_Latn",
			"Kabiyè | kbp_Latn",
			"Kabuverdianu | kea_Latn",
			"Kabyle | kab_Latn",
			"Kamba | kam_Latn",
			"Kannada | kan_Knda",
			"Kashmiri(Arabic script) | kas_Arab",
			"Kashmiri(Devanagari script) | kas_Deva",
			"Kazakh | kaz_Cyrl",
			"Khmer | khm_Khmr",
			"Kikongo | kon_Latn",
			"Kikuyu | kik_Latn",
			"Kimbundu | kmb_Latn",
			"Kinyarwanda | kin_Latn",
			"Korean | kor_Hang",
			"Kyrgyz | kir_Cyrl",
			"Lao | lao_Laoo",
			"Latgalian | ltg_Latn",
			"Ligurian | lij_Latn",
			"Limburgish | lim_Latn",
			"Lingala | lin_Latn",
			"Lithuanian | lit_Latn",
			"Lombard | lmo_Latn",
			"Luba - Kasai | lua_Latn",
			"Luo | luo_Latn",
			"Luxembourgish | ltz_Latn",
			"Macedonian | mkd_Cyrl",
			"Magahi | mag_Deva",
			"Maithili | mai_Deva",
			"Malayalam | mal_Mlym",
			"Maltese | mlt_Latn",
			"Maori | mri_Latn",
			"Marathi | mar_Deva",
			"Meitei(Bengali script) | mni_Beng",
			"Mesopotamian Arabic | acm_Arab",
			"Minangkabau(Arabic script) | min_Arab",
			"Minangkabau(Latin script) | min_Latn",
			"Mizo | lus_Latn",
			"Modern Standard Arabic | arb_Arab",
			"Modern Standard Arabic(Romanized) | arb_Latn",
			"Moroccan Arabic | ary_Arab",
			"Mossi | mos_Latn",
			"Najdi Arabic | ars_Arab",
			"Nepali | npi_Deva",
			"Nigerian Fulfulde | fuv_Latn",
			"North Azerbaijani | azj_Latn",
			"North Levantine Arabic | apc_Arab",
			"Northern Kurdish | kmr_Latn",
			"Northern Sotho | nso_Latn",
			"Northern Uzbek | uzn_Latn",
			"Norwegian Bokmål | nob_Latn",
			"Norwegian Nynorsk | nno_Latn",
			"Nuer | nus_Latn",
			"Nyanja | nya_Latn",
			"Occitan | oci_Latn",
			"Odia | ory_Orya",
			"Pangasinan | pag_Latn",
			"Papiamento | pap_Latn",
			"Plateau Malagasy | plt_Latn",
			"Polish | pol_Latn",
			"Portuguese | por_Latn",
			"Romanian | ron_Latn",
			"Rundi | run_Latn",
			"Russian | rus_Cyrl",
			"Samoan | smo_Latn",
			"Sango | sag_Latn",
			"Sanskrit | san_Deva",
			"Santali | sat_Olck",
			"Sardinian | srd_Latn",
			"Scottish Gaelic | gla_Latn",
			"Serbian | srp_Cyrl",
			"Shan | shn_Mymr",
			"Shona | sna_Latn",
			"Sicilian | scn_Latn",
			"Silesian | szl_Latn",
			"Sindhi | snd_Arab",
			"Sinhala | sin_Sinh",
			"Slovak | slk_Latn",
			"Slovenian | slv_Latn",
			"Somali | som_Latn",
			"South Azerbaijani | azb_Arab",
			"South Levantine Arabic | ajp_Arab",
			"Southern Pashto | pbt_Arab",
			"Southern Sotho | sot_Latn",
			"Southwestern Dinka | dik_Latn",
			"Spanish | spa_Latn",
			"Standard Latvian | lvs_Latn",
			"Standard Malay | zsm_Latn",
			"Standard Tibetan | bod_Tibt",
			"Sundanese | sun_Latn",
			"Swahili | swh_Latn",
			"Swati | ssw_Latn",
			"Swedish | swe_Latn",
			"Ta'izzi - Adeni Arabic | acq_Arab",
			"Tagalog | tgl_Latn",
			"Tajik | tgk_Cyrl",
			"Tamasheq(Latin script) | taq_Latn",
			"Tamasheq(Tifinagh script) | taq_Tfng",
			"Tamil | tam_Taml",
			"Tatar | tat_Cyrl",
			"Telugu | tel_Telu",
			"Thai | tha_Thai",
			"Tigrinya | tir_Ethi",
			"Tok Pisin | tpi_Latn",
			"Tosk Albanian | als_Latn",
			"Tsonga | tso_Latn",
			"Tswana | tsn_Latn",
			"Tumbuka | tum_Latn",
			"Tunisian Arabic | aeb_Arab",
			"Turkish | tur_Latn",
			"Turkmen | tuk_Latn",
			"Twi | twi_Latn",
			"Ukrainian | ukr_Cyrl",
			"Umbundu | umb_Latn",
			"Urdu | urd_Arab",
			"Uyghur | uig_Arab",
			"Venetian | vec_Latn",
			"Vietnamese | vie_Latn",
			"Waray | war_Latn",
			"Welsh | cym_Latn",
			"West Central Oromo | gaz_Latn",
			"Western Persian | pes_Arab",
			"Wolof | wol_Latn",
			"Xhosa | xho_Latn",
			"Yoruba | yor_Latn",
			"Yue Chinese | yue_Hant",
			"Zulu | zul_Latn",
		};
    const size_t kNumLangTargetChoices = sizeof(kLangTargetChoices) / sizeof(kLangTargetChoices[0]);
    constexpr int kLangTargetDefault = 0;  // do not translate

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
        "large-v1",
        "large-v2",
    };
    const size_t kNumModelChoices = sizeof(kModelChoices) / sizeof(kModelChoices[0]);
    constexpr int kModelDefault = 2;  // base.en

    const wxString kModelTranslationChoices[] = {
        "nllb-200-distilled-600M",
        "nllb-200-distilled-1.3B",
    };
    const size_t kNumModelTranslationChoices = sizeof(kModelTranslationChoices) / sizeof(kModelTranslationChoices[0]);
    constexpr int kModelTranslationDefault = 2;  // base.en

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
        "left thumbstick",
        "left a",
        "left b",
        "right thumbstick",
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

	std::optional<int> stoiInRange(wxTextCtrl* out, const std::string& int_s, const std::string int_name, int min, int max) {
		int res;
		try {
			res = std::stoi(int_s);
		}
		catch (const std::invalid_argument&) {
			Log(out, "Could not parse {} \"{}\" as an integer: invalid\n",
				int_name, int_s);
			return {};
		}
		catch (const std::out_of_range&) {
			Log(out, "Could not parse {} \"{}\" as an integer: out of "
				"range\n", int_name, int_s);
			return {};
		}
		if (res < min || res > max) {
			Log(out, "Int argument {} is out of the allowed range [{},{}]\n",
				int_name, min, max);
			return {};
		}
		return res;
	}

}  // namespace

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
		obs_app_ = p.get_future();
		p.set_value(true);
	}
	{
		auto p = std::promise<bool>();
		unity_app_ = p.get_future();
		p.set_value(true);
	}
	{
		auto p = std::promise<bool>();
		unity_auto_refresh_ = p.get_future();
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
	{
		auto p = std::promise<void>();
		reset_venv_proc_ = p.get_future();
		p.set_value();
	}

    auto* main_panel = new wxPanel(this, ID_MAIN_PANEL);
	main_panel_ = main_panel;
    {
        auto* navbar = new wxPanel(main_panel, ID_NAVBAR);
        {
			auto* navbar_button_transcribe = new wxButton(navbar,
                ID_NAVBAR_BUTTON_TRANSCRIBE, "Transcription");
			auto* navbar_button_unity = new wxButton(navbar,
                ID_NAVBAR_BUTTON_UNITY, "Unity");
			auto* navbar_button_debug = new wxButton(navbar,
                ID_NAVBAR_BUTTON_DEBUG, "Debug");

			auto* sizer = new wxBoxSizer(wxVERTICAL);
			navbar->SetSizer(sizer);

			sizer->Add(navbar_button_transcribe, /*proportion=*/0,
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
                        "speak in.");
                    py_app_lang_ = py_app_lang;

                    auto* py_app_translate_target = new wxChoice(py_app_config_panel_pairs,
                        ID_PY_APP_TRANSLATE_TARGET, wxDefaultPosition, wxDefaultSize,
                        kNumLangTargetChoices, kLangTargetChoices);
                    py_app_translate_target->SetToolTip("Select which "
                        "language to translate to. This is the language "
                        "that will appear in game. "
                        "If using a language with non-ASCII characters (i.e. "
                        "not English), make sure you have 'bytes per char' "
                        "set to 2.");
                    py_app_translate_target_ = py_app_translate_target;

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

                    auto* py_app_model_translation = new wxChoice(
                        py_app_config_panel_pairs, ID_PY_APP_MODEL_TRANSLATION,
                        wxDefaultPosition, wxDefaultSize, kNumModelTranslationChoices,
                        kModelTranslationChoices);
                    py_app_model_translation->SetToolTip("Select which "
                        "version of the translation model to use. 600M params "
                        "uses 4.1 GB of memory, while 1.3B uses ~7GB of "
                        "memory. If 'Translate to' is set to 'Do not "
                        "translate', this does nothing.");
                    py_app_model_translation_ = py_app_model_translation;

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

					auto* py_app_gpu_idx = new wxTextCtrl(
                        py_app_config_panel_pairs, ID_PY_APP_GPU_IDX,
                        std::to_string(app_c_->gpu_idx), wxDefaultPosition,
						wxDefaultSize, /*style=*/0);
					py_app_gpu_idx->SetToolTip(
						"The index of the GPU to use. 0 is usually your CPU's "
						"onboard GPU (if you have one), 1 is usually your "
						"discrete GPU.");
					py_app_gpu_idx_ = py_app_gpu_idx;

					auto* py_app_keybind = new wxTextCtrl(
						py_app_config_panel_pairs, ID_PY_APP_KEYBIND,
						app_c_->keybind, wxDefaultPosition,
						wxDefaultSize, /*style=*/0);
					py_app_keybind->SetToolTip(
						"The keybind to use to toggle the STT when in desktop "
						"mode. To dismiss the STT, double press the keybind "
						"quickly.");
					py_app_keybind_ = py_app_keybind;

					auto* py_app_browser_src_port = new wxTextCtrl(
						py_app_config_panel_pairs, ID_PY_APP_BROWSER_SRC_PORT,
						std::to_string(app_c_->browser_src_port), wxDefaultPosition,
						wxDefaultSize, /*style=*/0);
                    py_app_browser_src_port->SetToolTip(
                        "The port to send the transcript to when `Enable "
                        "browser source` is enabled. To preview, go to "
                        "localhost:$PORT in your browser, where $PORT is the "
                        "value you configure here.");
					py_app_browser_src_port_ = py_app_browser_src_port;

                    auto* sizer = new wxFlexGridSizer(/*cols=*/2);
                    py_app_config_panel_pairs->SetSizer(sizer);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Microphone:"));
                    sizer->Add(py_app_mic, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Spoken language:"));
                    sizer->Add(py_app_lang, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Transcription model:"));
                    sizer->Add(py_app_model, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Translate to:"));
                    sizer->Add(py_app_translate_target, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Translation model:"));
                    sizer->Add(py_app_model_translation, /*proportion=*/0,
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
                        wxID_ANY, /*label=*/"Desktop keybind:"));
                    sizer->Add(py_app_keybind, /*proportion=*/0,
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
                        wxID_ANY, /*label=*/"GPU index:"));
                    sizer->Add(py_app_gpu_idx, /*proportion=*/0,
                        /*flags=*/wxEXPAND);

                    sizer->Add(new wxStaticText(py_app_config_panel_pairs,
                        wxID_ANY, /*label=*/"Browser source port:"));
                    sizer->Add(py_app_browser_src_port, /*proportion=*/0,
                        /*flags=*/wxEXPAND);
                }

                auto* py_app_enable_browser_src = new wxCheckBox(py_config_panel,
                    ID_PY_APP_ENABLE_BROWSER_SRC, "Enable browser source");
                py_app_enable_browser_src->SetValue(app_c_->enable_browser_src);
                py_app_enable_browser_src->SetToolTip(
                    "Stream transcript to a browser source. To preview, go to "
                    "localhost:8097, or whatever port you configured.");
                py_app_enable_browser_src_ = py_app_enable_browser_src;

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

                auto* py_app_enable_uwu_filter = new wxCheckBox(py_config_panel,
                    ID_PY_APP_ENABLE_UWU_FILTER, "Enable uwu filter :3");
                py_app_enable_uwu_filter->SetValue(app_c_->enable_uwu_filter);
                py_app_enable_uwu_filter->SetToolTip(
                    "If checked, transcribed text will be passed through an "
                    "uwu filter."
                );
                py_app_enable_uwu_filter_ = py_app_enable_uwu_filter;

                auto* py_app_remove_trailing_period = new wxCheckBox(py_config_panel,
                    ID_PY_APP_REMOVE_TRAILING_PERIOD, "Remove trailing period");
                py_app_remove_trailing_period->SetValue(app_c_->remove_trailing_period);
                py_app_remove_trailing_period->SetToolTip(
                    "If checked, transcriptions will never end with a period."
                );
                py_app_remove_trailing_period_ = py_app_remove_trailing_period;

                auto* py_app_enable_uppercase_filter = new wxCheckBox(py_config_panel,
                    ID_PY_APP_ENABLE_UPPERCASE_FILTER, "Enable uppercase filter");
                py_app_enable_uppercase_filter->SetValue(app_c_->enable_uppercase_filter);
                py_app_enable_uppercase_filter->SetToolTip(
                    "If checked, transcribed text will be converted to UPPERCASE."
                );
                py_app_enable_uppercase_filter_ = py_app_enable_uppercase_filter;

                auto* py_app_enable_lowercase_filter = new wxCheckBox(py_config_panel,
                    ID_PY_APP_ENABLE_LOWERCASE_FILTER, "Enable lowercase filter");
                py_app_enable_lowercase_filter->SetValue(app_c_->enable_lowercase_filter);
                py_app_enable_lowercase_filter->SetToolTip(
                    "If checked, transcribed text will be converted to lowercase."
                );
                py_app_enable_lowercase_filter_ = py_app_enable_lowercase_filter;

                auto* py_app_enable_profanity_filter = new wxCheckBox(py_config_panel,
                    ID_PY_APP_ENABLE_PROFANITY_FILTER, "Enable profanity filter");
                py_app_enable_profanity_filter->SetValue(app_c_->enable_profanity_filter);
                py_app_enable_profanity_filter->SetToolTip(
                    "If checked, profane words in your transcript will have "
                    "their vowels replaced with asterisks. Currently only "
                    "English is supported."
                );
                py_app_enable_profanity_filter_ = py_app_enable_profanity_filter;

                auto* py_app_enable_debug_mode = new wxCheckBox(py_config_panel,
                    ID_PY_APP_ENABLE_DEBUG_MODE, "Enable debug mode");
                py_app_enable_debug_mode->SetValue(app_c_->enable_debug_mode);
                py_app_enable_debug_mode->SetToolTip(
                    "If checked, the transcription engine will print out "
                    "additional information. Use this if you're debugging a "
                    "technical issue."
                );
                py_app_enable_debug_mode_ = py_app_enable_debug_mode;

                auto* py_app_reset_on_toggle = new wxCheckBox(py_config_panel,
                    ID_PY_APP_RESET_ON_TOGGLE, "Reset transcript on toggle");
                py_app_reset_on_toggle->SetValue(app_c_->reset_on_toggle);
                py_app_reset_on_toggle->SetToolTip(
                    "If checked, the transcript will be reset (cleared) every "
                    "time that transcription is toggled on. Only affects "
                    "keyboard controls, not the VR controls."
                );
                py_app_reset_on_toggle_ = py_app_reset_on_toggle;

                auto* py_app_enable_previews = new wxCheckBox(py_config_panel,
                    ID_PY_APP_ENABLE_PREVIEWS, "Enable previews");
                py_app_enable_previews->SetValue(app_c_->enable_previews);
                py_app_enable_previews->SetToolTip(
                    "If checked, audio that has not yet stabilized will also "
                    "be transcribed and shown. Turn this off if you're on a "
                    "resource-constrained system or if transcription is "
                    "running slowly."
                );
                py_app_enable_previews_ = py_app_enable_previews;

                auto* py_app_enable_lock_at_spawn = new wxCheckBox(py_config_panel,
                    ID_PY_APP_ENABLE_LOCK_AT_SPAWN, "Lock chatbox at spawn");
                py_app_enable_lock_at_spawn->SetValue(app_c_->enable_lock_at_spawn);
                py_app_enable_lock_at_spawn->SetToolTip(
                    "If checked, the custom chatbox will be locked in world "
                    "space when spawned. This minimizes the visual "
                    "disruption for other players.");
                py_app_enable_lock_at_spawn_ = py_app_enable_lock_at_spawn;

                // Hack: Add newlines before and after the button text to make
                // the buttons bigger, and easier to click from inside VR.
                auto* py_app_start_button = new wxButton(py_config_panel,
                    ID_PY_APP_START_BUTTON, "\nBegin transcribing\n\n");
                auto* py_app_stop_button = new wxButton(py_config_panel,
                    ID_PY_APP_STOP_BUTTON, "\nStop transcribing\n\n");

                auto* sizer = new wxBoxSizer(wxVERTICAL);
                py_config_panel->SetSizer(sizer);
                sizer->Add(py_dump_mics_button, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_config_panel_pairs, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_reset_on_toggle, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_enable_previews, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_enable_lock_at_spawn, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_enable_browser_src, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_enable_local_beep, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_use_cpu, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_use_builtin, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_enable_uwu_filter, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_remove_trailing_period, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_enable_uppercase_filter, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_enable_lowercase_filter, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_enable_profanity_filter, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
                sizer->Add(py_app_enable_debug_mode, /*proportion=*/0,
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
                        /*style=*/0);
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

				auto* enable_phonemes = new wxCheckBox(unity_config_panel,
					ID_UNITY_ENABLE_PHONEMES, "Enable phonemes");
				enable_phonemes->SetValue(app_c_->enable_phonemes);
                enable_phonemes->SetToolTip(
                    "If checked, the chatbox will be created with 5 audio "
                    "sources for each English vowel sound: a, e, i, o, and u. "
                    "Whenever a page of data is sent into the game, any "
                    "vowels will have the corresponding audio source enabled. "
                    "This uses 6 parameter bits.");
                unity_enable_phonemes_ = enable_phonemes;

				auto* unity_button_gen_fx = new wxButton(unity_config_panel,
                    ID_UNITY_BUTTON_GEN_ANIMATOR, "Generate avatar assets");
                unity_button_gen_fx->SetWindowStyleFlag(wxBU_EXACTFIT);

				auto* unity_button_auto_refresh = new wxButton(unity_config_panel,
                    ID_UNITY_BUTTON_AUTO_REFRESH, "Begin auto generating assets on change");
                unity_button_auto_refresh->SetWindowStyleFlag(wxBU_EXACTFIT);
                unity_button_auto_refresh->SetToolTip(
                    "When the configured FX controller, parameters, or menu "
                    "change (as determined by its hash changing), "
                    "automatically regenerate TaSTT assets."
                );

				auto* unity_button_auto_refresh_stop = new wxButton(unity_config_panel,
                    ID_UNITY_BUTTON_AUTO_REFRESH_STOP,
                    "Stop auto generating assets on change");
                unity_button_auto_refresh_stop->SetWindowStyleFlag(wxBU_EXACTFIT);
				unity_button_auto_refresh_stop->SetToolTip(
					"Stop auto-generating TaSTT assets on change.");

				auto* sizer = new wxBoxSizer(wxVERTICAL);
				unity_config_panel->SetSizer(sizer);
				sizer->Add(unity_config_panel_pairs);
                sizer->Add(clear_osc);
                sizer->Add(enable_phonemes);
				sizer->Add(unity_button_gen_fx, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
				sizer->Add(unity_button_auto_refresh, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
				sizer->Add(unity_button_auto_refresh_stop, /*proportion=*/0,
                    /*flags=*/wxEXPAND);
            }

            auto* sizer = new wxBoxSizer(wxHORIZONTAL);
            unity_panel->SetSizer(sizer);
            sizer->Add(unity_config_panel, /*proportion=*/0,
                /*flags=*/wxEXPAND);
            sizer->Add(unity_out, /*proportion=*/1, /*flags=*/wxEXPAND);
        }
        unity_panel_->Hide();

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

				auto* debug_button_setup_venv = new wxButton(
                    debug_config_panel, ID_DEBUG_BUTTON_SETUP_VENV,
                    "Set up virtual env");
                debug_button_setup_venv->SetToolTip(
                    "Reinstall packages to the virtual environment");
				debug_button_setup_venv->SetWindowStyleFlag(wxBU_EXACTFIT);

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
				sizer->Add(debug_button_setup_venv, /*proportion=*/0,
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
    }

    // Now that transcribe_out_ has been created, we can deserialize.
    app_c_ = std::make_unique<AppConfig>(transcribe_out_);
    app_c_->Deserialize(AppConfig::kConfigPath);

	Bind(wxEVT_CLOSE_WINDOW, &Frame::OnExit, this);
	Bind(wxEVT_BUTTON, &Frame::OnNavbarTranscribe, this,
        ID_NAVBAR_BUTTON_TRANSCRIBE);
	Bind(wxEVT_BUTTON, &Frame::OnNavbarUnity, this, ID_NAVBAR_BUTTON_UNITY);
	Bind(wxEVT_BUTTON, &Frame::OnNavbarDebug, this, ID_NAVBAR_BUTTON_DEBUG);
	Bind(wxEVT_BUTTON, &Frame::OnAppStart, this, ID_PY_APP_START_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnAppStop, this, ID_PY_APP_STOP_BUTTON);
    Bind(wxEVT_TIMER,  &Frame::OnAppDrain, this, ID_PY_APP_DRAIN);
	Bind(wxEVT_BUTTON, &Frame::OnDumpMics, this, ID_PY_DUMP_MICS_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnGenerateFX, this,
        ID_UNITY_BUTTON_GEN_ANIMATOR);
	Bind(wxEVT_BUTTON, &Frame::OnUnityAutoRefresh, this,
        ID_UNITY_BUTTON_AUTO_REFRESH);
	Bind(wxEVT_BUTTON, &Frame::OnUnityAutoRefreshStop, this,
        ID_UNITY_BUTTON_AUTO_REFRESH_STOP);
	Bind(wxEVT_BUTTON, &Frame::OnListPip, this, ID_DEBUG_BUTTON_LIST_PIP);
	Bind(wxEVT_BUTTON, &Frame::OnClearPip, this, ID_DEBUG_BUTTON_CLEAR_PIP);
	Bind(wxEVT_BUTTON, &Frame::OnListPip, this, ID_DEBUG_BUTTON_LIST_PIP);
	Bind(wxEVT_BUTTON, &Frame::OnResetVenv, this, ID_DEBUG_BUTTON_RESET_VENV);
	Bind(wxEVT_BUTTON, &Frame::OnClearOSC, this, ID_DEBUG_BUTTON_CLEAR_OSC);
	Bind(wxEVT_BUTTON, &Frame::OnBackupVenv, this, ID_DEBUG_BUTTON_BACKUP_VENV);
	Bind(wxEVT_BUTTON, &Frame::OnRestoreVenv, this,
        ID_DEBUG_BUTTON_RESTORE_VENV);
	Bind(wxEVT_BUTTON, &Frame::OnSetupVenv, this,
        ID_DEBUG_BUTTON_SETUP_VENV);
    Bind(wxEVT_CHOICE, &Frame::OnUnityParamChange, this,
        ID_UNITY_CHARS_PER_SYNC);
    Bind(wxEVT_CHOICE, &Frame::OnUnityParamChange, this,
        ID_UNITY_BYTES_PER_CHAR);
    Bind(wxEVT_CHECKBOX, &Frame::OnUnityParamChange, this,
        ID_UNITY_ENABLE_PHONEMES);

	// wx needs this to be able to load PNGs.
	wxImage::AddHandler(&png_handler_);
	LoadAndSetIcons();

    // Make tooltips show up for longer.
    wxToolTip::SetAutoPop(/*milliseconds=*/ 10 * 1000);

    // Initialize input fields using AppConfig.
    ApplyConfigToInputFields();

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

    auto* py_app_translate_target = static_cast<wxChoice*>(FindWindowById(ID_PY_APP_TRANSLATE_TARGET));
	int translate_target_idx = GetDropdownChoiceIndex(kLangTargetChoices,
		kNumLangTargetChoices, app_c_->language_target, kLangTargetDefault);
	py_app_translate_target->SetSelection(translate_target_idx);

    auto* py_app_model = static_cast<wxChoice*>(FindWindowById(ID_PY_APP_MODEL));
	int model_idx = GetDropdownChoiceIndex(kModelChoices,
		kNumModelChoices, app_c_->model, kModelDefault);
	py_app_model->SetSelection(model_idx);

    auto* py_app_model_translation = static_cast<wxChoice*>(FindWindowById(ID_PY_APP_MODEL_TRANSLATION));
	int model_translation_idx = GetDropdownChoiceIndex(kModelTranslationChoices,
		kNumModelTranslationChoices, app_c_->model_translation, kModelTranslationDefault);
	py_app_model_translation->SetSelection(model_translation_idx);

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

    auto* py_app_button = static_cast<wxChoice*>(FindWindowById(ID_PY_APP_BUTTON));
	int button_idx = GetDropdownChoiceIndex(kButton,
		kNumButtons, app_c_->button, kButtonDefault);
	py_app_button->SetSelection(button_idx);

    auto* py_app_desktop_keybind = static_cast<wxTextCtrl*>(FindWindowById(ID_PY_APP_KEYBIND));
    py_app_desktop_keybind->Clear();
    py_app_desktop_keybind->AppendText(app_c_->keybind);

    auto* py_app_desktop_browser_src_port = static_cast<wxTextCtrl*>(FindWindowById(ID_PY_APP_BROWSER_SRC_PORT));
    py_app_desktop_browser_src_port->Clear();
    py_app_desktop_browser_src_port->AppendText(std::to_string(app_c_->browser_src_port));

    auto* py_app_rows = static_cast<wxTextCtrl*>(FindWindowById(ID_PY_APP_ROWS));
    py_app_rows->Clear();
    py_app_rows->AppendText(std::to_string(app_c_->rows));

    auto* py_app_cols = static_cast<wxTextCtrl*>(FindWindowById(ID_PY_APP_COLS));
    py_app_cols->Clear();
    py_app_cols->AppendText(std::to_string(app_c_->cols));

    auto* py_app_gpu_idx = static_cast<wxTextCtrl*>(FindWindowById(ID_PY_APP_GPU_IDX));
    py_app_gpu_idx->Clear();
    py_app_gpu_idx->AppendText(std::to_string(app_c_->gpu_idx));

    auto* py_app_enable_local_beep = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_ENABLE_LOCAL_BEEP));
    py_app_enable_local_beep->SetValue(app_c_->enable_local_beep);

    auto* py_app_enable_browser_src = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_ENABLE_BROWSER_SRC));
    py_app_enable_browser_src->SetValue(app_c_->enable_browser_src);

    auto* py_app_use_cpu = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_USE_CPU));
    py_app_use_cpu->SetValue(app_c_->use_cpu);

    auto* py_app_use_builtin = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_USE_BUILTIN));
    py_app_use_builtin->SetValue(app_c_->use_builtin);

    auto* py_app_enable_uwu_filter = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_ENABLE_UWU_FILTER));
    py_app_enable_uwu_filter->SetValue(app_c_->enable_uwu_filter);

    auto* py_app_remove_trailing_period = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_REMOVE_TRAILING_PERIOD));
    py_app_remove_trailing_period->SetValue(app_c_->remove_trailing_period);

    auto* py_app_enable_uppercase_filter = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_ENABLE_UPPERCASE_FILTER));
    py_app_enable_uppercase_filter->SetValue(app_c_->enable_uppercase_filter);

    auto* py_app_enable_lowercase_filter = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_ENABLE_LOWERCASE_FILTER));
    py_app_enable_lowercase_filter->SetValue(app_c_->enable_lowercase_filter);

    auto* py_app_enable_profanity_filter = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_ENABLE_PROFANITY_FILTER));
    py_app_enable_profanity_filter->SetValue(app_c_->enable_profanity_filter);

    auto* py_app_enable_debug_mode = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_ENABLE_DEBUG_MODE));
    py_app_enable_debug_mode->SetValue(app_c_->enable_debug_mode);

    auto* py_app_reset_on_toggle = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_RESET_ON_TOGGLE));
    py_app_reset_on_toggle->SetValue(app_c_->reset_on_toggle);

    auto* py_app_enable_previews = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_ENABLE_PREVIEWS));
    py_app_enable_previews->SetValue(app_c_->enable_previews);

    auto* py_app_enable_lock_at_spawn = static_cast<wxCheckBox*>(FindWindowById(ID_PY_APP_ENABLE_LOCK_AT_SPAWN));
    py_app_enable_lock_at_spawn->SetValue(app_c_->enable_lock_at_spawn);

    // Unity panel
    auto* unity_assets_path = static_cast<wxDirPickerCtrl*>(FindWindowById(ID_UNITY_ASSETS_FILE_PICKER));
    unity_assets_path->SetPath(app_c_->assets_path);

    auto* unity_animator_path = static_cast<wxFilePickerCtrl*>(FindWindowById(ID_UNITY_ANIMATOR_FILE_PICKER));
    unity_animator_path->SetPath(app_c_->fx_path);

    auto* unity_params_path = static_cast<wxFilePickerCtrl*>(FindWindowById(ID_UNITY_PARAMETERS_FILE_PICKER));
    unity_params_path->SetPath(app_c_->params_path);

    auto* unity_menu_path = static_cast<wxFilePickerCtrl*>(FindWindowById(ID_UNITY_MENU_FILE_PICKER));
    unity_menu_path->SetPath(app_c_->menu_path);

    auto* unity_generated_dir = static_cast<wxTextCtrl*>(FindWindowById(ID_UNITY_ANIMATOR_GENERATED_DIR));
    unity_generated_dir->Clear();
    unity_generated_dir->AppendText(app_c_->unity_generated_dir);

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

void Frame::OnExit(wxCloseEvent& event)
{
    OnAppStop();
    OnUnityAutoRefreshStop();
    event.Skip();
}

void Frame::OnNavbarTranscribe(wxCommandEvent& event)
{
    transcribe_panel_->Hide();
    unity_panel_->Hide();
    debug_panel_->Hide();

    // Initialize input fields using AppConfig.
    ApplyConfigToInputFields();

    transcribe_panel_->Show();
    Resize();
}

void Frame::OnNavbarUnity(wxCommandEvent& event)
{
    transcribe_panel_->Hide();
    unity_panel_->Hide();
    debug_panel_->Hide();

    // Initialize input fields using AppConfig.
    ApplyConfigToInputFields();

    unity_panel_->Show();
    Resize();
}

void Frame::OnNavbarDebug(wxCommandEvent& event)
{
    transcribe_panel_->Hide();
    unity_panel_->Hide();
    debug_panel_->Hide();

    // Initialize input fields using AppConfig.
    ApplyConfigToInputFields();

    debug_panel_->Show();
    Resize();
}

void Frame::EnsureVirtualEnv(bool block, bool force)
{
    auto status = env_proc_.wait_for(std::chrono::seconds(0));
    if (status != std::future_status::ready) {
		Log(transcribe_out_, "Virtual environment setup already running\n");
		return;
	}

	static const std::filesystem::path venv_flag = std::filesystem::current_path() / ".venv_is_set_up";
	if (!force && std::filesystem::exists(venv_flag)) {
		std::ifstream venv_flag_ifs(venv_flag);
		std::string venv_flag_ts_str;
		std::getline(venv_flag_ifs, venv_flag_ts_str);

		int64_t venv_flag_ts;
		bool is_valid = false;
		try {
			venv_flag_ts = std::stol(venv_flag_ts_str);
			is_valid = true;
		}
		catch (const std::invalid_argument&) {
			Log(transcribe_out_, "Could not venv flag timestamp \"{}\" as long "
				"- will re-setup venv");
		}
		catch (const std::out_of_range&) {
			Log(transcribe_out_, "Could not venv flag timestamp \"{}\" as long "
				"- will re-setup venv");
		}
        return;
	}

    env_proc_ = std::move(std::async(std::launch::async, [&]() {
        Log(transcribe_out_, "Setting up Python virtual environment\n");
		Log(transcribe_out_, "This could take several minutes, please be "
			"patient!\n");
		Log(transcribe_out_, "This will download ~1GB of dependencies.\n");

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

        std::ofstream venv_flag_ofs(venv_flag);
		auto now = std::chrono::system_clock::now();
		const int64_t seconds_since_epoch = std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count();
        venv_flag_ofs << std::to_string(seconds_since_epoch);

		return true;
	}));

    if (block) {
        // Spinning prevents the GUI from hanging.
        while (true) {
            auto status = env_proc_.wait_for(std::chrono::milliseconds(1));
            if (status == std::future_status::ready) {
                break;
            }
        }
    }
}

void Frame::OnDumpMics(wxCommandEvent& event)
{
    auto status = dump_mics_.wait_for(std::chrono::seconds(0));
    if (status != std::future_status::ready) {
		Log(transcribe_out_, "Mic dump already running\n");
		return;
	}
    dump_mics_ = std::move(std::async(std::launch::async, [&]() {
		EnsureVirtualEnv(/*block=*/true);
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

        EnsureVirtualEnv(/*block=*/true);

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
		int bytes_per_char_idx = unity_bytes_per_char_->GetSelection();
		if (bytes_per_char_idx == wxNOT_FOUND) {
			bytes_per_char_idx = kBytesDefault;
		}

		ASSIGN_OR_RETURN_BOOL(int, rows, stoiInRange(transcribe_out_, py_app_rows_->GetValue().ToStdString(), "rows", 1, 10));
		ASSIGN_OR_RETURN_BOOL(int, cols, stoiInRange(transcribe_out_, py_app_cols_->GetValue().ToStdString(), "cols", 1, 120));
		ASSIGN_OR_RETURN_BOOL(int, chars_per_sync, stoiInRange(transcribe_out_, kCharsPerSync[chars_per_sync_idx].ToStdString(), "chars_per_sync", 5, 24));
		ASSIGN_OR_RETURN_BOOL(int, bytes_per_char, stoiInRange(transcribe_out_, kBytesPerChar[bytes_per_char_idx].ToStdString(), "bytes_per_char", 1, 2));

		app_c_->assets_path = unity_assets_path.string();
		app_c_->fx_path = unity_animator_path.string();
		app_c_->params_path = unity_parameters_path.string();
		app_c_->menu_path = unity_menu_path.string();
        app_c_->unity_generated_dir = unity_animator_generated_dir;
		app_c_->bytes_per_char = bytes_per_char;
		app_c_->chars_per_sync = chars_per_sync;
		app_c_->rows = rows;
		app_c_->cols = cols;
		app_c_->clear_osc = unity_clear_osc_->GetValue();
		app_c_->enable_phonemes = unity_enable_phonemes_->GetValue();
		app_c_->Serialize(AppConfig::kConfigPath);

		std::string out;
		if (!PythonWrapper::GenerateAnimator(
			*app_c_,
            std::string(AppConfig::kConfigPath),
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

// Return a non-cryptographic hash of the file at `path`.
std::string hash_non_crypto(const std::string& path) {
    std::ifstream file_ifs(path, std::ios::binary);
    if (!file_ifs) {
        std::cerr << "Could not open the file: " << path << '\n';
        return 0;
    }

    // Read all bytes from the file into a vector
    std::vector<uint8_t> data((std::istreambuf_iterator<char>(file_ifs)),
        std::istreambuf_iterator<char>());

    // Compute the hash as a sum of all bytes
    uint32_t hash = std::accumulate(data.begin(), data.end(), 0);

    std::stringstream ss;
    ss << std::hex << hash;
    return ss.str();
}

void Frame::OnUnityAutoRefresh(wxCommandEvent& event)
{
    auto status = unity_auto_refresh_.wait_for(std::chrono::seconds(0));
    if (status != std::future_status::ready) {
		Log(unity_out_, "Auto refresh thread already running\n");
		return;
	}

	run_unity_auto_refresh_ = true;

    unity_auto_refresh_ = std::move(std::async(std::launch::async, [&]() {
        std::string fx_hash_prev;
        std::string params_hash_prev;
        std::string menu_hash_prev;
        while (run_unity_auto_refresh_) {
            std::this_thread::sleep_for(std::chrono::seconds(3));

			std::filesystem::path unity_animator_path;
			if (!GetUserPath(unity_out_,
				unity_animator_file_picker_->GetPath().ToStdString(),
				unity_animator_path,
				"Cannot auto-refresh FX layer: Failed to validate animator directory")) {
				return false;
			}
			std::filesystem::path unity_parameters_path;
			if (!GetUserPath(unity_out_,
				unity_parameters_file_picker_->GetPath().ToStdString(),
				unity_parameters_path,
				"Cannot auto-refresh FX layer: Failed to validate parameters directory")) {
				return false;
			}
			std::filesystem::path unity_menu_path;
			if (!GetUserPath(unity_out_, unity_menu_file_picker_->GetPath().ToStdString(),
				unity_menu_path,
				"Cannot auto-refresh FX layer: Failed to validate menu directory")) {
				return false;
			}

            if (fx_hash_prev.empty() || params_hash_prev.empty() || menu_hash_prev.empty()) {
                Log(unity_out_, "Generating initial hash of animator, parameters and menu\n");
                fx_hash_prev = hash_non_crypto(unity_animator_path.string());
                params_hash_prev = hash_non_crypto(unity_parameters_path.string());
                menu_hash_prev = hash_non_crypto(unity_menu_path.string());
                continue;
            }

			const std::string fx_hash = hash_non_crypto(unity_animator_path.string());
			const std::string params_hash = hash_non_crypto(unity_parameters_path.string());
			const std::string menu_hash = hash_non_crypto(unity_menu_path.string());

            if (fx_hash.empty() || params_hash.empty() || menu_hash.empty()) {
                Log(unity_out_, "Failed to hash animator ({}, {}), parameters ({}, {}), or menu ({}, {})\n",
                    unity_animator_path.string(), fx_hash,
                    unity_parameters_path.string(), params_hash,
                    unity_menu_path.string(), menu_hash);
                continue;
            }

            if (fx_hash != fx_hash_prev ||
                params_hash != params_hash_prev ||
                menu_hash != menu_hash_prev) {
                Log(unity_out_, "Detected change in animator ({}), params ({}), or menu ({}), regenerating unity assets\n",
                    fx_hash != fx_hash_prev ? "CHANGED" : "NO_CHANGE",
                    params_hash != params_hash_prev ? "CHANGED" : "NO_CHANGE",
                    menu_hash != menu_hash_prev ? "CHANGED" : "NO_CHANGE");
                OnGenerateFX(event);
                fx_hash_prev = fx_hash;
                params_hash_prev = params_hash;
                menu_hash_prev = menu_hash;
            }
		}
        Log(unity_out_, "Stopping unity asset auto-generation\n");
        return true;
        }));
}

void Frame::OnUnityAutoRefreshStop() {
	run_unity_auto_refresh_ = false;
    auto status = unity_auto_refresh_.wait_for(std::chrono::seconds(0));
    if (status == std::future_status::ready) {
        Log(transcribe_out_, "Auto-refresh thread already stopped.\n");
    }
    else {
		unity_auto_refresh_.wait();
		Log(transcribe_out_, "Stopped transcription engine\n");
    }
}

void Frame::OnUnityAutoRefreshStop(wxCommandEvent& event) {
    OnUnityAutoRefreshStop();
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
    auto status = reset_venv_proc_.wait_for(std::chrono::seconds(0));
    if (status != std::future_status::ready) {
		Log(debug_out_, "Virtual environment reset already running\n");
		return;
	}

    /*
    Equivalent shell:
    python -m pip freeze > venv_pkgs.txt
    python -m pip uninstall -r venv_pkgs.txt
    rm venv_pkgs.txt
    */

    reset_venv_proc_ = std::move(std::async(std::launch::async, [&]() {
		Log(debug_out_, "Resetting virtual environment...\n");

        {
            std::stringstream pkg_list_ss;
            auto out_cb = [&](const std::string& out, const std::string& err) {
                Log(debug_out_, "{}", out);
                Log(debug_out_, "{}", err);
                pkg_list_ss << out;
            };
            auto in_cb = [&](std::string& in) {};
            Log(debug_out_, "Freezing packages...\n");
            if (!PythonWrapper::InvokeWithArgs({ "-m pip freeze" }, out_cb, in_cb)) {
                Log(debug_out_, "failed!\n");
                return;
            }

            std::stringstream pkg_list_ss2;
            std::string pkg_line;
            while (std::getline(pkg_list_ss, pkg_line)) {
                if (pkg_line.find("future") != std::string::npos) {
                    continue;
                }
                pkg_list_ss2 << pkg_line << std::endl;
            }

            std::ofstream pkgs_ofs("venv_pkgs.txt");
            pkgs_ofs << pkg_list_ss2.str();
            pkgs_ofs.close();
        }

        // For now, leave venv_pkgs.txt on disk for better debuggability.
		//ScopeGuard venv_pkgs_cleanup([]() { std::filesystem::remove("venv_pkgs.txt"); });

		{
			auto out_cb = [&](const std::string& out, const std::string& err) {
				Log(debug_out_, "{}", out);
				Log(debug_out_, "{}", err);
			};
			auto in_cb = [&](std::string& in) {};
			Log(debug_out_, "Uninstalling packages...\n");
			if (!PythonWrapper::InvokeWithArgs({ "-m pip uninstall -y -r venv_pkgs.txt" }, out_cb, in_cb)) {
				Log(debug_out_, "failed!\n");
				return;
			}
		}

		Log(debug_out_, "Virtual environment reset done!\n");
	}));
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
    EnsureVirtualEnv(/*block=*/false);
}

void Frame::OnSetupVenv(wxCommandEvent& event)
{
	Log(debug_out_, "Setting up virtual environment. Output is printed to the "
        "transcription panel.\n");
    EnsureVirtualEnv(/*block=*/false, /*force=*/true);
}

void Frame::OnUnityParamChangeImpl() {
    int chars_per_sync_idx = unity_chars_per_sync_->GetSelection();
    if (chars_per_sync_idx == wxNOT_FOUND) {
        chars_per_sync_idx = kCharsDefault;
    }
	ASSIGN_OR_RETURN_VOID(int, chars_per_sync, stoiInRange(transcribe_out_, kCharsPerSync[chars_per_sync_idx].ToStdString(), "chars_per_sync", 5, 24));
    int bytes_per_char_idx = unity_bytes_per_char_->GetSelection();
    if (bytes_per_char_idx == wxNOT_FOUND) {
        bytes_per_char_idx = kBytesDefault;
    }
	ASSIGN_OR_RETURN_VOID(int, bytes_per_char, stoiInRange(transcribe_out_, kBytesPerChar[bytes_per_char_idx].ToStdString(), "bytes_per_char", 1, 2));

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
    int misc_bits = 5;

    int phoneme_bits = 0;
    if (unity_enable_phonemes_->GetValue()) {
        phoneme_bits = 6;
    }

    int total_bits = select_bits + layer_bits + scale_bits + misc_bits + phoneme_bits;

    Log(unity_out_, "This configuration will use {} bits of avatar parameter space:\n", total_bits);
    Log(unity_out_, "  {} bits coming from ({} characters per sync) * ({} bytes per character)\n", layer_bits, chars_per_sync, bytes_per_char);
    Log(unity_out_, "  {} bits coming from fixed overheads\n", select_bits + scale_bits + misc_bits);
    if (phoneme_bits > 0) {
        Log(unity_out_, "  {} bits coming from phonemes\n", phoneme_bits);
    }
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

    status = obs_app_.wait_for(std::chrono::seconds(0));
    if (status != std::future_status::ready) {
		Log(transcribe_out_, "Transcription engine (OBS server) already running\n");
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
    int which_translate_target = py_app_translate_target_->GetSelection();
    if (which_translate_target == wxNOT_FOUND) {
        which_translate_target = kLangDefault;
    }
    int which_model = py_app_model_->GetSelection();
    if (which_model == wxNOT_FOUND) {
        which_model = kModelDefault;
    }
    int which_model_translation = py_app_model_translation_->GetSelection();
    if (which_model_translation == wxNOT_FOUND) {
        which_model_translation = kModelTranslationDefault;
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
    const bool enable_browser_src = py_app_enable_browser_src_->GetValue();
    const bool use_cpu = py_app_use_cpu_->GetValue();
    const bool use_builtin = py_app_use_builtin_->GetValue();
    const bool enable_uwu_filter = py_app_enable_uwu_filter_->GetValue();
    const bool remove_trailing_period = py_app_remove_trailing_period_->GetValue();
    const bool enable_uppercase_filter = py_app_enable_uppercase_filter_->GetValue();
    const bool enable_lowercase_filter = py_app_enable_lowercase_filter_->GetValue();
    const bool enable_profanity_filter = py_app_enable_profanity_filter_->GetValue();
    const bool enable_debug_mode = py_app_enable_debug_mode_->GetValue();
    const bool reset_on_toggle = py_app_reset_on_toggle_->GetValue();
    const bool enable_previews = py_app_enable_previews_->GetValue();
    const bool enable_lock_at_spawn = py_app_enable_lock_at_spawn_->GetValue();

	ASSIGN_OR_RETURN_VOID(int, rows, stoiInRange(transcribe_out_, py_app_rows_->GetValue().ToStdString(), "rows", 1, 10));
	ASSIGN_OR_RETURN_VOID(int, cols, stoiInRange(transcribe_out_, py_app_cols_->GetValue().ToStdString(), "cols", 1, 120));
	ASSIGN_OR_RETURN_VOID(int, chars_per_sync, stoiInRange(transcribe_out_, kCharsPerSync[chars_per_sync_idx].ToStdString(), "chars_per_sync", 5, 24));
	ASSIGN_OR_RETURN_VOID(int, bytes_per_char, stoiInRange(transcribe_out_, kBytesPerChar[bytes_per_char_idx].ToStdString(), "bytes_per_char", 1, 2));
	ASSIGN_OR_RETURN_VOID(int, gpu_idx, stoiInRange(transcribe_out_, py_app_gpu_idx_->GetValue().ToStdString(), "gpu_idx", 0, 10));
	ASSIGN_OR_RETURN_VOID(int, browser_src_port, stoiInRange(transcribe_out_, py_app_browser_src_port_->GetValue().ToStdString(), "browser_src_port", 1024, 65535));

    std::string keybind = py_app_keybind_->GetValue().ToStdString();

    app_c_->microphone = kMicChoices[which_mic].ToStdString();
    app_c_->language = kLangChoices[which_lang].ToStdString();
    app_c_->language_target = kLangTargetChoices[which_translate_target].ToStdString();
    app_c_->model = kModelChoices[which_model].ToStdString();
    app_c_->model_translation = kModelTranslationChoices[which_model_translation].ToStdString();
    app_c_->chars_per_sync = chars_per_sync;
    app_c_->bytes_per_char = bytes_per_char;
    app_c_->button = kButton[button_idx].ToStdString();
    app_c_->rows = rows;
    app_c_->cols = cols;
    app_c_->enable_local_beep = enable_local_beep;
    app_c_->enable_browser_src = enable_browser_src;
    app_c_->browser_src_port = browser_src_port;
    app_c_->use_cpu = use_cpu;
    app_c_->use_builtin = use_builtin;
    app_c_->enable_uwu_filter = enable_uwu_filter;
    app_c_->remove_trailing_period = remove_trailing_period;
    app_c_->enable_uppercase_filter = enable_uppercase_filter;
    app_c_->enable_lowercase_filter = enable_lowercase_filter;
    app_c_->enable_profanity_filter = enable_profanity_filter;
    app_c_->enable_debug_mode = enable_debug_mode;
    app_c_->reset_on_toggle = reset_on_toggle;
    app_c_->enable_previews = enable_previews;
    app_c_->enable_lock_at_spawn = enable_lock_at_spawn;
    app_c_->gpu_idx = gpu_idx;
    app_c_->keybind = keybind;
    app_c_->Serialize(AppConfig::kConfigPath);

	auto out_cb = [&](const std::string& out, const std::string& err) {
		Log(transcribe_out_, "{}", out);
		Log(transcribe_out_, "{}", err);

		std::istringstream out_iss(out);
		std::string out_line;
		while (std::getline(out_iss, out_line)) {
			if (out_line.starts_with("Finalized: 1")) {
				transcript_.SetFinalized(true);
			}
			else if (out_line.starts_with("Finalized: 0")) {
				transcript_.SetFinalized(false);
			}

            std::regex pattern("^Transcript: ");
			if (std::regex_search(out_line, pattern)) {
				std::string filtered_transcript = std::regex_replace(out_line, pattern, "");
				filtered_transcript.erase(std::remove_if(filtered_transcript.begin(), filtered_transcript.end(), [](char c) {
					return c == '\n' || c == '\r';
					}), filtered_transcript.end());
				//Log(transcribe_out_, "Got transcription line! Transcript: \"{}\"", filtered_transcript);
				transcript_.Set(std::move(filtered_transcript));
			}
		}
	};
    auto in_cb = [&](std::string& in) {
        if (!run_py_app_) {
            std::ostringstream oss;
            oss << "exit" << std::endl;
            in = oss.str();
        }
    };
    auto run_cb = [&]() {
        return run_py_app_;
    };
    run_py_app_ = true;
    auto prestart_cb = [this]() -> void {
        EnsureVirtualEnv(/*block=*/true);
    };

    obs_app_ = std::async(std::launch::async,
        [this, enable_browser_src, browser_src_port]() -> bool {
            if (enable_browser_src) {
                BrowserSource browser_src(browser_src_port, transcribe_out_, &transcript_);
                browser_src.Run(&run_py_app_);
            }
            return true;
        });
    const std::string config_path(AppConfig::kConfigPath);
    py_app_ = std::move(PythonWrapper::StartApp(config_path, transcribe_out_,
        std::move(out_cb), std::move(in_cb), std::move(run_cb),
        std::move(prestart_cb)));
    Log(transcribe_out_, "py app valid: {}\n", py_app_.valid());
}

void Frame::OnAppStop() {
    run_py_app_ = false;
    auto status = py_app_.wait_for(std::chrono::seconds(0));
    if (status == std::future_status::ready) {
		Log(transcribe_out_, "Transcription engine already stopped\n");
    }
    else {
		py_app_.wait();
        Log(transcribe_out_, "Stopped transcription engine\n");
    }
    status = obs_app_.wait_for(std::chrono::seconds(0));
    if (status == std::future_status::ready) {
		Log(transcribe_out_, "Browser source already stopped\n");
    }
    else {
		obs_app_.wait();
        Log(transcribe_out_, "Stopped browser source\n");
    }
    transcript_.Clear();
}

void Frame::OnAppStop(wxCommandEvent& event) {
    OnAppStop();
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

