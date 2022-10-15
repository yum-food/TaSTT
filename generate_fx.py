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

from generate_utils import replaceMacros
from generate_utils import getDummyParam
from generate_utils import getResize0Param
from generate_utils import getResize1Param
from generate_utils import getLayerParam
from generate_utils import getSelectParam
from generate_utils import getEnableParam
from generate_utils import getShaderParam
from generate_utils import getAnimationPath
from generate_utils import NUM_LAYERS
from generate_utils import CHARS_PER_CELL

import generate_utils

# To debug, I recommend setting these values low and manually moving things
# around in the animator. Then run using Lyuma's avatar 3.0 emulator.
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
params["ANIMATOR_HEADER_U2"] = "9100000"

params["ANIMATOR_STATE_MACHINE_U"] = "1107"

params["MONO_BEHAVIOUR_U"] = "114"

params["ANIMATOR_STATE_U"] = "1102"

params["ANIMATOR_STATE_TRANSITION_U"] = "1101"

HEADER="""
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
"""[1:][:-1]

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
"""[1:][:-1]

ANIMATOR_PARAMETER_HEADER = """
  m_AnimatorParameters:
"""[1:][:-1]

ANIMATOR_PARAMETER_INT = """
  - m_Name: %ANIMATOR_PARAMETER_NAME%
    m_Type: 3
    m_DefaultFloat: 0
    m_DefaultInt: 64
    m_DefaultBool: 0
    m_Controller: {fileID: %ANIMATOR_HEADER_U2%}
"""[1:][:-1]

ANIMATOR_PARAMETER_BOOL = """
  - m_Name: %ANIMATOR_PARAMETER_NAME%
    m_Type: 4
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {fileID: %ANIMATOR_HEADER_U2%}
"""[1:][:-1]

ANIMATOR_LAYER_HEADER = """
  m_AnimatorLayers:
"""[1:][:-1]

ANIMATOR_LAYER_TASTT = """
  - serializedVersion: 5
    m_Name: %TASTT_LAYER_NAME%
    m_StateMachine: {fileID: %TASTT_LAYER_U2%}
    m_Mask: {fileID: 0}
    m_Motions: []
    m_Behaviours: []
    m_BlendingMode: 0
    m_SyncedLayerIndex: -1
    m_DefaultWeight: 1
    m_IKPass: 0
    m_SyncedLayerAffectsTiming: 0
    m_Controller: {fileID: %ANIMATOR_HEADER_U2%}
"""[1:][:-1]

def genAnimator(state):
    print(replaceMacros(ANIMATOR_HEADER, params))
    print(ANIMATOR_PARAMETER_HEADER)

    params["ANIMATOR_PARAMETER_NAME"] = getDummyParam()
    print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

    params["ANIMATOR_PARAMETER_NAME"] = generate_utils.getResizeEnableParam()
    print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

    params["ANIMATOR_PARAMETER_NAME"] = generate_utils.getResize0Param()
    print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

    params["ANIMATOR_PARAMETER_NAME"] = generate_utils.getResize1Param()
    print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

    params["ANIMATOR_PARAMETER_NAME"] = getEnableParam()
    print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

    params["ANIMATOR_PARAMETER_NAME"] = generate_utils.getHandToggleParam()
    print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

    params["ANIMATOR_PARAMETER_NAME"] = generate_utils.getHipToggleParam()
    print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

    for i in range(0, NUM_LAYERS):
        params["ANIMATOR_PARAMETER_NAME"] = getLayerParam(i)
        print(replaceMacros(ANIMATOR_PARAMETER_INT, params))

        params["ANIMATOR_PARAMETER_NAME"] = getSelectParam(i, 0)
        print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

        params["ANIMATOR_PARAMETER_NAME"] = getSelectParam(i, 1)
        print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

        params["ANIMATOR_PARAMETER_NAME"] = getSelectParam(i, 2)
        print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

        params["ANIMATOR_PARAMETER_NAME"] = getSelectParam(i, 3)
        print(replaceMacros(ANIMATOR_PARAMETER_BOOL, params))

    print(replaceMacros(ANIMATOR_LAYER_HEADER, params))

    for i in range(0, NUM_LAYERS):
        params[getLayerParam(i) + "_LAYER_U2"] = get_u2("1107", state)
        params["TASTT_LAYER_U2"] = params[getLayerParam(i) + "_LAYER_U2"]
        params["TASTT_LAYER_NAME"] = getLayerParam(i)
        print(replaceMacros(ANIMATOR_LAYER_TASTT, params))

    params["TASTT_HAND_TOGGLE_LAYER_U2"] = get_u2("1107", state)
    params["TASTT_LAYER_U2"] = params["TASTT_HAND_TOGGLE_LAYER_U2"]
    params["TASTT_LAYER_NAME"] = generate_utils.getHandToggleParam()
    print(replaceMacros(ANIMATOR_LAYER_TASTT, params))

    params["TASTT_HIP_TOGGLE_LAYER_U2"] = get_u2("1107", state)
    params["TASTT_LAYER_U2"] = params["TASTT_HIP_TOGGLE_LAYER_U2"]
    params["TASTT_LAYER_NAME"] = generate_utils.getHipToggleParam()
    print(replaceMacros(ANIMATOR_LAYER_TASTT, params))

    params["TASTT_RESIZE_LAYER_U2"] = get_u2("1107", state)
    params["TASTT_LAYER_U2"] = params["TASTT_RESIZE_LAYER_U2"]
    params["TASTT_LAYER_NAME"] = "TaSTT_Resize"
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
  m_Name: %TASTT_LAYER_NAME%
  m_ChildStates:
"""[1:][:-1]

