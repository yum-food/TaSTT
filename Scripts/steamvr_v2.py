from ctypes import cast, c_void_p, pointer
import xr

inst = xr.create_instance()
print(f"inst: {inst}")

system_get_info = xr.SystemGetInfo(
        form_factor=xr.FormFactor.HEAD_MOUNTED_DISPLAY)
system_id = xr.get_system(
        instance=inst,
        get_info=system_get_info)
print(f"system_id: {system_id}")

gfx_binding = xr.GraphicsBindingOpenGLWin32KHR()
gfx_binding_ptr = cast(pointer(gfx_binding), c_void_p)
session_info = xr.SessionCreateInfo(
        system_id=system_id,
        next=gfx_binding_ptr)
# TODO some issue with graphics binding.
session = xr.create_session(
        instance=inst,
        create_info=session_info)

action_set_info = xr.ActionSetCreateInfo(
        action_set_name="tastt_actions",
        localized_action_set_name="TaSTT_Actions",  # ignore internationalization for now
        priority=0)
print(f"action_set_info: {action_set_info}")

action_set = xr.create_action_set(
        instance=inst,
        create_info=action_set_info)
print(f"action_set: {action_set}")

action_create_info = xr.ActionCreateInfo(
        action_name="tastt_click",
        localized_action_name="TaSTT_Click",
        action_type=xr.ActionType.BOOLEAN_INPUT)
print(f"action_create_info: {action_create_info}")

print(dir(xr.create_action))
action = xr.create_action(
        action_set=action_set,
        create_info=action_create_info)
print(f"action: {action}")

input_path = xr.string_to_path(instance=inst, path_string="/user/hand/right/input/trigger/click")
print(f"input_path: {input_path}")

actions = xr.ActionSuggestedBinding(
        action=action,
        binding=input_path)
print(f"actions: {actions}")

interaction_profile_path = xr.string_to_path(instance=inst, path_string="/interaction_profiles/valve/index_controller")
print(f"interaction_profile_path: {interaction_profile_path}")

bindings = xr.InteractionProfileSuggestedBinding(
        interaction_profile=interaction_profile_path,
        count_suggested_bindings=1,
        suggested_bindings=[actions])
print(f"bindings: {bindings}")

xr.suggest_interaction_profile_bindings(
        instance=inst,
        suggested_bindings=bindings)

while True:
    action_info = xr.ActionStateGetInfo(
            action=action)

    action_bool = xr.get_action_state_boolean(
            session=session,
            get_info=action_info)

    break

xr.destroy_instance(inst)

# Paths:
# /usr/hand/{left,right}/input/{a,b,thumbstick}/{click,touch}

print("Done!")

