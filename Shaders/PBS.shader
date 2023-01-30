Shader "TaSTT/Simple_PBS"
{
  Properties
  {
    [MaterialToggle] BG_Enable("Enable custom background", float) = 0
    BG_BaseColor("Background base color", 2D) = "black" {}
    [NoScaleOffset] BG_NormalMap ("Background normal map", 2D) = "bump" {}
    BG_NormalStrength ("Background normal strength", Float) = 1
    BG_Smoothness("Background smoothness", 2D) = "black" {}
    [MaterialToggle]BG_Smoothness_Invert("Invert background smoothness", float) = 1
    BG_Metallic("Background metallic", 2D) = "black" {}
    BG_Emission_Mask("Background emission mask", 2D) = "black" {}
    BG_Emission_Color("Background emission color", Color) = (0, 0, 0)

    // %TEMPLATE__UNITY_ROW_COL_PARAMS%
  }
  SubShader
  {
    Pass {
      Tags {
        "RenderType"="Opaque"
        "Queue"="AlphaTest+499"
        "LightMode" = "ForwardBase"
      }
      Blend SrcAlpha OneMinusSrcAlpha

      CGPROGRAM
      #pragma target 3.0

      #pragma multi_compile _ VERTEXLIGHT_ON

      #pragma vertex vert
      #pragma fragment frag

      #define FORWARD_BASE_PASS

      #include "PBS_lighting.cginc"
      ENDCG
    }
    Pass {
      Tags {
        "RenderType" = "Opaque"
        "LightMode" = "ForwardAdd"
        "Queue"="AlphaTest+499"
      }
      Blend One One
      ZWrite Off

      CGPROGRAM
      #pragma target 3.0

      #pragma multi_compile_fwdadd

      #pragma vertex vert
      #pragma fragment frag

      #include "PBS_lighting.cginc"
      ENDCG
    }
  }
}