TASTT_LAYER_HEADER_CHILD_STATE = """
  - serializedVersion: 1
    m_State: {fileID: %TASTT_STATE_U2%}
    m_Position: {x: 330, y: -60, z: 0}
"""[1:][:-1]

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
"""[1:][:-1]

# State with one transition.
# Params:
#   %TASTT_STATE_NAME%: the name of this state
#   %TASTT_STATE_TRANSITION_U2%: the U2 of the transition to the next state
#   %TASTT_STATE_TRANSITION_U2%
TASTT_UNARY_STATE = """
--- !u!%ANIMATOR_STATE_U% &%TASTT_STATE_U2%
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
  - {fileID: %TASTT_STATE_TRANSITION_U2%}
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
"""[1:][:-1]

# State with two transitions.
# Params:
#   %TASTT_STATE_NAME%: the name of this state
#   %TASTT_STATE_TRANSITION_0_U2%
#   %TASTT_STATE_TRANSITION_1_U2%
#   %TASTT_STATE_TRANSITION_U2%
TASTT_BINARY_STATE = """
--- !u!%ANIMATOR_STATE_U% &%TASTT_STATE_U2%
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
  - {fileID: %TASTT_STATE_TRANSITION_0_U2%}
  - {fileID: %TASTT_STATE_TRANSITION_1_U2%}
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
"""[1:][:-1]

TASTT_NARY_STATE_HEADER = """
--- !u!%ANIMATOR_STATE_U% &%TASTT_STATE_U2%
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
"""[1:][:-1]

TASTT_NARY_STATE_HEADER_TRANSITION = """
  - {fileID: %TASTT_STATE_TRANSITION_U2%}
"""[1:][:-1]

TASTT_NARY_STATE_FOOTER = """
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
"""[1:][:-1]

# Transition from TaSTT_Do_nothing. to TaSTT_Active.
# Params:
#   %BOOL_PARAM% - the name of the parameter to branch on
#   %THRESHOLD% - the condition to branch on (1 == true)
#   %TASTT_ACTIVE_STATE_TRANSITION_U2%
#   %TASTT_ROW_STATE_U2% - address of row state we're transitioning to
# A bizarre quirk: when branching false, m_ConditionMode = 2; else
# m_ConditionMode = 1.
TASTT_BOOL_STATE_UNARY_TRANSITION = """
--- !u!1101 &%TASTT_STATE_TRANSITION_U2%
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: %MODE%
    m_ConditionEvent: %BOOL_PARAM%
    m_EventTreshold: %THRESHOLD%
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: %DST_STATE_U2%}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0
  m_TransitionOffset: 0
  m_ExitTime: 1
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
"""[1:][:-1]

TASTT_BOOL_STATE_BINARY_TRANSITION = """
--- !u!1101 &%TASTT_STATE_TRANSITION_U2%
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: %MODE0%
    m_ConditionEvent: %BOOL_PARAM0%
    m_EventTreshold: %THRESHOLD0%
  - m_ConditionMode: %MODE1%
    m_ConditionEvent: %BOOL_PARAM1%
    m_EventTreshold: %THRESHOLD1%
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: %DST_STATE_U2%}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0.5
  m_TransitionOffset: 0
  m_ExitTime: 1
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
"""[1:][:-1]

TASTT_INT_STATE_TRANSITION = """
--- !u!1101 &%TASTT_STATE_TRANSITION_U2%
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 6
    m_ConditionEvent: %INT_PARAM%
    m_EventTreshold: %TRANSITION_THRESHOLD%
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: %DST_STATE_U2%}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0
  m_TransitionOffset: 0
  m_ExitTime: 1
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
"""[1:][:-1]

# State reached after TaSTT_Row*_Col*.
# One transition back up to TaSTT_Do_Nothing.
# Params:
#   %TASTT_STATE_NAME%: TaSTT_Row[0-9][0-9]_Col[0-9][0-9]_Letter[0-9][0-9][0-9]
#  %TASTT_ANIM_GUID%: GUID of the animation to play
#  %TASTT_RESTART_TRANSITION_U2%: U2 of transition back to
#      TaSTT_Do_Nothing.
TASTT_ANIM_STATE = """
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
  - {fileID: %TASTT_STATE_TRANSITION_U2%}
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
"""[1:][:-1]

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
  m_ExitTime: 1
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
"""[1:][:-1]

