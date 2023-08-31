#!/usr/bin/env python3

import argparse
import array
import generate_utils
import libunity
import os
import pickle
import sys
import typing

# TODO(yum) we're getting the encoding scheme from here, but I think it should
# be in a different layer.
import osc_ctrl

SCALE_ANIMATION_TEMPLATE = """
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!74 &7400000
AnimationClip:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: TaSTT_Scale_0
  serializedVersion: 6
  m_Legacy: 0
  m_Compressed: 0
  m_UseHighQualityCurve: 1
  m_RotationCurves: []
  m_CompressedRotationCurves: []
  m_EulerCurves: []
  m_PositionCurves: []
  m_ScaleCurves:
  - curve:
      serializedVersion: 2
      m_Curve:
      - serializedVersion: 3
        time: 0
        value: {x: 5, y: 5, z: 5}
        inSlope: {x: 0, y: 0, z: 0}
        outSlope: {x: 0, y: 0, z: 0}
        tangentMode: 0
        weightedMode: 0
        inWeight: {x: 0, y: 0.33333334, z: 0.33333334}
        outWeight: {x: 0, y: 0.33333334, z: 0.33333334}
      m_PreInfinity: 2
      m_PostInfinity: 2
      m_RotationOrder: 4
    path: World Constraint/Container/TaSTT
  m_FloatCurves: []
  m_PPtrCurves: []
  m_SampleRate: 60
  m_WrapMode: 0
  m_Bounds:
    m_Center: {x: 0, y: 0, z: 0}
    m_Extent: {x: 0, y: 0, z: 0}
  m_ClipBindingConstant:
    genericBindings:
    - serializedVersion: 2
      path: 1272388438
      attribute: 3
      script: {fileID: 0}
      typeID: 4
      customType: 0
      isPPtrCurve: 0
    - serializedVersion: 2
      path: 1272388438
      attribute: 1225223716
      script: {fileID: 0}
      typeID: 23
      customType: 0
      isPPtrCurve: 0
    pptrCurveMapping: []
  m_AnimationClipSettings:
    serializedVersion: 2
    m_AdditiveReferencePoseClip: {fileID: 0}
    m_AdditiveReferencePoseTime: 0
    m_StartTime: 0
    m_StopTime: 0.016666668
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
        value: 5
        inSlope: 0
        outSlope: 0
        tangentMode: 136
        weightedMode: 0
        inWeight: 0
        outWeight: 0
      m_PreInfinity: 2
      m_PostInfinity: 2
      m_RotationOrder: 4
    attribute: m_LocalScale.x
    path: World Constraint/Container/TaSTT
    classID: 4
    script: {fileID: 0}
  - curve:
      serializedVersion: 2
      m_Curve:
      - serializedVersion: 3
        time: 0
        value: 5
        inSlope: 0
        outSlope: 0
        tangentMode: 136
        weightedMode: 0
        inWeight: 0
        outWeight: 0
      m_PreInfinity: 2
      m_PostInfinity: 2
      m_RotationOrder: 4
    attribute: m_LocalScale.y
    path: World Constraint/Container/TaSTT
    classID: 4
    script: {fileID: 0}
  - curve:
      serializedVersion: 2
      m_Curve:
      - serializedVersion: 3
        time: 0
        value: 5
        inSlope: 0
        outSlope: 0
        tangentMode: 136
        weightedMode: 0
        inWeight: 0
        outWeight: 0
      m_PreInfinity: 2
      m_PostInfinity: 2
      m_RotationOrder: 4
    attribute: m_LocalScale.z
    path: World Constraint/Container/TaSTT
    classID: 4
    script: {fileID: 0}
  m_EulerEditorCurves: []
  m_HasGenericRootTransform: 0
  m_HasMotionFloatCurves: 0
  m_Events: []
"""

