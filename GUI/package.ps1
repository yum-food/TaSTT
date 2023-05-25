param(
  [switch]$skip_zip = $false,
  [string]$release = "Release",
  [string]$install_pip = $true
)

echo "Skip zip: $skip_zip"
echo "Release: $release"
echo "Install pip: $install_pip"

$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

$install_dir = "TaSTT"

if (Test-Path $install_dir) {
  rm -Recurse -Force $install_dir
}

$py_dir = "Python"

if (Test-Path $py_dir) {
  rm -Recurse $py_dir
}
if (-Not (Test-Path $py_dir)) {
  echo "Fetching python"

  $PYTHON_3_10_9_URL = "https://www.python.org/ftp/python/3.10.9/python-3.10.9-embed-amd64.zip"
  $PYTHON_URL = $PYTHON_3_10_9_URL
  $PYTHON_FILE = $(Split-Path -Path $PYTHON_URL -Leaf)

  if (-Not (Test-Path $PYTHON_FILE)) {
    Invoke-WebRequest $PYTHON_URL -OutFile $PYTHON_FILE
  }

  mkdir Python
  Expand-Archive $PYTHON_FILE -DestinationPath Python

  echo "../Scripts" >> Python/python310._pth
  echo "import site" >> Python/python310._pth
}

$pip_path = "$py_dir/get-pip.py"

if (Test-Path $pip_path) {
  rm -Force $pip_path
}

if (-Not (Test-Path $pip_path)) {
  echo "Fetching pip"

  $PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
  $PIP_FILE = $(Split-Path -Path $PIP_URL -Leaf)

  if (-Not (Test-Path $PIP_FILE)) {
    Invoke-WebRequest $PIP_URL -OutFile $PIP_FILE
  }

  mv $PIP_FILE $pip_path
}

if ($install_pip) {
  ./Python/python.exe Python/get-pip.py

  echo "Installing future"
  echo "Assuming host has python 3.10.9 installed" # TODO test for this
  python -m pip install future==0.18.2 --target Python/Lib/site-packages
}

$git_dir = "PortableGit"

if (-Not (Test-Path $git_dir)) {
  echo "Fetching PortableGit"

  # When it's time to update this, get the latest version from here:
  #   https://git-scm.com/download/win
  $GIT_2_39_0_URL = "https://github.com/git-for-windows/git/releases/download/v2.39.0.windows.2/PortableGit-2.39.0.2-64-bit.7z.exe"
  $GIT_URL = $GIT_2_39_0_URL
  $GIT_FILE = $(Split-Path -Path $GIT_URL -Leaf)

  if (-Not (Test-Path $GIT_FILE)) {
    Invoke-WebRequest $GIT_URL -OutFile $GIT_FILE
  }
  & "./$GIT_FILE"

  Read-Host -Prompt "Press enter once PortableGit is installed at $pwd\PortableGit"
}

$nvidia_dir = "nvidia_dll"

if (-Not (Test-Path $nvidia_dir)) {
  echo "Fetching CUDNN dependencies"

  mkdir $nvidia_dir
  pushd $nvidia_dir > $null

  $ZLIB_URL = "https://drive.google.com/uc?export=download&id=1NpWU83JVOWG0tJtFK7ObygTbOasGWZpI"
  Invoke-WebRequest $ZLIB_URL -OutFile "zlibwapi.dll"

  # NVIDIA locks these files behind a fucking login making it a massive
  # pain in the dick for end users to download, so I rehosted them.
  # TODO check hashes.
  echo "Fetching NVIDIA dll 1/4 (600MB)"
  $CUDNN_CNN_INFER_URL = "https://drive.google.com/uc?export=download&confirm=yes&id=1Px7SGEOM8uAJNxxMGBSwo4sEE8H7GzkB"
  Invoke-WebRequest $CUDNN_CNN_INFER_URL -OutFile "cudnn_cnn_infer64_8.dll"

  echo "Fetching NVIDIA dll 2/4 (80MB)"
  $CUDNN_OPS_INFER_URL = "https://drive.google.com/uc?export=download&confirm=yes&id=1mw6Ds1x-4G_GtSzM-GM8y27E9vpQRi_P"
  Invoke-WebRequest $CUDNN_OPS_INFER_URL -OutFile "cudnn_ops_infer64_8.dll"

  echo "Fetching NVIDIA dll 3/4 (80MB)"
  $CUBLAS_64_DLL = "https://drive.google.com/uc?export=download&confirm=yes&id=1bflxDt83inYM0N2N0ebD1tw0Jh9la33R"
  Invoke-WebRequest $CUBLAS_64_DLL -OutFile "cublas64_11.dll"

  echo "Fetching NVIDIA dll 4/4 (150MB)"
  $CUBLAS_LT64_DLL = "https://drive.google.com/uc?export=download&confirm=yes&id=1fQuVgpkbI8tNPTwueEeiLCSDzqSSGldI"
  Invoke-WebRequest $CUBLAS_Lt64_DLL -OutFile "cublasLt64_11.dll"

  popd > $null
}

if (-Not (Test-Path UwwwuPP)) {
  git clone https://github.com/Leonetienne/UwwwuPP
  pushd UwwwuPP > $null
  git submodule update --init --recursive

  mkdir build
  pushd build > $null

  cmake.exe ..
  cmake.exe --build .

  popd > $null
  popd > $null
}

mkdir $install_dir > $null
mkdir $install_dir/Resources > $null
cp -Recurse ../Animations TaSTT/Resources/Animations
mkdir TaSTT/Resources/Fonts
cp -Recurse ../Fonts/Bitmaps TaSTT/Resources/Fonts/Bitmaps
cp -Recurse ../Fonts/Emotes TaSTT/Resources/Fonts/Emotes
cp -Recurse ../Images TaSTT/Resources/Images
cp -Recurse Python TaSTT/Resources/Python
cp -Recurse PortableGit TaSTT/Resources/PortableGit
cp -Recurse ../Scripts TaSTT/Resources/Scripts
cp $nvidia_dir/*.dll TaSTT/Resources/Scripts/
cp -Recurse ../Shaders TaSTT/Resources/Shaders
cp -Recurse ../Sounds TaSTT/Resources/Sounds
cp -Recurse ../UnityAssets TaSTT/Resources/UnityAssets
cp -Recurse ../BrowserSource TaSTT/Resources/BrowserSource
cp GUI/x64/$release/GUI.exe TaSTT/TaSTT.exe
cp ../"TaSTT-Whisper"/x64/Release/Whisper.dll TaSTT/Whisper.dll
mkdir TaSTT/Resources/Models
mkdir TaSTT/Resources/Uwu
cp UwwwuPP/build/Src/Debug/Uwwwu.exe TaSTT/Resources/Uwu/
cp UwwwuPP/LICENSE TaSTT/Resources/Uwu/

if (-Not $skip_zip) {
  Compress-Archive -Path "$install_dir" -DestinationPath "$install_dir.zip" -Force
}