def getAnimationGuid(anim_meta_filename):
    with open(anim_meta_filename, 'r') as f:
        for line in f:
            if "guid" in line:
                return line.split()[1]

def getDefaultStateName(which_layer):
    return "TaSTT_L%02d_Do_Nothing" % which_layer

def getDefaultStateNameResizeLayer():
    return "TaSTT_Resize_Do_Nothing"

def getActiveStateName(which_layer):
    return "TaSTT_L%02d_Active" % which_layer

def getS0StateName(which_layer, s0):
    return "TaSTT_L%02d_S%02d" % (which_layer, s0)

def getS1StateName(which_layer, s0, s1):
    return "TaSTT_L%02d_S%02d_S%02d" % (which_layer, s0, s1)

def getS2StateName(which_layer, s0, s1, s2):
    return "TaSTT_L%02d_S%02d_S%02d_S%02d" % (which_layer, s0, s1, s2)

def getS3StateName(which_layer, s0, s1, s2, s3):
    return "TaSTT_L%02d_S%02d_S%02d_S%02d_S%02d" % (which_layer, s0, s1, s2, s3)

def getLetterStateName(which_layer, s0, s1, s2, s3, letter):
    return "TaSTT_L%02d_S%02d_S%02d_S%02d_S%02d_L%03d" % (which_layer, s0, s1, s2, s3, letter)

def getResizeStateName(e0, e1):
    return "TaSTT_Resize_E%d_E%d" % (e0, e1)

def getReturnHomeTransitionName(which_layer, s0, s1, s2, s3, letter):
    return "TASTT_RETURN_HOME_TRANSITION_L%02d_S%02d_S%02d_S%02d_S%02d_L%03d" % (which_layer, s0, s1, s2, s3, letter)

def getReturnHomeTransitionNameResizeLayer(e0, e1):
    return "TASTT_RETURN_HOME_TRANSITION_E%d_E%d" % (e0, e1)

