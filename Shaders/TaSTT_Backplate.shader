Shader "Unlit/TaSTT_Backplate"
{
  Properties
  {
    _MainTex ("Texture", 2D) = "black" {}
  }
  SubShader
  {
    Tags { "RenderType"="Opaque" "Queue"="AlphaTest-1"}
    LOD 100

    Pass
    {
      Blend SrcAlpha OneMinusSrcAlpha
      Cull Off

      CGPROGRAM
      #pragma vertex vert
      #pragma fragment frag
      #pragma multi_compile

      #include "UnityCG.cginc"

      struct appdata
      {
        float4 vertex : POSITION;
        float2 uv : TEXCOORD0;
        float3 normal : NORMAL;
      };

      struct v2f
      {
        float2 uv : TEXCOORD0;
        float4 vertex : SV_POSITION;
      };

      Texture2D _MainTex;
      SamplerState sampler_linear_repeat;
      float4 _MainTex_ST;

      v2f vert (appdata v)
      {
        v2f o;
        o.vertex = UnityObjectToClipPos(v.vertex);
        o.uv = 1.0 - v.uv;
        return o;
      }

      fixed4 frag (v2f i) : SV_Target
      {

        fixed4 result = _MainTex.Sample(sampler_linear_repeat, i.uv);
        result.a = 1.0;
        return result;
      }
      ENDCG
    }
  }
}
