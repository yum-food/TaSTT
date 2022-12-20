#!/usr/bin/env python3

import argparse
import generate_utils
import libunity
import os
import pickle
import sys
import typing

# TODO(yum) we're getting the encoding scheme from here, but I think it should
# be in a different layer.
import osc_ctrl

LETTER_ANIMATION_TEMPLATE = """
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!74 &7400000
AnimationClip:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: REPLACEME_ANIMATION_NAME
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
        value: REPLACEME_LETTER_VALUE
        inSlope: 0
        outSlope: 0
        tangentMode: 136
        weightedMode: 0
        inWeight: 0
        outWeight: 0
      - serializedVersion: 3
        time: 0.016666668
        value: REPLACEME_LETTER_VALUE
        inSlope: 0
        outSlope: 0
        tangentMode: 136
        weightedMode: 0
        inWeight: 0
        outWeight: 0
      m_PreInfinity: 2
      m_PostInfinity: 2
      m_RotationOrder: 4
    attribute: material.REPLACEME_LETTER_PARAM
    path: TaSTT
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
        value: REPLACEME_LETTER_VALUE
        inSlope: 0
        outSlope: 0
        tangentMode: 136
        weightedMode: 0
        inWeight: 0
        outWeight: 0
      - serializedVersion: 3
        time: 0.016666668
        value: REPLACEME_LETTER_VALUE
        inSlope: 0
        outSlope: 0
        tangentMode: 136
        weightedMode: 0
        inWeight: 0
        outWeight: 0
      m_PreInfinity: 2
      m_PostInfinity: 2
      m_RotationOrder: 4
    attribute: material.REPLACEME_LETTER_PARAM
    path: TaSTT
    classID: 137
    script: {fileID: 0}
  m_EulerEditorCurves: []
  m_HasGenericRootTransform: 0
  m_HasMotionFloatCurves: 0
  m_Events: []
"""

ANIMATOR_TEMPLATE = """
--- !u!91 &9100000
AnimatorController:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: TaSTT_fx
  serializedVersion: 5
  m_AnimatorParameters: []
  m_AnimatorLayers: []
"""

# For whatever reason, running unrelated animations s.a.
# facial expressions can have a slight effect on supposedly
# unrelated parameters, causing letter to flip. Add a
# little buffer to reduce the odds that this effect causes
# a letter to change after it has been written.
UNITY_ANIMATION_FUDGE_MARGIN = 0.1

def generateClearAnimation(anim_dir, guid_map):
    print("Generating board clearing animation", file=sys.stderr)

    parser = libunity.UnityParser()
    parser.parse(LETTER_ANIMATION_TEMPLATE)

    anim_node = parser.nodes[0]
    anim_clip = anim_node.mapping['AnimationClip']
    curve_template = anim_clip.mapping['m_FloatCurves'].sequence[0]
    anim_clip.mapping['m_FloatCurves'].sequence = []
    anim_clip.mapping['m_EditorCurves'].sequence = []

    letter = 0

    for byte in range(0, generate_utils.BYTES_PER_CHAR):
        for row in range(0, generate_utils.BOARD_ROWS):
            for col in range(0, generate_utils.BOARD_COLS):
                curve = curve_template.copy()
                for keyframe in curve.mapping['curve'].mapping['m_Curve'].sequence:
                    keyframe.mapping['value'] = str(letter +
                        UNITY_ANIMATION_FUDGE_MARGIN)
                    curve.mapping['attribute'] = "material.{}".format(generate_utils.getShaderParamByRowColByte(row, col, byte))
                    curve.mapping['path'] = "World Constraint/Container/TaSTT"
                # Add curve to animation
                anim_clip.mapping['m_FloatCurves'].sequence.append(curve)
                anim_clip.mapping['m_EditorCurves'].sequence.append(curve)
    # Serialize animation to file
    anim_name = generate_utils.getClearAnimationName()
    anim_path = os.path.join(anim_dir, anim_name + ".anim")
    print("Generating clear animation at {}".format(anim_path))
    with open(anim_path, "w") as f:
        f.write(libunity.unityYamlToString([anim_node]))
    # Generate metadata
    meta = libunity.Metadata()
    with open(anim_path + ".meta", "w") as f:
        f.write(str(meta))
    # Add metadata to guid map
    guid_map[anim_path] = meta.guid
    guid_map[meta.guid] = anim_path

