#!/usr/bin/env python3

import argparse
import copy
import enum
import math
import os
import pickle
import random
import sys
# python3 -m pip install pyyaml
import yaml

import multiprocessing as mp

WRITE_DEFAULTS_ANIM_TEMPLATE = """
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!74 &7400000
AnimationClip:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: TaSTT_Reset_Animations
  serializedVersion: 6
  m_Legacy: 0
  m_Compressed: 0
  m_UseHighQualityCurve: 1
  m_RotationCurves: []
  m_CompressedRotationCurves: []
  m_EulerCurves: []
  m_PositionCurves: []
  m_ScaleCurves: []
  m_FloatCurves:
  - curve:
      serializedVersion: 2
      m_Curve:
      - serializedVersion: 3
        time: 0
        value: 0
        inSlope: 0
        outSlope: 0
        tangentMode: 136
        weightedMode: 0
        inWeight: 0
        outWeight: 0
      m_PreInfinity: 2
      m_PostInfinity: 2
      m_RotationOrder: 4
    attribute: REPLACEME_ATTRIBUTE
    path: REPLACEME_PATH
    classID: 137
    script: {fileID: 0}
  m_PPtrCurves: []
  m_SampleRate: 60
  m_WrapMode: 0
  m_Bounds:
    m_Center: {x: 0, y: 0, z: 0}
    m_Extent: {x: 0, y: 0, z: 0}
  m_ClipBindingConstant:
    genericBindings:
    - serializedVersion: 2
      path: 2794480623
      attribute: 2284639795
      script: {fileID: 0}
      typeID: 137
      customType: 22
      isPPtrCurve: 0
    pptrCurveMapping: []
  m_AnimationClipSettings:
    serializedVersion: 2
    m_AdditiveReferencePoseClip: {fileID: 0}
    m_AdditiveReferencePoseTime: 0
    m_StartTime: 0
    m_StopTime: 0
    m_OrientationOffsetY: 0
    m_Level: 0
    m_CycleOffset: 0
    m_HasAdditiveReferencePose: 0
    m_LoopTime: 1
    m_LoopBlend: 0
    m_LoopBlendOrientation: 0
    m_LoopBlendPositionY: 0
    m_LoopBlendPositionXZ: 0
    m_KeepOriginalOrientation: 0
    m_KeepOriginalPositionY: 1
    m_KeepOriginalPositionXZ: 0
    m_HeightFromFeet: 0
    m_Mirror: 0
  m_EditorCurves:
  - curve:
      serializedVersion: 2
      m_Curve:
      - serializedVersion: 3
        time: 0
        value: 0
        inSlope: 0
        outSlope: 0
        tangentMode: 136
        weightedMode: 0
        inWeight: 0
        outWeight: 0
      m_PreInfinity: 2
      m_PostInfinity: 2
      m_RotationOrder: 4
    attribute: REPLACEME_ATTRIBUTE
    path: REPLACEME_PATH
    classID: 137
    script: {fileID: 0}
  m_EulerEditorCurves: []
  m_HasGenericRootTransform: 0
  m_HasMotionFloatCurves: 0
  m_Events: []
"""[1:][:-1]

METADATA_TEMPLATE = """
fileFormatVersion: 2
guid: REPLACEME_GUID
NativeFormatImporter:
  externalObjects: {}
  mainObjectFileID: 7400000
  userData:
  assetBundleName:
  assetBundleVariant: 
"""[1:][:-1]

ANIMATION_STATE_TEMPLATE = """
--- !u!1102 &110200000
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: REPLACEME_ANIMATION_NAME
  m_Speed: 1
  m_CycleOffset: 0
  m_Transitions: []
  m_StateMachineBehaviours: []
  m_Position: {x: 50, y: 50, z: 0}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 0
  m_Mirror: 0
  m_SpeedParameterActive: 0
  m_MirrorParameterActive: 0
  m_CycleOffsetParameterActive: 0
  m_TimeParameterActive: 0
  m_Motion: {fileID: 7400000, guid: REPLACEME_ANIMATION_GUID, type: 2}
  m_Tag: 
  m_SpeedParameter: 
  m_MirrorParameter: 
  m_CycleOffsetParameter: 
  m_TimeParameter: 
"""[1:][:-1]

