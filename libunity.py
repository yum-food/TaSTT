#!/usr/bin/env python3

import copy
import enum
import sys
# python3 -m pip install pyyaml
import yaml

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

    def forEach(self, cb):
        for k in self.sequence:
            cb(k)

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

    def forEach(self, cb):
        for k, v in self.mapping.items():
            cb(v)

def classId(anchor):
    # AnimatorController
    if anchor.startswith("91"):
        return "91"
    # MonoBehaviour
    if anchor.startswith("114"):
        return "114"
    # BlendTree
    if anchor.startswith("206"):
        return "206"
    # AnimatorStateTransition
    if anchor.startswith("1101"):
        return "1101"
    # AnimatorState
    if anchor.startswith("1102"):
        return "1102"
    # AnimatorStateMachine
    if anchor.startswith("1107"):
        return "1107"
    # AnimatorTransition
    if anchor.startswith("1109"):
        return "1109"

    # IDK what this is lmao
    if anchor.startswith("74"):
        return "74"
    if anchor.startswith("115"):
        return "115"

    raise Exception("Unrecognized object: {}".format(anchor))

class UnityDocument(Mapping):
    def __str__(self):
        return super().__str__()

    def classId(self):
        return classId(self.anchor)

class UnityAnimator():
    def __init__(self):
        self.nodes = []
        self.id_to_node = {}

    def addNodes(self, nodes):
        for node in nodes:
            self.nodes.append(node)
            if node.anchor == None:
                raise Exception("Node is missing anchor: {}".format(str(node)))
            if node.anchor in self.id_to_node:
                raise Exception("Duplicate anchor: {}, node 1: {}, node 2: {}".format(node.anchor, str(node), str(self.id_to_node[node.anchor])))
            self.id_to_node[node.anchor] = node

    def getUniqueId(self, anchor):
        if anchor in self.id_mapping.keys():
            return self.id_mapping[anchor]

        if classId(anchor) in self.class_to_next_id:
            new_id = self.class_to_next_id[classId(anchor)]
            self.class_to_next_id[classId(anchor)] += 1
            self.id_mapping[anchor] = new_id
        else:
            new_id = int("%s%05d" % (classId(anchor), 0))
            next_id = new_id + 1
            self.class_to_next_id[classId(anchor)] = next_id
            self.id_mapping[anchor] = new_id

        #print("Map {} to {}".format(anchor, self.id_mapping[anchor]), file=sys.stderr)
        return self.id_mapping[anchor]

    def mergeIterator(self, v):
        if hasattr(v, "mapping"):
            # Don't relabel anything that's defined in an external file.
            # TODO(yum) do this.
            if 'fileID' in v.mapping and not 'guid' in v.mapping:
                if v.mapping['fileID'] != '0':
                    old_id = v.mapping['fileID']
                    new_id = self.getUniqueId(old_id)
                    v.mapping['fileID'] = str(new_id)
        if hasattr(v, "forEach"):
            v.forEach(self.mergeIterator)

    def popNodeOfClass(self, classId):
        result = None
        for node in self.nodes:
            if node.classId() == classId:
                result = node
                self.nodes.remove(result)
                break
        del self.id_to_node[result.anchor]
        return result

    def pushNode(self, node):
        self.nodes.append(node)
        self.id_to_node[node.anchor] = node

    def mergeAnimatorControllers(self, ctrl0, ctrl1):
        ctrl0 = copy.deepcopy(ctrl0)
        ctrl1 = copy.deepcopy(ctrl1)

        self.id_mapping0 = {}
        self.id_mapping1 = {}

        p0 = ctrl0.mapping['AnimatorController'].mapping['m_AnimatorParameters']
        p1 = ctrl1.mapping['AnimatorController'].mapping['m_AnimatorParameters']

        a0 = ctrl0.mapping['AnimatorController'].mapping['m_AnimatorLayers']
        a1 = ctrl1.mapping['AnimatorController'].mapping['m_AnimatorLayers']

        self.id_mapping = self.id_mapping0
        p0.forEach(self.mergeIterator)
        a0.forEach(self.mergeIterator)

        # Hack to prevent ctrl1 from getting a new ID for the animator.
        del self.class_to_next_id['91']

        self.id_mapping = self.id_mapping1
        p1.forEach(self.mergeIterator)
        a1.forEach(self.mergeIterator)

        p0.sequence += p1.sequence
        a0.sequence += a1.sequence

        return ctrl0

    def merge(self, other):
        # Mapping from class ID (string) to next ID (int)
        self.class_to_next_id = {}

        ctrl0 = self.popNodeOfClass('91')
        ctrl1 = other.popNodeOfClass('91')
        merged_anim = self.mergeAnimatorControllers(ctrl0, ctrl1)

        # Mapping from class ID (string) to new class ID (int)
        self.id_mapping = self.id_mapping0
        for node in self.nodes:
            new_id = self.getUniqueId(node.anchor)
            node.anchor = str(new_id)
            node.forEach(self.mergeIterator)

        self.id_mapping = self.id_mapping1
        for node in other.nodes:
            new_id = self.getUniqueId(node.anchor)
            node.anchor = str(new_id)
            node.forEach(self.mergeIterator)

        nodes = self.nodes
        self.nodes = []
        self.id_to_node = {}
        self.pushNode(merged_anim)
        self.addNodes(nodes)
        self.addNodes(other.nodes)

