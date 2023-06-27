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

popd > $null  # $PSScriptRoot