SOUND_ANIMATION_TEMPLATE = """
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!74 &7400000
AnimationClip:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: Sound1_On
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
        value: 1
        inSlope: Infinity
        outSlope: Infinity
        tangentMode: 103
        weightedMode: 0
        inWeight: 0
        outWeight: 0
      m_PreInfinity: 2
      m_PostInfinity: 2
      m_RotationOrder: 4
    attribute: m_IsActive
    path: World Constraint/Container/TaSTT/Audio 1
    classID: 1
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
      path: 2267216663
      attribute: 2086281974
      script: {fileID: 0}
      typeID: 1
      customType: 0
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
    m_LoopTime: 0
    m_LoopBlend: 0
    m_LoopBlendOrientation: 0
    m_LoopBlendPositionY: 0
    m_LoopBlendPositionXZ: 0
    m_KeepOriginalOrientation: 0
    m_KeepOriginalPositionY: 1
    m_KeepOriginalPositionXZ: 0
    m_HeightFromFeet: 0
    m_Mirror: 0
  m_EditorCurves: []
  m_EulerEditorCurves: []
  m_HasGenericRootTransform: 0
  m_HasMotionFloatCurves: 0
  m_Events: []
"""

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
    classID: 23
    script: {fileID: 0}
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
    classID: 23
    script: {fileID: 0}
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

    for byte in range(0, generate_utils.config.BYTES_PER_CHAR):
        for row in range(0, generate_utils.config.BOARD_ROWS):
            for col in range(0, generate_utils.config.BOARD_COLS):
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
    print("Generating clear animation at {}".format(anim_path), file=sys.stderr)
    with open(anim_path, "w", encoding="utf-8") as f:
        f.write(libunity.unityYamlToString([anim_node]))
    # Generate metadata
    meta = libunity.Metadata()
    with open(anim_path + ".meta", "w", encoding="utf-8") as f:
        f.write(str(meta))
    # Add metadata to guid map
    guid_map[anim_path] = meta.guid
    guid_map[meta.guid] = anim_path

# sound_chord: whether to play a, e, i, o, u
# value: 0 or 1
def generateSoundAnimation(sound_chord: typing.Tuple[int,int,int,int,int],
        value: int,
        anim_name: str,
        anim_dir: str, guid_map: typing.Dict[str, str],
        anim_delay_frames = 2):
    print(f"Generating sound animation {sound_chord} / {anim_name}", file=sys.stderr)

    parser = libunity.UnityParser()
    parser.parse(SOUND_ANIMATION_TEMPLATE)

    anim_node = parser.nodes[0]
    anim_clip = anim_node.mapping['AnimationClip']
    curve_template = anim_clip.mapping['m_FloatCurves'].sequence[0]
    anim_clip.mapping['m_FloatCurves'].sequence = []
    anim_clip.mapping['m_EditorCurves'].sequence = []

    # Animate all notes.
    for note_i in range(len(sound_chord)):
        curve = curve_template.copy()

        keyframe_template = curve.mapping['curve'].mapping['m_Curve'].sequence[0]
        curve.mapping['curve'].mapping['m_Curve'].sequence = []

        # First keyframe: zero all but first note
        if note_i != 0:
            keyframe = keyframe_template.copy()
            keyframe.mapping['time'] = 0
            keyframe.mapping['value'] = 0
            curve.mapping['path'] = f"World Constraint/Container/TaSTT/Audio {note_i + 1}"
            curve.mapping['curve'].mapping['m_Curve'].sequence.append(keyframe)

        # Subsequent keyframes: animate as normal
        keyframe = keyframe_template.copy()
        keyframe.mapping['time']= str(note_i * anim_delay_frames * 1.0 / 60.0)
        keyframe.mapping['value'] = str(sound_chord[note_i])
        curve.mapping['path'] = f"World Constraint/Container/TaSTT/Audio {note_i + 1}"
        curve.mapping['curve'].mapping['m_Curve'].sequence.append(keyframe)

        # Add curve to animation
        anim_clip.mapping['m_FloatCurves'].sequence.append(curve)
        anim_clip.mapping['m_EditorCurves'].sequence.append(curve)

    anim_clip.mapping['m_AnimationClipSettings'].mapping['m_StopTime'] = str((len(sound_chord)-1) * anim_delay_frames * 1.0 / 60.0)

    # Serialize animation to file
    anim_path = os.path.join(anim_dir, anim_name + ".anim")
    with open(anim_path, "w", encoding="utf-8") as f:
        f.write(libunity.unityYamlToString([anim_node]))
    # Generate metadata
    meta = libunity.Metadata()
    with open(anim_path + ".meta", "w", encoding="utf-8") as f:
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
        with open(anim_path, "w", encoding="utf-8") as f:
            f.write(libunity.unityYamlToString([anim_node]))
        # Generate metadata
        meta = libunity.Metadata()
        with open(anim_path + ".meta", "w", encoding="utf-8") as f:
            f.write(str(meta))
        # Add metadata to guid map
        guid_map[anim_path] = meta.guid
        guid_map[meta.guid] = anim_path

