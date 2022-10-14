#!/usr/bin/env python3

import enum
# python3 -m pip install pyyaml
import yaml

def getObjectIds(fx):
    fx_ids = set()
    with open(fx, "r") as f:
        for line in f:
            parts = line.split()
            if line.startswith("---") and len(parts) == 3:
                obj_id = parts[2]
                # Remove & from beginning of object ID.
                obj_id = obj_id[1:]
                fx_ids.add(obj_id)
    return fx_ids

def getOldIds(old_fx_ids, unified_fx_ids):
    id_mapping = {}

    for old_id in old_fx_ids:
        id_mapping[old_id] = str(old_id)
        unified_fx_ids.add(int(old_id))

    return id_mapping

# Map an object ID from old namespace to unified.
def getNewIds(old_fx_ids, unified_fx_ids):
    id_mapping = {}

    for old_id in old_fx_ids:
        new_id = int(old_id)

        # 9100000 is the ID of the animator. There's only one, and we take care
        # to merge it. So no need to create a new identifier for it.
        if new_id != 9100000:
            while (new_id in unified_fx_ids or new_id in old_fx_ids):
                new_id += 1

        unified_fx_ids.add(new_id)
        id_mapping[old_id] = str(new_id)

    return id_mapping

def replaceIds(old_str, id_map):
    result = old_str
    lines = []
    for line in result.split("\n"):
        for old_id, new_id in id_map.items():
            line = line.replace(old_id, new_id)
        lines.append(line)
    return '\n'.join(lines)

def cat(path):
    lines = []
    with open(path, "r") as f:
        for line in f:
            lines.append(line)
    return ''.join(lines)

# Extract the first block whose '---' line matches `prefix`.
def extractFirstBlock(fx, begin_prefix, end_prefix):
    lines = []
    in_block = False
    for line in fx.split("\n"):
        if in_block and line.startswith(end_prefix):
            break
        if line.startswith(begin_prefix):
            in_block = True
        if in_block:
            lines.append(line)
    return '\n'.join(lines) + "\n"

def mergeAnimatorControllers(fx0, fx1, fx0_ids, fx1_ids):
    fx0_anim = extractFirstBlock(cat(fx0), "--- !u!91", "---")
    fx1_anim = extractFirstBlock(cat(fx1), "--- !u!91", "---")

    fx0_anim_params = extractFirstBlock(fx0_anim, "  m_AnimatorParameters:", "  m_AnimatorLayers:")
    fx0_anim_params = "\n".join(fx0_anim_params.split("\n")[1:])
    fx0_anim_params = replaceIds(fx0_anim_params, fx0_ids)

    fx0_anim_layers = extractFirstBlock(fx0_anim, "  m_AnimatorLayers:", "---")
    fx0_anim_layers = "\n".join(fx0_anim_layers.split("\n")[1:])
    fx0_anim_layers = replaceIds(fx0_anim_layers, fx0_ids)

    fx1_anim_params = extractFirstBlock(fx1_anim, "  m_AnimatorParameters:", "  m_AnimatorLayers:")
    fx1_anim_params = "\n".join(fx1_anim_params.split("\n")[1:])
    fx1_anim_params = replaceIds(fx1_anim_params, fx1_ids)

    fx1_anim_layers = extractFirstBlock(fx1_anim, "  m_AnimatorLayers:", "---")
    fx1_anim_layers = "\n".join(fx1_anim_layers.split("\n")[1:])
    fx1_anim_layers = replaceIds(fx1_anim_layers, fx1_ids)

    result = """
--- !u!91 &9100000
AnimatorController:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: FX
  serializedVersion: 5
  m_AnimatorParameters:
"""[1:]

    result += fx0_anim_params
    result += fx1_anim_params

    result += "  m_AnimatorLayers:\n"

    result += fx0_anim_layers
    result += fx1_anim_layers

    return result

# Merge two FX layers.
# fx0, fx1 are both paths to animators.
# The object IDs for fx1 are reassigned to not collide with those used by fx0.
def mergeFX(fx0, fx1):
    fx0_ids = getObjectIds(fx0)
    fx1_ids = getObjectIds(fx1)

    # Get unique identifiers for all objects in both layers.
    new_ids = set()
    fx0_id_mapping = getOldIds(fx0_ids, new_ids)
    fx1_id_mapping = getNewIds(fx1_ids, new_ids)

    # Merge animators
    anim_ctrl = mergeAnimatorControllers(fx0, fx1, fx0_id_mapping, fx1_id_mapping)

    # Remove animators and prefix
    fx0_str = cat(fx0)
    fx1_str = cat(fx1)

    fx0_anim = extractFirstBlock(fx0_str, "--- !u!91", "---")
    fx1_anim = extractFirstBlock(fx1_str, "--- !u!91", "---")

    fx0_str = fx0_str.replace(fx0_anim, "")
    fx1_str = fx1_str.replace(fx1_anim, "")

    prefix = """
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
"""[1:]

    fx0_str = fx0_str.replace(prefix, "")
    fx1_str = fx1_str.replace(prefix, "")

    # Replace old IDs
    #fx0_str = replaceIds(fx0_str, fx0_id_mapping)
    fx1_str = replaceIds(fx1_str, fx1_id_mapping)

    # Output
    return deleteEmptyLines(prefix + anim_ctrl + fx0_str + fx1_str)

