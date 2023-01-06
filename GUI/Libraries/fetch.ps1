Set-PSDebug -trace 0

$WX_3_2_1_URL = "https://github.com/wxWidgets/wxWidgets/releases/download/v3.2.1/wxWidgets-3.2.1.zip"
$WX_URL = $WX_3_2_1_URL
$WX_FILE = $(Split-Path -Path $WX_URL -Leaf)

pushd $PSScriptRoot

# WX
if (Test-Path wx) {
  rm -Recurse wx
}

mkdir wx
pushd wx > $null
Invoke-WebRequest $WX_URL -OutFile $WX_FILE
Expand-Archive $WX_FILE -DestinationPath .
popd > $null

# RAPIDYAML
if (Test-Path rapidyaml) {
  rm -Recurse rapidyaml
}

git clone https://github.com/biojppm/rapidyaml
pushd rapidyaml > $null
git checkout v0.5.0
git submodule update --init --recursive

python3 tools/amalgamate.py ryml.h
cp ryml.h ../../GUI/GUI/ryml.h

popd > $null  # rapidyaml

popd > $null  # $PSScriptRoot