# Generate a toggle animation for a shader parameter.
def generateScaleAnimation(anim_name: str, anim_dir: str,
        path: str,
        value: float,
        guid_map: typing.Dict[str, str]) -> str:
    print("Generating scale animation {}".format(path),
            file=sys.stderr)

    parser = libunity.UnityParser()
    parser.parse(SCALE_ANIMATION_TEMPLATE)

    #print("kill me", file=sys.stderr)
    #print(libunity.unityYamlToString([parser.nodes[0]]), file=sys.stdout)
    #print("NOW", file=sys.stdout)

    # 0.0 represents false, 1.0 represents true. Don't forget that we add
    # `UNITY_ANIMATION_FUDGE_MARGIN` to everything.
    anim_node = parser.nodes[0]
    anim_clip = anim_node.mapping['AnimationClip']
    #print("here 3", file=sys.stderr)
    for curve in anim_clip.mapping['m_ScaleCurves'].sequence:
        for keyframe in curve.mapping['curve'].mapping['m_Curve'].sequence:
            keyframe.mapping['value'].mapping['x'] = str(value)
            keyframe.mapping['value'].mapping['y'] = str(value)
            keyframe.mapping['value'].mapping['z'] = str(value)
    #print("here 4", file=sys.stderr)
    for curve in anim_clip.mapping['m_EditorCurves'].sequence:
        for keyframe in curve.mapping['curve'].mapping['m_Curve'].sequence:
            keyframe.mapping['value'] = value

    #print("here 5", file=sys.stderr)

    # Serialize animation to file
    anim_path = os.path.join(anim_dir, anim_name + ".anim")
    with open(anim_path, "w", encoding="utf-8") as f:
        f.write(libunity.unityYamlToString([anim_node]))
    # Generate metadata
    meta = libunity.Metadata()
    with open(anim_path + ".meta", "w", encoding="utf-8") as f:
        f.write(str(meta))
    # Add metadata to guid map
    guid_map[anim_path] = meta.guid
    guid_map[meta.guid] = anim_path

    return meta.guid

def generateAnimations(anim_dir, guid_map):
    generateClearAnimation(anim_dir, guid_map)

    for chord_bits in range(2**5):
        chord = [0, 0, 0, 0, 0]
        for i in range(5):
            if (chord_bits >> i) % 2 == 1:
                chord[i] = 1
        print(f"Generating chord {chord}", file=sys.stderr)
        anim_name = f"Sound_a{chord[0]}_e{chord[1]}_i{chord[2]}_o{chord[3]}_u{chord[4]}"
        generateSoundAnimation(chord, 0, anim_name, anim_dir, guid_map)

    print("Generating letter animations", file=sys.stderr)

    parser = libunity.UnityParser()
    parser.parse(LETTER_ANIMATION_TEMPLATE)

    anim_node = parser.nodes[0]
    anim_clip = anim_node.mapping['AnimationClip']
    curve_template = anim_clip.mapping['m_FloatCurves'].sequence[0]
    anim_clip.mapping['m_FloatCurves'].sequence = []
    anim_clip.mapping['m_EditorCurves'].sequence = []

    # To support more languages, we use 2 bytes per character, giving us a 64K character set.
    for byte in range(0, generate_utils.config.BYTES_PER_CHAR):
        for row in range(0, generate_utils.config.BOARD_ROWS):
            print("Generating letter animations (row {}/{}) (byte {}/2)".format(row,
                generate_utils.config.BOARD_ROWS, byte), file=sys.stderr)
            for col in range(0, generate_utils.config.BOARD_COLS):
                for letter in range(0, 2):
                    if letter == 1:
                        letter = generate_utils.config.CHARS_PER_CELL - 1

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
                    with open(anim_path, "w", encoding="utf-8") as f:
                        f.write(libunity.unityYamlToString([node]))
                    # Generate metadata
                    meta = libunity.Metadata()
                    with open(anim_path + ".meta", "w", encoding="utf-8") as f:
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
    anim.addParameter(generate_utils.getClearBoardParam(), bool)
    anim.addParameter(generate_utils.getScaleParam(), float)

    for i in range(5):
        anim.addParameter(generate_utils.getSoundParam(i+1), bool)

    anim.addLayer("=== TaSTT ===", weight=0.0)

    layers = {}
    for byte in range(0, generate_utils.config.BYTES_PER_CHAR):
        layers[byte] = {}
        for i in range(0, generate_utils.config.CHARS_PER_SYNC):
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
    for i in range(0, generate_utils.config.numRegions(which_layer)):
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
                        which_layer, i, generate_utils.config.CHARS_PER_CELL - 1, byte) + \
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
        parameter_name: str,
        gen_anim_dir: str,
        off_anim_basename: str,
        on_anim_basename: str,
        anim: libunity.UnityAnimator,
        guid_map: typing.Dict[str, str],
        duration_s: float = 0.0) -> typing.Dict[str,
                libunity.UnityDocument]:
    layer = anim.addLayer(layer_name)

    # For simplicity, use the layer name as the parameter name.
    anim.addParameter(parameter_name, bool)

    off_state = anim.addAnimatorState(layer, layer_name + "_Off",
            is_default_state = True)
    on_state  = anim.addAnimatorState(layer, layer_name + "_On", dy=100)

    if off_anim_basename:
        off_anim_path = os.path.join(gen_anim_dir, off_anim_basename)
        off_anim_meta = libunity.Metadata()
        off_anim_meta.loadOrCreate(off_anim_path, guid_map)
        anim.setAnimatorStateAnimation(off_state, off_anim_meta.guid)

    if on_anim_basename:
        on_anim_path = os.path.join(gen_anim_dir, on_anim_basename)
        on_anim_meta = libunity.Metadata()
        on_anim_meta.loadOrCreate(on_anim_path, guid_map)
        anim.setAnimatorStateAnimation(on_state, on_anim_meta.guid)

    off_to_on_trans = anim.addTransition(on_state, duration_s)
    anim.addTransitionBooleanCondition(off_state,
            off_to_on_trans, parameter_name, True)

    on_to_off_trans = anim.addTransition(off_state, duration_s)
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

    guid_lo = generateScaleAnimation("TaSTT_Scale_0", gen_anim_dir,
            path,
            5.0, guid_map)
    guid_hi = generateScaleAnimation("TaSTT_Scale_100", gen_anim_dir,
            path,
            100.0, guid_map)

    anim.addAnimatorBlendTree(scale_layer,
            generate_utils.getScaleParam(),
            generate_utils.getScaleParam(),
            guid_lo, guid_hi,
            lo_threshold = 0.0, hi_threshold = 1.0);

    pass

