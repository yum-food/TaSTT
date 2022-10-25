#!/usr/bin/env python3

import argparse
import generate_utils
import libunity
import os
import pickle
import sys
import typing

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

def generateAnimations(anim_dir, guid_map):
    parser = libunity.UnityParser()
    parser.parse(LETTER_ANIMATION_TEMPLATE)

    anim_node = parser.nodes[0]
    anim_clip = anim_node.mapping['AnimationClip']
    curve_template = anim_clip.mapping['m_FloatCurves'].sequence[0]
    anim_clip.mapping['m_FloatCurves'].sequence = []
    anim_clip.mapping['m_EditorCurves'].sequence = []

    for row in range(0, generate_utils.BOARD_ROWS):
        for col in range(0, generate_utils.BOARD_COLS):
            for letter in range(0, generate_utils.CHARS_PER_CELL):
                # Make a deep copy of the templates
                node = anim_node.copy()
                curve = curve_template.copy()
                clip = node.mapping['AnimationClip']
                # Populate animation name
                anim_name = generate_utils.getAnimationName(row, col, letter)
                clip.mapping['m_Name'] = anim_name
                # Populate letter value
                for keyframe in curve.mapping['curve'].mapping['m_Curve'].sequence:
                    # For whatever reason, running unrelated animations s.a.
                    # facial expressions can have a slight effect on supposedly
                    # unrelated parameters, causing letter to flip. Add a
                    # little buffer to reduce the odds that this effect causes
                    # a letter to change after it has been written.
                    keyframe.mapping['value'] = str(letter + 0.1)
                # Populate path to letter parameter
                curve.mapping['attribute'] = "material.{}".format(generate_utils.getShaderParamByRowCol(row, col))
                curve.mapping['path'] = "World Constraint/Container/TaSTT"
                # Add curve to animation
                clip.mapping['m_FloatCurves'].sequence.append(curve)
                clip.mapping['m_EditorCurves'].sequence.append(curve)
                # Serialize animation to file
                anim_path = anim_dir + anim_name + ".anim"
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
    anim.addParameter(generate_utils.getResizeEnableParam(), bool)
    anim.addParameter(generate_utils.getResize0Param(), bool)
    anim.addParameter(generate_utils.getResize1Param(), bool)
    anim.addParameter(generate_utils.getHipToggleParam(), bool)
    anim.addParameter(generate_utils.getHandToggleParam(), bool)
    anim.addParameter(generate_utils.getToggleParam(), bool)
    anim.addParameter(generate_utils.getSpeechNoiseEnableParam(), bool)

    layers = {}
    for i in range(0, generate_utils.NUM_LAYERS):
        anim.addParameter(generate_utils.getLayerParam(i), int)
        for j in range(0, generate_utils.INDEX_BITS):
            anim.addParameter(generate_utils.getSelectParam(i, j), bool)

        layer = anim.addLayer(generate_utils.getLayerName(i))
        layers[i] = layer

    return layers

