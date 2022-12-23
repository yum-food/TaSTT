$install_dir = "TaSTT"

if (Test-Path $install_dir) {
  rm -Recurse $install_dir
}

mkdir $install_dir > $null
mkdir $install_dir/Resources > $null
cp -Recurse ../Animations TaSTT/Resources/Animations
mkdir TaSTT/Resources/Fonts
cp -Recurse ../Fonts/Bitmaps TaSTT/Resources/Fonts/Bitmaps
cp -Recurse ../Images TaSTT/Resources/Images
cp -Recurse ../Python TaSTT/Resources/Python
cp -Recurse ../Scripts TaSTT/Resources/Scripts
cp -Recurse ../Shaders TaSTT/Resources/Shaders
cp -Recurse ../Sounds TaSTT/Resources/Sounds
cp -Recurse ../UnityAssets TaSTT/Resources/UnityAssets
cp GUI/x64/Release/GUI.exe TaSTT/TaSTT.exe

Compress-Archive -Path "$install_dir" -DestinationPath "$install_dir.zip" -Force