# Generate a toggle animation for a shader parameter.
def generateToggleAnimations(anim_dir, shader_param, guid_map):
    print("Generating shader toggle animation", file=sys.stderr)

    parser = libunity.UnityParser()
    parser.parse(LETTER_ANIMATION_TEMPLATE)

    # 0.0 represents false, 1.0 represents true. Don't forget that we add
    # `UNITY_ANIMATION_FUDGE_MARGIN` to everything.
    for shader_value in range(0, 2):
        anim_node = parser.nodes[0]
        anim_clip = anim_node.mapping['AnimationClip']
        curve_template = anim_clip.mapping['m_FloatCurves'].sequence[0]
        anim_clip.mapping['m_FloatCurves'].sequence = []
        anim_clip.mapping['m_EditorCurves'].sequence = []

        curve = curve_template.copy()
        for keyframe in curve.mapping['curve'].mapping['m_Curve'].sequence:
            keyframe.mapping['value'] = str(float(shader_value) +
                UNITY_ANIMATION_FUDGE_MARGIN)
            curve.mapping['attribute'] = "material.{}".format(shader_param)
            curve.mapping['path'] = "World Constraint/Container/TaSTT"
        # Add curve to animation
        anim_clip.mapping['m_FloatCurves'].sequence.append(curve)
        anim_clip.mapping['m_EditorCurves'].sequence.append(curve)

        # Serialize animation to file
        anim_name = generate_utils.getClearAnimationName()
        anim_suffix = "_Off"
        if shader_value == 1:
            anim_suffix = "_On"
        anim_path = os.path.join(anim_dir, shader_param + anim_suffix +
                ".anim")
        with open(anim_path, "w") as f:
            f.write(libunity.unityYamlToString([anim_node]))
        # Generate metadata
        meta = libunity.Metadata()
        with open(anim_path + ".meta", "w") as f:
            f.write(str(meta))
        # Add metadata to guid map
        guid_map[anim_path] = meta.guid
        guid_map[meta.guid] = anim_path

# Generate a toggle animation for a shader parameter.
def generateFloatAnimation(anim_name: str, anim_dir: str,
        path: str, attribute: str,
        value: float,
        guid_map: typing.Dict[str, str]) -> str:
    print("Generating float toggle animation {}/{}".format(path,attribute),
            file=sys.stderr)

    parser = libunity.UnityParser()
    parser.parse(LETTER_ANIMATION_TEMPLATE)

    # 0.0 represents false, 1.0 represents true. Don't forget that we add
    # `UNITY_ANIMATION_FUDGE_MARGIN` to everything.
    anim_node = parser.nodes[0]
    anim_clip = anim_node.mapping['AnimationClip']
    curve_template = anim_clip.mapping['m_FloatCurves'].sequence[0]
    anim_clip.mapping['m_FloatCurves'].sequence = []
    anim_clip.mapping['m_EditorCurves'].sequence = []

    curve = curve_template.copy()
    for keyframe in curve.mapping['curve'].mapping['m_Curve'].sequence:
        keyframe.mapping['value'] = str(value)
        curve.mapping['attribute'] = attribute
        curve.mapping['path'] = path
    # Add curve to animation
    anim_clip.mapping['m_FloatCurves'].sequence.append(curve)
    anim_clip.mapping['m_EditorCurves'].sequence.append(curve)

    # Serialize animation to file
    anim_path = os.path.join(anim_dir, anim_name + ".anim")
    with open(anim_path, "w") as f:
        f.write(libunity.unityYamlToString([anim_node]))
    # Generate metadata
    meta = libunity.Metadata()
    with open(anim_path + ".meta", "w") as f:
        f.write(str(meta))
    # Add metadata to guid map
    guid_map[anim_path] = meta.guid
    guid_map[meta.guid] = anim_path

    return meta.guid