def genTasttLayer(state, which_layer):
    # Default state.
    params["TASTT_DEFAULT_STATE_U2"] = get_u2("1102", state)
    params["TASTT_STATE_U2"] = params["TASTT_DEFAULT_STATE_U2"]
    params["TASTT_STATE_NAME"] = getDefaultStateName(which_layer)
    params["TASTT_STATE_TRANSITION_U2"] = get_u2("1101", state)
    anim_meta_filename = "Animations/TaSTT_Do_Nothing.anim.meta"
    params["TASTT_ANIM_GUID"] = getAnimationGuid(anim_meta_filename)
    print(replaceMacros(TASTT_ANIM_STATE, params))

    # Active state transition.
    params["BOOL_PARAM"] = getEnableParam()
    params["THRESHOLD"] = str(1)
    params["MODE"] = str(1)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
    params["ACTIVE_STATE_U2"] = get_u2("1102", state)
    params["DST_STATE_U2"] = params["ACTIVE_STATE_U2"]
    print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # Active state.
    params["TASTT_STATE_U2"] = params["ACTIVE_STATE_U2"]
    params["TASTT_STATE_NAME"] = getActiveStateName(which_layer)
    params[getS0StateName(which_layer, 0) + "_TRANSITION_U2"] = get_u2("1101", state)
    params["TASTT_STATE_TRANSITION_0_U2"] = params[getS0StateName(which_layer, 0) + "_TRANSITION_U2"]
    params[getS0StateName(which_layer, 1) + "_TRANSITION_U2"] = get_u2("1101", state)
    params["TASTT_STATE_TRANSITION_1_U2"] = params[getS0StateName(which_layer, 1) + "_TRANSITION_U2"]
    print(replaceMacros(TASTT_BINARY_STATE, params))

    # S0 state transition.
    for s0 in range(0,2):
        params["TASTT_STATE_TRANSITION_U2"] = params[getS0StateName(which_layer, s0) + "_TRANSITION_U2"]
        params["BOOL_PARAM"] = getSelectParam(which_layer, 0)
        params["THRESHOLD"] = str(s0)
        params["MODE"] = str(2 - s0)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
        params[getS0StateName(which_layer, s0) + "_U2"] = get_u2("1102", state)
        params["DST_STATE_U2"] = params[getS0StateName(which_layer, s0) + "_U2"]
        print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # S0 state.
    for s0 in range(0,2):
        params["TASTT_STATE_U2"] = params[getS0StateName(which_layer, s0) + "_U2"]
        params["TASTT_STATE_NAME"] = getS0StateName(which_layer, s0)
        params[getS1StateName(which_layer, s0, 0) + "_TRANSITION_U2"] = get_u2("1101", state)
        params["TASTT_STATE_TRANSITION_0_U2"] = params[getS1StateName(which_layer, s0, 0) + "_TRANSITION_U2"]
        params[getS1StateName(which_layer, s0, 1) + "_TRANSITION_U2"] = get_u2("1101", state)
        params["TASTT_STATE_TRANSITION_1_U2"] = params[getS1StateName(which_layer, s0, 1) + "_TRANSITION_U2"]
        print(replaceMacros(TASTT_BINARY_STATE, params))

    # S1 state transition.
    for s0 in range(0,2):
        for s1 in range(0,2):
            params["TASTT_STATE_TRANSITION_U2"] = params[getS1StateName(which_layer, s0, s1) + "_TRANSITION_U2"]
            params["BOOL_PARAM"] = getSelectParam(which_layer, 1)
            params["THRESHOLD"] = str(s1)
            params["MODE"] = str(2 - s1)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
            params[getS1StateName(which_layer, s0, s1) + "_U2"] = get_u2("1102", state)
            params["DST_STATE_U2"] = params[getS1StateName(which_layer, s0, s1) + "_U2"]
            print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # S1 state.
    for s0 in range(0,2):
        for s1 in range(0,2):
            params["TASTT_STATE_U2"] = params[getS1StateName(which_layer, s0, s1) + "_U2"]
            params["TASTT_STATE_NAME"] = getS1StateName(which_layer, s0, s1)
            params[getS2StateName(which_layer, s0, s1, 0) + "_TRANSITION_U2"] = get_u2("1101", state)
            params["TASTT_STATE_TRANSITION_0_U2"] = params[getS2StateName(which_layer, s0, s1, 0) + "_TRANSITION_U2"]
            params[getS2StateName(which_layer, s0, s1, 1) + "_TRANSITION_U2"] = get_u2("1101", state)
            params["TASTT_STATE_TRANSITION_1_U2"] = params[getS2StateName(which_layer, s0, s1, 1) + "_TRANSITION_U2"]
            print(replaceMacros(TASTT_BINARY_STATE, params))

    # S2 state transition.
    for s0 in range(0,2):
        for s1 in range(0,2):
            for s2 in range(0,2):
                params["TASTT_STATE_TRANSITION_U2"] = params[getS2StateName(which_layer, s0, s1, s2) + "_TRANSITION_U2"]
                params["BOOL_PARAM"] = getSelectParam(which_layer, 2)
                params["THRESHOLD"] = str(s2)
                params["MODE"] = str(2 - s2)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
                params[getS2StateName(which_layer, s0, s1, s2) + "_U2"] = get_u2("1102", state)
                params["DST_STATE_U2"] = params[getS2StateName(which_layer, s0, s1, s2) + "_U2"]
                print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # S2 state.
    for s0 in range(0,2):
        for s1 in range(0,2):
            for s2 in range(0,2):
                params["TASTT_STATE_U2"] = params[getS2StateName(which_layer, s0, s1, s2) + "_U2"]
                params["TASTT_STATE_NAME"] = getS2StateName(which_layer, s0, s1, s2)
                params[getS3StateName(which_layer, s0, s1, s2, 0) + "_TRANSITION_U2"] = get_u2("1101", state)
                params["TASTT_STATE_TRANSITION_0_U2"] = params[getS3StateName(which_layer, s0, s1, s2, 0) + "_TRANSITION_U2"]
                params[getS3StateName(which_layer, s0, s1, s2, 1) + "_TRANSITION_U2"] = get_u2("1101", state)
                params["TASTT_STATE_TRANSITION_1_U2"] = params[getS3StateName(which_layer, s0, s1, s2, 1) + "_TRANSITION_U2"]
                print(replaceMacros(TASTT_BINARY_STATE, params))

    # S3 state transition.
    for s0 in range(0,2):
        for s1 in range(0,2):
            for s2 in range(0,2):
                for s3 in range(0,2):
                    params["TASTT_STATE_TRANSITION_U2"] = params[getS3StateName(which_layer, s0, s1, s2, s3) + "_TRANSITION_U2"]
                    params["BOOL_PARAM"] = getSelectParam(which_layer, 3)
                    params["THRESHOLD"] = str(s3)
                    params["MODE"] = str(2 - s3)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
                    params[getS3StateName(which_layer, s0, s1, s2, s3) + "_U2"] = get_u2("1102", state)
                    params["DST_STATE_U2"] = params[getS3StateName(which_layer, s0, s1, s2, s3) + "_U2"]
                    print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # S3 state.
    for s0 in range(0,2):
        for s1 in range(0,2):
            for s2 in range(0,2):
                for s3 in range(0,2):
                    params["TASTT_STATE_U2"] = params[getS3StateName(which_layer, s0, s1, s2, s3) + "_U2"]
                    params["TASTT_STATE_NAME"] = getS3StateName(which_layer, s0, s1, s2, s3)
                    print(replaceMacros(TASTT_NARY_STATE_HEADER, params))
                    for letter in range(0, CHARS_PER_CELL):
                        params[getLetterStateName(which_layer, s0, s1, s2, s3, letter) + "_TRANSITION_U2"] = get_u2("1101", state)
                        params["TASTT_STATE_TRANSITION_U2"] = params[getLetterStateName(which_layer, s0, s1, s2, s3, letter) + "_TRANSITION_U2"]
                        print(replaceMacros(TASTT_NARY_STATE_HEADER_TRANSITION, params))
                    print(replaceMacros(TASTT_NARY_STATE_FOOTER, params))

    # Letter state transition.
    for s0 in range(0,2):
        for s1 in range(0,2):
            for s2 in range(0,2):
                for s3 in range(0,2):
                    for letter in range(0, CHARS_PER_CELL):
                        params["TASTT_STATE_TRANSITION_U2"] = params[getLetterStateName(which_layer, s0, s1, s2, s3, letter) + "_TRANSITION_U2"]
                        params["INT_PARAM"] = getLayerParam(which_layer)
                        params["TRANSITION_THRESHOLD"] = str(letter)
                        params[getLetterStateName(which_layer, s0, s1, s2, s3, letter) + "_U2"] = get_u2("1102", state)
                        params["DST_STATE_U2"] = params[getLetterStateName(which_layer, s0, s1, s2, s3, letter) + "_U2"]
                        print(replaceMacros(TASTT_INT_STATE_TRANSITION, params))

    # Letter state.
    for s0 in range(0,2):
        for s1 in range(0,2):
            for s2 in range(0,2):
                for s3 in range(0,2):
                    for letter in range(0, CHARS_PER_CELL):
                        params["TASTT_STATE_U2"] = params[getLetterStateName(which_layer, s0, s1, s2, s3, letter) + "_U2"]
                        params["TASTT_STATE_NAME"] = getLetterStateName(which_layer, s0, s1, s2, s3, letter)
                        transition_name = getReturnHomeTransitionName(which_layer, s0, s1, s2, s3, letter) + "_U2"
                        params[transition_name] = get_u2("1101", state)
                        params["TASTT_STATE_TRANSITION_U2"] = params[transition_name]
                        anim_meta_filename = getAnimationPath(getShaderParam(which_layer, s0, s1, s2, s3), letter) + ".meta"
                        params["TASTT_ANIM_GUID"] = getAnimationGuid(anim_meta_filename)
                        print(replaceMacros(TASTT_ANIM_STATE, params))

    # Return-home transitions.
    for s0 in range(0,2):
        for s1 in range(0,2):
            for s2 in range(0,2):
                for s3 in range(0,2):
                    for letter in range(0, CHARS_PER_CELL):
                        transition_name = getReturnHomeTransitionName(which_layer, s0, s1, s2, s3, letter) + "_U2"
                        params["TASTT_STATE_TRANSITION_U2"] = params[transition_name]
                        params["BOOL_PARAM"] = getDummyParam()
                        params["THRESHOLD"] = str(0)
                        params["MODE"] = str(2)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
                        params["DST_STATE_U2"] = params["TASTT_DEFAULT_STATE_U2"]
                        print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # TaSTT layer.
    params["TASTT_LAYER_U2"] = params[getLayerParam(which_layer) + "_LAYER_U2"]

    params["TASTT_LAYER_NAME"] = getLayerParam(which_layer)
    print(replaceMacros(TASTT_LAYER_HEADER, params))

    params["TASTT_STATE_U2"] = params["TASTT_DEFAULT_STATE_U2"]
    print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    params["TASTT_STATE_U2"] = params["ACTIVE_STATE_U2"]
    print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    for s0 in range(0,2):
        params["TASTT_STATE_U2"] = params[getS0StateName(which_layer, s0) + "_U2"]
        print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    for s0 in range(0,2):
        for s1 in range(0,2):
            params["TASTT_STATE_U2"] = params[getS1StateName(which_layer, s0, s1) + "_U2"]
            print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    for s0 in range(0,2):
        for s1 in range(0,2):
            for s2 in range(0,2):
                params["TASTT_STATE_U2"] = params[getS2StateName(which_layer, s0, s1, s2) + "_U2"]
                print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    for s0 in range(0,2):
        for s1 in range(0,2):
            for s2 in range(0,2):
                for s3 in range(0,2):
                    params["TASTT_STATE_U2"] = params[getS3StateName(which_layer, s0, s1, s2, s3) + "_U2"]
                    print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    for s0 in range(0,2):
        for s1 in range(0,2):
            for s2 in range(0,2):
                for s3 in range(0,2):
                    for letter in range(0, CHARS_PER_CELL):
                        params["TASTT_STATE_U2"] = params[getLetterStateName(which_layer, s0, s1, s2, s3, letter) + "_U2"]
                        print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    params["TASTT_DEFAULT_STATE_U2"] = params["TASTT_DEFAULT_STATE_U2"]
    print(replaceMacros(TASTT_LAYER_FOOTER, params))

