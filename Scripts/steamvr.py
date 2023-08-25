import ctypes
import time
import xr

EVENT_NONE = 0
EVENT_RISING_EDGE = 1
EVENT_FALLING_EDGE = 2

# hand: either "right" or "left"
# button: either "a" or "b"
def pollButtonPress(hand: str = "right", button: str = "b") -> int:
    # ContextObject is a high level pythonic class meant to keep simple cases simple.
    with xr.ContextObject(
        instance_create_info=xr.InstanceCreateInfo(
            enabled_extension_names=[
                xr.KHR_OPENGL_ENABLE_EXTENSION_NAME,  # A graphics extension is mandatory
            ],
        ),
    ) as context:
        controller_path_str = f"/user/hand/{hand}"
        binding_path_str = f"/user/hand/{hand}/input/{button}/click"
        print(f"Controller path: {controller_path_str}")
        print(f"Binding path: {binding_path_str}")

        # Set up the B button action
        controller_paths = (xr.Path * 1)(
            xr.string_to_path(context.instance, controller_path_str,)
        )
        b_button_action = xr.create_action(
            action_set=context.default_action_set,
            create_info=xr.ActionCreateInfo(
                action_type=xr.ActionType.BOOLEAN_INPUT,
                action_name="tastt_button_press",
                localized_action_name="TaSTT Button Press",
                count_subaction_paths=len(controller_paths),
                subaction_paths=controller_paths,
            ),
        )
        suggested_bindings = (xr.ActionSuggestedBinding * 1)(
            xr.ActionSuggestedBinding(
                action=b_button_action,
                binding=xr.string_to_path(
                    instance=context.instance,
                    path_string=binding_path_str,
                ),
            ),
        )
        xr.suggest_interaction_profile_bindings(
            instance=context.instance,
            suggested_bindings=xr.InteractionProfileSuggestedBinding(
                interaction_profile=xr.string_to_path(
                    context.instance,
                    "/interaction_profiles/valve/index_controller",
                ),
                count_suggested_bindings=len(suggested_bindings),
                suggested_bindings=suggested_bindings,
            ),
        )

        last_change_time = 0
        for frame_index, frame_state in enumerate(context.frame_loop()):
            if context.session_state != xr.SessionState.FOCUSED:
                yield EVENT_NONE
                continue

            active_action_set = xr.ActiveActionSet(
                action_set=context.default_action_set,
                subaction_path=xr.NULL_PATH,
            )
            xr.sync_actions(
                session=context.session,
                sync_info=xr.ActionsSyncInfo(
                    count_active_action_sets=1,
                    active_action_sets=ctypes.pointer(active_action_set),
                ),
            )

            action_info = xr.ActionStateGetInfo(action=b_button_action)
            action_bool = xr.get_action_state_boolean(
                session=context.session, get_info=action_info
            )

            if action_bool.changed_since_last_sync == 0:
                yield EVENT_NONE
                continue

            if action_bool.current_state == 1:
                yield EVENT_RISING_EDGE
                continue
            else:
                yield EVENT_FALLING_EDGE
                continue

if __name__ == "__main__":
    gen = run()
    while True:
        event = next(gen)
        print(f"event: {event}")

