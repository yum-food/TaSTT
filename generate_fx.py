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
params["EXPAND_GROUPS_LAYER_U2"] = get_u2("1107", state)
params["CELL_LAYER_U2"] = get_u2("1107", state)

params["MONO_BEHAVIOUR_U"] = "114"
params["SET_LETTERS_SCRIPT_U2"] = get_u2("114", state)

params["ANIMATOR_STATE_U"] = "1102"
params["EXPAND_GROUPS_LAYER_STATE_U2"] = get_u2("1102", state)

params["ANIMATOR_STATE_TRANSITION_U"] = "1101"

# By default, the board shows an empty character in every group/cell.
# Technically we only have to initialize groups, since SetLetters.cs will use
# the groups to populate the cells.
DEFAULT_CHAR=64  # 64 == space == blank
params["DEFAULT_GROUP_VAL"] = str((DEFAULT_CHAR << 24) | (DEFAULT_CHAR << 16) | (DEFAULT_CHAR << 8) | DEFAULT_CHAR)
params["DEFAULT_CELL_VAL"] = str(DEFAULT_CHAR)
params["DEFAULT_INT_VAL"] = str(0)

# Get from SetLetters.cs.meta
with open("SetLetters.cs.meta") as f:
    guid = None
    for line in f:
        if "guid" in line:
            guid = line.split()[1]
assert(guid != None)
params["SET_LETTERS_GUID"]=guid

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
    m_DefaultInt: %DEFAULT_INT_VAL%
    m_DefaultBool: 0
    m_Controller: {fileID: %ANIMATOR_HEADER_U2%}
"""[1:]

ANIMATOR_LAYER_HEADER = """
  m_AnimatorLayers:
"""[1:]

ANIMATOR_LAYER_EXPAND_GROUPS = """
  - serializedVersion: 5
    m_Name: TaSTT_Expand_Groups
    m_StateMachine: {fileID: %EXPAND_GROUPS_LAYER_U2%}
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
    m_Controller: {fileID: 9100000}
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
    for group_name in GROUP_NAMES:
        params["ANIMATOR_PARAMETER_NAME"] = group_name
        params["DEFAULT_INT_VAL"] = params["DEFAULT_GROUP_VAL"]
        print(replaceMacros(ANIMATOR_PARAMETER_INT, params))
    for cell_name in CELL_NAMES:
        params["ANIMATOR_PARAMETER_NAME"] = cell_name
        params["DEFAULT_INT_VAL"] = params["DEFAULT_CELL_VAL"]
        print(replaceMacros(ANIMATOR_PARAMETER_INT, params))
    print(replaceMacros(ANIMATOR_LAYER_HEADER, params))
    print(replaceMacros(ANIMATOR_LAYER_EXPAND_GROUPS, params))
    for cell_name in CELL_NAMES:
        params[cell_name + "_U2"] = get_u2("1102", state)
        params["LAYER_NAME"] = cell_name
        params["LAYER_STATE_MACHINE_U2"] = params[cell_name + "_U2"]
        print(replaceMacros(ANIMATOR_LAYER_CELL_ANIM, params))
genAnimator(state)

EXPAND_GROUPS_LAYER = """
--- !u!%ANIMATOR_STATE_MACHINE_U% &%EXPAND_GROUPS_LAYER_U2%
AnimatorStateMachine:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: TaSTT_Expand_Groups
  m_ChildStates:
  - serializedVersion: 1
    m_State: {fileID: %EXPAND_GROUPS_LAYER_STATE_U2%}
    m_Position: {x: 280, y: 90, z: 0}
  m_ChildStateMachines: []
  m_AnyStateTransitions: []
  m_EntryTransitions: []
  m_StateMachineTransitions: {}
  m_StateMachineBehaviours: []
  m_AnyStatePosition: {x: 50, y: 20, z: 0}
  m_EntryPosition: {x: 50, y: 120, z: 0}
  m_ExitPosition: {x: 800, y: 120, z: 0}
  m_ParentStateMachinePosition: {x: 800, y: 20, z: 0}
  m_DefaultState: {fileID: %EXPAND_GROUPS_LAYER_STATE_U2%}
"""[1:]

EXPAND_GROUPS_LAYER_STATE = """
--- !u!%ANIMATOR_STATE_U% &%EXPAND_GROUPS_LAYER_STATE_U2%
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: SetLetters
  m_Speed: 1
  m_CycleOffset: 0
  m_Transitions: []
  m_StateMachineBehaviours:
  - {fileID: %SET_LETTERS_SCRIPT_U2%}
  m_Position: {x: 50, y: 50, z: 0}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 1
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

SET_LETTERS_SCRIPT = """
--- !u!%MONO_BEHAVIOUR_U% &%SET_LETTERS_SCRIPT_U2%
MonoBehaviour:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: 0}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {fileID: 11500000, guid: %SET_LETTERS_GUID%, type: 3}
  m_Name: 
  m_EditorClassIdentifier: 
"""[1:]

# Generate the layer that converts our select few 32-bit int parameters into
# 4x as many int parameters, each containing the letter value for one cell.
def genExpandGroupsLayer():
    tmp = EXPAND_GROUPS_LAYER + EXPAND_GROUPS_LAYER_STATE + SET_LETTERS_SCRIPT
    print(replaceMacros(tmp, params))
genExpandGroupsLayer()

CELL_LAYER_HEADER="""
--- !u!%ANIMATOR_STATE_MACHINE_U% &%CELL_LAYER_U2%
AnimatorStateMachine:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: %LAYER_NAME%
  m_ChildStates:
