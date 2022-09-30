#!/usr/bin/env python3

# Template parameters:
# 1.  %*_U% - the !u! identifier for a block.
# 2.  %*_U2% - the & identifier for a block.
# 3.  %ANIMATOR_PARAMETER_NAME% - the name of an animator parameter.
# 4.  %SET_LETTERS_GUID% - the GUID from SetLetters.cs.meta
# 5.  %SERIALIZED_VERSION% - the value of serializedVersion (usually a small int
#       like 0-5)
# 6.  %DEFAULT_GROUP_VAL% - the default value of the group parameters.
# 8.  %DEFAULT_CELL_VAL% - the default value of the cell parameters.
# 9.  %LAYER_NAME% - the name to use for the current animator layer.
# 10. %LAYER_STATE_MACHINE_U2% - the U2 to use for the current layer's state machine.
# 11. %TRANSITION_DST_STATE_U2% - in an animatorstatetransition, this specifies
#     where we're transitioning to.
# 12. %TRANSITION_THRESHOLD% - the threshold to use when transitioning.

# To debug, I recommend setting these values low and manually moving things
# around in the animator. Then run using Lyuma's avatar 3.0 emulator.
NUM_ROWS=6
NUM_COLS=14
NUM_LETTERS=80

params = {}

class EvilGlobalState:
    u2_ticker = 0
state = EvilGlobalState()

def get_u2(class_id, state):
    state.u2_ticker += 1
    return class_id + ("%05d" % (state.u2_ticker))

# These !u! and & numbers are, respectively, a class ID and an instance ID.
# The instance ID begins with the class ID then has a 5-digit suffix.
params["ANIMATOR_CONTROLLER_U"] = "91"
params["ANIMATOR_HEADER_U2"] = "9100000" # this is a special value

params["ANIMATOR_STATE_MACHINE_U"] = "1107"
params["TASTT_LAYER_U2"] = get_u2("1107", state)

params["MONO_BEHAVIOUR_U"] = "114"
params["SET_LETTERS_SCRIPT_U2"] = get_u2("114", state)

params["ANIMATOR_STATE_U"] = "1102"
params["TASTT_DEFAULT_STATE_U2"] = get_u2("1102", state)
params["TASTT_ACTIVE_STATE_U2"] = get_u2("1102", state)

params["ANIMATOR_STATE_TRANSITION_U"] = "1101"
params["TASTT_ACTIVE_STATE_TRANSITION_U2"] = get_u2("1101", state)
params["TASTT_RESTART_TRANSITION_U2"] = get_u2("1101", state)

HEADER="""
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
"""[1:]

# Generates the sed cmd args required to replace all parameters defined in
# $1, which is an associative array like `params`.
def replaceMacros(lines, macro_defs):
    for k,v in macro_defs.items():
        lines = lines.replace("%" + k + "%", v)
    return lines

def genHeader():
    return replaceMacros(HEADER, params)
print(genHeader())

ANIMATOR_HEADER = """
--- !u!%ANIMATOR_CONTROLLER_U% &%ANIMATOR_HEADER_U2%
AnimatorController:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: TaSTT_fx
  serializedVersion: 5
"""[1:]

ANIMATOR_PARAMETER_HEADER = """
  m_AnimatorParameters:
"""[1:]

ANIMATOR_PARAMETER_INT = """
  - m_Name: %ANIMATOR_PARAMETER_NAME%
    m_Type: 3
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {fileID: 0}
"""[1:]

ANIMATOR_PARAMETER_BOOL = """
  - m_Name: %ANIMATOR_PARAMETER_NAME%
    m_Type: 4
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {fileID: 0}
"""[1:]

ANIMATOR_LAYER_HEADER = """
  m_AnimatorLayers:
"""[1:]

# We have a single animator layer which does everything.
ANIMATOR_LAYER_TASTT = """
  - serializedVersion: 5
    m_Name: TaSTT
    m_StateMachine: {fileID: %TASTT_LAYER_U2%}
    m_Mask: {fileID: 0}
    m_Motions: []
    m_Behaviours: []
    m_BlendingMode: 0
    m_SyncedLayerIndex: -1
    m_DefaultWeight: 0
    m_IKPass: 0
    m_SyncedLayerAffectsTiming: 0
    m_Controller: {fileID: %ANIMATOR_HEADER_U2%}
"""[1:]