for i in range(0, NUM_LAYERS):
    genTasttLayer(state, i)

def genTasttResizeLayer(state):
    # Default state.
    params["TASTT_DEFAULT_STATE_U2"] = get_u2("1102", state)
    params["TASTT_STATE_U2"] = params["TASTT_DEFAULT_STATE_U2"]
    params["TASTT_STATE_NAME"] = getDefaultStateNameResizeLayer()
    anim_meta_filename = "Animations/TaSTT_Do_Nothing.anim.meta"
    params["TASTT_ANIM_GUID"] = getAnimationGuid(anim_meta_filename)
    params["TASTT_STATE_TRANSITION_U2"] = get_u2("1101", state)
    print(replaceMacros(TASTT_ANIM_STATE, params))

    # Active state transition.
    params["BOOL_PARAM"] = generate_utils.getResizeEnableParam()
    params["THRESHOLD"] = str(1)
    params["MODE"] = str(1)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
    params["ACTIVE_STATE_U2"] = get_u2("1102", state)
    params["DST_STATE_U2"] = params["ACTIVE_STATE_U2"]
    print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # Active state.
    params["TASTT_STATE_U2"] = params["ACTIVE_STATE_U2"]
    params["TASTT_STATE_NAME"] = "TaSTT_Resize_Enabled"
    print(replaceMacros(TASTT_NARY_STATE_HEADER, params))

    for e0 in range(0, 2):
        for e1 in range(0, 2):
            params[getResizeStateName(e0, e1) + "_TRANSITION_U2"] = get_u2("1101", state)
            params["TASTT_STATE_TRANSITION_U2"] = params[getResizeStateName(e0, e1) + "_TRANSITION_U2"]
            print(replaceMacros(TASTT_NARY_STATE_HEADER_TRANSITION, params))

    print(replaceMacros(TASTT_NARY_STATE_FOOTER, params))

    # Animation transitions.
    for e0 in range(0, 2):
        params["THRESHOLD0"] = str(e0)
        params["BOOL_PARAM0"] = generate_utils.getResize0Param()
        params["MODE0"] = str(2 - e0)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
        for e1 in range(0, 2):
            params["THRESHOLD1"] = str(e1)
            params["BOOL_PARAM1"] = generate_utils.getResize1Param()
            params["MODE1"] = str(2 - e1)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.

            params["TASTT_STATE_TRANSITION_U2"] = params[getResizeStateName(e0, e1) + "_TRANSITION_U2"]

            params[getResizeStateName(e0, e1) + "_U2"] = get_u2("1102", state)
            params["DST_STATE_U2"] = params[getResizeStateName(e0, e1) + "_U2"]

            print(replaceMacros(TASTT_BOOL_STATE_BINARY_TRANSITION, params))

    # Animation states.
    for e0 in range(0, 2):
        for e1 in range(0, 2):
            params["TASTT_STATE_NAME"] = getResizeStateName(e0, e1)
            params["TASTT_STATE_U2"] = params[getResizeStateName(e0, e1) + "_U2"]
            transition_name = getReturnHomeTransitionNameResizeLayer(e0, e1) + "_U2"
            params[transition_name] = get_u2("1101", state)
            params["TASTT_STATE_TRANSITION_U2"] = params[transition_name]
            anim_meta_filename="Animations/"
            if e0 == 0 and e1 == 0:
                anim_meta_filename += "TaSTT_Backplate_Resize_00_to_50.anim.meta"
            elif e0 == 0 and e1 == 1:
                anim_meta_filename += "TaSTT_Backplate_Resize_50_to_100.anim.meta"
            elif e0 == 1 and e1 == 0:
                anim_meta_filename += "TaSTT_Backplate_Resize_100_to_50.anim.meta"
            elif e0 == 1 and e1 == 1:
                anim_meta_filename += "TaSTT_Backplate_Resize_50_to_00.anim.meta"
            params["TASTT_ANIM_GUID"] = getAnimationGuid(anim_meta_filename)
            print(replaceMacros(TASTT_ANIM_STATE, params))

    # Generate return-home transitions
    for e0 in range(0, 2):
        for e1 in range(0, 2):
            transition_name = getReturnHomeTransitionNameResizeLayer(e0, e1) + "_U2"
            params["TASTT_STATE_TRANSITION_U2"] = params[transition_name]
            params["BOOL_PARAM"] = getDummyParam()
            params["THRESHOLD"] = str(0)
            params["MODE"] = str(2)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
            params["DST_STATE_U2"] = params["TASTT_DEFAULT_STATE_U2"]
            print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # Layer
    params["TASTT_LAYER_U2"] = params["TASTT_RESIZE_LAYER_U2"]
    print(replaceMacros(TASTT_LAYER_HEADER, params))

    params["TASTT_STATE_U2"] = params["TASTT_DEFAULT_STATE_U2"]
    print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))
    params["TASTT_STATE_U2"] = params["ACTIVE_STATE_U2"]
    print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))
    for e0 in range(0, 2):
        for e1 in range(0, 2):
            params["TASTT_STATE_U2"] = params[getResizeStateName(e0, e1) + "_U2"]
            print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))
    print(replaceMacros(TASTT_LAYER_FOOTER, params))

