## Build instructions

0. Open WSL.
1. Execute Libraries/fetch.sh.
2. Install Visual Studio 2022.
3. Open Libraries/wx/build/msw/wx\_vc17.sln with Visual Studio 2022.
4. Build x64/Release.
5. Open GUI/GUI.sln with Visual Studio 2022.
6. Build x64/Release.
7. Run package.ps1 from powershell.

## High level design

* The GUI is written using wxWidgets.
* Python executes core business logic. We can't migrate away since
  there's no CUDA-enabled Whisper implementation available in a good
  systems programming language.
* To skirt licensing complexity, we distribute an embedded python
  that's hacked up to allow installing packages via pip. We use this
  to install packages at runtime (like a net installer), so we don't
  actually distribute all our transitive dependencies. This also keeps
  the package size small.

## How the embedded python environment works

I'm distributing an embeddable version of python from the official
python website. It's modified so that packages are installed under
Python/Lib/site-packages, instead of the usual filesystem paths.

To bootstrap pip & fetch the dependencies needed:

```
cd TaSTT
./Resources/Python/python.exe Resources/Python/get-pip.py
./Resources/Python/python.exe -m pip install $YOUR\_PACKAGE\_HERE
```

This is logically what the GUI does internally when it creates the
python environment.

