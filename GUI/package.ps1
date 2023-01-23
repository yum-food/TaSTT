$install_dir = "TaSTT"

if (Test-Path $install_dir) {
  rm -Recurse $install_dir
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

  # Required for pip to work with embedded python
  echo "import site" | Out-File -FilePath Python/python310._pth -Encoding "utf8" -Append
  # Required for TaSTT python script imports to work
  echo "../Scripts" | Out-File -FilePath Python/python310._pth -Encoding "utf8" -Append
  # Required for pip-installed dependency imports to work
  echo "Lib" | Out-File -FilePath Python/python310._pth -Encoding "utf8" -Append
  echo "Lib/site-packages" | Out-File -FilePath Python/python310._pth -Encoding "utf8" -Append
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

$future_version = "0.18.3"
$future_path = "future-$future_version.tar.gz"
if (-Not (Test-Path $future_path)) {
  # Source: https://pypi.org/project/future/#files
  $FUTURE_0_18_3_URL = "https://files.pythonhosted.org/packages/8f/2e/cf6accf7415237d6faeeebdc7832023c90e0282aa16fd3263db0eb4715ec/future-0.18.3.tar.gz"
  $FUTURE_URL = $FUTURE_0_18_3_URL
  $FUTURE_FILE = $(Split-Path -Path $FUTURE_URL -Leaf)

  if (-Not (Test-Path $FUTURE_FILE)) {
    Invoke-WebRequest $FUTURE_URL -OutFile $FUTURE_FILE
  }
  if (-Not (Test-Path Python/Dependencies)) {
    mkdir Python/Dependencies
  }
  if (-Not (Test-Path Python/Dependencies/future-$future_version)) {
    mkdir Python/Dependencies/future-$future_version
  }
  pushd Python/Dependencies >$null
  tar -xvzf ../../$FUTURE_FILE
  popd >$null

  echo "Dependencies/future-$future_version" >> Python/python310._pth
}

mkdir $install_dir > $null
mkdir $install_dir/Resources > $null
cp -Recurse ../Animations TaSTT/Resources/Animations
mkdir TaSTT/Resources/Fonts
cp -Recurse ../Fonts/Bitmaps TaSTT/Resources/Fonts/Bitmaps
cp -Recurse ../Images TaSTT/Resources/Images
cp -Recurse Python TaSTT/Resources/Python
cp -Recurse PortableGit TaSTT/Resources/PortableGit
cp -Recurse ../Scripts TaSTT/Resources/Scripts
cp -Recurse ../Shaders TaSTT/Resources/Shaders
cp -Recurse ../Sounds TaSTT/Resources/Sounds
cp -Recurse ../UnityAssets TaSTT/Resources/UnityAssets
cp GUI/x64/Release/GUI.exe TaSTT/TaSTT.exe

Compress-Archive -Path "$install_dir" -DestinationPath "$install_dir.zip" -Force