def generateAnimations(anim_dir, guid_map):
    generateClearAnimation(anim_dir, guid_map)

    generateToggleAnimations(anim_dir, generate_utils.getIndicator0Param(), guid_map)
    generateToggleAnimations(anim_dir, generate_utils.getIndicator1Param(), guid_map)

    print("Generating letter animations", file=sys.stderr)

    parser = libunity.UnityParser()
    parser.parse(LETTER_ANIMATION_TEMPLATE)

    anim_node = parser.nodes[0]
    anim_clip = anim_node.mapping['AnimationClip']
    curve_template = anim_clip.mapping['m_FloatCurves'].sequence[0]
    anim_clip.mapping['m_FloatCurves'].sequence = []
    anim_clip.mapping['m_EditorCurves'].sequence = []

    # To support more languages, we use 2 bytes per character, giving us a 64K character set.
    for byte in range(0, generate_utils.BYTES_PER_CHAR):
        for row in range(0, generate_utils.BOARD_ROWS):
            print("Generating letter animations (row {}/{}) (byte {}/2)".format(row,
                generate_utils.BOARD_ROWS, byte), file=sys.stderr)
            for col in range(0, generate_utils.BOARD_COLS):
                for letter in range(0, 2):
                    if letter == 1:
                        letter = generate_utils.CHARS_PER_CELL - 1

                    # Make a deep copy of the templates
                    node = anim_node.copy()
                    curve = curve_template.copy()
                    clip = node.mapping['AnimationClip']
                    # Populate animation name
                    anim_name = generate_utils.getLetterAnimationName(row, col, letter, byte)
                    clip.mapping['m_Name'] = anim_name
                    # Populate letter value
                    for keyframe in curve.mapping['curve'].mapping['m_Curve'].sequence:
                        keyframe.mapping['value'] = str(letter + UNITY_ANIMATION_FUDGE_MARGIN)
                    # Populate path to letter parameter
                    curve.mapping['attribute'] = "material.{}".format(generate_utils.getShaderParamByRowColByte(row, col, byte))
                    curve.mapping['path'] = "World Constraint/Container/TaSTT"
                    # Add curve to animation
                    clip.mapping['m_FloatCurves'].sequence.append(curve)
                    clip.mapping['m_EditorCurves'].sequence.append(curve)
                    # Serialize animation to file
                    anim_path = os.path.join(anim_dir, anim_name + ".anim")
                    with open(anim_path, "w") as f:
                        f.write(libunity.unityYamlToString([node]))
                    # Generate metadata
                    meta = libunity.Metadata()
                    with open(anim_path + ".meta", "w") as f:
                        f.write(str(meta))
                    # Add metadata to guid map
                    guid_map[anim_path] = meta.guid
                    guid_map[meta.guid] = anim_path

def generateFXController(anim: libunity.UnityAnimator) -> typing.Dict[int, libunity.UnityDocument]:
    parser = libunity.UnityParser()
    parser.parse(ANIMATOR_TEMPLATE)
    anim.addNodes(parser.nodes)

    anim.addParameter(generate_utils.getEnableParam(), bool)
    anim.addParameter(generate_utils.getDummyParam(), bool)
    anim.addParameter(generate_utils.getHipToggleParam(), bool)
    anim.addParameter(generate_utils.getHandToggleParam(), bool)
    anim.addParameter(generate_utils.getToggleParam(), bool)
    anim.addParameter(generate_utils.getSpeechNoiseEnableParam(), bool)
    anim.addParameter(generate_utils.getClearBoardParam(), bool)
    anim.addParameter(generate_utils.getIndicator0Param(), bool)
    anim.addParameter(generate_utils.getIndicator1Param(), bool)
    anim.addParameter(generate_utils.getScaleParam(), float)

    layers = {}
    for byte in range(0, generate_utils.BYTES_PER_CHAR):
        layers[byte] = {}
        for i in range(0, generate_utils.NUM_LAYERS):
            anim.addParameter(generate_utils.getBlendParam(i, byte), float)

            layer = anim.addLayer(generate_utils.getLayerName(i, byte))
            layers[byte][i] = layer
    anim.addParameter(generate_utils.getSelectParam(), int)

    return layers