TRANSITION_TEMPLATE = """
--- !u!1101 &110100000
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions: []
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: 0}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0
  m_TransitionOffset: 0
  m_ExitTime: 1.0
  m_HasExitTime: 1
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
"""[1:][:-1]

class Metadata:
    def __init__(self):
        self.guid = "%032x" % random.randrange(16 ** 32)

    def load(self, path):
        if not path.endswith(".meta"):
            path = path + ".meta"

        self.guid = None
        with open(path, "r") as f:
            for line in f:
                if line.startswith("guid"):
                    self.guid = line.split()[1]

    def __str__(self):
        return METADATA_TEMPLATE.replace("REPLACEME_GUID", self.guid)

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

    def copy(self):
        new = Sequence()
        new.anchor = self.anchor
        new.parent = self.parent

        for v in self.sequence:
            if hasattr(v, "copy"):
                new.sequence.append(v.copy())
                new.sequence[-1].parent = new
            else:
                new.sequence.append(v)

        return new

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

    def addChildMapping(self, anchor = None, add_to_head = False):
        child = Mapping()
        child.anchor = anchor
        child.parent = self
        child.sequence = []

        if add_to_head:
            self.sequence = [child] + self.sequence
        else:
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

    def copy(self):
        new = Mapping()
        new.anchor = self.anchor
        new.parent = self.parent

        for k, v in self.mapping.items():
            if hasattr(v, "copy"):
                new.mapping[k] = v.copy()
                new.mapping[k].parent = new
            else:
                new.mapping[k] = v

        return new

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

        # Empty mappings are represented by '{}'. If we don't do this, Unity
        # will assume that they are Sequences and get very sad.
        if len(self.mapping.keys()) == 0:
            return "{}"

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

