param(
  [switch]$skip_zip = $false,
  [string]$release = "Release"
)

echo "Skip zip: $skip_zip"
echo "Release: $release"

$install_dir = "TaSTT"

if (Test-Path $install_dir) {
  rm -Recurse -Force $install_dir
}

$py_dir = "Python"

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

  rm Python/python310._pth
}

$pip_path = "$py_dir/get-pip.py"

if (-Not (Test-Path $pip_path)) {
  echo "Fetching pip"

  $PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
  $PIP_FILE = $(Split-Path -Path $PIP_URL -Leaf)

  if (-Not (Test-Path $PIP_FILE)) {
    Invoke-WebRequest $PIP_URL -OutFile $PIP_FILE
  }

  mv $PIP_FILE $pip_path
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

#$WHISPER_CHECKPOINT_URL = "https://huggingface.co/datasets/ggerganov/whisper.cpp/resolve/main/ggml-base.bin"
#$WHISPER_CHECKPOINT_FILE = $(Split-Path -Path $WHISPER_CHECKPOINT_URL -Leaf)
#if (-Not (Test-Path $WHISPER_CHECKPOINT_FILE)) {
#  Invoke-WebRequest $WHISPER_CHECKPOINT_URL -OutFile $WHISPER_CHECKPOINT_FILE
#}

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
cp -Recurse ../Shaders TaSTT/Resources/Shaders
cp -Recurse ../Sounds TaSTT/Resources/Sounds
cp -Recurse ../UnityAssets TaSTT/Resources/UnityAssets
cp -Recurse ../BrowserSource TaSTT/Resources/BrowserSource
cp GUI/x64/$release/GUI.exe TaSTT/TaSTT.exe
cp GUI/GUI/Whisper/Whisper.dll TaSTT/Whisper.dll
mkdir TaSTT/Resources/Models
#cp $WHISPER_CHECKPOINT_FILE TaSTT/Resources/Models/

if (-Not $skip_zip) {
  Compress-Archive -Path "$install_dir" -DestinationPath "$install_dir.zip" -Force
}

