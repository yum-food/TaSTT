import argparse
import libunity
import sys

def setTextureSize(path: str, size: int):
    parser = libunity.MulticoreUnityParser()
    anim = parser.parseFile(path)

    node = anim.nodes[0]
    node.mapping['TextureImporter'].mapping['maxTextureSize'] = size
    for plat in node.mapping['TextureImporter'].mapping['platformSettings'].sequence:
        plat.mapping['maxTextureSize'] = size

    with open(path, "w", encoding="utf-8") as f:
        f.write(libunity.unityYamlToString(anim.nodes))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", type=str, help="Path to texture .meta file.")
    parser.add_argument("--size", type=int, help="Texture size.")
    args = parser.parse_args()

    setTextureSize(args.meta, args.size)

