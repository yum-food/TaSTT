#!/usr/bin/env python3

import app_config
import argparse
import generate_utils
import sys

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
"""[1:]

INT_PARAM = """
  - name: %PARAM_NAME%
    valueType: 0
    saved: 0
    defaultValue: 0
    networkSynced: %SYNCED%
"""[1:]

BOOL_PARAM = """
  - name: %PARAM_NAME%
    valueType: 2
    saved: %SAVED%
    defaultValue: 0
    networkSynced: %SYNCED%
"""[1:]

FLOAT_PARAM = """
  - name: %PARAM_NAME%
    valueType: 1
    saved: 0
    defaultValue: %DEFAULT_FLOAT%
    networkSynced: %SYNCED%
"""[1:]

def generate(cfg):
    result = ""

    # We're working with an 84-character board, and each FX layer is responsible
    # for 8 of those characters.
    params = {}
    params["SAVED"] = "0"
    params["DEFAULT_FLOAT"] = "0"
    params["SYNCED"] = "1"

    params["PARAM_NAME"] = generate_utils.getDummyParam()
    result += generate_utils.replaceMacros(BOOL_PARAM, params)

    params["PARAM_NAME"] = generate_utils.getEnableParam()
    result += generate_utils.replaceMacros(BOOL_PARAM, params)

    params["PARAM_NAME"] = generate_utils.getEllipsisParam()
    result += generate_utils.replaceMacros(BOOL_PARAM, params)

    if not cfg["enable_phonemes"]:
        params["SYNCED"] = "0"
    for i in range(5):
        params["PARAM_NAME"] = generate_utils.getSoundParam(i+1)
        result += generate_utils.replaceMacros(BOOL_PARAM, params)
    params["PARAM_NAME"] = generate_utils.getEnablePhonemeParam()
    result += generate_utils.replaceMacros(BOOL_PARAM, params)
    params["SYNCED"] = "1"

    params["PARAM_NAME"] = generate_utils.getScaleParam()
    params["DEFAULT_FLOAT"] = "0.05"
    result += generate_utils.replaceMacros(FLOAT_PARAM, params)
    params["DEFAULT_FLOAT"] = "0"

    params["PARAM_NAME"] = generate_utils.getToggleParam()
    result += generate_utils.replaceMacros(BOOL_PARAM, params)

    params["PARAM_NAME"] = generate_utils.getLockWorldParam()
    result += generate_utils.replaceMacros(BOOL_PARAM, params)

    params["PARAM_NAME"] = generate_utils.getClearBoardParam()
    result += generate_utils.replaceMacros(BOOL_PARAM, params)

    params["PARAM_NAME"] = generate_utils.getSelectParam()
    result += generate_utils.replaceMacros(INT_PARAM, params)

    for byte in range(0, generate_utils.config.BYTES_PER_CHAR):
        for i in range(0, generate_utils.config.CHARS_PER_SYNC):
            params["PARAM_NAME"] = generate_utils.getBlendParam(i, byte)
            result += generate_utils.replaceMacros(FLOAT_PARAM, params)

    return result

def append(old_path, params, new_path):
    merged = ""
    with open(old_path, "r") as f:
        merged = f.read()
    merged += params
    with open(new_path, "w") as f:
        f.write(merged)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--old_params", type=str, help="The parameters to append to")
    parser.add_argument("--new_params", type=str, help="The parameters to create")
    parser.add_argument("--config", type=str, help="The path to the app config.")
    parser.add_argument("--chars_per_sync", type=str, help="The number of characters to send on each sync event")
    args = parser.parse_args()

    if not args.old_params or not args.new_params:
        print("--old_params and --new_params are both required",
                file=sys.stderr)
        parser.print_help()
        parser.exit(1)

    cfg = app_config.getConfig(args.config)

    generate_utils.config.BYTES_PER_CHAR = int(cfg["bytes_per_char"])
    generate_utils.config.CHARS_PER_SYNC = int(cfg["chars_per_sync"])

    append(args.old_params, generate(cfg), args.new_params)