ANIMATOR_LAYER_CELL_ANIM = """
  - serializedVersion: 5
    m_Name: %LAYER_NAME%
    m_StateMachine: {fileID: %LAYER_STATE_MACHINE_U2%}
    m_Mask: {fileID: 0}
    m_Motions: []
    m_Behaviours: []
    m_BlendingMode: 0
    m_SyncedLayerIndex: -1
    m_DefaultWeight: 1
    m_IKPass: 0
    m_SyncedLayerAffectsTiming: 0
    m_Controller: {fileID: %ANIMATOR_HEADER_U2%}
"""[1:]

GROUP_NAMES = [
        "_Letter_Row00_Col00_03",
        "_Letter_Row00_Col04_07",
        "_Letter_Row00_Col08_11",
        "_Letter_Row00_Col12_13",
        "_Letter_Row01_Col00_03",
        "_Letter_Row01_Col04_07",
        "_Letter_Row01_Col08_11",
        "_Letter_Row01_Col12_13",
        "_Letter_Row02_Col00_03",
        "_Letter_Row02_Col04_07",
        "_Letter_Row02_Col08_11",
        "_Letter_Row02_Col12_13",
        "_Letter_Row03_Col00_03",
        "_Letter_Row03_Col04_07",
        "_Letter_Row03_Col08_11",
        "_Letter_Row03_Col12_13",
        "_Letter_Row04_Col00_03",
        "_Letter_Row04_Col04_07",
        "_Letter_Row04_Col08_11",
        "_Letter_Row04_Col12_13",
        "_Letter_Row05_Col00_03",
        "_Letter_Row05_Col04_07",
        "_Letter_Row05_Col08_11",
        "_Letter_Row05_Col12_13",
        ]

CELL_NAMES = [
        "_Letter_Row00_Col00",
        "_Letter_Row00_Col01",
        "_Letter_Row00_Col02",
        "_Letter_Row00_Col03",
        "_Letter_Row00_Col04",
        "_Letter_Row00_Col05",
        "_Letter_Row00_Col06",
        "_Letter_Row00_Col07",
        "_Letter_Row00_Col08",
        "_Letter_Row00_Col09",
        "_Letter_Row00_Col10",
        "_Letter_Row00_Col11",
        "_Letter_Row00_Col12",
        "_Letter_Row00_Col13",
        "_Letter_Row01_Col00",
        "_Letter_Row01_Col01",
        "_Letter_Row01_Col02",
        "_Letter_Row01_Col03",
        "_Letter_Row01_Col04",
        "_Letter_Row01_Col05",
        "_Letter_Row01_Col06",
        "_Letter_Row01_Col07",
        "_Letter_Row01_Col08",
        "_Letter_Row01_Col09",
        "_Letter_Row01_Col10",
        "_Letter_Row01_Col11",
        "_Letter_Row01_Col12",
        "_Letter_Row01_Col13",
        "_Letter_Row02_Col00",
        "_Letter_Row02_Col01",
        "_Letter_Row02_Col02",
        "_Letter_Row02_Col03",
        "_Letter_Row02_Col04",
        "_Letter_Row02_Col05",
        "_Letter_Row02_Col06",
        "_Letter_Row02_Col07",
        "_Letter_Row02_Col08",
        "_Letter_Row02_Col09",
        "_Letter_Row02_Col10",
        "_Letter_Row02_Col11",
        "_Letter_Row02_Col12",
        "_Letter_Row02_Col13",
        "_Letter_Row03_Col00",
        "_Letter_Row03_Col01",
        "_Letter_Row03_Col02",
        "_Letter_Row03_Col03",
        "_Letter_Row03_Col04",
        "_Letter_Row03_Col05",
        "_Letter_Row03_Col06",
        "_Letter_Row03_Col07",
        "_Letter_Row03_Col08",
        "_Letter_Row03_Col09",
        "_Letter_Row03_Col10",
        "_Letter_Row03_Col11",
        "_Letter_Row03_Col12",
        "_Letter_Row03_Col13",
        "_Letter_Row04_Col00",
        "_Letter_Row04_Col01",
        "_Letter_Row04_Col02",
        "_Letter_Row04_Col03",
        "_Letter_Row04_Col04",
        "_Letter_Row04_Col05",
        "_Letter_Row04_Col06",
        "_Letter_Row04_Col07",
        "_Letter_Row04_Col08",
        "_Letter_Row04_Col09",
        "_Letter_Row04_Col10",
        "_Letter_Row04_Col11",
        "_Letter_Row04_Col12",
        "_Letter_Row04_Col13",
        "_Letter_Row05_Col00",
        "_Letter_Row05_Col01",
        "_Letter_Row05_Col02",
        "_Letter_Row05_Col03",
        "_Letter_Row05_Col04",
        "_Letter_Row05_Col05",
        "_Letter_Row05_Col06",
        "_Letter_Row05_Col07",
        "_Letter_Row05_Col08",
        "_Letter_Row05_Col09",
        "_Letter_Row05_Col10",
        "_Letter_Row05_Col11",
        "_Letter_Row05_Col12",
        "_Letter_Row05_Col13",
        ]

