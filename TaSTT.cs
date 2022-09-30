using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;
using VRC.SDK3.Avatars.Components;
using VRC.SDK3.Avatars.ScriptableObjects;

namespace TaSTT
{
    public class TaSTT : EditorWindow
    {
        private static TaSTT instance_;
        private GameObject avatar_root_;
        private AnimatorController fx_controller_;

        [MenuItem("Window/TaSTT")]
        private static void ShowWindow()
        {
            instance_ = GetWindow<TaSTT>();
            instance_.titleContent = new GUIContent("TaSTT");
        }

        private void Draw()
        {
            GUILayout.Label("TaSTT: A free VRChat STT");
            GUILayout.Label("Made with love by yum_food");
            GUILayout.Label("");

            avatar_root_ = (GameObject)EditorGUILayout.ObjectField(
                new GUIContent("Avatar Root"), avatar_root_,
                typeof(GameObject), true);
            fx_controller_ = (AnimatorController)EditorGUILayout.ObjectField(
                new GUIContent("FX Controller"), fx_controller_,
                typeof(AnimatorController), true);

            if (GUILayout.Button("Create animations!"))
            {
                if (avatar_root_ == null || !fx_controller_ == null)
                {
                    // TODO(yum_food) why doesn't EditorGUILayout.HelpBox() work here?
                    Debug.LogError("Avatar root or FX controller are not set! Cannot create animations.");
                    return;
                }
                // TODO(yum_food)
            }
            if (GUILayout.Button("Create FX layer!"))
            {
                if (!avatar_root_ == null || !fx_controller_ == null)
                {
                    Debug.LogError("Avatar root or FX controller are not set! Cannot create FX layer.");
                    return;
                }
                // TODO(yum_food)
            }
        }

        private static void CreateAnimations()
        {
            VRCAvatarDescriptor descriptor = avatar_root_.GetComponent<VRCAvatarDescriptor>();
            if (descriptor == null)
            {
                Debug.LogError("Failed to get avatar descriptor");
                return;
            }
            AnimationClip anim = new AnimationClip();
            clip.frameRate = 1f;
        }

        private void OnGUI()
        {
            if (instance_ != null)
            {
                Draw();
            }
        }
    }
}
