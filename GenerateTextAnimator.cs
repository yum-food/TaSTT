#if UNITY_EDITOR
using AnimatorAsCode.V1;
using AnimatorAsCode.V1.ModularAvatar;
using YumTools;
using nadena.dev.ndmf;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;
using VRC.SDK3.Avatars.Components;
using VRC.SDKBase;

// This example uses NDMF. See https://github.com/bdunderscore/ndmf?tab=readme-ov-file#getting-started
[assembly: ExportsPlugin(typeof(GenerateTextAnimatorPlugin))]
namespace YumTools
{
  public class GenerateTextAnimator : MonoBehaviour, IEditorOnly
  {
    // The number of blocks addressable.
    public int numBlocks = 10;
    // The number of datums sent per block.
    public int blockWidth = 5;
    // The number of bytes per datum.
    public int bytesPerDatum = 2;

    public string oscPointerParam = "_Unigram_Letter_Grid_OSC_Pointer";

    // Data sent through OSC uses this pattern.
    public string[] oscParamPerBlockDatumByte = {"_Unigram_Letter_Grid_OSC_Datum{0:00}_Byte{1:00}"};
    // The pattern of the parameters which this script will animate.
    public string[] matPropPerBlockDatumByte = {"_Unigram_Letter_Grid_Data_Block{0:00}_Datum{1:00}_Byte{2:00}_Animated"};

    public string[] oscParamPerBlockDatum = {};
    public string[] matPropPerBlockDatum = {};

    public string[] oscParamPerBlock = {"_Unigram_Letter_Grid_OSC_Visual_Pointer"};
    public string[] matPropPerBlock = {"_Unigram_Letter_Grid_Block_{0:00}_Visual_Pointer_Animated"};
  }

  public class GenerateTextAnimatorPlugin : Plugin<GenerateTextAnimatorPlugin>
  {
    public override string QualifiedName => "yum.generate_chat_animator";
    public override string DisplayName => "Chat Animator";

    private const string SystemName = "GenerateTextAnimator";
    // Direct blendtrees have special semantics with write defaults. We want
    // them on. They will not fuck up the rest of the animator, whether it uses
    // write defaults or not.
    private const bool UseWriteDefaults = true;

    protected override void Configure()
    {
      InPhase(BuildPhase.Generating).Run($"Generate {DisplayName}", Generate);
    }

    private AacFlBlendTreeDirect Add8BitBlendTree(
        AacFlBase aac,
        AacFlLayer layer,
        GenerateTextAnimator cfg,
        AacFlBlendTreeDirect tree,
        string matProp, string oscParam, string oneParam) {
      var offAnim = aac.NewClip().Animating(clip =>
          {
          clip.Animates(cfg.GetComponent<Renderer>(), "material." + matProp).WithFrameCountUnit(keyframes =>
              keyframes.Constant(/*when=*/0, /*value=*/0));
          });
      var onAnim = aac.NewClip().Animating(clip =>
          {
          clip.Animates(cfg.GetComponent<Renderer>(), "material." + matProp).WithFrameCountUnit(keyframes =>
              keyframes.Constant(/*when=*/0, /*value=*/255));
          });
      var subtree = aac.NewBlendTree().Simple1D(layer.FloatParameter(oscParam))
        .WithAnimation(offAnim, /*threshold=*/-1)
        .WithAnimation(onAnim,  /*threshold=*/ 1);
      return tree.WithAnimation(subtree, layer.FloatParameter("AlwaysOne"));
    }

