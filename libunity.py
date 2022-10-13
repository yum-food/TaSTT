#!/usr/bin/env python3

def getObjectIds(fx):
    fx_ids = set()
    with open(fx, "r") as f:
        for line in f:
            parts = line.split()
            if line.startswith("---") and len(parts) == 3:
                obj_id = parts[2]
                # Remove & from beginning of object ID.
                obj_id = obj_id[1:]
                fx_ids.add(obj_id)
    return fx_ids

def getOldIds(old_fx_ids, unified_fx_ids):
    id_mapping = {}

    for old_id in old_fx_ids:
        id_mapping[old_id] = str(old_id)
        unified_fx_ids.add(int(old_id))

    return id_mapping

# Map an object ID from old namespace to unified.
def getNewIds(old_fx_ids, unified_fx_ids):
    id_mapping = {}

    for old_id in old_fx_ids:
        new_id = int(old_id)

        # 9100000 is the ID of the animator. There's only one, and we take care
        # to merge it. So no need to create a new identifier for it.
        if new_id != 9100000:
            while (new_id in unified_fx_ids or new_id in old_fx_ids):
                new_id += 1

        unified_fx_ids.add(new_id)
        id_mapping[old_id] = str(new_id)

    return id_mapping

def replaceIds(old_str, id_map):
    result = old_str
    lines = []
    for line in result.split("\n"):
        for old_id, new_id in id_map.items():
            line = line.replace(old_id, new_id)
        lines.append(line)
    return '\n'.join(lines)

def cat(path):
    lines = []
    with open(path, "r") as f:
        for line in f:
            lines.append(line)
    return ''.join(lines)

# Extract the first block whose '---' line matches `prefix`.
def extractFirstBlock(fx, begin_prefix, end_prefix):
    lines = []
    in_block = False
    for line in fx.split("\n"):
        if in_block and line.startswith(end_prefix):
            break
        if line.startswith(begin_prefix):
            in_block = True
        if in_block:
            lines.append(line)
    return '\n'.join(lines) + "\n"

def mergeAnimatorControllers(fx0, fx1, fx0_ids, fx1_ids):
    fx0_anim = extractFirstBlock(cat(fx0), "--- !u!91", "---")
    fx1_anim = extractFirstBlock(cat(fx1), "--- !u!91", "---")

    fx0_anim_params = extractFirstBlock(fx0_anim, "  m_AnimatorParameters:", "  m_AnimatorLayers:")
    fx0_anim_params = "\n".join(fx0_anim_params.split("\n")[1:])
    fx0_anim_params = replaceIds(fx0_anim_params, fx0_ids)

    fx0_anim_layers = extractFirstBlock(fx0_anim, "  m_AnimatorLayers:", "---")
    fx0_anim_layers = "\n".join(fx0_anim_layers.split("\n")[1:])
    fx0_anim_layers = replaceIds(fx0_anim_layers, fx0_ids)

    fx1_anim_params = extractFirstBlock(fx1_anim, "  m_AnimatorParameters:", "  m_AnimatorLayers:")
    fx1_anim_params = "\n".join(fx1_anim_params.split("\n")[1:])
    fx1_anim_params = replaceIds(fx1_anim_params, fx1_ids)

    fx1_anim_layers = extractFirstBlock(fx1_anim, "  m_AnimatorLayers:", "---")
    fx1_anim_layers = "\n".join(fx1_anim_layers.split("\n")[1:])
    fx1_anim_layers = replaceIds(fx1_anim_layers, fx1_ids)

    result = """
--- !u!91 &9100000
AnimatorController:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: FX
  serializedVersion: 5
  m_AnimatorParameters:
"""[1:]

    result += fx0_anim_params
    result += fx1_anim_params

    result += "  m_AnimatorLayers:\n"

    result += fx0_anim_layers
    result += fx1_anim_layers

    return result

# Merge two FX layers.
# fx0, fx1 are both paths to animators.
# The object IDs for fx1 are reassigned to not collide with those used by fx0.
def mergeFX(fx0, fx1):
    fx0_ids = getObjectIds(fx0)
    fx1_ids = getObjectIds(fx1)

    # Get unique identifiers for all objects in both layers.
    new_ids = set()
    fx0_id_mapping = getOldIds(fx0_ids, new_ids)
    fx1_id_mapping = getNewIds(fx1_ids, new_ids)

    # Merge animators
    anim_ctrl = mergeAnimatorControllers(fx0, fx1, fx0_id_mapping, fx1_id_mapping)

    # Remove animators and prefix
    fx0_str = cat(fx0)
    fx1_str = cat(fx1)

    fx0_anim = extractFirstBlock(fx0_str, "--- !u!91", "---")
    fx1_anim = extractFirstBlock(fx1_str, "--- !u!91", "---")

    fx0_str = fx0_str.replace(fx0_anim, "")
    fx1_str = fx1_str.replace(fx1_anim, "")

    prefix = """
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
"""[1:]

    fx0_str = fx0_str.replace(prefix, "")
    fx1_str = fx1_str.replace(prefix, "")

    # Replace old IDs
    #fx0_str = replaceIds(fx0_str, fx0_id_mapping)
    fx1_str = replaceIds(fx1_str, fx1_id_mapping)

    # Output
    return deleteEmptyLines(prefix + anim_ctrl + fx0_str + fx1_str)

def deleteEmptyLines(fx):
    return fx.replace("\n\n", "\n")

if __name__ == "__main__":
    #mergeFX("FX.controller", "TaSTT/generated_fx.controller")
    #print(extractFirstBlock("../FX.controller", "--- !u!91", "---"))
    print(mergeFX("TaSTT_fx.controller", "../FX.controller"))