genTasttResizeLayer(state)

def genTasttHipToggleLayer(state):
    # Default state.
    params["TASTT_HIP_TOGGLE_ON_U2"] = get_u2("1102", state)
    params["TASTT_DEFAULT_STATE_U2"] = params["TASTT_HIP_TOGGLE_ON_U2"]
    params["TASTT_STATE_U2"] = params["TASTT_HIP_TOGGLE_ON_U2"]
    params["TASTT_STATE_NAME"] = generate_utils.getHipToggleParam() + "_ON"
    params["TASTT_STATE_TRANSITION_U2"] = get_u2("1101", state)
    anim_meta_filename = "Animations/TaSTT_Lock_World_Enable.anim.meta"
    params["TASTT_ANIM_GUID"] = getAnimationGuid(anim_meta_filename)
    print(replaceMacros(TASTT_ANIM_STATE, params))

    # Active state transition.
    params["BOOL_PARAM"] = generate_utils.getHipToggleParam()
    params["THRESHOLD"] = str(0)
    params["MODE"] = str(2)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
    params["TASTT_HIP_TOGGLE_OFF_U2"] = get_u2("1102", state)
    params["DST_STATE_U2"] = params["TASTT_HIP_TOGGLE_OFF_U2"]
    print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # Active state.
    params["TASTT_STATE_U2"] = params["TASTT_HIP_TOGGLE_OFF_U2"]
    params["TASTT_STATE_NAME"] = generate_utils.getHipToggleParam() + "_OFF"
    params["TASTT_STATE_TRANSITION_U2"] = get_u2("1101", state)
    anim_meta_filename = "Animations/TaSTT_Lock_World_Disable.anim.meta"
    params["TASTT_ANIM_GUID"] = getAnimationGuid(anim_meta_filename)
    print(replaceMacros(TASTT_ANIM_STATE, params))

    # Default state transition.
    params["BOOL_PARAM"] = generate_utils.getHipToggleParam()
    params["THRESHOLD"] = str(1)
    params["MODE"] = str(1)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
    params["DST_STATE_U2"] = params["TASTT_HIP_TOGGLE_ON_U2"]
    print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # Layer
    params["TASTT_LAYER_U2"] = params["TASTT_HIP_TOGGLE_LAYER_U2"]
    params["TASTT_LAYER_NAME"] = generate_utils.getHipToggleParam()
    print(replaceMacros(TASTT_LAYER_HEADER, params))

    params["TASTT_STATE_U2"] = params["TASTT_HIP_TOGGLE_ON_U2"]
    print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))
    params["TASTT_STATE_U2"] = params["TASTT_HIP_TOGGLE_OFF_U2"]
    print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    print(replaceMacros(TASTT_LAYER_FOOTER, params))