def generateSoundLayer(anim: libunity.UnityAnimator,
        gen_anim_dir: str,
        guid_map: typing.Dict[str, str],
        anim_len_s = 12.0/60.0):

    layer = anim.addLayer("TaSTT_Sound")

    # Create `a` state.
    a_state = anim.addAnimatorState(layer, "a", is_default_state=True)

    for a_bool in range(2):
        dy = 100
        dx = a_bool * 800
        # Create `e` state.
        ax_e_state = anim.addAnimatorState(layer,
                f"a{a_bool}_e",
                dy=dy, dx=dx)
        # Create transition based on whether `a` is set.
        trans = anim.addTransition(ax_e_state)
        param = generate_utils.getSoundParam(1)
        anim.addTransitionBooleanCondition(a_state, trans, param, a_bool)

        for e_bool in range(2):
            dy = 200
            dx = a_bool * 800 + e_bool * 400

            # Create `i` state.
            ax_ex_i_state = anim.addAnimatorState(layer,
                    f"a{a_bool}_e{e_bool}_i",
                    dy=dy, dx=dx)

            # Create transition based on whether `e` is set.
            trans = anim.addTransition(ax_ex_i_state)
            param = generate_utils.getSoundParam(2)
            anim.addTransitionBooleanCondition(ax_e_state, trans, param, e_bool)

            for i_bool in range(2):
                dy = 300
                dx = a_bool * 800 + e_bool * 400 + i_bool * 200

                # Create `o` state.
                ax_ex_ix_o_state = anim.addAnimatorState(layer,
                        f"a{a_bool}_e{e_bool}_i{i_bool}_o",
                        dy=dy, dx=dx)
                # Create transition based on whether `i` is set.
                trans = anim.addTransition(ax_ex_ix_o_state)
                param = generate_utils.getSoundParam(3)
                anim.addTransitionBooleanCondition(ax_ex_i_state, trans, param, i_bool)

                for o_bool in range(2):
                    dy = 400
                    dx = a_bool * 800 + e_bool * 400 + i_bool * 200 + o_bool * 100

                    # Create `u` state.
                    ax_ex_ix_ox_u_state = anim.addAnimatorState(layer,
                            f"a{a_bool}_e{e_bool}_i{i_bool}_o{o_bool}_u",
                            dy=dy, dx=dx)
                    # Create transition based on whether `o` is set.
                    trans = anim.addTransition(ax_ex_ix_ox_u_state)
                    param = generate_utils.getSoundParam(4)
                    anim.addTransitionBooleanCondition(ax_ex_ix_o_state,
                            trans, param, o_bool)

                    for u_bool in range(2):
                        dy = 500
                        dx = a_bool * 800 + e_bool * 400 + i_bool * 200 + o_bool * 100 + u_bool * 50
                        if u_bool == 1:
                            dy = 550

                        # Create `u` state.
                        ax_ex_ix_ox_ux_state = anim.addAnimatorState(layer,
                                f"a{a_bool}_e{e_bool}_i{i_bool}_o{o_bool}_u{u_bool}",
                                dy=dy, dx=dx)
                        # Create transition based on whether `u` is set.
                        trans = anim.addTransition(ax_ex_ix_ox_ux_state)
                        param = generate_utils.getSoundParam(5)
                        anim.addTransitionBooleanCondition(ax_ex_ix_ox_u_state,
                                trans, param, u_bool)

                        chord = [a_bool, e_bool, i_bool, o_bool, u_bool]
                        anim_name = f"Sound_a{chord[0]}_e{chord[1]}_i{chord[2]}_o{chord[3]}_u{chord[4]}"
                        anim_path = os.path.join(gen_anim_dir, anim_name + ".anim")
                        anim_guid = guid_map[anim_path]
                        anim.setAnimatorStateAnimation(ax_ex_ix_ox_ux_state, anim_guid)

                        # Create return-home transitions.
                        trans = anim.addTransition(a_state, dur_s = anim_len_s)
                        trans.mapping['AnimatorStateTransition'].mapping['m_InterruptionSource'] = '0'
                        param = generate_utils.getSoundParam(1)
                        anim.addTransitionBooleanCondition(ax_ex_ix_ox_ux_state, trans, param, 1 - a_bool)

                        trans = anim.addTransition(a_state, dur_s = anim_len_s)
                        trans.mapping['AnimatorStateTransition'].mapping['m_InterruptionSource'] = '0'
                        param = generate_utils.getSoundParam(2)
                        anim.addTransitionBooleanCondition(ax_ex_ix_ox_ux_state, trans, param, 1 - e_bool)

                        trans = anim.addTransition(a_state, dur_s = anim_len_s)
                        trans.mapping['AnimatorStateTransition'].mapping['m_InterruptionSource'] = '0'
                        param = generate_utils.getSoundParam(3)
                        anim.addTransitionBooleanCondition(ax_ex_ix_ox_ux_state, trans, param, 1 - i_bool)

                        trans = anim.addTransition(a_state, dur_s = anim_len_s)
                        trans.mapping['AnimatorStateTransition'].mapping['m_InterruptionSource'] = '0'
                        param = generate_utils.getSoundParam(4)
                        anim.addTransitionBooleanCondition(ax_ex_ix_ox_ux_state, trans, param, 1 - o_bool)

                        trans = anim.addTransition(a_state, dur_s = anim_len_s)
                        trans.mapping['AnimatorStateTransition'].mapping['m_InterruptionSource'] = '0'
                        param = generate_utils.getSoundParam(5)
                        anim.addTransitionBooleanCondition(ax_ex_ix_ox_ux_state, trans, param, 1 - u_bool)

