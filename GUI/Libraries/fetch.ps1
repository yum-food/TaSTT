param(
  [switch]$overwrite = $False,
  [string]$release = "Release"
)

echo "Overwrite: $overwrite"
echo "Release: $release"

Set-PSDebug -trace 0

$WX_3_2_1_URL = "https://github.com/wxWidgets/wxWidgets/releases/download/v3.2.1/wxWidgets-3.2.1.zip"
$WX_URL = $WX_3_2_1_URL
$WX_FILE = $(Split-Path -Path $WX_URL -Leaf)

$WHISPER_1_7_0_URL = "https://github.com/Const-me/Whisper/releases/download/1.7.0/Library.zip"
$WHISPER_URL = $WHISPER_1_7_0_URL
$WHISPER_FILE = $(Split-Path -Path $WHISPER_URL -Leaf)

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

popd > $null  # $PSScriptRoot