    private void Generate(BuildContext ctx)
    {
      var components = ctx.AvatarRootTransform.GetComponentsInChildren<GenerateTextAnimator>(true);
      if (components.Length == 0) return;

      var aac = AacV1.Create(new AacConfiguration
          {
          SystemName = SystemName,
          AnimatorRoot = ctx.AvatarRootTransform,
          DefaultValueRoot = ctx.AvatarRootTransform,
          AssetKey = GUID.Generate().ToString(),
          AssetContainer = ctx.AssetContainer,
          ContainerMode = AacConfiguration.Container.OnlyWhenPersistenceRequired,
          AssetContainerProvider = new NDMFContainerProvider(ctx),
          DefaultsProvider = new AacDefaultsProvider(UseWriteDefaults)
          });

      // Create a new object in the scene. We will add Modular Avatar components inside it.
      var modularAvatar = MaAc.Create(new GameObject(SystemName)
          {
          transform = { parent = ctx.AvatarRootTransform }
          });

      var ctrl = aac.NewAnimatorController();
      for (int component_i = 0; component_i < components.Length; component_i++) {
        GenerateTextAnimator cfg = components[component_i];
        var layer = ctrl.NewLayer($"Chatbox Plumbing (component #{component_i})");

        var baseState = layer.NewState("Entry (noop)").WithWriteDefaultsSetTo(false);

        // Create "always one" value to use in DBT.
        // See https://vrc.school/docs/Other/DBT-Combining/ for details.
        layer.OverrideValue(layer.FloatParameter("AlwaysOne"), 1.0f);

        // Create blendtrees. One for each block of data.
        var block_trees = new List<AacFlState>();
        AacFlState last_block_state = null;
        // For each block.
        for (int i = 0; i < cfg.numBlocks; i++) {
          var block_tree = aac.NewBlendTree().Direct();

          // Create block-level animations.
          for (int ii = 0; ii < cfg.oscParamPerBlock.Length; ii++) {
            string matPropB = string.Format(cfg.matPropPerBlock[ii], i);
            string oscParamB = cfg.oscParamPerBlock[ii];
            block_tree = Add8BitBlendTree(aac, layer, cfg, block_tree, matPropB, oscParamB, "AlwaysOne");
          }

          // For each datum per block.
          for (int j = 0; j < cfg.blockWidth; j++) {
            // Create (block, datum)-level animations.
            for (int ii = 0; ii < cfg.oscParamPerBlockDatum.Length; ii++) {
              string matPropBD = string.Format(cfg.matPropPerBlockDatum[ii], i, j);
              string oscParamBD = string.Format(cfg.oscParamPerBlockDatum[ii], j);
              block_tree = Add8BitBlendTree(aac, layer, cfg, block_tree, matPropBD, oscParamBD, "AlwaysOne");
            }

            // For each byte per datum.
            for (int k = 0; k < cfg.bytesPerDatum; k++) {
              // Create (block, datum, byte)-level animations.
              for (int ii = 0; ii < cfg.oscParamPerBlockDatumByte.Length; ii++) {
                string matPropBDB = string.Format(cfg.matPropPerBlockDatumByte[ii], i, j, k);
                //Debug.Log($"animating property: {matPropBDB}");
                string oscParamBDB = string.Format(cfg.oscParamPerBlockDatumByte[ii], j, k);
                block_tree = Add8BitBlendTree(aac, layer, cfg, block_tree, matPropBDB, oscParamBDB, "AlwaysOne");
              }
            }
          }

          var cur_block_state = layer.NewState($"Block {i}").WithAnimation(block_tree);
          if (last_block_state != null) {
            cur_block_state = cur_block_state.Under(last_block_state);
          }
          last_block_state = cur_block_state;
          block_trees.Add(cur_block_state);
        }

        // Create transitions to each block's blendtree.
        for (int i = 0; i < cfg.numBlocks; i++) {
          block_trees[i].TransitionsFromAny()
            //.WithInterruption(TransitionInterruptionSource.Source)
            .When(layer.IntParameter(cfg.oscPointerParam).IsEqualTo(i));
        }

        // Create sync params (VRCSDK)
        for (int ii = 0; ii < cfg.oscParamPerBlock.Length; ii++) {
          string bParam = cfg.oscParamPerBlock[ii];
          modularAvatar.NewParameter(layer.FloatParameter(bParam));
        }
        for (int i = 0; i < cfg.blockWidth; i++) {
          for (int ii = 0; ii < cfg.oscParamPerBlockDatum.Length; ii++) {
            string bdParam = string.Format(cfg.oscParamPerBlockDatum[ii], i);
            modularAvatar.NewParameter(layer.FloatParameter(bdParam));
          }
          for (int j = 0; j < cfg.bytesPerDatum; j++) {
            for (int ii = 0; ii < cfg.oscParamPerBlockDatumByte.Length; ii++) {
              string bdbParam = string.Format(cfg.oscParamPerBlockDatumByte[ii], i, j);
              modularAvatar.NewParameter(layer.FloatParameter(bdbParam)).WithDefaultValue(1.0f);
            }
          }
        }

        modularAvatar.NewParameter(layer.IntParameter(cfg.oscPointerParam));
      }

      // By creating a Modular Avatar Merge Animator component,
      // our animator controller will be added to the avatar's FX layer.
      modularAvatar.NewMergeAnimator(ctrl.AnimatorController, VRCAvatarDescriptor.AnimLayerType.FX);
    }
  }

  // (For AAC 1.2.0 and above) This is recommended starting from NDMF 1.6.0. You only need to define this class once.
  internal class NDMFContainerProvider : IAacAssetContainerProvider
  {
    private readonly BuildContext _ctx;
    public NDMFContainerProvider(BuildContext ctx) => _ctx = ctx;
    public void SaveAsPersistenceRequired(Object objectToAdd) => _ctx.AssetSaver.SaveAsset(objectToAdd);
    public void SaveAsRegular(Object objectToAdd) { } // Let NDMF crawl our assets when it finishes
    public void ClearPreviousAssets() { } // ClearPreviousAssets is never used in non-destructive contexts
  }
}
#endif