# Class representing a Unity AnimatorController. Implements manipulations, like
# merging and reanchoring.
class UnityAnimator():
    def __init__(self):
        self.nodes = []
        self.id_to_node = {}
        self.class_to_next_id = {}

    def __str__(self):
        return unityAnimatorToString(self.nodes)

    def addNodes(self, nodes):
        for node in nodes:
            self.nodes.append(node)
            anchor = node.anchor
            if anchor == None:
                raise Exception("Node is missing anchor: {}".format(str(node)))
            if anchor in self.id_to_node:
                raise Exception("Duplicate anchor: {}, node 1: {}, node 2: {}".format(anchor, str(node), str(self.id_to_node[anchor])))
            self.id_to_node[anchor] = node

            if classId(anchor) in self.class_to_next_id:
                cur_next = self.class_to_next_id[classId(anchor)]
                self.class_to_next_id[classId(anchor)] = max(int(anchor), cur_next)
            else:
                self.class_to_next_id[classId(anchor)] = int(anchor)

        for k in self.class_to_next_id.keys():
            self.class_to_next_id[k] += 1

    def allocateId(self, class_id):
        new_id = None
        if class_id in self.class_to_next_id:
            new_id = self.class_to_next_id[class_id]
            self.class_to_next_id[class_id] += 1
        else:
            new_id = int("%s%05d" % (class_id, 0))
            next_id = new_id + 1
            self.class_to_next_id[class_id] = next_id

        return new_id

    def getUniqueId(self, anchor):
        # For whatever reason, generating a new ID for the MonoBehaviour
        # embedded in VRChat's default animation ctrler makes Unity spit out
        # warnings. Reuse the old one.
        if classId(anchor) == "114":
            return int(anchor)

        if anchor in self.id_mapping.keys():
            return self.id_mapping[anchor]

        new_id = self.allocateId(classId(anchor))
        self.id_mapping[anchor] = new_id
        return new_id

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

    def peekNodeOfClass(self, classId):
        for node in self.nodes:
            if node.classId() == classId:
                return node
        return None

    def popNodeOfClass(self, classId):
        result = None
        for node in self.nodes:
            if node.classId() == classId:
                result = node
                self.nodes.remove(result)
                break
        if result:
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

    # TODO(yum) support overwriting duplicates
    def addParameter(self, param_name, param_type):
        unity_type = None
        if param_type == float:
            unity_type = '1'
        elif param_type == int:
            unity_type = '3'
        elif param_type == bool:
            unity_type = '4'
        anim = self.peekNodeOfClass('91')
        params = anim.mapping['AnimatorController'].mapping['m_AnimatorParameters']
        param = params.addChildMapping()
        param.mapping['m_Name'] = param_name
        param.mapping['m_Type'] = unity_type
        param.mapping['m_DefaultFloat'] = '0'
        param.mapping['m_DefaultInt'] = '0'
        param.mapping['m_DefaultBool'] = '0'
        ctrl = param.addChildMapping('m_Controller')
        ctrl.mapping['fileID'] = anim.anchor

    def addLayer(self, layer_name, add_to_head = False):
        # Add layer to controller
        anim = self.peekNodeOfClass('91')
        layers = anim.mapping['AnimatorController'].mapping['m_AnimatorLayers']
        layer = layers.addChildMapping(add_to_head = add_to_head)
        layer.mapping['serializedVersion'] = '5'
        layer.mapping['m_Name'] = layer_name
        new_id = self.allocateId('1107')
        layer.addChildMapping('m_StateMachine').mapping['fileID'] = str(new_id)
        layer.addChildMapping('m_Mask').mapping['fileID'] = '0'
        layer.addChildSequence('m_Motions')
        layer.addChildSequence('m_Behaviours')
        layer.mapping['m_BlendingMode'] = '0'
        layer.mapping['m_SyncedLayerIndex'] = '-1'
        layer.mapping['m_DefaultWeight'] = '1'
        layer.mapping['m_IKPass'] = '0'
        layer.mapping['m_SyncedLayerAffectsTiming'] = '0'
        layer.addChildMapping('m_Controller').mapping['fileID'] = anim.anchor

        # Create layer object
        layer = UnityDocument()
        layer.anchor = str(new_id)
        mach = layer.addChildMapping('AnimatorStateMachine')

        mach.mapping['serializedVersion'] = '6'

        mach.mapping['m_ObjectHideFlags'] = '1'
        mach.addChildMapping('m_CorrespondingSourceObject').mapping['fileID'] = '0'
        mach.addChildMapping('m_PrefabInstance').mapping['fileID'] = '0'
        mach.addChildMapping('m_PrefabAsset').mapping['fileID'] = '0'
        mach.mapping['m_Name'] = layer_name
        mach.addChildSequence('m_ChildStates')
        mach.addChildSequence('m_ChildStateMachines')
        mach.addChildSequence('m_AnyStateTransitions')
        mach.addChildSequence('m_EntryTransitions')
        mach.addChildMapping('m_StateMachineTransitions')
        mach.addChildSequence('m_StateMachineBehaviours')
        pos = mach.addChildMapping('m_AnyStatePosition')
        pos.mapping['x'] = '50'
        pos.mapping['y'] = '20'
        pos.mapping['z'] = '0'
        pos = mach.addChildMapping('m_EntryPosition')
        pos.mapping['x'] = '50'
        pos.mapping['y'] = '120'
        pos.mapping['z'] = '0'
        pos = mach.addChildMapping('m_ExitPosition')
        pos.mapping['x'] = '800'
        pos.mapping['y'] = '120'
        pos.mapping['z'] = '0'
        pos = mach.addChildMapping('m_ParentStateMachinePosition')
        pos.mapping['x'] = '800'
        pos.mapping['y'] = '20'
        pos.mapping['z'] = '0'
        mach.addChildMapping('m_DefaultState')

        self.nodes.append(layer)
        return layer

    def addAnimatorState(self, layer, state_name, is_default_state = False):
        # Create animation state
        parser = UnityParser()
        parser.parse(ANIMATION_STATE_TEMPLATE)
        new_anim = UnityAnimator()
        new_anim.addNodes(parser.nodes)
        node = new_anim.nodes[0]

        new_id = self.allocateId('1102')
        node.anchor = str(new_id)
        state = node.mapping['AnimatorState']
        state.mapping['m_Name'] = state_name
        #state.mapping['m_Motion'].mapping['guid'] = anim_guid
        self.nodes.append(node)

        # Add state to layer
        child_state = layer.mapping['AnimatorStateMachine'].mapping['m_ChildStates'].addChildMapping()
        child_state.mapping['serializedVersion'] = '1'
        child_state.addChildMapping('m_State').mapping['fileID'] = str(new_id)
        state_pos = child_state.addChildMapping('m_Position')
        state_pos.mapping['x'] = '280'
        state_pos.mapping['y'] = '80'
        state_pos.mapping['z'] = '0'

        if is_default_state:
            layer.mapping['AnimatorStateMachine'].mapping['m_DefaultState'].mapping['fileID'] = str(new_id)

        return node

    def setAnimatorStateAnimation(self, anim_state, anim_guid):
        anim_state.mapping['AnimatorState'].mapping['m_Motion'].mapping['guid'] = anim_guid

    def addTransition(self, dst_state_id):
        # Create animation state
        parser = UnityParser()
        parser.parse(TRANSITION_TEMPLATE)
        new_transition = UnityAnimator()
        new_transition.addNodes(parser.nodes)
        node = new_transition.nodes[0]

        new_id = self.allocateId('1101')
        node.anchor = str(new_id)
        state = node.mapping['AnimatorStateTransition']
        state.mapping['m_DstState'].mapping['fileID'] = dst_state_id
        self.nodes.append(node)

        return node

    def fixWriteDefaults(self, guid_map, generated_anim_path):
        # TODO(yum) we should have an Animation class which encapsulates all
        # this stuff.
        parser = UnityParser()
        parser.parse(WRITE_DEFAULTS_ANIM_TEMPLATE)
        new_anim = UnityAnimator()
        new_anim.addNodes(parser.nodes)

        new_clip = new_anim.peekNodeOfClass('74').mapping['AnimationClip']
        curve_template = new_clip.mapping['m_FloatCurves'].sequence[0]
        new_clip.mapping['m_FloatCurves'].sequence = []
        new_clip.mapping['m_EditorCurves'].sequence = []

        # Keep track of the (attribute, path) tuples we've already set to avoid
        # animating the same thing twice.
        attributes_set = set()

        animator_state_id = '1102'
        for node in self.nodes:
            if node.classId() != animator_state_id:
                continue

            # Looking at an animator state.
            if node.mapping['AnimatorState'].mapping['m_WriteDefaultValues'] != '1':
                continue

            # Disable write defaults.
            node.mapping['AnimatorState'].mapping['m_WriteDefaultValues'] = '0'

            # Looking at an animator state with write defaults.
            motion = node.mapping['AnimatorState'].mapping['m_Motion']
            # Some animations have write defaults but don't trigger an
            # animation. No idea what that's about. For now, just ignore.
            if not 'guid' in motion.mapping:
                continue
            guid = motion.mapping['guid']

            # Again, not really sure what's going on here, just ignore and
            # revisit if we hit problems.
            if not guid in guid_map.keys():
                continue

            # OK, we found an animation with write defaults, and we know where
            # the animation lives. Crack it open and see what it's writing.
            animation_path = guid_map[guid]
            print("Animation has write defaults: {}".format(animation_path), file=sys.stderr)
            parser = UnityParser()
            parser.parseFile(animation_path)
            anim = UnityAnimator()
            anim.addNodes(parser.nodes)

            clip = anim.peekNodeOfClass('74')

            for curve in clip.mapping['AnimationClip'].mapping['m_FloatCurves'].sequence:
                attr = curve.mapping['attribute']
                path = curve.mapping['path']
                if (attr, path) in attributes_set:
                    continue
                #print("Fix attr/path {}/{}".format(attr, path), file=sys.stderr)
                attributes_set.add((attr, path))

                new_curve = curve_template.copy()
                new_curve.mapping['attribute'] = attr
                new_curve.mapping['path'] = path

                new_clip.mapping['m_FloatCurves'].sequence.append(new_curve)
                new_clip.mapping['m_EditorCurves'].sequence.append(new_curve)

                #print("len float curves: {}".format(len(new_clip.mapping['m_FloatCurves'].sequence)), file=sys.stderr)

        #print("generated animation: {}".format(str(new_anim)), file=sys.stderr)
        with open(generated_anim_path, "w") as f:
            f.write(str(new_anim))

        meta = Metadata()
        with open(generated_anim_path + ".meta", "w") as f:
            f.write(str(meta))

        # OK, we have an animation and a GUID. Let's generate a layer now.
        layer = self.addLayer('TaSTT_Reset_Animations', add_to_head = True)

        reset_left_state = self.addAnimatorState(layer, 'TaSTT_Reset_Animations_Left')
        self.setAnimatorStateAnimation(reset_left_state, meta.guid)
        reset_right_state = self.addAnimatorState(layer, 'TaSTT_Reset_Animations_Right')
        self.setAnimatorStateAnimation(reset_right_state, meta.guid)

        # Add noop state
        noop_state = self.addAnimatorState(layer, 'TaSTT_Reset_Animations_Noop', is_default_state = True)
        noop_anim_meta = Metadata()
        noop_anim_meta.load('Animations/TaSTT_Do_Nothing.anim')
        self.setAnimatorStateAnimation(noop_state, noop_anim_meta.guid)
        noop_trans = self.addTransition(noop_state.anchor)
        self.addTransitionIntegerGreaterCondition(None, noop_trans,
                'GestureLeft', 0)
        self.addTransitionIntegerGreaterCondition(None, noop_trans,
                'GestureRight', 0)
        tmp_trans = layer.mapping['AnimatorStateMachine'].mapping['m_AnyStateTransitions'].addChildMapping()
        tmp_trans.mapping['fileID'] = noop_trans.anchor

        # Create any state transitions to the animated
        # states. When Gesture{Left,Right} is 0 in either hand, AKA no gesture
        # is being used, we fire the animation.
        left_trans = self.addTransition(reset_left_state.anchor)
        self.addTransitionIntegerEqualityCondition(None, left_trans,
                'GestureLeft', 0)
        tmp_trans = layer.mapping['AnimatorStateMachine'].mapping['m_AnyStateTransitions'].addChildMapping()
        tmp_trans.mapping['fileID'] = left_trans.anchor

        right_trans = self.addTransition(reset_right_state.anchor)
        self.addTransitionIntegerEqualityCondition(None, right_trans,
                'GestureRight', 0)
        tmp_trans = layer.mapping['AnimatorStateMachine'].mapping['m_AnyStateTransitions'].addChildMapping()
        tmp_trans.mapping['fileID'] = right_trans.anchor

    def addTransitionBooleanCondition(self, from_state, trans, param, branch):
        # Populate the transition's condition logic.
        cond = trans.mapping['AnimatorStateTransition'].mapping['m_Conditions'].addChildMapping()
        if branch:
            cond.mapping['m_ConditionMode'] = '1'
        else:
            cond.mapping['m_ConditionMode'] = '2'
        cond.mapping['m_ConditionEvent'] = param
        cond.mapping['m_EventThreshold'] = '0'
        # Register the transition with the `from_state`.
        if from_state:
            from_state_trans = from_state.mapping['AnimatorState'].mapping['m_Transitions'].addChildMapping()
            from_state_trans.mapping['fileID'] = trans.anchor

    def addTransitionIntegerEqualityCondition(self, from_state, trans, param, param_val):
        # Populate the transition's condition logic.
        cond = trans.mapping['AnimatorStateTransition'].mapping['m_Conditions'].addChildMapping()
        cond.mapping['m_ConditionMode'] = '6'
        cond.mapping['m_ConditionEvent'] = param
        cond.mapping['m_EventThreshold'] = str(param_val)
        # Register the transition with the `from_state`.
        if from_state:
            from_state_trans = from_state.mapping['AnimatorState'].mapping['m_Transitions'].addChildMapping()
            from_state_trans.mapping['fileID'] = trans.anchor

    def addTransitionIntegerGreaterCondition(self, from_state, trans, param, param_val):
        # Populate the transition's condition logic.
        cond = trans.mapping['AnimatorStateTransition'].mapping['m_Conditions'].addChildMapping()
        cond.mapping['m_ConditionMode'] = '3'
        cond.mapping['m_ConditionEvent'] = param
        cond.mapping['m_EventThreshold'] = str(param_val)
        # Register the transition with the `from_state`.
        if from_state:
            from_state_trans = from_state.mapping['AnimatorState'].mapping['m_Transitions'].addChildMapping()
            from_state_trans.mapping['fileID'] = trans.anchor

    # TODO(yum) this should be factored out into generate_fx.py
    def addTasttToggle(self, off_anim_path, on_anim_path, toggle_param):
        self.addParameter(toggle_param, bool)

        off_anim_meta = Metadata()
        off_anim_meta.load(off_anim_path)

        on_anim_meta = Metadata()
        on_anim_meta.load(on_anim_path)

        layer = self.addLayer('TaSTT_Toggle')
        off_anim = self.addAnimatorState(layer, 'TaSTT_Toggle_Off', is_default_state = True)
        self.setAnimatorStateAnimation(off_anim, off_anim_meta.guid)
        on_anim = self.addAnimatorState(layer, 'TaSTT_Toggle_On')
        self.setAnimatorStateAnimation(on_anim, on_anim_meta.guid)

        # TODO(yum) make a Transition class with methods for adding boolean
        # conditions
        off_to_on = self.addTransition(on_anim.anchor)
        self.addTransitionBooleanCondition(off_anim, off_to_on, toggle_param, True)

        on_to_off = self.addTransition(off_anim.anchor)
        self.addTransitionBooleanCondition(on_anim, on_to_off, toggle_param, False)

    def setNoopAnimations(self, guid_map, noop_anim_path):
        noop_anim_meta = Metadata()
        noop_anim_meta.load(noop_anim_path)

        for node in self.nodes:
            if classId(node.anchor) != "1102":
                continue
            motion = node.mapping['AnimatorState'].mapping['m_Motion']
            replace = False
            if not "guid" in motion.mapping.keys():
                replace = True
            elif not motion.mapping["guid"] in guid_map:
                replace = True
            if not replace:
                continue
            motion.mapping["fileID"] = "7400000"
            motion.mapping["guid"] = noop_anim_meta.guid
            motion.mapping["type"] = "2"

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
        got_document = False
        for line in yaml_str.split("\n"):
            # Add end-of-document indicators.
            if line.startswith("---"):
                got_document = True
                if not first_document:
                    lines.append("...\n")
                first_document = False

            # Remove class ID tag from each block.
            if line.startswith("---"):
                parts = line.split()
                lines.append(parts[0] + " " + parts[2] + "\n")
                continue
            lines.append(line)

        if got_document:
            lines.append("...\n")
        return '\n'.join(lines)

    def parseFile(self, yaml_file):
        yaml_str = ""
        with open(yaml_file, "r") as f:
            yaml_str = f.read()
        return self.parse(yaml_str)

    def parse(self, yaml_str):
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