"""[1:]

CELL_LAYER_STATE_HEADER="""
  - serializedVersion: 1
    m_State: {fileID: %CELL_LAYER_STATE_U2%}
    m_Position: {x: 350.6628, y: %STATE_Y%, z: 0}
"""[1:]

CELL_LAYER_MIDDLE="""
  m_ChildStateMachines: []
  m_AnyStateTransitions:
"""[1:]

CELL_LAYER_TRANSITION_HEADER="""
  - {fileID: %CELL_LAYER_TRANSITION_U2%}
"""[1:]

CELL_LAYER_SUFFIX="""
  m_ChildStateMachines: []
  m_EntryTransitions: []
  m_StateMachineTransitions: {}
  m_StateMachineBehaviours: []
  m_AnyStatePosition: {x: 50, y: 20, z: 0}
  m_EntryPosition: {x: 50, y: 120, z: 0}
  m_ExitPosition: {x: 800, y: 120, z: 0}
  m_ParentStateMachinePosition: {x: 800, y: 20, z: 0}
  m_DefaultState: {fileID: %CELL_LAYER_DEFAULT_STATE_U2%}
"""[1:]

CELL_LAYER_STATE = """
--- !u!%ANIMATOR_STATE_U% &%CELL_LAYER_STATE_U2%
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: %ANIMATION_NAME%
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
  m_Motion: {fileID: 7400000, guid: %CELL_LAYER_STATE_ANIM_GUID%, type: 2}
  m_Tag: 
  m_SpeedParameter: 
  m_MirrorParameter: 
  m_CycleOffsetParameter: 
  m_TimeParameter: 
"""[1:]

CELL_LAYER_TRANSITION="""
--- !u!%ANIMATOR_STATE_TRANSITION_U% &%CELL_LAYER_TRANSITION_U2%
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 6
    m_ConditionEvent: %LAYER_NAME%
    m_EventTreshold: %TRANSITION_THRESHOLD%
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: %CELL_LAYER_DST_STATE_U2%}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0.1
  m_TransitionOffset: 0
  m_ExitTime: 0.75
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
"""[1:]

def getAnimationGuid(anim_meta_filename):
    with open(anim_meta_filename, 'r') as f:
        for line in f:
            if "guid" in line:
                return line.split()[1]
    return None

def genCellAnimationLayers(state):
    for layer in CELL_NAMES:
        params["CELL_LAYER_U2"] = params[layer + "_U2"]
        params["CELL_LAYER_U2" + layer] = params["CELL_LAYER_U2"]
        params["LAYER_NAME"] = layer
        print(replaceMacros(CELL_LAYER_HEADER, params))

        # Add a state for each animation, i.e. for each character writeable in this slot.
        for i in range(0,128):
            params["CELL_LAYER_STATE_U2"] = get_u2(params["ANIMATOR_STATE_U"], state)
            params["CELL_LAYER_STATE_U2" + layer + ("_Letter%02d" % i)] = params["CELL_LAYER_STATE_U2"]
            params["STATE_Y"] = str(-190 - i * 40)
            print(replaceMacros(CELL_LAYER_STATE_HEADER, params))

        print(CELL_LAYER_MIDDLE)

        for i in range(0,128):
            params["CELL_LAYER_TRANSITION_U2"] = get_u2(params["ANIMATOR_STATE_TRANSITION_U"], state)
            params["CELL_LAYER_TRANSITION_U2" + layer + ("_Letter%02d" % i)] = params["CELL_LAYER_TRANSITION_U2"]
            print(replaceMacros(CELL_LAYER_TRANSITION_HEADER, params))

        # Set the default layer to the 0th animation.
        params["CELL_LAYER_DEFAULT_STATE_U2"] = params["CELL_LAYER_STATE_U2" + layer + ("_Letter%02d" % 0)]
        print(replaceMacros(CELL_LAYER_SUFFIX, params))

        # Done creating the layer header! Phew. Let's make the states next.
        for i in range(0,128):
            params["ANIMATION_NAME"] = layer + ("_Letter%02d" % i)
            params["CELL_LAYER_STATE_U2"] = params["CELL_LAYER_STATE_U2" + layer + ("_Letter%02d" % i)]
            # Get the GUID of the animation we will play at this state.
            anim_meta_filename = "generated/animations/" + layer + ("_Letter%02d" % i) + ".anim.meta"
            params["CELL_LAYER_STATE_ANIM_GUID"] = getAnimationGuid(anim_meta_filename)
            print(replaceMacros(CELL_LAYER_STATE, params))

        # OK, finally, let's wire up the states.
        for i in range(0,128):
            params["CELL_LAYER_TRANSITION_U2"] = params["CELL_LAYER_TRANSITION_U2" + layer + ("_Letter%02d" % i)]
            params["TRANSITION_THRESHOLD"] = str(i)
            params["CELL_LAYER_DST_STATE_U2"] = params["CELL_LAYER_STATE_U2" + layer + ("_Letter%02d" % i)]
            print(replaceMacros(CELL_LAYER_TRANSITION, params))
genCellAnimationLayers(state)