genTasttHipToggleLayer(state)

def genTasttHandToggleLayer(state):
    # Default state.
    params["TASTT_HAND_TOGGLE_ON_U2"] = get_u2("1102", state)
    params["TASTT_DEFAULT_STATE_U2"] = params["TASTT_HAND_TOGGLE_ON_U2"]
    params["TASTT_STATE_U2"] = params["TASTT_HAND_TOGGLE_ON_U2"]
    params["TASTT_STATE_NAME"] = generate_utils.getHandToggleParam() + "_ON"
    params["TASTT_STATE_TRANSITION_U2"] = get_u2("1101", state)
    anim_meta_filename = "Animations/TaSTT_Lock_Hand_Enable.anim.meta"
    params["TASTT_ANIM_GUID"] = getAnimationGuid(anim_meta_filename)
    print(replaceMacros(TASTT_ANIM_STATE, params))

    # Active state transition.
    params["BOOL_PARAM"] = generate_utils.getHandToggleParam()
    params["THRESHOLD"] = str(0)
    params["MODE"] = str(2)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
    params["TASTT_HAND_TOGGLE_OFF_U2"] = get_u2("1102", state)
    params["DST_STATE_U2"] = params["TASTT_HAND_TOGGLE_OFF_U2"]
    print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # Active state.
    params["TASTT_STATE_U2"] = params["TASTT_HAND_TOGGLE_OFF_U2"]
    params["TASTT_STATE_NAME"] = generate_utils.getHandToggleParam() + "_OFF"
    params["TASTT_STATE_TRANSITION_U2"] = get_u2("1101", state)
    anim_meta_filename = "Animations/TaSTT_Lock_Hand_Disable.anim.meta"
    params["TASTT_ANIM_GUID"] = getAnimationGuid(anim_meta_filename)
    print(replaceMacros(TASTT_ANIM_STATE, params))

    # Default state transition.
    params["BOOL_PARAM"] = generate_utils.getHandToggleParam()
    params["THRESHOLD"] = str(1)
    params["MODE"] = str(1)  # See comment above TASTT_BOOL_STATE_UNARY_TRANSITION.
    params["DST_STATE_U2"] = params["TASTT_HAND_TOGGLE_ON_U2"]
    print(replaceMacros(TASTT_BOOL_STATE_UNARY_TRANSITION, params))

    # Layer
    params["TASTT_LAYER_U2"] = params["TASTT_HAND_TOGGLE_LAYER_U2"]
    params["TASTT_LAYER_NAME"] = generate_utils.getHandToggleParam()
    print(replaceMacros(TASTT_LAYER_HEADER, params))

    params["TASTT_STATE_U2"] = params["TASTT_HAND_TOGGLE_ON_U2"]
    print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))
    params["TASTT_STATE_U2"] = params["TASTT_HAND_TOGGLE_OFF_U2"]
    print(replaceMacros(TASTT_LAYER_HEADER_CHILD_STATE, params))

    print(replaceMacros(TASTT_LAYER_FOOTER, params))

genTasttHandToggleLayer(state)