def deleteEmptyLines(fx):
    return fx.replace("\n\n", "\n")

# Import a Unity YAML, modifying it to make it legal YAML 1.1.
def importUnityYaml(fx_old, fx_new):
    lines = []
    with open(fx_old, "r") as f:
        first_document = True
        for line in f:
            # Add end-of-document indicators.
            if line.startswith("---"):
                if not first_document:
                    lines.append("...\n")
                first_document = False

            # Remove class ID tag from each block.
            if line.startswith("---"):
                parts = line.split()
                lines.append(parts[0] + " " + parts[2] + "\n")
                continue
            lines.append(line)

    lines.append("...\n")
    with open(fx_new, "w") as f:
        for line in lines:
            f.write(f"{line}")

def AnimatorControllerConstructor(loader, tag_suffix, node):
    print("Got animator node: {}".format(node))
    return None

class Node:
    def __init__(self):
        # Optional. In Unity, this is the fileID of an object. Not all YAML
        # mappings have an anchor.
        self.anchor = None

        # Pointer to the Node containing this one.
        self.parent = None

class Sequence(Node):
    def __init__(self):
        super().__init__()
        self.sequence = []

    def prettyPrint(self, first_indent=None, leading_newline=None):
        depth = 0
        p = self.parent
        while p != None:
            depth += 1
            p = p.parent
        indent = "  " * depth

        lines = []
        first = True
        for item in self.sequence:
            cur_indent = indent
            if first:
                if first_indent != None:
                    cur_indent = first_indent
                first = False
            if hasattr(item, "prettyPrint"):
                lines.append("{}- {}".format(cur_indent, item.prettyPrint(first_indent="", leading_newline=False)))
            else:
                lines.append("{}- {}".format(cur_indent, item))

        if len(lines) == 0:
            return "[]"

        return "\n" + '\n'.join(lines)

    def __str__(self):
        return self.prettyPrint()

    def addChildMapping(self, anchor = None):
        child = Mapping()
        child.anchor = anchor
        child.parent = self
        child.sequence = []

        self.sequence.append(child)

        return child

    def addChildSequence(self, anchor = None):
        child = Sequence()
        child.anchor = anchor
        child.parent = self
        child.sequence = []

        self.sequence.append(child)

        return child

class Mapping(Node):
    def __init__(self):
        super().__init__()
        self.mapping = {}

    def prettyPrint(self, first_indent=None, leading_newline=True):
        depth = 0
        p = self.parent
        while p != None:
            depth += 1
            p = p.parent
        indent = "  " * depth

        lines = []
        first = True
        for k, v in self.mapping.items():
            cur_indent = indent
            if first:
                if first_indent != None:
                    cur_indent = first_indent
                first = False
            lines.append("{}{}: {}".format(cur_indent, k, v))

        result = '\n'.join(lines)

        # Inline 1-item mappings, matching Unity behavior.
        if len(self.mapping.keys()) == 1 and len(result.split("\n")) == 1:
            if first_indent == None:
                return self.prettyPrint(first_indent="")
            return "{" + lines[0] + "}"

        if leading_newline:
            result = "\n" + result

        return result

    def __str__(self):
        return self.prettyPrint()

    def addChildMapping(self, key, anchor = None):
        child = Mapping()
        child.anchor = anchor
        child.parent = self
        child.mapping = {}

        self.mapping[key] = child

        return child

    def addChildSequence(self, key, anchor = None):
        child = Sequence()
        child.anchor = anchor
        child.parent = self
        child.mapping = {}

        self.mapping[key] = child

        return child

class UnityDocument(Mapping):
    def __str__(self):
        return super().__str__()

    def classId(self):
        # AnimatorController
        if self.anchor.startswith("91"):
            return "91"
        # MonoBehaviour
        if self.anchor.startswith("114"):
            return "114"
        # BlendTree
        if self.anchor.startswith("206"):
            return "206"
        # AnimatorStateTransition
        if self.anchor.startswith("1101"):
            return "1101"
        # AnimatorState
        if self.anchor.startswith("1102"):
            return "1102"
        # AnimatorStateMachine
        if self.anchor.startswith("1107"):
            return "1107"
        # AnimatorTransition
        if self.anchor.startswith("1109"):
            return "1109"
        raise Exception("Unrecognized object: {}".format(self.anchor))

