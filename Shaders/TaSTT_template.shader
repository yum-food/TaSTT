Shader "TaSTT"
{
  Properties
  {
    Text_Color ("Text Color", Color) = (1, 1, 1, 1)
    Background_Color ("Background Color", Color) = (0, 0, 0, 1)
    Margin_Color ("Margin color", Color) = (1, 1, 1, 1)

    [Gamma] Metallic("Metallic", Range(0, 1)) = 0.5
    Smoothness("Smoothness", Range(0, 1)) = 0.2
    Emissive("Emissive", Range(0, 1)) = 0.1

    [MaterialToggle] Render_Margin("Render margin", float) = 1
    [MaterialToggle] Render_Visual_Indicator("Render visual speech indicator", float) = 1
    Margin_Scale("Margin scale", float) = 0.03
    Margin_Rounding_Scale("Margin rounding scale", float) = 0.03
    [MaterialToggle] Enable_Margin_Effect_Squares(
        "Enable margin effect: Squares", float) = 0

    [MaterialToggle] Enable_Dithering("Enable font dithering", float) = 1

    [MaterialToggle] BG_Enable("Enable custom background", float) = 0
    BG_BaseColor("Background base color", 2D) = "black" {}
    [NoScaleOffset] BG_NormalMap ("Background normal map", 2D) = "bump" {}
    BG_NormalStrength ("Background normal strength", Float) = 1
    BG_Smoothness("Background smoothness", 2D) = "black" {}
    [MaterialToggle]BG_Smoothness_Invert("Invert background smoothness", float) = 1
    BG_Metallic("Background metallic", 2D) = "black" {}
    BG_Emission_Mask("Background emission mask", 2D) = "black" {}
    BG_Emission_Color("Background emission color", Color) = (0, 0, 0)

    _Font_0x0000_0x1FFF ("_Font 0 (unicode 0x0000 - 0x1FFFF)", 2D) = "white" {}
    _Font_0x2000_0x3FFF ("_Font 1 (unicode 0x2000 - 0x3FFFF)", 2D) = "white" {}
    _Font_0x4000_0x5FFF ("_Font 2 (unicode 0x4000 - 0x5FFFF)", 2D) = "white" {}
    _Font_0x6000_0x7FFF ("_Font 3 (unicode 0x6000 - 0x7FFFF)", 2D) = "white" {}
    _Font_0x8000_0x9FFF ("_Font 4 (unicode 0x8000 - 0x9FFFF)", 2D) = "white" {}
    _Font_0xA000_0xBFFF ("_Font 5 (unicode 0xA000 - 0xBFFFF)", 2D) = "white" {}
    _Font_0xC000_0xDFFF ("_Font 6 (unicode 0xC000 - 0xDFFFF)", 2D) = "white" {}
    _Img_0xE000_0xE03F  ("_Images 0", 2D) = "white" {}
    _TaSTT_Indicator_0("_TaSTT_Indicator_0", float) = 0
    _TaSTT_Indicator_1("_TaSTT_Indicator_1", float) = 0

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

      #include "TaSTT_lighting.cginc"
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

      #include "TaSTT_lighting.cginc"
      ENDCG
    }
  }
  //CustomEditor "TaSTTShaderGUI"
}