def generateFX(guid_map, gen_anim_dir):
    anim = libunity.UnityAnimator()

    layers = generateFXController(anim)

    # TODO(yum) parallelize
    for byte in range(0, generate_utils.config.BYTES_PER_CHAR):
        for which_layer, layer in layers[byte].items():
            print("Generating layer {}/{}".format(which_layer, len(layers[byte].items())), file=sys.stderr)
            generateFXLayer(which_layer, anim, layer, gen_anim_dir, byte)

    generateToggle(generate_utils.getToggleParam(),
            generate_utils.getToggleParam(),
            gen_anim_dir,
            "TaSTT_Toggle_Off.anim",
            "TaSTT_Toggle_On.anim",
            anim, guid_map)
    generateToggle(generate_utils.getLockWorldParam(),
            generate_utils.getLockWorldParam(),
            gen_anim_dir,
            "TaSTT_Lock_World_Disable.anim",
            "TaSTT_Lock_World_Enable.anim",
            anim, guid_map)
    generateToggle(generate_utils.getEllipsisParam(),
            generate_utils.getEllipsisParam(),
            gen_anim_dir,
            "TaSTT_Ellipsis_Off.anim",
            "TaSTT_Ellipsis_On.anim",
            anim, guid_map)
    generateToggle(
            generate_utils.getClearBoardParam(),
            generate_utils.getClearBoardParam(),
            gen_anim_dir,
            None,  # No animation in the `off` state.
            generate_utils.getClearAnimationName() + ".anim",
            anim, guid_map)
    generateToggle("TaSTT_Expand",
            generate_utils.getToggleParam(),
            gen_anim_dir,
            "TaSTT_Emerge_000.anim",
            "TaSTT_Emerge_100.anim",
            anim, guid_map, 0.5)

    generateScaleLayer(anim, gen_anim_dir, guid_map)
    generateSoundLayer(anim, gen_anim_dir, guid_map)

    return anim