class MulticoreUnityParser:
    def parseFile(self, yaml_file):
        yaml_str = ""
        with open(yaml_file, "r") as f:
            yaml_str = f.read()
        return self.parse(yaml_str)

    def parse(self, yaml_str):
        lines = []
        documents = []
        first = True
        n_lines = 0
        for line in yaml_str.split("\n"):
            n_lines += 1
            if line.startswith("---"):
                if not first:
                    documents.append("\n".join(lines))
                    lines = []
                first = False
            lines.append(line)
        if len(lines) > 0:
            documents.append("\n".join(lines))
            lines = []
        print("Got {} documents out of {} lines".format(len(documents), n_lines), file=sys.stderr)

        # Divide the work evenly among the # of CPUs we have available.
        n_threads = os.cpu_count()
        window_size = int(math.ceil(len(documents) / n_threads))
        merge_window = []
        merged_documents = []
        for i in range(0, len(documents)):
            if i > 0 and i % window_size == 0:
                merged_documents.append("\n".join(merge_window))
                merge_window = []
            merge_window.append(documents[i])
        if len(merge_window) > 0:
            merged_documents.append("\n".join(merge_window))
            merge_window = []
        documents = merged_documents

        mgr = mp.Manager()

        print("Spawning {} threads".format(len(documents)), file=sys.stderr)
        threads = []
        for document in documents:
            res = mgr.dict()
            thread = mp.Process(target = self.parseOneSerial, args = (document, res,))
            threads.append((thread, res))
            thread.start()

        print("Joining threads", file=sys.stderr)
        nodes = []
        for thread, res in threads:
            thread.join()
            nodes += res['nodes']

        print("Creating animator", file=sys.stderr)
        result = UnityAnimator()
        result.addNodes(nodes)

        return result

    def parseOneSerial(self, document, res):
        parser = UnityParser()
        parser.parse(document)
        res['nodes'] = parser.nodes

    def parseFile(self, yaml_file):
        yaml_str = ""
        with open(yaml_file, "r") as f:
            yaml_str = f.read()
        return self.parse(yaml_str)

