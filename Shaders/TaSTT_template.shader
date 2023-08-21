Shader "TaSTT/Chatbox"
{
  Properties
  {
    _Text_Color ("Text color", Color) = (1, 1, 1, 1)
    _Text_Metallic ("Text metallic", Range(0, 1)) = 0
    _Text_Smoothness ("Text smoothness", Range(0, 1)) = 0
    _Text_Emissive ("Text emission", Range(0, 1)) = 0.2

    _BG_Color ("Background color", Color) = (0, 0, 0, 1)
    _BG_Metallic ("Background metallic", Range(0, 1)) = 0
    _BG_Smoothness ("Background smoothness", Range(0, 1)) = 0
    _BG_Emissive ("Background emission", Range(0, 1)) = 0.2

    _Frame_Color ("Frame color", Color) = (1, 1, 1, 1)
    _Frame_Metallic ("Frame metallic", Range(0, 1)) = 0
    _Frame_Smoothness ("Frame smoothness", Range(0, 1)) = 0
    _Frame_Emissive ("Frame emission", Range(0, 1)) = 0.2

    _Emerge("Emerge animation time", Range(0, 1)) = 1.0
    [MaterialToggle] _Ellipsis("Show ellipsis", float) = 0

    _Font_0x0000_0x1FFF ("_Font 0 (unicode 0x0000 - 0x1FFFF)", 2D) = "white" {}
    _Font_0x2000_0x3FFF ("_Font 1 (unicode 0x2000 - 0x3FFFF)", 2D) = "white" {}
    _Font_0x4000_0x5FFF ("_Font 2 (unicode 0x4000 - 0x5FFFF)", 2D) = "white" {}
    _Font_0x6000_0x7FFF ("_Font 3 (unicode 0x6000 - 0x7FFFF)", 2D) = "white" {}
    _Font_0x8000_0x9FFF ("_Font 4 (unicode 0x8000 - 0x9FFFF)", 2D) = "white" {}
    _Font_0xA000_0xBFFF ("_Font 5 (unicode 0xA000 - 0xBFFFF)", 2D) = "white" {}
    _Font_0xC000_0xDFFF ("_Font 6 (unicode 0xC000 - 0xDFFFF)", 2D) = "white" {}
    _Img_0xE000_0xE03F  ("_Images", 2D) = "white" {}

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
      Cull Back
      ZWrite On
      ZTest LEqual

      CGPROGRAM
      #pragma target 5.0

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
      Cull Back
      ZWrite On
      ZTest LEqual

      CGPROGRAM
      #pragma target 5.0

      #pragma multi_compile_fwdadd

      #pragma vertex vert
      #pragma fragment frag

      #include "TaSTT_lighting.cginc"
      ENDCG
    }
  }
  //CustomEditor "TaSTTShaderGUI"
}