def generateFXLayer(which_layer: int, anim: libunity.UnityAnimator, layer:
        libunity.UnityDocument, gen_anim_dir: str, byte: int):
    is_default_state = True
    default_state = anim.addAnimatorState(layer,
            generate_utils.getDefaultStateName(which_layer, byte), is_default_state)

    dy = 100
    active_state = anim.addAnimatorState(layer,
            generate_utils.getActiveStateName(which_layer, byte), dy = dy)

    active_state_transition = anim.addTransition(active_state)
    enable_param = generate_utils.getEnableParam()
    anim.addTransitionBooleanCondition(default_state, active_state_transition,
           enable_param, True)

    select_states = {}
    for i in range(0, generate_utils.NUM_REGIONS):
        dx = i * 200
        dy = 200

        # Create blend tree for this region.
        anim_lo_path = os.path.join(gen_anim_dir,
                generate_utils.getAnimationNameByLayerAndIndex(
                        which_layer, i, 0, byte) + \
                ".anim")
        guid_lo = guid_map[anim_lo_path]
        anim_hi_path = os.path.join(gen_anim_dir,
                generate_utils.getAnimationNameByLayerAndIndex(
                        which_layer, i, generate_utils.CHARS_PER_CELL - 1, byte) + \
                ".anim")
        guid_hi = guid_map[anim_hi_path]

        select_states[i] = anim.addAnimatorBlendTree(layer,
                generate_utils.getBlendStateName(which_layer, i, byte),
                generate_utils.getBlendParam(which_layer, byte),
                guid_lo, guid_hi, dx = dx, dy = dy)
        state = select_states[i]

        # Create transition to state.
        select_state_transition = anim.addTransition(state)
        select_param = generate_utils.getSelectParam()
        anim.addTransitionIntegerEqualityCondition(active_state,
                select_state_transition, select_param, i)

        # Create return-home transition.
        home_state_transition = anim.addTransition(default_state)
        home_state_transition.mapping['AnimatorStateTransition'].mapping['m_InterruptionSource'] = '0'
        dummy_param = generate_utils.getDummyParam()
        anim.addTransitionBooleanCondition(state,
                home_state_transition, dummy_param, False)
    pass

# Generic toggle adding utility.
# Generates the layer and parameter.
# Returns a map containing the off and on states, as well as the
# transitions between them.
def generateToggle(layer_name: str,
        gen_anim_dir: str,
        off_anim_basename: str,
        on_anim_basename: str,
        anim: libunity.UnityAnimator) -> typing.Dict[str,
                libunity.UnityDocument]:
    layer = anim.addLayer(layer_name)

    # For simplicity, use the layer name as the parameter name.
    parameter_name = layer_name
    anim.addParameter(parameter_name, bool)

    off_state = anim.addAnimatorState(layer, layer_name + "_Off",
            is_default_state = True)
    on_state  = anim.addAnimatorState(layer, layer_name + "_On", dy=100)

    if off_anim_basename:
        off_anim_path = os.path.join(gen_anim_dir, off_anim_basename)
        off_anim_meta = libunity.Metadata()
        off_anim_meta.load(off_anim_path)
        anim.setAnimatorStateAnimation(off_state, off_anim_meta.guid)

    if on_anim_basename:
        on_anim_path = os.path.join(gen_anim_dir, on_anim_basename)
        on_anim_meta = libunity.Metadata()
        on_anim_meta.load(on_anim_path)
        anim.setAnimatorStateAnimation(on_state, on_anim_meta.guid)

    off_to_on_trans = anim.addTransition(on_state)
    anim.addTransitionBooleanCondition(off_state,
            off_to_on_trans, parameter_name, True)

    on_to_off_trans = anim.addTransition(off_state)
    anim.addTransitionBooleanCondition(on_state,
            on_to_off_trans, parameter_name, False)

    result = {}
    result["off"] = off_state
    result["on"] = on_state
    result["off_to_on"] = off_to_on_trans
    result["on_to_off"] = on_to_off_trans

    return result

