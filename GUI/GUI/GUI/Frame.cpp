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
        ID_PY_OUT,
    };
};

Frame::Frame()
	: wxFrame(nullptr, wxID_ANY, "TaSTT"),
	py_panel_(this, ID_PY_PANEL),
	py_panel_sizer_(wxVERTICAL),
	py_version_button_(&py_panel_, ID_PY_VERSION_BUTTON, "Check embedded Python version"),
	py_setup_button_(&py_panel_, ID_PY_SETUP_BUTTON, "Set up Python virtual environment"),
	py_out_(&py_panel_, ID_PY_OUT, wxEmptyString, wxDefaultPosition,
        wxSize(/*x_px=*/480, /*y_px=*/160), wxTE_MULTILINE)
{
	Bind(wxEVT_MENU, &Frame::OnExit, this, wxID_EXIT);
	Bind(wxEVT_BUTTON, &Frame::OnGetPythonVersion, this, ID_PY_VERSION_BUTTON);
	Bind(wxEVT_BUTTON, &Frame::OnSetupPython, this, ID_PY_SETUP_BUTTON);

	// wx needs this to be able to load PNGs.
	wxImage::AddHandler(&png_handler_);
	const std::string icon_path = "Resources/logo.png";
	LoadAndSetIcon(icon_path);

    wxSize py_out_size(/*x=*/80, /*y=*/20);
    py_out_.SetSize(py_out_size);

	py_panel_.SetSizer(&py_panel_sizer_);
    py_panel_sizer_.Add(&py_version_button_);
    py_panel_sizer_.Add(&py_setup_button_);
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
    py_out_.AppendText("Dependencies are installed in the executable folder, "
        "so deleting the folder is all that's needed to undo this.");

    {
        std::string py_out;
        std::ostringstream py_out_oss;
        py_out_oss << "Installing pip" << std::endl;
        py_out_.AppendText(py_out_oss.str());
        if (!py.InstallPip(&py_out)) {
            std::ostringstream py_out_oss;
            py_out_oss << "Failed to install pip: " << py_out;
            py_out_.AppendText(py_out_oss.str());
        }
    }

    const std::vector<std::string> pip_deps{
        "pillow",
        "pydub",
        "pyaudio",
        "playsound==1.2.2",
        "torch --extra-index-url https://download.pytorch.org/whl/cu116",
        "git+https://github.com/openai/whisper.git",
        "openvr",
        "editdistance",
        "pydub",
        "python-osc",
    };

    for (const auto& pip_dep : pip_deps) {
        {
            std::ostringstream py_out_oss;
            py_out_oss << "Installing " << pip_dep << std::endl;
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

void Frame::LoadAndSetIcon(const std::string& icon_path) {
    if (!std::filesystem::exists(icon_path)) {
        wxLogFatalError("Logo is missing from %s", icon_path.c_str());
    }
    wxBitmap icon_img(icon_path, wxBITMAP_TYPE_PNG);
    wxIcon icon;
    icon.CopyFromBitmap(icon_img);
    SetIcon(icon);
}