def genAnimator(state):
    print(replaceMacros(ANIMATOR_HEADER, params))
    print(ANIMATOR_PARAMETER_HEADER)

    params["ANIMATOR_PARAMETER_NAME"] = "TaSTT_Letter"
    print(replaceMacros(ANIMATOR_PARAMETER_INT, params))
    params["ANIMATOR_PARAMETER_NAME"] = "TaSTT_Row"
    print(replaceMacros(ANIMATOR_PARAMETER_INT, params))
    params["ANIMATOR_PARAMETER_NAME"] = "TaSTT_Col"
    print(replaceMacros(ANIMATOR_PARAMETER_INT, params))
    params["ANIMATOR_PARAMETER_NAME"] = "TaSTT_Active"
    print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))
    params["ANIMATOR_PARAMETER_NAME"] = "TaSTT_Dummy"
    print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

    print(replaceMacros(ANIMATOR_LAYER_HEADER, params))
    print(replaceMacros(ANIMATOR_LAYER_TASTT, params))
genAnimator(state)

TASTT_LAYER_HEADER = """
--- !u!%ANIMATOR_STATE_MACHINE_U% &%TASTT_LAYER_U2%
AnimatorStateMachine:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: TaSTT
  m_ChildStates:
"""[1:]

TASTT_LAYER_HEADER_CHILD_STATE = """
  - serializedVersion: 1
    m_State: {fileID: %TASTT_STATE_U2%}
    m_Position: {x: 330, y: -60, z: 0}
"""[1:]

TASTT_LAYER_FOOTER = """
  m_ChildStateMachines: []
  m_AnyStateTransitions: []
  m_EntryTransitions: []
  m_StateMachineTransitions: {}
  m_StateMachineBehaviours: []
  m_AnyStatePosition: {x: 50, y: 20, z: 0}
  m_EntryPosition: {x: 50, y: 120, z: 0}
  m_ExitPosition: {x: 800, y: 120, z: 0}
  m_ParentStateMachinePosition: {x: 800, y: 20, z: 0}
  m_DefaultState: {fileID: %TASTT_DEFAULT_STATE_U2%}
"""[1:]

# Default state.
# One transition to TaSTT_Active.
TASTT_DEFAULT_STATE = """
--- !u!%ANIMATOR_STATE_U% &%TASTT_DEFAULT_STATE_U2%
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: TaSTT_Do_Nothing
  m_Speed: 1
  m_CycleOffset: 0
  m_Transitions:
  - {fileID: %TASTT_ACTIVE_STATE_TRANSITION_U2%}
  m_StateMachineBehaviours: []
  m_Position: {x: 50, y: 50, z: 0}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 0
  m_Mirror: 0
  m_SpeedParameterActive: 0
  m_MirrorParameterActive: 0
  m_CycleOffsetParameterActive: 0
  m_TimeParameterActive: 0
  m_Motion: {fileID: 0}
  m_Tag: 
  m_SpeedParameter: 
  m_MirrorParameter: 
  m_CycleOffsetParameter: 
  m_TimeParameter: 
"""[1:]

# Transition from TaSTT_Do_nothing. to TaSTT_Active.
# Params:
#   %TASTT_ACTIVE_STATE_TRANSITION_U2%
#   %TASTT_ROW_STATE_U2% - address of row state we're transitioning to
TASTT_ACTIVE_STATE_TRANSITION = """
--- !u!1101 &%TASTT_ACTIVE_STATE_TRANSITION_U2%
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 1
    m_ConditionEvent: TaSTT_Active
    m_EventTreshold: 1
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: %TASTT_ACTIVE_STATE_U2%}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0
  m_TransitionOffset: 0
  m_ExitTime: 0.75
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
"""[1:]

# State reached when TaSTT_Active = True.
# One transition per row.
TASTT_ACTIVE_STATE_HEADER = """
--- !u!1102 &%TASTT_ACTIVE_STATE_U2%
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: TaSTT_Active
  m_Speed: 1
  m_CycleOffset: 0
  m_Transitions:
"""[1:]

