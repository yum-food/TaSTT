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

