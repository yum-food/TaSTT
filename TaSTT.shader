Shader "Unlit/TaSTT"
{
  Properties
  {
    _MainTex ("Texture", 2D) = "white" {}
    // software "engineering" LULW
    _Letter_Row00_Col00("_Letter_Row00_Col00", float) = 64
    _Letter_Row00_Col01("_Letter_Row00_Col01", float) = 64
    _Letter_Row00_Col02("_Letter_Row00_Col02", float) = 64
    _Letter_Row00_Col03("_Letter_Row00_Col03", float) = 64
    _Letter_Row00_Col04("_Letter_Row00_Col04", float) = 64
    _Letter_Row00_Col05("_Letter_Row00_Col05", float) = 64
    _Letter_Row00_Col06("_Letter_Row00_Col06", float) = 64
    _Letter_Row00_Col07("_Letter_Row00_Col07", float) = 64
    _Letter_Row00_Col08("_Letter_Row00_Col08", float) = 64
    _Letter_Row00_Col09("_Letter_Row00_Col09", float) = 64
    _Letter_Row00_Col10("_Letter_Row00_Col10", float) = 64
    _Letter_Row00_Col11("_Letter_Row00_Col11", float) = 64
    _Letter_Row00_Col12("_Letter_Row00_Col12", float) = 64
    _Letter_Row00_Col13("_Letter_Row00_Col13", float) = 64
    _Letter_Row00_Col14("_Letter_Row00_Col14", float) = 64
    _Letter_Row00_Col15("_Letter_Row00_Col15", float) = 64
    _Letter_Row00_Col16("_Letter_Row00_Col16", float) = 64
    _Letter_Row00_Col17("_Letter_Row00_Col17", float) = 64
    _Letter_Row00_Col18("_Letter_Row00_Col18", float) = 64
    _Letter_Row00_Col19("_Letter_Row00_Col19", float) = 64
    _Letter_Row00_Col20("_Letter_Row00_Col20", float) = 64
    _Letter_Row00_Col21("_Letter_Row00_Col21", float) = 64
    _Letter_Row00_Col22("_Letter_Row00_Col22", float) = 64
    _Letter_Row00_Col23("_Letter_Row00_Col23", float) = 64
    _Letter_Row00_Col24("_Letter_Row00_Col24", float) = 64
    _Letter_Row00_Col25("_Letter_Row00_Col25", float) = 64
    _Letter_Row00_Col26("_Letter_Row00_Col26", float) = 64
    _Letter_Row00_Col27("_Letter_Row00_Col27", float) = 64
    _Letter_Row00_Col28("_Letter_Row00_Col28", float) = 64
    _Letter_Row00_Col29("_Letter_Row00_Col29", float) = 64
    _Letter_Row00_Col30("_Letter_Row00_Col30", float) = 64
    _Letter_Row00_Col31("_Letter_Row00_Col31", float) = 64
    _Letter_Row00_Col32("_Letter_Row00_Col32", float) = 64
    _Letter_Row00_Col33("_Letter_Row00_Col33", float) = 64
    _Letter_Row00_Col34("_Letter_Row00_Col34", float) = 64
    _Letter_Row00_Col35("_Letter_Row00_Col35", float) = 64
    _Letter_Row00_Col36("_Letter_Row00_Col36", float) = 64
    _Letter_Row00_Col37("_Letter_Row00_Col37", float) = 64
    _Letter_Row00_Col38("_Letter_Row00_Col38", float) = 64
    _Letter_Row00_Col39("_Letter_Row00_Col39", float) = 64
    _Letter_Row00_Col40("_Letter_Row00_Col40", float) = 64
    _Letter_Row00_Col41("_Letter_Row00_Col41", float) = 64
    _Letter_Row00_Col42("_Letter_Row00_Col42", float) = 64
    _Letter_Row00_Col43("_Letter_Row00_Col43", float) = 64
    _Letter_Row01_Col00("_Letter_Row01_Col00", float) = 64
    _Letter_Row01_Col01("_Letter_Row01_Col01", float) = 64
    _Letter_Row01_Col02("_Letter_Row01_Col02", float) = 64
    _Letter_Row01_Col03("_Letter_Row01_Col03", float) = 64
    _Letter_Row01_Col04("_Letter_Row01_Col04", float) = 64
    _Letter_Row01_Col05("_Letter_Row01_Col05", float) = 64
    _Letter_Row01_Col06("_Letter_Row01_Col06", float) = 64
    _Letter_Row01_Col07("_Letter_Row01_Col07", float) = 64
    _Letter_Row01_Col08("_Letter_Row01_Col08", float) = 64
    _Letter_Row01_Col09("_Letter_Row01_Col09", float) = 64
    _Letter_Row01_Col10("_Letter_Row01_Col10", float) = 64
    _Letter_Row01_Col11("_Letter_Row01_Col11", float) = 64
    _Letter_Row01_Col12("_Letter_Row01_Col12", float) = 64
    _Letter_Row01_Col13("_Letter_Row01_Col13", float) = 64
    _Letter_Row01_Col14("_Letter_Row01_Col14", float) = 64
    _Letter_Row01_Col15("_Letter_Row01_Col15", float) = 64
    _Letter_Row01_Col16("_Letter_Row01_Col16", float) = 64
    _Letter_Row01_Col17("_Letter_Row01_Col17", float) = 64
    _Letter_Row01_Col18("_Letter_Row01_Col18", float) = 64
    _Letter_Row01_Col19("_Letter_Row01_Col19", float) = 64
    _Letter_Row01_Col20("_Letter_Row01_Col20", float) = 64
    _Letter_Row01_Col21("_Letter_Row01_Col21", float) = 64
    _Letter_Row01_Col22("_Letter_Row01_Col22", float) = 64
    _Letter_Row01_Col23("_Letter_Row01_Col23", float) = 64
    _Letter_Row01_Col24("_Letter_Row01_Col24", float) = 64
    _Letter_Row01_Col25("_Letter_Row01_Col25", float) = 64
    _Letter_Row01_Col26("_Letter_Row01_Col26", float) = 64
    _Letter_Row01_Col27("_Letter_Row01_Col27", float) = 64
    _Letter_Row01_Col28("_Letter_Row01_Col28", float) = 64
    _Letter_Row01_Col29("_Letter_Row01_Col29", float) = 64
    _Letter_Row01_Col30("_Letter_Row01_Col30", float) = 64
    _Letter_Row01_Col31("_Letter_Row01_Col31", float) = 64
    _Letter_Row01_Col32("_Letter_Row01_Col32", float) = 64
    _Letter_Row01_Col33("_Letter_Row01_Col33", float) = 64
    _Letter_Row01_Col34("_Letter_Row01_Col34", float) = 64
    _Letter_Row01_Col35("_Letter_Row01_Col35", float) = 64
    _Letter_Row01_Col36("_Letter_Row01_Col36", float) = 64
    _Letter_Row01_Col37("_Letter_Row01_Col37", float) = 64
    _Letter_Row01_Col38("_Letter_Row01_Col38", float) = 64
    _Letter_Row01_Col39("_Letter_Row01_Col39", float) = 64
    _Letter_Row01_Col40("_Letter_Row01_Col40", float) = 64
    _Letter_Row01_Col41("_Letter_Row01_Col41", float) = 64
    _Letter_Row01_Col42("_Letter_Row01_Col42", float) = 64
    _Letter_Row01_Col43("_Letter_Row01_Col43", float) = 64
    _Letter_Row02_Col00("_Letter_Row02_Col00", float) = 64
    _Letter_Row02_Col01("_Letter_Row02_Col01", float) = 64
    _Letter_Row02_Col02("_Letter_Row02_Col02", float) = 64
    _Letter_Row02_Col03("_Letter_Row02_Col03", float) = 64
    _Letter_Row02_Col04("_Letter_Row02_Col04", float) = 64
    _Letter_Row02_Col05("_Letter_Row02_Col05", float) = 64
    _Letter_Row02_Col06("_Letter_Row02_Col06", float) = 64
    _Letter_Row02_Col07("_Letter_Row02_Col07", float) = 64
    _Letter_Row02_Col08("_Letter_Row02_Col08", float) = 64
    _Letter_Row02_Col09("_Letter_Row02_Col09", float) = 64
    _Letter_Row02_Col10("_Letter_Row02_Col10", float) = 64
    _Letter_Row02_Col11("_Letter_Row02_Col11", float) = 64
    _Letter_Row02_Col12("_Letter_Row02_Col12", float) = 64
    _Letter_Row02_Col13("_Letter_Row02_Col13", float) = 64
    _Letter_Row02_Col14("_Letter_Row02_Col14", float) = 64
    _Letter_Row02_Col15("_Letter_Row02_Col15", float) = 64
    _Letter_Row02_Col16("_Letter_Row02_Col16", float) = 64
    _Letter_Row02_Col17("_Letter_Row02_Col17", float) = 64
    _Letter_Row02_Col18("_Letter_Row02_Col18", float) = 64
    _Letter_Row02_Col19("_Letter_Row02_Col19", float) = 64
    _Letter_Row02_Col20("_Letter_Row02_Col20", float) = 64
    _Letter_Row02_Col21("_Letter_Row02_Col21", float) = 64
    _Letter_Row02_Col22("_Letter_Row02_Col22", float) = 64
    _Letter_Row02_Col23("_Letter_Row02_Col23", float) = 64
    _Letter_Row02_Col24("_Letter_Row02_Col24", float) = 64
    _Letter_Row02_Col25("_Letter_Row02_Col25", float) = 64
    _Letter_Row02_Col26("_Letter_Row02_Col26", float) = 64
    _Letter_Row02_Col27("_Letter_Row02_Col27", float) = 64
    _Letter_Row02_Col28("_Letter_Row02_Col28", float) = 64
    _Letter_Row02_Col29("_Letter_Row02_Col29", float) = 64
    _Letter_Row02_Col30("_Letter_Row02_Col30", float) = 64
    _Letter_Row02_Col31("_Letter_Row02_Col31", float) = 64
    _Letter_Row02_Col32("_Letter_Row02_Col32", float) = 64
    _Letter_Row02_Col33("_Letter_Row02_Col33", float) = 64
    _Letter_Row02_Col34("_Letter_Row02_Col34", float) = 64
    _Letter_Row02_Col35("_Letter_Row02_Col35", float) = 64
    _Letter_Row02_Col36("_Letter_Row02_Col36", float) = 64
    _Letter_Row02_Col37("_Letter_Row02_Col37", float) = 64
    _Letter_Row02_Col38("_Letter_Row02_Col38", float) = 64
    _Letter_Row02_Col39("_Letter_Row02_Col39", float) = 64
    _Letter_Row02_Col40("_Letter_Row02_Col40", float) = 64
    _Letter_Row02_Col41("_Letter_Row02_Col41", float) = 64
    _Letter_Row02_Col42("_Letter_Row02_Col42", float) = 64
    _Letter_Row02_Col43("_Letter_Row02_Col43", float) = 64
    _Letter_Row03_Col00("_Letter_Row03_Col00", float) = 64
    _Letter_Row03_Col01("_Letter_Row03_Col01", float) = 64
    _Letter_Row03_Col02("_Letter_Row03_Col02", float) = 64
    _Letter_Row03_Col03("_Letter_Row03_Col03", float) = 64
    _Letter_Row03_Col04("_Letter_Row03_Col04", float) = 64
    _Letter_Row03_Col05("_Letter_Row03_Col05", float) = 64
    _Letter_Row03_Col06("_Letter_Row03_Col06", float) = 64
    _Letter_Row03_Col07("_Letter_Row03_Col07", float) = 64
    _Letter_Row03_Col08("_Letter_Row03_Col08", float) = 64
    _Letter_Row03_Col09("_Letter_Row03_Col09", float) = 64
    _Letter_Row03_Col10("_Letter_Row03_Col10", float) = 64
    _Letter_Row03_Col11("_Letter_Row03_Col11", float) = 64
    _Letter_Row03_Col12("_Letter_Row03_Col12", float) = 64
    _Letter_Row03_Col13("_Letter_Row03_Col13", float) = 64
    _Letter_Row03_Col14("_Letter_Row03_Col14", float) = 64
    _Letter_Row03_Col15("_Letter_Row03_Col15", float) = 64
    _Letter_Row03_Col16("_Letter_Row03_Col16", float) = 64
    _Letter_Row03_Col17("_Letter_Row03_Col17", float) = 64
    _Letter_Row03_Col18("_Letter_Row03_Col18", float) = 64
    _Letter_Row03_Col19("_Letter_Row03_Col19", float) = 64
    _Letter_Row03_Col20("_Letter_Row03_Col20", float) = 64
    _Letter_Row03_Col21("_Letter_Row03_Col21", float) = 64
    _Letter_Row03_Col22("_Letter_Row03_Col22", float) = 64
    _Letter_Row03_Col23("_Letter_Row03_Col23", float) = 64
    _Letter_Row03_Col24("_Letter_Row03_Col24", float) = 64
    _Letter_Row03_Col25("_Letter_Row03_Col25", float) = 64
    _Letter_Row03_Col26("_Letter_Row03_Col26", float) = 64
    _Letter_Row03_Col27("_Letter_Row03_Col27", float) = 64
    _Letter_Row03_Col28("_Letter_Row03_Col28", float) = 64
    _Letter_Row03_Col29("_Letter_Row03_Col29", float) = 64
    _Letter_Row03_Col30("_Letter_Row03_Col30", float) = 64
    _Letter_Row03_Col31("_Letter_Row03_Col31", float) = 64
    _Letter_Row03_Col32("_Letter_Row03_Col32", float) = 64
    _Letter_Row03_Col33("_Letter_Row03_Col33", float) = 64
    _Letter_Row03_Col34("_Letter_Row03_Col34", float) = 64
    _Letter_Row03_Col35("_Letter_Row03_Col35", float) = 64
    _Letter_Row03_Col36("_Letter_Row03_Col36", float) = 64
    _Letter_Row03_Col37("_Letter_Row03_Col37", float) = 64
    _Letter_Row03_Col38("_Letter_Row03_Col38", float) = 64
    _Letter_Row03_Col39("_Letter_Row03_Col39", float) = 64
    _Letter_Row03_Col40("_Letter_Row03_Col40", float) = 64
    _Letter_Row03_Col41("_Letter_Row03_Col41", float) = 64
    _Letter_Row03_Col42("_Letter_Row03_Col42", float) = 64
    _Letter_Row03_Col43("_Letter_Row03_Col43", float) = 64
  }
  SubShader
  {
    Tags { "RenderType"="Opaque" "Queue"="AlphaTest"}
    LOD 100

    Pass
    {
      Blend SrcAlpha OneMinusSrcAlpha

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

      float _Letter_Row00_Col00;
      float _Letter_Row00_Col01;
      float _Letter_Row00_Col02;
      float _Letter_Row00_Col03;
      float _Letter_Row00_Col04;
      float _Letter_Row00_Col05;
      float _Letter_Row00_Col06;
      float _Letter_Row00_Col07;
      float _Letter_Row00_Col08;
      float _Letter_Row00_Col09;
      float _Letter_Row00_Col10;
      float _Letter_Row00_Col11;
      float _Letter_Row00_Col12;
      float _Letter_Row00_Col13;
      float _Letter_Row00_Col14;
      float _Letter_Row00_Col15;
      float _Letter_Row00_Col16;
      float _Letter_Row00_Col17;
      float _Letter_Row00_Col18;
      float _Letter_Row00_Col19;
      float _Letter_Row00_Col20;
      float _Letter_Row00_Col21;
      float _Letter_Row00_Col22;
      float _Letter_Row00_Col23;
      float _Letter_Row00_Col24;
      float _Letter_Row00_Col25;
      float _Letter_Row00_Col26;
      float _Letter_Row00_Col27;
      float _Letter_Row00_Col28;
      float _Letter_Row00_Col29;
      float _Letter_Row00_Col30;
      float _Letter_Row00_Col31;
      float _Letter_Row00_Col32;
      float _Letter_Row00_Col33;
      float _Letter_Row00_Col34;
      float _Letter_Row00_Col35;
      float _Letter_Row00_Col36;
      float _Letter_Row00_Col37;
      float _Letter_Row00_Col38;
      float _Letter_Row00_Col39;
      float _Letter_Row00_Col40;
      float _Letter_Row00_Col41;
      float _Letter_Row00_Col42;
      float _Letter_Row00_Col43;
      float _Letter_Row01_Col00;
      float _Letter_Row01_Col01;
      float _Letter_Row01_Col02;
      float _Letter_Row01_Col03;
      float _Letter_Row01_Col04;
      float _Letter_Row01_Col05;
      float _Letter_Row01_Col06;
      float _Letter_Row01_Col07;
      float _Letter_Row01_Col08;
      float _Letter_Row01_Col09;
      float _Letter_Row01_Col10;
      float _Letter_Row01_Col11;
      float _Letter_Row01_Col12;
      float _Letter_Row01_Col13;
      float _Letter_Row01_Col14;
      float _Letter_Row01_Col15;
      float _Letter_Row01_Col16;
      float _Letter_Row01_Col17;
      float _Letter_Row01_Col18;
      float _Letter_Row01_Col19;
      float _Letter_Row01_Col20;
      float _Letter_Row01_Col21;
      float _Letter_Row01_Col22;
      float _Letter_Row01_Col23;
      float _Letter_Row01_Col24;
      float _Letter_Row01_Col25;
      float _Letter_Row01_Col26;
      float _Letter_Row01_Col27;
      float _Letter_Row01_Col28;
      float _Letter_Row01_Col29;
      float _Letter_Row01_Col30;
      float _Letter_Row01_Col31;
      float _Letter_Row01_Col32;
      float _Letter_Row01_Col33;
      float _Letter_Row01_Col34;
      float _Letter_Row01_Col35;
      float _Letter_Row01_Col36;
      float _Letter_Row01_Col37;
      float _Letter_Row01_Col38;
      float _Letter_Row01_Col39;
      float _Letter_Row01_Col40;
      float _Letter_Row01_Col41;
      float _Letter_Row01_Col42;
      float _Letter_Row01_Col43;
      float _Letter_Row02_Col00;
      float _Letter_Row02_Col01;
      float _Letter_Row02_Col02;
      float _Letter_Row02_Col03;
      float _Letter_Row02_Col04;
      float _Letter_Row02_Col05;
      float _Letter_Row02_Col06;
      float _Letter_Row02_Col07;
      float _Letter_Row02_Col08;
      float _Letter_Row02_Col09;
      float _Letter_Row02_Col10;
      float _Letter_Row02_Col11;
      float _Letter_Row02_Col12;
      float _Letter_Row02_Col13;
      float _Letter_Row02_Col14;
      float _Letter_Row02_Col15;
      float _Letter_Row02_Col16;
      float _Letter_Row02_Col17;
      float _Letter_Row02_Col18;
      float _Letter_Row02_Col19;
      float _Letter_Row02_Col20;
      float _Letter_Row02_Col21;
      float _Letter_Row02_Col22;
      float _Letter_Row02_Col23;
      float _Letter_Row02_Col24;
      float _Letter_Row02_Col25;
      float _Letter_Row02_Col26;
      float _Letter_Row02_Col27;
      float _Letter_Row02_Col28;
      float _Letter_Row02_Col29;
      float _Letter_Row02_Col30;
      float _Letter_Row02_Col31;
      float _Letter_Row02_Col32;
      float _Letter_Row02_Col33;
      float _Letter_Row02_Col34;
      float _Letter_Row02_Col35;
      float _Letter_Row02_Col36;
      float _Letter_Row02_Col37;
      float _Letter_Row02_Col38;
      float _Letter_Row02_Col39;
      float _Letter_Row02_Col40;
      float _Letter_Row02_Col41;
      float _Letter_Row02_Col42;
      float _Letter_Row02_Col43;
      float _Letter_Row03_Col00;
      float _Letter_Row03_Col01;
      float _Letter_Row03_Col02;
      float _Letter_Row03_Col03;
      float _Letter_Row03_Col04;
      float _Letter_Row03_Col05;
      float _Letter_Row03_Col06;
      float _Letter_Row03_Col07;
      float _Letter_Row03_Col08;
      float _Letter_Row03_Col09;
      float _Letter_Row03_Col10;
      float _Letter_Row03_Col11;
      float _Letter_Row03_Col12;
      float _Letter_Row03_Col13;
      float _Letter_Row03_Col14;
      float _Letter_Row03_Col15;
      float _Letter_Row03_Col16;
      float _Letter_Row03_Col17;
      float _Letter_Row03_Col18;
      float _Letter_Row03_Col19;
      float _Letter_Row03_Col20;
      float _Letter_Row03_Col21;
      float _Letter_Row03_Col22;
      float _Letter_Row03_Col23;
      float _Letter_Row03_Col24;
      float _Letter_Row03_Col25;
      float _Letter_Row03_Col26;
      float _Letter_Row03_Col27;
      float _Letter_Row03_Col28;
      float _Letter_Row03_Col29;
      float _Letter_Row03_Col30;
      float _Letter_Row03_Col31;
      float _Letter_Row03_Col32;
      float _Letter_Row03_Col33;
      float _Letter_Row03_Col34;
      float _Letter_Row03_Col35;
      float _Letter_Row03_Col36;
      float _Letter_Row03_Col37;
      float _Letter_Row03_Col38;
      float _Letter_Row03_Col39;
      float _Letter_Row03_Col40;
      float _Letter_Row03_Col41;
      float _Letter_Row03_Col42;
      float _Letter_Row03_Col43;

      v2f vert (appdata v)
      {
        v2f o;
        o.vertex = UnityObjectToClipPos(v.vertex);
        o.uv = 1.0 - v.uv;
        return o;
      }

      float2 AddMarginToUV(float2 uv, float x_frac, float y_frac)
      {
        float2 lo = float2(-x_frac / 2, -y_frac / 2);
        float2 hi = float2(1.0 + x_frac / 2, 1.0 + y_frac / 2);

        return clamp(lerp(lo, hi, uv), 0.0, 1.0);
      }

      // Write the nth letter in the current cell and return the value of the
      // pixel.
      float2 GetLetter(float2 uv, int nth_letter)
      {
        // UV spans from [0,1] to [0,1].
        // 'U' is horizontal; cols.
        // 'V' is vertical; rows.
        //
        // I want to divide the mesh into an m x n grid.
        // I want to know what grid cell I'm in. This is simply u * m, v * n.
        int CHAR_ROWS = 4;
        int CHAR_COLS = 44;

        // OK, I know what cell I'm in. Now I need to know how far across it I
        // am. Produce a float in the range [0, CHAR_COLS).
        float CHAR_FRAC_COL = uv.x * CHAR_COLS - floor(uv.x * CHAR_COLS);
        float CHAR_FRAC_ROW = uv.y * CHAR_ROWS - floor(uv.y * CHAR_ROWS);

        // This is the number of rows and columns in the actual texture.
        float LETTER_COLS = 26.6;
        float LETTER_ROWS = 11.7;

        float LETTER_COL = fmod(nth_letter, floor(LETTER_COLS));
        float LETTER_ROW = floor(LETTER_ROWS) - floor(nth_letter / floor(LETTER_COLS));

        float LETTER_UV_ROW = (LETTER_ROW + CHAR_FRAC_ROW - 0.35) / LETTER_ROWS;
        float LETTER_UV_COL = (LETTER_COL + CHAR_FRAC_COL) / LETTER_COLS;

        float2 result;
        result.x = LETTER_UV_COL;
        result.y = LETTER_UV_ROW;

        return result;
      }

      // Get the value of the parameter for the cell we're in.
      float GetLetterParameter(float2 uv)
      {
        float CHAR_ROWS = 4.0;
        float CHAR_COLS = 44.0;
        float CHAR_COL = floor(uv.x * CHAR_COLS);
        float CHAR_ROW = floor(uv.y * CHAR_ROWS);

        [forcecase] switch (CHAR_ROW)
        {
          case 3:
            [forcecase] switch (CHAR_COL) {
              case 0:
                return _Letter_Row00_Col00;
              case 1:
                return _Letter_Row00_Col01;
              case 2:
                return _Letter_Row00_Col02;
              case 3:
                return _Letter_Row00_Col03;
              case 4:
                return _Letter_Row00_Col04;
              case 5:
                return _Letter_Row00_Col05;
              case 6:
                return _Letter_Row00_Col06;
              case 7:
                return _Letter_Row00_Col07;
              case 8:
                return _Letter_Row00_Col08;
              case 9:
                return _Letter_Row00_Col09;
              case 10:
                return _Letter_Row00_Col10;
              case 11:
                return _Letter_Row00_Col11;
              case 12:
                return _Letter_Row00_Col12;
              case 13:
                return _Letter_Row00_Col13;
              case 14:
                return _Letter_Row00_Col14;
              case 15:
                return _Letter_Row00_Col15;
              case 16:
                return _Letter_Row00_Col16;
              case 17:
                return _Letter_Row00_Col17;
              case 18:
                return _Letter_Row00_Col18;
              case 19:
                return _Letter_Row00_Col19;
              case 20:
                return _Letter_Row00_Col20;
              case 21:
                return _Letter_Row00_Col21;
              case 22:
                return _Letter_Row00_Col22;
              case 23:
                return _Letter_Row00_Col23;
              case 24:
                return _Letter_Row00_Col24;
              case 25:
                return _Letter_Row00_Col25;
              case 26:
                return _Letter_Row00_Col26;
              case 27:
                return _Letter_Row00_Col27;
              case 28:
                return _Letter_Row00_Col28;
              case 29:
                return _Letter_Row00_Col29;
              case 30:
                return _Letter_Row00_Col30;
              case 31:
                return _Letter_Row00_Col31;
              case 32:
                return _Letter_Row00_Col32;
              case 33:
                return _Letter_Row00_Col33;
              case 34:
                return _Letter_Row00_Col34;
              case 35:
                return _Letter_Row00_Col35;
              case 36:
                return _Letter_Row00_Col36;
              case 37:
                return _Letter_Row00_Col37;
              case 38:
                return _Letter_Row00_Col38;
              case 39:
                return _Letter_Row00_Col39;
              case 40:
                return _Letter_Row00_Col40;
              case 41:
                return _Letter_Row00_Col41;
              case 42:
                return _Letter_Row00_Col42;
              case 43:
                return _Letter_Row00_Col43;
              default:
                return 0;
            }
          case 2:
            [forcecase] switch (CHAR_COL) {
              case 0:
                return _Letter_Row01_Col00;
              case 1:
                return _Letter_Row01_Col01;
              case 2:
                return _Letter_Row01_Col02;
              case 3:
                return _Letter_Row01_Col03;
              case 4:
                return _Letter_Row01_Col04;
              case 5:
                return _Letter_Row01_Col05;
              case 6:
                return _Letter_Row01_Col06;
              case 7:
                return _Letter_Row01_Col07;
              case 8:
                return _Letter_Row01_Col08;
              case 9:
                return _Letter_Row01_Col09;
              case 10:
                return _Letter_Row01_Col10;
              case 11:
                return _Letter_Row01_Col11;
              case 12:
                return _Letter_Row01_Col12;
              case 13:
                return _Letter_Row01_Col13;
              case 14:
                return _Letter_Row01_Col14;
              case 15:
                return _Letter_Row01_Col15;
              case 16:
                return _Letter_Row01_Col16;
              case 17:
                return _Letter_Row01_Col17;
              case 18:
                return _Letter_Row01_Col18;
              case 19:
                return _Letter_Row01_Col19;
              case 20:
                return _Letter_Row01_Col20;
              case 21:
                return _Letter_Row01_Col21;
              case 22:
                return _Letter_Row01_Col22;
              case 23:
                return _Letter_Row01_Col23;
              case 24:
                return _Letter_Row01_Col24;
              case 25:
                return _Letter_Row01_Col25;
              case 26:
                return _Letter_Row01_Col26;
              case 27:
                return _Letter_Row01_Col27;
              case 28:
                return _Letter_Row01_Col28;
              case 29:
                return _Letter_Row01_Col29;
              case 30:
                return _Letter_Row01_Col30;
              case 31:
                return _Letter_Row01_Col31;
              case 32:
                return _Letter_Row01_Col32;
              case 33:
                return _Letter_Row01_Col33;
              case 34:
                return _Letter_Row01_Col34;
              case 35:
                return _Letter_Row01_Col35;
              case 36:
                return _Letter_Row01_Col36;
              case 37:
                return _Letter_Row01_Col37;
              case 38:
                return _Letter_Row01_Col38;
              case 39:
                return _Letter_Row01_Col39;
              case 40:
                return _Letter_Row01_Col40;
              case 41:
                return _Letter_Row01_Col41;
              case 42:
                return _Letter_Row01_Col42;
              case 43:
                return _Letter_Row01_Col43;
              default:
                return 0;
            }
          case 1:
            [forcecase] switch (CHAR_COL) {
              case 0:
                return _Letter_Row02_Col00;
              case 1:
                return _Letter_Row02_Col01;
              case 2:
                return _Letter_Row02_Col02;
              case 3:
                return _Letter_Row02_Col03;
              case 4:
                return _Letter_Row02_Col04;
              case 5:
                return _Letter_Row02_Col05;
              case 6:
                return _Letter_Row02_Col06;
              case 7:
                return _Letter_Row02_Col07;
              case 8:
                return _Letter_Row02_Col08;
              case 9:
                return _Letter_Row02_Col09;
              case 10:
                return _Letter_Row02_Col10;
              case 11:
                return _Letter_Row02_Col11;
              case 12:
                return _Letter_Row02_Col12;
              case 13:
                return _Letter_Row02_Col13;
              case 14:
                return _Letter_Row02_Col14;
              case 15:
                return _Letter_Row02_Col15;
              case 16:
                return _Letter_Row02_Col16;
              case 17:
                return _Letter_Row02_Col17;
              case 18:
                return _Letter_Row02_Col18;
              case 19:
                return _Letter_Row02_Col19;
              case 20:
                return _Letter_Row02_Col20;
              case 21:
                return _Letter_Row02_Col21;
              case 22:
                return _Letter_Row02_Col22;
              case 23:
                return _Letter_Row02_Col23;
              case 24:
                return _Letter_Row02_Col24;
              case 25:
                return _Letter_Row02_Col25;
              case 26:
                return _Letter_Row02_Col26;
              case 27:
                return _Letter_Row02_Col27;
              case 28:
                return _Letter_Row02_Col28;
              case 29:
                return _Letter_Row02_Col29;
              case 30:
                return _Letter_Row02_Col30;
              case 31:
                return _Letter_Row02_Col31;
              case 32:
                return _Letter_Row02_Col32;
              case 33:
                return _Letter_Row02_Col33;
              case 34:
                return _Letter_Row02_Col34;
              case 35:
                return _Letter_Row02_Col35;
              case 36:
                return _Letter_Row02_Col36;
              case 37:
                return _Letter_Row02_Col37;
              case 38:
                return _Letter_Row02_Col38;
              case 39:
                return _Letter_Row02_Col39;
              case 40:
                return _Letter_Row02_Col40;
              case 41:
                return _Letter_Row02_Col41;
              case 42:
                return _Letter_Row02_Col42;
              case 43:
                return _Letter_Row02_Col43;
              default:
                return 0;
            }
          case 0:
            [forcecase] switch (CHAR_COL) {
              case 0:
                return _Letter_Row03_Col00;
              case 1:
                return _Letter_Row03_Col01;
              case 2:
                return _Letter_Row03_Col02;
              case 3:
                return _Letter_Row03_Col03;
              case 4:
                return _Letter_Row03_Col04;
              case 5:
                return _Letter_Row03_Col05;
              case 6:
                return _Letter_Row03_Col06;
              case 7:
                return _Letter_Row03_Col07;
              case 8:
                return _Letter_Row03_Col08;
              case 9:
                return _Letter_Row03_Col09;
              case 10:
                return _Letter_Row03_Col10;
              case 11:
                return _Letter_Row03_Col11;
              case 12:
                return _Letter_Row03_Col12;
              case 13:
                return _Letter_Row03_Col13;
              case 14:
                return _Letter_Row03_Col14;
              case 15:
                return _Letter_Row03_Col15;
              case 16:
                return _Letter_Row03_Col16;
              case 17:
                return _Letter_Row03_Col17;
              case 18:
                return _Letter_Row03_Col18;
              case 19:
                return _Letter_Row03_Col19;
              case 20:
                return _Letter_Row03_Col20;
              case 21:
                return _Letter_Row03_Col21;
              case 22:
                return _Letter_Row03_Col22;
              case 23:
                return _Letter_Row03_Col23;
              case 24:
                return _Letter_Row03_Col24;
              case 25:
                return _Letter_Row03_Col25;
              case 26:
                return _Letter_Row03_Col26;
              case 27:
                return _Letter_Row03_Col27;
              case 28:
                return _Letter_Row03_Col28;
              case 29:
                return _Letter_Row03_Col29;
              case 30:
                return _Letter_Row03_Col30;
              case 31:
                return _Letter_Row03_Col31;
              case 32:
                return _Letter_Row03_Col32;
              case 33:
                return _Letter_Row03_Col33;
              case 34:
                return _Letter_Row03_Col34;
              case 35:
                return _Letter_Row03_Col35;
              case 36:
                return _Letter_Row03_Col36;
              case 37:
                return _Letter_Row03_Col37;
              case 38:
                return _Letter_Row03_Col38;
              case 39:
                return _Letter_Row03_Col39;
              case 40:
                return _Letter_Row03_Col40;
              case 41:
                return _Letter_Row03_Col41;
              case 42:
                return _Letter_Row03_Col42;
              case 43:
                return _Letter_Row03_Col43;
              default:
                return 0;
            }
        }

        return 0;
      }

      fixed4 frag (v2f i) : SV_Target
      {
        float2 uv = i.uv;

        // Derived from github.com/pema99/shader-knowledge (MIT license).
        if (unity_CameraProjection[2][0] != 0.0 ||
            unity_CameraProjection[2][1] != 0.0) {
          uv.x = 1.0 - uv.x;
        }

        float uv_x_margin = 0.03;
        float uv_y_margin = 0.06;
        uv = AddMarginToUV(uv, uv_x_margin, uv_y_margin);

        float letter = floor(GetLetterParameter(uv));
        uv = GetLetter(uv, letter);
        fixed4 ret = _MainTex.Sample(sampler_linear_repeat, uv);
        return ret;
      }
      ENDCG
    }
  }
}