TASTT_ACTIVE_STATE_HEADER_TRANSITION = """
  - {fileID: %TASTT_TRANSITION_U2%}
"""[1:]

TASTT_ACTIVE_STATE_FOOTER = """
  m_StateMachineBehaviours: []
  m_Position: {x: 50, y: 50, z: 0}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 0
  m_Mirror: 0
  m_SpeedParameterActive: 0
  m_MirrorParameterActive: 0
  m_CycleOffsetParameterActive: 0
  m_TimeParameterActive: 0
  m_Motion: {fileID: 0}
  m_Tag: 
  m_SpeedParameter: 
  m_MirrorParameter: 
  m_CycleOffsetParameter: 
  m_TimeParameter: 
"""[1:]

# Transition from TaSTT_Active to TaSTT_Row*.
# Params:
#   TRANSITION_THRESHOLD: The row to transition to (int).
#   DST_STATE_U2
TASTT_ROW_STATE_TRANSITION = """
--- !u!1101 &%TRANSITION_U2%
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 6
    m_ConditionEvent: TaSTT_Row
    m_EventTreshold: %TRANSITION_THRESHOLD%
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: %DST_STATE_U2%}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0
  m_TransitionOffset: 0
  m_ExitTime: 0.75
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
"""[1:]

# State reached after TaSTT_Active.
# One transition per column.
# Params:
#   %TASTT_STATE_NAME%: TaSTT_Row[0-9][0-9].
#   %TASTT_TRANSITION_U2%
TASTT_ROW_STATE_HEADER = """
--- !u!1102 &%TASTT_STATE_U2%
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: %TASTT_STATE_NAME%
  m_Speed: 1
  m_CycleOffset: 0
  m_Transitions:
"""[1:]

TASTT_ROW_STATE_HEADER_TRANSITION = """
  - {fileID: %TASTT_TRANSITION_U2%}
"""[1:]

TASTT_ROW_STATE_FOOTER = """
  m_StateMachineBehaviours: []
  m_Position: {x: 50, y: 50, z: 0}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 0
  m_Mirror: 0
  m_SpeedParameterActive: 0
  m_MirrorParameterActive: 0
  m_CycleOffsetParameterActive: 0
  m_TimeParameterActive: 0
  m_Motion: {fileID: 0}
  m_Tag: 
  m_SpeedParameter: 
  m_MirrorParameter: 
  m_CycleOffsetParameter: 
  m_TimeParameter: 
"""[1:]

# Transition from TaSTT_Row* to TaSTT_Row*_Col*.
# Params:
#   TRANSITION_THRESHOLD: The col to transition to (int).
#   DST_STATE_U2
TASTT_COL_STATE_TRANSITION = """
--- !u!1101 &%TASTT_TRANSITION_U2%
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 6
    m_ConditionEvent: TaSTT_Col
    m_EventTreshold: %TRANSITION_THRESHOLD%
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: %DST_STATE_U2%}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0
  m_TransitionOffset: 0
  m_ExitTime: 0.75
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
"""[1:]

# State reached after TaSTT_Row*.
# One transition per letter.
# Params:
#   %TASTT_STATE_NAME%: TaSTT_Row[0-9][0-9]_Col[0-9][0-9]
#   %TASTT_TRANSITION_U2%
TASTT_COL_STATE_HEADER = """
--- !u!1102 &%TASTT_STATE_U2%
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: %TASTT_STATE_NAME%
  m_Speed: 1
  m_CycleOffset: 0
  m_Transitions:
"""[1:]

TASTT_COL_STATE_HEADER_TRANSITION = """
  - {fileID: %TASTT_TRANSITION_U2%}
"""[1:]

TASTT_COL_STATE_FOOTER = """
  m_StateMachineBehaviours: []
  m_Position: {x: 50, y: 50, z: 0}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 0
  m_Mirror: 0
  m_SpeedParameterActive: 0
  m_MirrorParameterActive: 0
  m_CycleOffsetParameterActive: 0
  m_TimeParameterActive: 0
  m_Motion: {fileID: 0}
  m_Tag: 
  m_SpeedParameter: 
  m_MirrorParameter: 
  m_CycleOffsetParameter: 
  m_TimeParameter: 
"""

