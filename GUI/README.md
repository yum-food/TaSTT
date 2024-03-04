## Build instructions

0. Install build dependencies: cmake, git, python3, Visual Studio Community
   2022
  0.0. When installing Visual Studio, make sure `Desktop development with C++`
       is selected.
  0.1. Make sure Windows is using Python 3.10.9. From Powershell, the command
       `python.exe --version` should show that it's using 3.10.9. Direct link:
       https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe
1. Open Powershell.
2. Make sure you've downloaded submodules:
```
$ git submodule init
$ git submodule update
```
3. Execute Libraries/fetch.ps1. This will take 2-3 minutes.
  3.0. If you can't run the script, run `Set-ExecutionPolicyPolicy
      Unrestricted` in an admin instance of powershell. Heed the warning,
      this is a security risk! Never run code from someone you don't trust
      unless you've carefully audited it.
4. Open `Libraries/wx/build/msw/wx_vc17.sln` with Visual Studio 2022.
5. Select every project in the Solution Explorer except for `_custom_build`.
6. Right click, select Properties, go to C/C++, Code Generation, and set
   Runtime Library to Multi-threaded (/MT). Make sure this applies to the
   configuration x64/Release. Click Apply.
7. Build x64/Release.
  1. The build configuration is in the top. By default it's probably Debug/x64.
  2. To build: ctrl+shift+B
  3. If you saw an error in 7.1, rerun Libraries/fetch.ps1.
8. Open GUI/GUI.sln with Visual Studio 2022.
9. Build x64/Release.
10. Run package.ps1 from powershell.
  10.0. If you're not creating a redistributable release, use this command
        instead (it's way faster): `package.ps1 -skip_zip`.
  10.1. When PortableGit creates a window, wait for it to complete, then press
        then press enter in Powershell.
  10.2. The first time you run this it'll take a long time since it has to
        fetch a few large packages. Subsequent invocations will be much faster
        since it won't reacquire anything already downloaded. On my connection,
        it took 90 minutes to finish downloading, mostly because Google Drive
        downloads are slower than dirt.

## High level design

* The GUI is written using wxWidgets.
* Python executes core business logic. With libraries like faster\_whisper
  available, this provides a nice balance between flexibility and performance.
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

