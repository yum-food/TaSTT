import libunity
import sys

def removeAudioSources(path: str):
    parser = libunity.MulticoreUnityParser()
    anim = parser.parseFile(path)
    anchors = set()
    node = anim.popNodeOfClass("82")
    while node:
        print("Killed audio source")
        anchors.add(node.anchor)
        node = anim.popNodeOfClass("82")
    for node in anim.nodes:
        anim.scrubReferencesByValue(node, values=anchors)
    with open(path, "w", encoding="utf-8") as f:
        f.write(libunity.unityYamlToString(anim.nodes))

if __name__ == "__main__":
    removeAudioSources(sys.argv[1])