def generateScaleLayer(anim: libunity.UnityAnimator,
        gen_anim_dir: str,
        guid_map: typing.Dict[str, str]):

    scale_layer = anim.addLayer(generate_utils.getScaleParam())

    path = "World Constraint/Container/TaSTT"
    attribute = "blendShape.Scale"

    guid_lo = generateFloatAnimation("TaSTT_Scale_0", gen_anim_dir,
            path, attribute,
            0.0, guid_map)
    guid_hi = generateFloatAnimation("TaSTT_Scale_100", gen_anim_dir,
            path, attribute,
            100.0, guid_map)

    anim.addAnimatorBlendTree(scale_layer,
            generate_utils.getScaleParam(),
            generate_utils.getScaleParam(),
            guid_lo, guid_hi,
            lo_threshold = 0.0, hi_threshold = 1.0);

    pass

def generateFX(guid_map, gen_anim_dir):
    anim = libunity.UnityAnimator()

    layers = generateFXController(anim)

    # TODO(yum) parallelize
    for byte in range(0, generate_utils.BYTES_PER_CHAR):
        for which_layer, layer in layers[byte].items():
            print("Generating layer {}/{}".format(which_layer, len(layers[byte].items())), file=sys.stderr)
            generateFXLayer(which_layer, anim, layer, gen_anim_dir, byte)

    states = generateToggle(
            generate_utils.getSpeechNoiseToggleParam(),
            "Animations/",
            "TaSTT_Speech_Noise_Off.anim",
            "TaSTT_Speech_Noise_On.anim",
            anim)
    # Enable beeping only if user has turned it on.
    anim.addTransitionBooleanCondition(states["off"],
            states["off_to_on"], generate_utils.getSpeechNoiseEnableParam(), True)
    # Enable beeping only if board is out.
    anim.addTransitionBooleanCondition(states["off"],
            states["off_to_on"], generate_utils.getToggleParam(), True)

    generateToggle(generate_utils.getToggleParam(),
            "Animations/",
            "TaSTT_Toggle_Off.anim",
            "TaSTT_Toggle_On.anim",
            anim)
    generateToggle(generate_utils.getLockWorldParam(),
            "Animations/",
            "TaSTT_Lock_World_Disable.anim",
            "TaSTT_Lock_World_Enable.anim",
            anim)
    generateToggle(
            generate_utils.getClearBoardParam(),
            gen_anim_dir,
            None,  # No animation in the `off` state.
            generate_utils.getClearAnimationName() + ".anim",
            anim)
    generateToggle(generate_utils.getIndicator0Param(),
            gen_anim_dir,
            generate_utils.getIndicator0Param() + "_Off.anim",
            generate_utils.getIndicator0Param() + "_On.anim",
            anim)
    generateToggle(generate_utils.getIndicator1Param(),
            gen_anim_dir,
            generate_utils.getIndicator1Param() + "_Off.anim",
            generate_utils.getIndicator1Param() + "_On.anim",
            anim)
    generateScaleLayer(anim, gen_anim_dir, guid_map)

    return anim

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", type=str, help="")
    parser.add_argument("--gen_dir", type=str, help="The directory under " +
            "which all generated assets are placed")
    parser.add_argument("--gen_anim_dir", type=str, help="The directory under " +
            "which all generated animations are placed.")
    parser.add_argument("--guid_map", type=str, help="The path to a file which will store guids")
    args = parser.parse_args()

    if not args.gen_dir:
        args.gen_dir = "generated/"

    if not args.gen_anim_dir:
        args.gen_anim_dir = args.gen_dir + "animations/"

    if not args.guid_map:
        args.guid_map = "guid.map"

    return args

if __name__ == "__main__":
    args = parseArgs()

    if args.cmd == "gen_anims":
        guid_map = {}
        with open(args.guid_map, 'rb') as f:
            guid_map = pickle.load(f)

        os.makedirs(args.gen_anim_dir, exist_ok=True)
        generateAnimations(args.gen_anim_dir, guid_map)

        with open(args.guid_map, 'wb') as f:
            pickle.dump(guid_map, f)
    elif args.cmd == "gen_fx":
        guid_map = {}
        with open(args.guid_map, 'rb') as f:
            guid_map = pickle.load(f)

        print(str(generateFX(guid_map, args.gen_anim_dir)))