def parseArgs():
    print("args: {}".format(" ".join(sys.argv)))

    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", type=str, help="")
    parser.add_argument("--gen_dir", type=str, help="The directory under " +
            "which all generated assets are placed")
    parser.add_argument("--gen_anim_dir", type=str, help="The directory under " +
            "which all generated animations are placed.")
    parser.add_argument("--guid_map", type=str, help="The path to a file which will store guids")
    parser.add_argument("--fx_dest", type=str, help="The path at which to save the generated FX controller")
    parser.add_argument("--bytes_per_char", type=str, help="The number of bytes to use to represent each character")
    parser.add_argument("--chars_per_sync", type=str, help="The number of characters to send on each sync event")
    parser.add_argument("--rows", type=int, help="The number of rows on the board")
    parser.add_argument("--cols", type=int, help="The number of columns on the board")
    args = parser.parse_args()

    if not args.gen_dir:
        args.gen_dir = "generated/"

    if not args.gen_anim_dir:
        args.gen_anim_dir = args.gen_dir + "animations/"

    if not args.guid_map:
        args.guid_map = "guid.map"

    if not args.fx_dest:
        args.fx_dest = args.gen_dir + "TaSTT_fx.controller"

    return args

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    args = parseArgs()

    if args.cmd == "gen_anims":
        if not args.bytes_per_char or not args.chars_per_sync:
            print("--bytes_per_char and --chars_per_sync required", file=sys.stderr)
            sys.exit(1)

        if not args.rows or not args.cols:
            print("--rows and --cols required", file=sys.stderr)
            sys.exit(1)

        generate_utils.config.BYTES_PER_CHAR = int(args.bytes_per_char)
        generate_utils.config.CHARS_PER_SYNC = int(args.chars_per_sync)
        generate_utils.config.BOARD_ROWS = int(args.rows)
        generate_utils.config.BOARD_COLS = int(args.cols)

        guid_map = {}
        with open(args.guid_map, 'rb') as f:
            guid_map = pickle.load(f)

        os.makedirs(args.gen_anim_dir, exist_ok=True)
        generateAnimations(args.gen_anim_dir, guid_map)

        with open(args.guid_map, 'wb') as f:
            pickle.dump(guid_map, f)
    elif args.cmd == "gen_fx":
        if not args.bytes_per_char or not args.chars_per_sync:
            print("--bytes_per_char and --chars_per_sync required", file=sys.stderr)
            sys.exit(1)

        if not args.rows or not args.cols:
            print("--rows and --cols required", file=sys.stderr)
            sys.exit(1)

        generate_utils.config.BYTES_PER_CHAR = int(args.bytes_per_char)
        generate_utils.config.CHARS_PER_SYNC = int(args.chars_per_sync)
        generate_utils.config.BOARD_ROWS = int(args.rows)
        generate_utils.config.BOARD_COLS = int(args.cols)

        guid_map = {}
        with open(args.guid_map, 'rb') as f:
            guid_map = pickle.load(f)
        os.makedirs(os.path.dirname(args.fx_dest), exist_ok=True)
        with open(args.fx_dest, "w", encoding="utf-8") as f:
            f.write(str(generateFX(guid_map, args.gen_anim_dir)))
        with open(args.guid_map, 'wb') as f:
            pickle.dump(guid_map, f)

        # If we don't do this, then VRChat will fail to update the animator
        # when users update their avatars.
        if os.path.exists(args.fx_dest + ".meta"):
            os.remove(args.fx_dest + ".meta")

