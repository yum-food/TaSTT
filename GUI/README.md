## Build instructions

0. Install build dependencies: cmake, git, python3, Visual Studio 2022
1. Open Powershell.
2. Make sure you've downloaded submodules:
```
$ git submodule init
$ git submodule update
```
3. Execute Libraries/fetch.ps1.
4. Open `Libraries/wx/build/msw/wx_vc17.sln` with Visual Studio 2022.
5. Select every project in the Solution Explorer except for `_custom_build`.
6. Right click, select Properties, go to C/C++, Code Generation, and set
   Runtime Library to Multi-threaded (/MT). Make sure this applies to the
   configuration x64/Release.
7. Build x64/Release.
  1. The build configuration is in the top. By default it's probably Debug/x64.
  2. To build: ctrl+shift+B
8. Follow TaSTT-Whisper README and build it as x64/Release.
9. Open GUI/GUI.sln with Visual Studio 2022.
10. Build x64/Release.
11. Run package.ps1 from powershell.

## High level design

* The GUI is written using wxWidgets.
* Python executes core business logic. We can't migrate away since
  there's no CUDA-enabled Whisper implementation available in a good
  systems programming language.
* To skirt licensing complexity, we distribute an embedded python
  that's hacked up to allow installing packages via pip. We use this
  to install packages at runtime (like a net installer), so we don't
  actually distribute all our transitive dependencies. This also keeps
  the initial package size small.

## C++ Style

Follow the Google C++ style guide. This is not absolutely strict but
it will be used to settle arguments.

https://google.github.io/styleguide/cppguide.html

This should get you 80% of the way there:

* When in doubt, use K&R style
* 2 space indents
* Class members `look_like_this_`
* Functions and methods `LookLikeThis()`
* Local variables `look_like_this`
* Global constexprs `kLookLikeThis`

Consistent style reduces cognitive burden. Follow it for the benefit of
your peers.

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

The `future` package imports extra modules, and the embedded python
search path needs to be told where that is. For that reason, we also
redistribute the `future` package in source format.

This is logically what the GUI does internally when it creates the
python environment.