def generateFXLayer(which_layer: int, anim: libunity.UnityAnimator, layer:
        libunity.UnityDocument, gen_anim_dir: str):
    is_default_state = True
    default_state = anim.addAnimatorState(layer,
            generate_utils.getDefaultStateName(which_layer), is_default_state)

    dy = 100
    active_state = anim.addAnimatorState(layer,
            generate_utils.getActiveStateName(which_layer), dy = dy)

    active_state_transition = anim.addTransition(active_state)
    enable_param = generate_utils.getEnableParam()
    anim.addTransitionBooleanCondition(default_state, active_state_transition,
           enable_param, True)

    s0_states = {}
    for s0 in range(0,2):
        dx = s0 * 200
        dy = 200
        s0_states[s0] = anim.addAnimatorState(layer,
                generate_utils.getS0StateName(which_layer, s0),
                dx = dx, dy = dy)
        state = s0_states[s0]

        s0_state_transition = anim.addTransition(state)
        s0_param = generate_utils.getSelectParam(which_layer, 0)
        anim.addTransitionBooleanCondition(active_state, s0_state_transition,
                s0_param, s0 != 0)

    s1_states = {}
    for s0 in range(0,2):
        s1_states[s0] = {}
        for s1 in range(0,2):
            dx = ((s0 << 1) | (s1)) * 200
            dy = 300
            s1_states[s0][s1] = anim.addAnimatorState(layer,
                    generate_utils.getS1StateName(which_layer, s0, s1),
                    dx = dx, dy = dy)
            state = s1_states[s0][s1]

            s1_state_transition = anim.addTransition(state)
            s1_param = generate_utils.getSelectParam(which_layer, 1)
            anim.addTransitionBooleanCondition(s0_states[s0], s1_state_transition,
                    s1_param, s1 != 0)

    s2_states = {}
    for s0 in range(0,2):
        s2_states[s0] = {}
        for s1 in range(0,2):
            s2_states[s0][s1] = {}
            for s2 in range(0,2):
                dx = ((s0 << 2) | (s1 << 1) | (s2)) * 200
                dy = 400
                s2_states[s0][s1][s2] = anim.addAnimatorState(layer,
                        generate_utils.getS2StateName(which_layer, s0, s1, s2),
                        dx = dx, dy = dy)
                state = s2_states[s0][s1][s2]

                s2_state_transition = anim.addTransition(state)
                s2_param = generate_utils.getSelectParam(which_layer, 2)
                anim.addTransitionBooleanCondition(s1_states[s0][s1], s2_state_transition,
                        s2_param, s2 != 0)

    s3_states = {}
    for s0 in range(0,2):
        s3_states[s0] = {}
        for s1 in range(0,2):
            s3_states[s0][s1] = {}
            for s2 in range(0,2):
                s3_states[s0][s1][s2] = {}
                for s3 in range(0,2):
                    dx = ((s0 << 3) | (s1 << 2) | (s2 << 1) | (s3)) * 200
                    dy = 500
                    s3_states[s0][s1][s2][s3] = anim.addAnimatorState(layer,
                            generate_utils.getS3StateName(which_layer, s0, s1, s2, s3),
                            dx = dx, dy = dy)
                    state = s3_states[s0][s1][s2][s3]

                    s3_state_transition = anim.addTransition(state)
                    s3_param = generate_utils.getSelectParam(which_layer, 3)
                    anim.addTransitionBooleanCondition(s2_states[s0][s1][s2], s3_state_transition,
                            s3_param, s3 != 0)

    l_states = {}  # shorthand for `letter_states`
    for s0 in range(0,2):
        l_states[s0] = {}
        for s1 in range(0,2):
            l_states[s0][s1] = {}
            for s2 in range(0,2):
                l_states[s0][s1][s2] = {}
                for s3 in range(0,2):
                    l_states[s0][s1][s2][s3] = {}
                    for letter in range(0, generate_utils.CHARS_PER_CELL):
                        dy = 600
                        l_states[s0][s1][s2][s3][letter] = anim.addAnimatorState(layer,
                                generate_utils.getLetterStateName(which_layer,
                                    s0, s1, s2, s3, letter),
                                dy = dy)
                        state = l_states[s0][s1][s2][s3][letter]

                        animation_path = gen_anim_dir + \
                                generate_utils.getAnimationNameByLayerAndIndex(
                                        which_layer, s0, s1, s2, s3, letter) + \
                                ".anim"
                        guid = guid_map[animation_path]
                        anim.setAnimatorStateAnimation(state, guid)

                        # TODO(yum) see if we can get away with reusing the
                        # same transition object, but just stitch it into every
                        # state.
                        l_state_transition = anim.addTransition(state)
                        l_param = generate_utils.getLayerParam(which_layer)
                        #print("add condition on letter {}".format(letter),
                        #        file=sys.stderr)
                        anim.addTransitionIntegerEqualityCondition(s3_states[s0][s1][s2][s3],
                                l_state_transition, l_param, letter)

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

    off_anim_path = gen_anim_dir + off_anim_basename
    off_anim_meta = libunity.Metadata()
    off_anim_meta.load(off_anim_path)
    on_anim_path = gen_anim_dir + on_anim_basename
    on_anim_meta = libunity.Metadata()
    on_anim_meta.load(on_anim_path)

    anim.setAnimatorStateAnimation(off_state, off_anim_meta.guid)
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

def generateFX(guid_map, gen_anim_dir):
    anim = libunity.UnityAnimator()

    layers = generateFXController(anim)

    # TODO(yum) parallelize
    for which_layer, layer in layers.items():
        print("Generating layer {}/{}".format(which_layer, len(layers.items())), file=sys.stderr)
        generateFXLayer(which_layer, anim, layer, gen_anim_dir)

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

