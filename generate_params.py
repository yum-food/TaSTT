#!/usr/bin/env python3

import generate_utils

PARAM_HEADER = """
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!114 &11400000
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: 0}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {fileID: -1506855854, guid: 67cc4cb7839cd3741b63733d5adf0442, type: 3}
  m_Name: TaSTT_params
  m_EditorClassIdentifier: 
  parameters:
"""[1:][0:-1]

INT_PARAM = """
  - name: %PARAM_NAME%
    valueType: 0
    saved: 0
    defaultValue: 0
"""[1:][0:-1]

BOOL_PARAM = """
  - name: %PARAM_NAME%
    valueType: 2
    saved: 0
    defaultValue: 0
"""[1:][0:-1]

# We're working with an 84-character board, and each FX layer is responsible
# for 8 of those characters.
params = {}
print(generate_utils.replaceMacros(PARAM_HEADER, params))

# Implementation detail. We use this parameter to return from the terminal
# state of the FX layer to the starting state.
params["PARAM_NAME"] = "TaSTT_Dummy"
print(generate_utils.replaceMacros(BOOL_PARAM, params))

for i in range(0, generate_utils.NUM_LAYERS):
    params["PARAM_NAME"] = generate_utils.getLayerParam(i)
    print(generate_utils.replaceMacros(INT_PARAM, params))

    params["PARAM_NAME"] = generate_utils.getSelectParam(i, 0)
    print(generate_utils.replaceMacros(BOOL_PARAM, params))

    params["PARAM_NAME"] = generate_utils.getSelectParam(i, 1)
    print(generate_utils.replaceMacros(BOOL_PARAM, params))

    params["PARAM_NAME"] = generate_utils.getSelectParam(i, 2)
    print(generate_utils.replaceMacros(BOOL_PARAM, params))

    params["PARAM_NAME"] = generate_utils.getEnableParam(i)
    print(generate_utils.replaceMacros(BOOL_PARAM, params))
