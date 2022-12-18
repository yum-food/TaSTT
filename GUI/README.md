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