def unityAnimatorToString(nodes):
    lines = []
    preamble = """
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
"""[1:][:-1]
    lines.append(preamble)
    for doc in nodes:
        lines.append("--- !u!" + doc.classId() + " &" + doc.anchor)
        lines.append(str(doc))
    result = '\n'.join(lines)

    for i in range(0,10):
        result = result.replace("\n\n", "\n")

    return result

class UnityParser:
    STREAM_START = 100
    STREAM_END = 199

    DOCUMENT_START = 200
    DOCUMENT_END = 299

    MAPPING_START = 300
    MAPPING_KEY = 301

    SEQUENCE_VALUE = 400

    def __init__(self):
        self.state = self.STREAM_START
        self.cur_scalar = None
        self.cur_node = None

        # Simple list of parsed documents. Populated by parse().
        self.nodes = []
        self.prev_states = []

    def __str__(self):
        return unityAnimatorToString(self.nodes)

    def pushState(self, state):
        self.prev_states.append(self.state)
        self.state = state
        #print("state {} ({})".format(self.state, len(self.prev_states)))

    def popState(self):
        self.state = self.prev_states[-1]
        self.prev_states = self.prev_states[0:len(self.prev_states) - 1]
        #print("state {} ({})".format(self.state, len(self.prev_states)))
        return self.state

    def cleanYaml(self, yaml_str):
        lines = []
        first_document = True
        for line in yaml_str.split("\n"):
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
        return '\n'.join(lines)

    def parse(self, yaml_file):
        yaml_str = ""
        with open(yaml_file, "r") as f:
            yaml_str = f.read()
        yaml_str = self.cleanYaml(yaml_str)

        for event in yaml.parse(yaml_str):
            if isinstance(event, yaml.StreamStartEvent):
                if len(self.prev_states) > 0:
                    raise Exception("Multiple StreamStartEvents received")
                self.pushState(self.STREAM_START)

            elif isinstance(event, yaml.StreamEndEvent):
                if self.state != self.STREAM_START:
                    raise Exception("Document end received after state {}".format(self.state))
                self.popState()
                if len(self.prev_states) > 0:
                    raise Exception("Extra states at stream end")

            elif isinstance(event, yaml.DocumentStartEvent):
                if self.state != self.STREAM_START and self.state != self.DOCUMENT_END:
                    raise Exception("Document start received after state {}".format(self.state))
                self.pushState(self.DOCUMENT_START)

            elif isinstance(event, yaml.DocumentEndEvent):
                if self.state != self.DOCUMENT_START:
                    raise Exception("Document end received after state {}".format(self.state))
                self.popState()
                self.nodes.append(self.cur_node)
                self.cur_node = None

            elif isinstance(event, yaml.MappingStartEvent):
                if self.cur_node == None:
                    self.cur_node = UnityDocument()
                    self.cur_node.anchor = event.anchor
                else:
                    self.cur_node = self.cur_node.addChildMapping(self.cur_scalar)
                self.pushState(self.MAPPING_START)

            elif isinstance(event, yaml.MappingEndEvent):
                if self.state != self.MAPPING_START:
                    raise Exception("Mapping end received after state {}".format(self.state))
                self.popState()
                if self.state == self.MAPPING_KEY:
                    self.popState()
                if self.cur_node.parent != None:
                    self.cur_node = self.cur_node.parent

            elif isinstance(event, yaml.SequenceStartEvent):
                self.cur_node = self.cur_node.addChildSequence(self.cur_scalar)
                self.pushState(self.SEQUENCE_VALUE)

            elif isinstance(event, yaml.SequenceEndEvent):
                if self.state != self.SEQUENCE_VALUE:
                    raise Exception("Sequence end received after state {}".format(self.state))
                self.popState()
                if self.state == self.MAPPING_KEY:
                    self.popState()
                self.cur_node = self.cur_node.parent

            elif isinstance(event, yaml.ScalarEvent):
                if self.state == self.MAPPING_START:
                    self.cur_scalar = event.value
                    self.pushState(self.MAPPING_KEY)
                elif self.state == self.MAPPING_KEY:
                    self.cur_node.mapping[self.cur_scalar] = event.value
                    self.popState()
                elif self.state == self.SEQUENCE_VALUE:
                    self.cur_node.sequence.append(event.value)
                else:
                    raise Exception("Scalar event received after state {}".format(self.state))
            else:
                raise Exception("Unhandled event {}".format(event))
            continue

if __name__ == "__main__":

    arg0 = "../FX.controller"
    print("Parsing {}".format(arg0), file=sys.stderr)
    parser0 = UnityParser()
    try:
        parser0.parse(arg0)
    except Exception as e:
        print("exception: {}".format(e))

    anim0 = UnityAnimator()
    anim0.addNodes(parser0.nodes)

    arg1 = "TaSTT_fx.controller"
    print("Parsing {}".format(arg1), file=sys.stderr)
    parser1 = UnityParser()
    try:
        parser1.parse(arg1)
    except Exception as e:
        print("exception: {}".format(e))

    anim1 = UnityAnimator()
    anim1.addNodes(parser1.nodes)

    #anim1.nodes = []
    #anim1.id_to_node = {}
    print("Merging animators", file=sys.stderr)
    anim0.merge(anim1)

    #print(unityAnimatorToString(parser0.nodes))
    print("Serializing", file=sys.stderr)
    print(unityAnimatorToString(anim0.nodes))

