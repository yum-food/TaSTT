param(
  [switch]$overwrite = $false
)

Set-PSDebug -trace 0

$WX_3_2_1_URL = "https://github.com/wxWidgets/wxWidgets/releases/download/v3.2.1/wxWidgets-3.2.1.zip"
$WX_URL = $WX_3_2_1_URL
$WX_FILE = $(Split-Path -Path $WX_URL -Leaf)

$WHISPER_1_7_0_URL = "https://github.com/Const-me/Whisper/releases/download/1.7.0/Library.zip"
$WHISPER_URL = $WHISPER_1_7_0_URL
$WHISPER_FILE = $(Split-Path -Path $WHISPER_URL -Leaf)

$OATPP_1_3_0_URL = "https://github.com/oatpp/oatpp/archive/refs/tags/1.3.0.zip"
$OATPP_URL = $OATPP_1_3_0_URL
$OATPP_FILE = $(Split-Path -Path $OATPP_URL -Leaf)
$OATPP_VER = $OATPP_FILE -replace '\.[a-z\.]*$'
$OATPP_DIR = "oatpp-$OATPP_VER"

$NPROC = $(Get-CimInstance Win32_Processor).NumberOfCores
echo "nproc: $NPROC"

pushd $PSScriptRoot

# WX
if ((Test-Path wx) -And ($overwrite)) {
  rm -Recurse wx
}

if (-Not (Test-Path wx)) {
  mkdir wx
  pushd wx > $null
  Invoke-WebRequest $WX_URL -OutFile $WX_FILE
  Expand-Archive $WX_FILE -DestinationPath .
  popd > $null
}

# RAPIDYAML
if ((Test-Path rapidyaml) -And ($overwrite)) {
  rm -Recurse rapidyaml
}

if (-Not (Test-Path rapidyaml)) {
  git clone https://github.com/biojppm/rapidyaml
  pushd rapidyaml > $null
  git checkout v0.5.0
  git submodule update --init --recursive

  python3 tools/amalgamate.py ryml.h
  cp ryml.h ../../GUI/GUI/ryml.h
}

if ((Test-Path whisper) -And ($overwrite)) {
  rm -Recurse whisper
}

if (-Not (Test-Path whisper)) {
  mkdir whisper
  pushd whisper > $null
  Invoke-WebRequest $WHISPER_URL -OutFile $WHISPER_FILE
  Expand-Archive $WHISPER_FILE -DestinationPath .
  if (Test-Path ../../GUI/GUI/whisper/) {
    rm -Recurse ../../GUI/GUI/whisper/
  }
  mkdir ../../GUI/GUI/whisper/
  cp Include/*.h ../../GUI/GUI/whisper/
  cp Linker/*.lib ../../GUI/GUI/whisper/Whisper.lib
  cp Binary/*.dll ../../GUI/GUI/whisper/Whisper.dll
  popd > $null
}

if ((Test-Path oatpp) -And ($overwrite)) {
  rm -Recurse oatpp
}

if (-Not (Test-Path oatpp)) {
  mkdir oatpp
  pushd oatpp > $null
  Invoke-WebRequest $OATPP_URL -OutFile $OATPP_FILE
  Expand-Archive $OATPP_FILE -DestinationPath .
  if (Test-Path ../../GUI/GUI/oatpp/) {
    rm -Recurse ../../GUI/GUI/oatpp/
  }
  mkdir ../../GUI/GUI/oatpp/
  pushd $OATPP_DIR > $null
  mkdir build
  pushd build > $null
  cmake.exe .. -DCMAKE_BUILD_TYPE=Release -DOATPP_BUILD_TESTS=OFF
  cmake.exe --build . -j $NPROC --config Release
  popd > $null
  popd > $null
}

popd > $null  # rapidyaml

popd > $null  # $PSScriptRoot