class UnityParser:
    STREAM_START = 100
    STREAM_END = 199

    DOCUMENT_START = 200
    DOCUMENT_END = 299

    MAPPING_START = 300
    MAPPING_KEY = 301

    SEQUENCE_VALUE = 400

    state = STREAM_START
    cur_scalar = None
    cur_node = None

    # Simple list of parsed documents. Populated by parse().
    nodes = []
    prev_states = []

    def __str__(self):
        lines = []
        preamble = """
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
"""[1:][:-1]
        lines.append(preamble)
        for doc in self.nodes:
            lines.append("--- !u!" + doc.classId() + " &" + doc.anchor)
            lines.append(str(doc))
        result = '\n'.join(lines)

        for i in range(0,10):
            result = result.replace("\n\n", "\n")

        return result

    def pushState(self, state):
        self.prev_states.append(self.state)
        self.state = state
        #print("state {} ({})".format(self.state, len(self.prev_states)))

    def peekState(self):
        return self.state

    def popState(self):
        self.state = self.prev_states[-1]
        self.prev_states = self.prev_states[0:len(self.prev_states) - 1]
        #print("state {} ({})".format(self.state, len(self.prev_states)))
        return self.state

    def parse(self, yaml_file):
        with open(yaml_file, "r") as f:
            yaml_str = f.read()
            for event in yaml.parse(yaml_str):
                #print("event {}".format(event))

                if isinstance(event, yaml.StreamStartEvent):
                    if len(self.prev_states) > 0:
                        raise Exception("Multiple StreamStartEvents received")
                    self.pushState(self.STREAM_START)
                    continue

                if isinstance(event, yaml.StreamEndEvent):
                    if self.peekState() != self.STREAM_START:
                        raise Exception("Document end received after state {}".format(self.peekState()))
                    self.popState()
                    if len(self.prev_states) > 0:
                        raise Exception("Extra states at stream end")
                    continue

                if isinstance(event, yaml.DocumentStartEvent):
                    if self.peekState() != self.STREAM_START and self.peekState() != self.DOCUMENT_END:
                        raise Exception("Document start received after state {}".format(self.peekState()))
                    self.pushState(self.DOCUMENT_START)
                    continue

                if isinstance(event, yaml.DocumentEndEvent):
                    if self.peekState() != self.DOCUMENT_START:
                        raise Exception("Document end received after state {}".format(self.peekState()))
                    self.popState()
                    self.nodes.append(self.cur_node)
                    self.cur_node = None
                    continue

                if isinstance(event, yaml.MappingStartEvent):
                    if self.cur_node == None:
                        self.cur_node = UnityDocument()
                        self.cur_node.anchor = event.anchor
                    else:
                        self.cur_node = self.cur_node.addChildMapping(self.cur_scalar)
                    self.pushState(self.MAPPING_START)
                    continue

                if isinstance(event, yaml.MappingEndEvent):
                    if self.peekState() != self.MAPPING_START:
                        raise Exception("Mapping end received after state {}".format(self.peekState()))
                    self.popState()
                    if self.peekState() == self.MAPPING_KEY:
                        self.popState()
                    if self.cur_node.parent != None:
                        self.cur_node = self.cur_node.parent
                    continue

                if isinstance(event, yaml.SequenceStartEvent):
                    self.cur_node = self.cur_node.addChildSequence(self.cur_scalar)
                    self.pushState(self.SEQUENCE_VALUE)
                    continue

                if isinstance(event, yaml.SequenceEndEvent):
                    if self.peekState() != self.SEQUENCE_VALUE:
                        raise Exception("Sequence end received after state {}".format(self.peekState()))
                    self.popState()
                    if self.peekState() == self.MAPPING_KEY:
                        self.popState()
                    self.cur_node = self.cur_node.parent
                    continue

                if isinstance(event, yaml.ScalarEvent):
                    if self.peekState() == self.MAPPING_START:
                        self.cur_scalar = event.value
                        self.pushState(self.MAPPING_KEY)
                    elif self.peekState() == self.MAPPING_KEY:
                        self.cur_node.mapping[self.cur_scalar] = event.value
                        self.popState()
                    elif self.peekState() == self.SEQUENCE_VALUE:
                        self.cur_node.sequence.append(event.value)
                    else:
                        raise Exception("Scalar event received after state {}".format(self.peekState()))
                    continue

                raise Exception("Unhandled event {}".format(event))

if __name__ == "__main__":
    arg0 = "tst.fx"

    tmp0 = "fx0.controller"
    importUnityYaml(arg0, tmp0)

    parser = UnityParser()
    try:
        parser.parse(tmp0)
    except Exception as e:
        print("exception: {}".format(e))
    print(parser)