# Transition from TaSTT_Row*_Col* to TaSTT_Row*_Col*_Letter*.
# Params:
#   TRANSITION_THRESHOLD: The row to transition to (int).
#   DST_STATE_U2
TASTT_LETTER_STATE_TRANSITION = """
--- !u!1101 &%TASTT_TRANSITION_U2%
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 6
    m_ConditionEvent: TaSTT_Letter
    m_EventTreshold: %TRANSITION_THRESHOLD%
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: %DST_STATE_U2%}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0
  m_TransitionOffset: 0
  m_ExitTime: 0.75
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
"""[1:]

# State reached after TaSTT_Row*_Col*.
# One transition back up to TaSTT_Do_Nothing.
# Params:
#   %TASTT_STATE_NAME%: TaSTT_Row[0-9][0-9]_Col[0-9][0-9]_Letter[0-9][0-9][0-9]
#  %TASTT_ANIM_GUID%: GUID of the animation to play
#  %TASTT_RESTART_TRANSITION_U2%: U2 of transition back to
#      TaSTT_Do_Nothing.
TASTT_LETTER_STATE = """
--- !u!1102 &%TASTT_STATE_U2%
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: %TASTT_STATE_NAME%
  m_Speed: 1
  m_CycleOffset: 0
  m_Transitions:
  - {fileID: %TASTT_RESTART_TRANSITION_U2%}
  m_StateMachineBehaviours: []
  m_Position: {x: 50, y: 50, z: 0}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 0
  m_Mirror: 0
  m_SpeedParameterActive: 0
  m_MirrorParameterActive: 0
  m_CycleOffsetParameterActive: 0
  m_TimeParameterActive: 0
  m_Motion: {fileID: 7400000, guid: %TASTT_ANIM_GUID%, type: 2}
  m_Tag: 
  m_SpeedParameter: 
  m_MirrorParameter: 
  m_CycleOffsetParameter: 
  m_TimeParameter: 
"""[1:]

TASTT_RESTART_TRANSITION = """
--- !u!1101 &%TASTT_RESTART_TRANSITION_U2%
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 2
    m_ConditionEvent: TaSTT_Dummy
    m_EventTreshold: 0
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: %TASTT_DEFAULT_STATE_U2%}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0
  m_TransitionOffset: 0
  m_ExitTime: 0.75
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
"""

def getAnimationGuid(anim_meta_filename):
    with open(anim_meta_filename, 'r') as f:
        for line in f:
            if "guid" in line:
                return line.split()[1]

