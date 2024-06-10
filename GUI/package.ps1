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
  echo "Fetching NVIDIA dll 1/4 (90 MB)"
  $CUDNN_1_URL = "https://www.dropbox.com/scl/fi/d21dsoa982ce7wigng510/cudnn_ops_infer64_8.dll?rlkey=xflxyux0ekhr0fs11m4gs58md&st=0wff5fyn&dl=1"
  Invoke-WebRequest $CUDNN_1_URL -OutFile "cudnn_ops_infer64_8.dll"

  echo "Fetching NVIDIA dll 2/4 (570 MB)"
  $CUDNN_2_URL = "https://www.dropbox.com/scl/fi/uqccevwk9h2q84dt9vr6u/cudnn_cnn_infer64_8.dll?rlkey=sik7xd0ozg06nr4eayzdym4la&st=031bb8pa&dl=1"
  Invoke-WebRequest $CUDNN_2_URL -OutFile "cudnn_cnn_infer64_8.dll"

  echo "Fetching NVIDIA dll 3/4 (470 MB)"
  $CUBLAS_1_URL = "https://www.dropbox.com/scl/fi/3vrd4fzwno8q5ejigqz6l/cublasLt64_12.dll?rlkey=uvbdn5e7dmm8ajdhm7yztjmhc&st=dguf57q4&dl=1"
  Invoke-WebRequest $CUBLAS_1_URL -OutFile "cublasLt64_12.dll"

  echo "Fetching NVIDIA dll 4/4 (100 MB)"
  $CUBLAS_2_URL = "https://www.dropbox.com/scl/fi/hoxjdru7qmwbzelw1gr2t/cublas64_12.dll?rlkey=mcmq5t0b62wjc2uc7ylrixwi6&st=z1la337w&dl=1"
  Invoke-WebRequest $CUBLAS_2_URL -OutFile "cublas64_12.dll"

  popd > $null
}

if (-Not (Test-Path UwwwuPP)) {
  git clone https://github.com/yum-food/UwwwuPP
  pushd UwwwuPP > $null
  git submodule update --init --recursive

  mkdir build
  pushd build > $null

  cmake.exe ..
  cmake.exe --build .

  popd > $null
  popd > $null
}

if (-Not (Test-Path Profanity)) {
  mkdir Profanity
  pushd Profanity > $null

  $repo = "List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words"
  git clone https://github.com/LDNOOBW/$repo

  mkdir Profanity
  cp $repo/LICENSE Profanity/
  cp $repo/en Profanity/

  echo "Source: https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words" > Profanity/AUTHOR

  popd > $null
}

if (-Not (Test-Path "silero-vad")) {
  git clone "https://github.com/snakers4/silero-vad"
}

mkdir $install_dir > $null
mkdir $install_dir/Resources > $null
cp -Recurse ../Animations TaSTT/Resources/Animations
mkdir TaSTT/Resources/Fonts
cp -Recurse ../Fonts/Bitmaps TaSTT/Resources/Fonts/Bitmaps
cp -Recurse ../Fonts/Emotes TaSTT/Resources/Fonts/Emotes
cp -Recurse Python TaSTT/Resources/Python
cp -Recurse PortableGit TaSTT/Resources/PortableGit
cp -Recurse ../Scripts TaSTT/Resources/Scripts
cp $nvidia_dir/*.dll TaSTT/Resources/Scripts/
mkdir TaSTT/Resources/Images
cp ../Images/logo*.png TaSTT/Resources/Images/
cp -Recurse ../Shaders TaSTT/Resources/Shaders
cp -Recurse ../Sounds TaSTT/Resources/Sounds
cp -Recurse ../UnityAssets TaSTT/Resources/UnityAssets
cp -Recurse ../BrowserSource TaSTT/Resources/BrowserSource
cp GUI/x64/$release/GUI.exe TaSTT/TaSTT.exe
mkdir TaSTT/Resources/Models
cp "silero-vad/files/silero_vad.onnx" TaSTT/Resources/Models/
cp "silero-vad/LICENSE" TaSTT/Resources/Models/silero_vad.onnx.LICENSE
mkdir TaSTT/Resources/Uwu
cp UwwwuPP/build/Src/Debug/Uwwwu.exe TaSTT/Resources/Uwu/
cp UwwwuPP/LICENSE TaSTT/Resources/Uwu/
cp -r Profanity/Profanity TaSTT/Resources/Profanity

if (-Not $skip_zip) {
  Compress-Archive -Path "$install_dir" -DestinationPath "$install_dir.zip" -Force
}