def getGuidMap(d):
    result = {}
    for f in os.scandir(d):
        path = f.path
        if f.is_dir():
            result.update(getGuidMap(path))
        if not f.is_file():
            continue
        suffix = ".meta"
        if path.endswith(suffix):
            with open(path, "r") as f:
                for line in f:
                    if line.startswith("guid"):
                        guid = line.split()[1]
                        result[guid] = path[:-len(suffix)]
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", type=str, help="One of merge, guid_map, fix_write_defaults")
    parser.add_argument("--fx0", type=str, help="The first animator to merge")
    parser.add_argument("--fx1", type=str, help="The second animator to merge")
    parser.add_argument("--project_root", type=str, help="The path to the " +
            "Unity project Assets folder")
    parser.add_argument("--save_to", type=str, help="The path to save the " +
            "result of the computation")
    parser.add_argument("--guid_map", type=str, help="Path to guid.map, " +
            "generated by a previous call to `guid_map`")
    args = parser.parse_args()

    if args.cmd == "merge":
        if not args.fx0 or not args.fx1:
            print("--fx0 and --fx1 required", file=sys.stderr)
            parser.print_help()
            parser.exit(1)

        print("Parsing {}".format(args.fx0), file=sys.stderr)
        parser0 = MulticoreUnityParser()
        anim0 = parser0.parseFile(args.fx0)

        arg1 = "TaSTT_fx.controller"
        print("Parsing {}".format(args.fx1), file=sys.stderr)
        parser1 = MulticoreUnityParser()
        anim1 = parser1.parseFile(args.fx1)

        print("Merging animators", file=sys.stderr)
        anim0.merge(anim1)

        print("Serializing", file=sys.stderr)
        print(unityAnimatorToString(anim0.nodes))
    elif args.cmd == "guid_map":
        if not args.project_root or not args.save_to:
            print("--project_root and --save_to required")
            parser.print_help()
            parser.exit(1)

        print("Looking up GUIDs under {}".format(args.project_root),
                file=sys.stderr)
        guid_map = getGuidMap(args.project_root)
        print("Saving to {}".format(args.save_to), file=sys.stderr)
        with open(args.save_to, 'wb') as f:
            pickle.dump(guid_map, f)
    elif args.cmd == "fix_write_defaults":
        if not args.fx0 or not args.guid_map:
            print("--fx0 and --guid_map required")
            parser.print_help()
            parser.exit(1)

        guid_map = {}
        with open(args.guid_map, 'rb') as f:
            guid_map = pickle.load(f)

        print("Parsing {}".format(args.fx0), file=sys.stderr)
        parser0 = MulticoreUnityParser()
        anim = parser0.parseFile(args.fx0)

        print("Fixing write defaults", file=sys.stderr)
        anim.fixWriteDefaults(guid_map, "generated/animations/TaSTT_Reset_Animation.anim")
        print(str(anim))

    elif args.cmd == "add_toggle":
        if not args.fx0:
            print("--fx0 required")
            parser.print_help()
            parser.exit(1)

        print("Parsing {}".format(args.fx0), file=sys.stderr)
        parser0 = MulticoreUnityParser()
        anim = parser0.parseFile(args.fx0)

        print("Adding toggle", file=sys.stderr)
        anim.addTasttToggle("Animations/TaSTT_Toggle_Off.anim",
                "Animations/TaSTT_Toggle_On.anim", "TaSTT_Toggle")
        print(str(anim))

    elif args.cmd == "fast_parse_test":
        if not args.fx0:
            print("--fx0 required")
            parser.print_help()
            parser.exit(1)

        print("Parsing {}".format(args.fx0), file=sys.stderr)
        parser0 = MulticoreUnityParser()
        anim = parser0.parseFile(args.fx0)
        print(str(anim))

    elif args.cmd == "set_noop_anim":
        if not args.fx0 or not args.guid_map:
            print("--fx0 and --guid_map required")
            parser.print_help()
            parser.exit(1)

        guid_map = {}
        with open(args.guid_map, 'rb') as f:
            guid_map = pickle.load(f)

        print("Parsing {}".format(args.fx0), file=sys.stderr)
        parser = MulticoreUnityParser()
        anim = parser.parseFile(args.fx0)

        anim.setNoopAnimations(guid_map, "Animations/TaSTT_Do_Nothing.anim")

        print(str(anim))

    else:
        print("Unrecognized command: {}".format(args.cmd))