def genTasttLayer(state):
    # Generate return-home transition
    print(replaceMacros(TASTT_RESTART_TRANSITION, params))

    # Default state.
    print(replaceMacros(TASTT_DEFAULT_STATE, params))

    # Active state transition.
    print(replaceMacros(TASTT_ACTIVE_STATE_TRANSITION, params))

    # Active state.
    print(replaceMacros(TASTT_ACTIVE_STATE_HEADER, params))
    for row in range(0, NUM_ROWS):
        params["TASTT_TRANSITION_ROW%02d_U2" % row] = get_u2("1101", state)
        params["TASTT_TRANSITION_U2"] = params["TASTT_TRANSITION_ROW%02d_U2" % row]
        print(replaceMacros(TASTT_ACTIVE_STATE_HEADER_TRANSITION, params))
    print(replaceMacros(TASTT_ACTIVE_STATE_FOOTER, params))

    # Row state transitions (one per row).
    for row in range(0, NUM_ROWS):
        params["TRANSITION_U2"] = params["TASTT_TRANSITION_ROW%02d_U2" % row]
        params["TRANSITION_THRESHOLD"] = str(row)
        params["TASTT_ROW%02d_STATE_U2" % row] = get_u2("1102", state)
        params["DST_STATE_U2"] = params["TASTT_ROW%02d_STATE_U2" % row]
        print(replaceMacros(TASTT_ROW_STATE_TRANSITION, params))

    # Row states (one per row)..
    for row in range(0, NUM_ROWS):
        params["TASTT_STATE_U2"] = params["TASTT_ROW%02d_STATE_U2" % row]
        params["TASTT_STATE_NAME"] = "TaSTT_Row%02d" % row
        print(replaceMacros(TASTT_ROW_STATE_HEADER, params))
        for col in range(0, NUM_COLS):
            params["TASTT_TRANSITION_ROW%02d_COL%02d_U2" % (row, col)] = get_u2("1101", state)
            params["TASTT_TRANSITION_U2"] = params["TASTT_TRANSITION_ROW%02d_COL%02d_U2" % (row, col)]
            print(replaceMacros(TASTT_ROW_STATE_HEADER_TRANSITION, params))
        print(replaceMacros(TASTT_ROW_STATE_FOOTER, params))

    # Column state transitions (one per row * column).
    for row in range(0, NUM_ROWS):
        for col in range(0, NUM_COLS):
            params["TASTT_TRANSITION_U2"] = params["TASTT_TRANSITION_ROW%02d_COL%02d_U2" % (row, col)]
            params["TRANSITION_THRESHOLD"] = str(col)
            params["TASTT_ROW%02d_COL%02d_STATE_U2" % (row, col)] = get_u2("1102", state)
            params["DST_STATE_U2"] = params["TASTT_ROW%02d_COL%02d_STATE_U2" % (row, col)]
            print(replaceMacros(TASTT_COL_STATE_TRANSITION, params))

    # Column states (one per row * column).
    for row in range(0, NUM_ROWS):
        for col in range(0, NUM_COLS):
            params["TASTT_STATE_U2"] = params["TASTT_ROW%02d_COL%02d_STATE_U2" % (row, col)]
            params["TASTT_STATE_NAME"] = "TaSTT_Row%02d_Col%02d" % (row,
                    col)
            print(replaceMacros(TASTT_COL_STATE_HEADER, params))
            for letter in range(0, NUM_LETTERS):
                params["TASTT_TRANSITION_ROW%02d_COL%02d_LETTER%02d_U2" % (row, col, letter)] = get_u2("1101", state)
                params["TASTT_TRANSITION_U2"] = params["TASTT_TRANSITION_ROW%02d_COL%02d_LETTER%02d_U2" % (row, col, letter)]
                print(replaceMacros(TASTT_COL_STATE_HEADER_TRANSITION, params))
            print(replaceMacros(TASTT_COL_STATE_FOOTER, params))

    # Letter state transitions (one per row * column * letter).
    for row in range(0, NUM_ROWS):
        for col in range(0, NUM_COLS):
            for letter in range(0, NUM_LETTERS):
                params["TASTT_TRANSITION_U2"] = params["TASTT_TRANSITION_ROW%02d_COL%02d_LETTER%02d_U2" % (row, col, letter)]
                params["TRANSITION_THRESHOLD"] = str(letter)
                params["TASTT_ROW%02d_COL%02d_LETTER%02d_STATE_U2" % (row, col, letter)] = get_u2("1102", state)
                params["DST_STATE_U2"] = params["TASTT_ROW%02d_COL%02d_LETTER%02d_STATE_U2" % (row, col, letter)]
                print(replaceMacros(TASTT_LETTER_STATE_TRANSITION, params))

    # Letter states (one per row * column * letter).
    for row in range(0, NUM_ROWS):
        for col in range(0, NUM_COLS):
            for letter in range(0, NUM_LETTERS):
                params["TASTT_STATE_U2"] = params["TASTT_ROW%02d_COL%02d_LETTER%02d_STATE_U2" % (row, col, letter)]
                params["TASTT_STATE_NAME"] = "TaSTT_Row%02d_Col%02d_Letter%02d" % (row, col, letter)
                # Get the GUID of the animation we will play here.
                anim_meta_filename = "generated/animations/_Letter_Row%02d_Col%02d_Letter%02d.anim.meta" % (row, col, letter)
                params["TASTT_ANIM_GUID"] = getAnimationGuid(anim_meta_filename)
                print(replaceMacros(TASTT_LETTER_STATE, params))

    # TaSTT layer.
    print(replaceMacros(TASTT_LAYER_HEADER, params))

    params["TASTT_STATE_U2"] = params["TASTT_DEFAULT_STATE_U2"]
    print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    params["TASTT_STATE_U2"] = params["TASTT_ACTIVE_STATE_U2"]
    print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    for row in range(0, NUM_ROWS):
        params["TASTT_STATE_U2"] = params["TASTT_ROW%02d_STATE_U2" % row]
        print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    for row in range(0, NUM_ROWS):
        for col in range(0, NUM_COLS):
            params["TASTT_STATE_U2"] = params["TASTT_ROW%02d_COL%02d_STATE_U2" % (row, col)]
            print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    for row in range(0, NUM_ROWS):
        for col in range(0, NUM_COLS):
            for letter in range(0, NUM_LETTERS):
                params["TASTT_STATE_U2"] = params["TASTT_ROW%02d_COL%02d_LETTER%02d_STATE_U2" % (row, col, letter)]
                print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

genTasttLayer(state)
