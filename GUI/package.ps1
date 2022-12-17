$install_dir = "TaSTT"

if (Test-Path $install_dir) {
  rm -Recurse $install_dir
}

mkdir $install_dir > $null
mkdir $install_dir/Resources > $null
cp ../Images/logo.png TaSTT/Resources
cp GUI/x64/Release/GUI.exe TaSTT/TaSTT.exe

