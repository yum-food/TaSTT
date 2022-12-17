#include "App.h"
#include "Frame.h"

bool MyApp::OnInit()
{
    Frame* frame = new Frame();
    frame->Show(true);

    return true;
}
