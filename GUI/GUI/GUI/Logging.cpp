#include "Logging.h"

#include <wx/wxprec.h>

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <wx/process.h>
#include <wx/tokenzr.h>
#include <wx/txtstrm.h>

#include <fstream>
#include <regex>
#include <sstream>
#include <string>

Logging::ThreadLogger Logging::kThreadLogger = Logging::ThreadLogger();

Logging::ThreadLogger::ThreadLogger() {}

void Logging::ThreadLogger::Append(wxTextCtrl* frame, const std::string&& message)
{
	std::scoped_lock l(mu_);
	auto entry = messages_.find(frame);
	if (entry == messages_.end()) {
		messages_[frame] = { std::move(message) };
	}
	else {
		messages_[frame].push_back(message);
	}
}

void Logging::ThreadLogger::Drain()
{
	std::scoped_lock l(mu_);
	std::ofstream log_ofs("Resources/log.txt", std::ios_base::app);
	for (const auto& [frame, messages] : messages_) {
		for (const auto& message : messages) {
			if (frame) {
				frame->AppendText(message);
			}
			else {
				wxLogError("%s", message);
			}
			log_ofs << message;
		}

		// Constrain wxTextCtrl's to 1000 lines to keep memory in check.
		if (frame) {
			wxString allText = frame->GetValue();
			wxArrayString lines = wxStringTokenize(allText, "\n");
			size_t count = lines.GetCount();
			if (count > 2000) {
				// Keep only the last 1000 lines.
				size_t linesToRemove = count - 1000;

				// Remove lines from the beginning
				lines.RemoveAt(0, linesToRemove);

				// Join the lines back into a single string
				wxString newText = wxJoin(lines, '\n');

				// Update the text in the wxTextCtrl
				frame->Clear();
				frame->AppendText(newText);
			}
		}
	}

	log_ofs.close();
	messages_.clear();
}

std::string Logging::HidePII(const std::string&& str,
	const std::string& replacement) {
	try {
		std::regex c_users("([A-Za-z]:\\\\+[Uu]sers\\\\+)[a-zA-Z0-9_ ]+");
		std::string real_replacement = "$1" + replacement;
		return std::regex_replace(str, c_users, real_replacement);
	}
	catch (const std::exception& e) {
		wxLogFatalError(e.what());
	}
	wxLogFatalError("Unhandled regex error (HidePII)");
	return "";  // Compiler thinks we can get here (we can't) and prints a warning.
}

void Logging::DrainAsyncOutput(wxProcess* proc, wxTextCtrl* frame) {
	if (!proc) {
		return;
	}

	while (proc->IsInputAvailable()) {
		wxTextInputStream iss(*(proc->GetInputStream()));
		Log(frame, "  {}\n", iss.ReadLine().ToStdString());
	}

	while (proc->IsErrorAvailable()) {
		wxTextInputStream iss(*(proc->GetErrorStream()));
		Log(frame, "  {}\n", iss.ReadLine().ToStdString());
	}
}
