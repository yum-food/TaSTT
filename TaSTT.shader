Shader "Unlit/TaSTT"
{
  Properties
  {
    _MainTex ("Texture", 2D) = "white" {}
    // software "engineering" LULW
    _Letter_Row00_Col00("_Letter_Row00_Col00", int) = 64
    _Letter_Row00_Col01("_Letter_Row00_Col01", int) = 64
    _Letter_Row00_Col02("_Letter_Row00_Col02", int) = 64
    _Letter_Row00_Col03("_Letter_Row00_Col03", int) = 64
    _Letter_Row00_Col04("_Letter_Row00_Col04", int) = 64
    _Letter_Row00_Col05("_Letter_Row00_Col05", int) = 64
    _Letter_Row00_Col06("_Letter_Row00_Col06", int) = 64
    _Letter_Row00_Col07("_Letter_Row00_Col07", int) = 64
    _Letter_Row00_Col08("_Letter_Row00_Col08", int) = 64
    _Letter_Row00_Col09("_Letter_Row00_Col09", int) = 64
    _Letter_Row00_Col10("_Letter_Row00_Col10", int) = 64
    _Letter_Row00_Col11("_Letter_Row00_Col11", int) = 64
    _Letter_Row00_Col12("_Letter_Row00_Col12", int) = 64
    _Letter_Row00_Col13("_Letter_Row00_Col13", int) = 64
    _Letter_Row00_Col14("_Letter_Row00_Col14", int) = 64
    _Letter_Row00_Col15("_Letter_Row00_Col15", int) = 64
    _Letter_Row00_Col16("_Letter_Row00_Col16", int) = 64
    _Letter_Row00_Col17("_Letter_Row00_Col17", int) = 64
    _Letter_Row00_Col18("_Letter_Row00_Col18", int) = 64
    _Letter_Row00_Col19("_Letter_Row00_Col19", int) = 64
    _Letter_Row00_Col20("_Letter_Row00_Col20", int) = 64
    _Letter_Row00_Col21("_Letter_Row00_Col21", int) = 64
    _Letter_Row01_Col00("_Letter_Row01_Col00", int) = 64
    _Letter_Row01_Col01("_Letter_Row01_Col01", int) = 64
    _Letter_Row01_Col02("_Letter_Row01_Col02", int) = 64
    _Letter_Row01_Col03("_Letter_Row01_Col03", int) = 64
    _Letter_Row01_Col04("_Letter_Row01_Col04", int) = 64
    _Letter_Row01_Col05("_Letter_Row01_Col05", int) = 64
    _Letter_Row01_Col06("_Letter_Row01_Col06", int) = 64
    _Letter_Row01_Col07("_Letter_Row01_Col07", int) = 64
    _Letter_Row01_Col08("_Letter_Row01_Col08", int) = 64
    _Letter_Row01_Col09("_Letter_Row01_Col09", int) = 64
    _Letter_Row01_Col10("_Letter_Row01_Col10", int) = 64
    _Letter_Row01_Col11("_Letter_Row01_Col11", int) = 64
    _Letter_Row01_Col12("_Letter_Row01_Col12", int) = 64
    _Letter_Row01_Col13("_Letter_Row01_Col13", int) = 64
    _Letter_Row01_Col14("_Letter_Row01_Col14", int) = 64
    _Letter_Row01_Col15("_Letter_Row01_Col15", int) = 64
    _Letter_Row01_Col16("_Letter_Row01_Col16", int) = 64
    _Letter_Row01_Col17("_Letter_Row01_Col17", int) = 64
    _Letter_Row01_Col18("_Letter_Row01_Col18", int) = 64
    _Letter_Row01_Col19("_Letter_Row01_Col19", int) = 64
    _Letter_Row01_Col20("_Letter_Row01_Col20", int) = 64
    _Letter_Row01_Col21("_Letter_Row01_Col21", int) = 64
    _Letter_Row02_Col00("_Letter_Row02_Col00", int) = 64
    _Letter_Row02_Col01("_Letter_Row02_Col01", int) = 64
    _Letter_Row02_Col02("_Letter_Row02_Col02", int) = 64
    _Letter_Row02_Col03("_Letter_Row02_Col03", int) = 64
    _Letter_Row02_Col04("_Letter_Row02_Col04", int) = 64
    _Letter_Row02_Col05("_Letter_Row02_Col05", int) = 64
    _Letter_Row02_Col06("_Letter_Row02_Col06", int) = 64
    _Letter_Row02_Col07("_Letter_Row02_Col07", int) = 64
    _Letter_Row02_Col08("_Letter_Row02_Col08", int) = 64
    _Letter_Row02_Col09("_Letter_Row02_Col09", int) = 64
    _Letter_Row02_Col10("_Letter_Row02_Col10", int) = 64
    _Letter_Row02_Col11("_Letter_Row02_Col11", int) = 64
    _Letter_Row02_Col12("_Letter_Row02_Col12", int) = 64
    _Letter_Row02_Col13("_Letter_Row02_Col13", int) = 64
    _Letter_Row02_Col14("_Letter_Row02_Col14", int) = 64
    _Letter_Row02_Col15("_Letter_Row02_Col15", int) = 64
    _Letter_Row02_Col16("_Letter_Row02_Col16", int) = 64
    _Letter_Row02_Col17("_Letter_Row02_Col17", int) = 64
    _Letter_Row02_Col18("_Letter_Row02_Col18", int) = 64
    _Letter_Row02_Col19("_Letter_Row02_Col19", int) = 64
    _Letter_Row02_Col20("_Letter_Row02_Col20", int) = 64
    _Letter_Row02_Col21("_Letter_Row02_Col21", int) = 64
    _Letter_Row03_Col00("_Letter_Row03_Col00", int) = 64
    _Letter_Row03_Col01("_Letter_Row03_Col01", int) = 64
    _Letter_Row03_Col02("_Letter_Row03_Col02", int) = 64
    _Letter_Row03_Col03("_Letter_Row03_Col03", int) = 64
    _Letter_Row03_Col04("_Letter_Row03_Col04", int) = 64
    _Letter_Row03_Col05("_Letter_Row03_Col05", int) = 64
    _Letter_Row03_Col06("_Letter_Row03_Col06", int) = 64
    _Letter_Row03_Col07("_Letter_Row03_Col07", int) = 64
    _Letter_Row03_Col08("_Letter_Row03_Col08", int) = 64
    _Letter_Row03_Col09("_Letter_Row03_Col09", int) = 64
    _Letter_Row03_Col10("_Letter_Row03_Col10", int) = 64
    _Letter_Row03_Col11("_Letter_Row03_Col11", int) = 64
    _Letter_Row03_Col12("_Letter_Row03_Col12", int) = 64
    _Letter_Row03_Col13("_Letter_Row03_Col13", int) = 64
    _Letter_Row03_Col14("_Letter_Row03_Col14", int) = 64
    _Letter_Row03_Col15("_Letter_Row03_Col15", int) = 64
    _Letter_Row03_Col16("_Letter_Row03_Col16", int) = 64
    _Letter_Row03_Col17("_Letter_Row03_Col17", int) = 64
    _Letter_Row03_Col18("_Letter_Row03_Col18", int) = 64
    _Letter_Row03_Col19("_Letter_Row03_Col19", int) = 64
    _Letter_Row03_Col20("_Letter_Row03_Col20", int) = 64
    _Letter_Row03_Col21("_Letter_Row03_Col21", int) = 64
    _Letter_Row04_Col00("_Letter_Row04_Col00", int) = 64
    _Letter_Row04_Col01("_Letter_Row04_Col01", int) = 64
    _Letter_Row04_Col02("_Letter_Row04_Col02", int) = 64
    _Letter_Row04_Col03("_Letter_Row04_Col03", int) = 64
    _Letter_Row04_Col04("_Letter_Row04_Col04", int) = 64
    _Letter_Row04_Col05("_Letter_Row04_Col05", int) = 64
    _Letter_Row04_Col06("_Letter_Row04_Col06", int) = 64
    _Letter_Row04_Col07("_Letter_Row04_Col07", int) = 64
    _Letter_Row04_Col08("_Letter_Row04_Col08", int) = 64
    _Letter_Row04_Col09("_Letter_Row04_Col09", int) = 64
    _Letter_Row04_Col10("_Letter_Row04_Col10", int) = 64
    _Letter_Row04_Col11("_Letter_Row04_Col11", int) = 64
    _Letter_Row04_Col12("_Letter_Row04_Col12", int) = 64
    _Letter_Row04_Col13("_Letter_Row04_Col13", int) = 64
    _Letter_Row04_Col14("_Letter_Row04_Col14", int) = 64
    _Letter_Row04_Col15("_Letter_Row04_Col15", int) = 64
    _Letter_Row04_Col16("_Letter_Row04_Col16", int) = 64
    _Letter_Row04_Col17("_Letter_Row04_Col17", int) = 64
    _Letter_Row04_Col18("_Letter_Row04_Col18", int) = 64
    _Letter_Row04_Col19("_Letter_Row04_Col19", int) = 64
    _Letter_Row04_Col20("_Letter_Row04_Col20", int) = 64
    _Letter_Row04_Col21("_Letter_Row04_Col21", int) = 64
    _Letter_Row05_Col00("_Letter_Row05_Col00", int) = 64
    _Letter_Row05_Col01("_Letter_Row05_Col01", int) = 64
    _Letter_Row05_Col02("_Letter_Row05_Col02", int) = 64
    _Letter_Row05_Col03("_Letter_Row05_Col03", int) = 64
    _Letter_Row05_Col04("_Letter_Row05_Col04", int) = 64
    _Letter_Row05_Col05("_Letter_Row05_Col05", int) = 64
    _Letter_Row05_Col06("_Letter_Row05_Col06", int) = 64
    _Letter_Row05_Col07("_Letter_Row05_Col07", int) = 64
    _Letter_Row05_Col08("_Letter_Row05_Col08", int) = 64
    _Letter_Row05_Col09("_Letter_Row05_Col09", int) = 64
    _Letter_Row05_Col10("_Letter_Row05_Col10", int) = 64
    _Letter_Row05_Col11("_Letter_Row05_Col11", int) = 64
    _Letter_Row05_Col12("_Letter_Row05_Col12", int) = 64
    _Letter_Row05_Col13("_Letter_Row05_Col13", int) = 64
    _Letter_Row05_Col14("_Letter_Row05_Col14", int) = 64
    _Letter_Row05_Col15("_Letter_Row05_Col15", int) = 64
    _Letter_Row05_Col16("_Letter_Row05_Col16", int) = 64
    _Letter_Row05_Col17("_Letter_Row05_Col17", int) = 64
    _Letter_Row05_Col18("_Letter_Row05_Col18", int) = 64
    _Letter_Row05_Col19("_Letter_Row05_Col19", int) = 64
    _Letter_Row05_Col20("_Letter_Row05_Col20", int) = 64
    _Letter_Row05_Col21("_Letter_Row05_Col21", int) = 64
    _Letter_Row06_Col00("_Letter_Row06_Col00", int) = 64
    _Letter_Row06_Col01("_Letter_Row06_Col01", int) = 64
    _Letter_Row06_Col02("_Letter_Row06_Col02", int) = 64
    _Letter_Row06_Col03("_Letter_Row06_Col03", int) = 64
    _Letter_Row06_Col04("_Letter_Row06_Col04", int) = 64
    _Letter_Row06_Col05("_Letter_Row06_Col05", int) = 64
    _Letter_Row06_Col06("_Letter_Row06_Col06", int) = 64
    _Letter_Row06_Col07("_Letter_Row06_Col07", int) = 64
    _Letter_Row06_Col08("_Letter_Row06_Col08", int) = 64
    _Letter_Row06_Col09("_Letter_Row06_Col09", int) = 64
    _Letter_Row06_Col10("_Letter_Row06_Col10", int) = 64
    _Letter_Row06_Col11("_Letter_Row06_Col11", int) = 64
    _Letter_Row06_Col12("_Letter_Row06_Col12", int) = 64
    _Letter_Row06_Col13("_Letter_Row06_Col13", int) = 64
    _Letter_Row06_Col14("_Letter_Row06_Col14", int) = 64
    _Letter_Row06_Col15("_Letter_Row06_Col15", int) = 64
    _Letter_Row06_Col16("_Letter_Row06_Col16", int) = 64
    _Letter_Row06_Col17("_Letter_Row06_Col17", int) = 64
    _Letter_Row06_Col18("_Letter_Row06_Col18", int) = 64
    _Letter_Row06_Col19("_Letter_Row06_Col19", int) = 64
    _Letter_Row06_Col20("_Letter_Row06_Col20", int) = 64
    _Letter_Row06_Col21("_Letter_Row06_Col21", int) = 64
    _Letter_Row07_Col00("_Letter_Row07_Col00", int) = 64
    _Letter_Row07_Col01("_Letter_Row07_Col01", int) = 64
    _Letter_Row07_Col02("_Letter_Row07_Col02", int) = 64
    _Letter_Row07_Col03("_Letter_Row07_Col03", int) = 64
    _Letter_Row07_Col04("_Letter_Row07_Col04", int) = 64
    _Letter_Row07_Col05("_Letter_Row07_Col05", int) = 64
    _Letter_Row07_Col06("_Letter_Row07_Col06", int) = 64
    _Letter_Row07_Col07("_Letter_Row07_Col07", int) = 64
    _Letter_Row07_Col08("_Letter_Row07_Col08", int) = 64
    _Letter_Row07_Col09("_Letter_Row07_Col09", int) = 64
    _Letter_Row07_Col10("_Letter_Row07_Col10", int) = 64
    _Letter_Row07_Col11("_Letter_Row07_Col11", int) = 64
    _Letter_Row07_Col12("_Letter_Row07_Col12", int) = 64
    _Letter_Row07_Col13("_Letter_Row07_Col13", int) = 64
    _Letter_Row07_Col14("_Letter_Row07_Col14", int) = 64
    _Letter_Row07_Col15("_Letter_Row07_Col15", int) = 64
    _Letter_Row07_Col16("_Letter_Row07_Col16", int) = 64
    _Letter_Row07_Col17("_Letter_Row07_Col17", int) = 64
    _Letter_Row07_Col18("_Letter_Row07_Col18", int) = 64
    _Letter_Row07_Col19("_Letter_Row07_Col19", int) = 64
    _Letter_Row07_Col20("_Letter_Row07_Col20", int) = 64
    _Letter_Row07_Col21("_Letter_Row07_Col21", int) = 64
    // This does nothing, it's just used by the 'Do Nothing' animation.
    _Dummy("_Dummy", int) = 0
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

      int _Letter_Row00_Col00;
      int _Letter_Row00_Col01;
      int _Letter_Row00_Col02;
      int _Letter_Row00_Col03;
      int _Letter_Row00_Col04;
      int _Letter_Row00_Col05;
      int _Letter_Row00_Col06;
      int _Letter_Row00_Col07;
      int _Letter_Row00_Col08;
      int _Letter_Row00_Col09;
      int _Letter_Row00_Col10;
      int _Letter_Row00_Col11;
      int _Letter_Row00_Col12;
      int _Letter_Row00_Col13;
      int _Letter_Row00_Col14;
      int _Letter_Row00_Col15;
      int _Letter_Row00_Col16;
      int _Letter_Row00_Col17;
      int _Letter_Row00_Col18;
      int _Letter_Row00_Col19;
      int _Letter_Row00_Col20;
      int _Letter_Row00_Col21;
      int _Letter_Row01_Col00;
      int _Letter_Row01_Col01;
      int _Letter_Row01_Col02;
      int _Letter_Row01_Col03;
      int _Letter_Row01_Col04;
      int _Letter_Row01_Col05;
      int _Letter_Row01_Col06;
      int _Letter_Row01_Col07;
      int _Letter_Row01_Col08;
      int _Letter_Row01_Col09;
      int _Letter_Row01_Col10;
      int _Letter_Row01_Col11;
      int _Letter_Row01_Col12;
      int _Letter_Row01_Col13;
      int _Letter_Row01_Col14;
      int _Letter_Row01_Col15;
      int _Letter_Row01_Col16;
      int _Letter_Row01_Col17;
      int _Letter_Row01_Col18;
      int _Letter_Row01_Col19;
      int _Letter_Row01_Col20;
      int _Letter_Row01_Col21;
      int _Letter_Row02_Col00;
      int _Letter_Row02_Col01;
      int _Letter_Row02_Col02;
      int _Letter_Row02_Col03;
      int _Letter_Row02_Col04;
      int _Letter_Row02_Col05;
      int _Letter_Row02_Col06;
      int _Letter_Row02_Col07;
      int _Letter_Row02_Col08;
      int _Letter_Row02_Col09;
      int _Letter_Row02_Col10;
      int _Letter_Row02_Col11;
      int _Letter_Row02_Col12;
      int _Letter_Row02_Col13;
      int _Letter_Row02_Col14;
      int _Letter_Row02_Col15;
      int _Letter_Row02_Col16;
      int _Letter_Row02_Col17;
      int _Letter_Row02_Col18;
      int _Letter_Row02_Col19;
      int _Letter_Row02_Col20;
      int _Letter_Row02_Col21;
      int _Letter_Row03_Col00;
      int _Letter_Row03_Col01;
      int _Letter_Row03_Col02;
      int _Letter_Row03_Col03;
      int _Letter_Row03_Col04;
      int _Letter_Row03_Col05;
      int _Letter_Row03_Col06;
      int _Letter_Row03_Col07;
      int _Letter_Row03_Col08;
      int _Letter_Row03_Col09;
      int _Letter_Row03_Col10;
      int _Letter_Row03_Col11;
      int _Letter_Row03_Col12;
      int _Letter_Row03_Col13;
      int _Letter_Row03_Col14;
      int _Letter_Row03_Col15;
      int _Letter_Row03_Col16;
      int _Letter_Row03_Col17;
      int _Letter_Row03_Col18;
      int _Letter_Row03_Col19;
      int _Letter_Row03_Col20;
      int _Letter_Row03_Col21;
      int _Letter_Row04_Col00;
      int _Letter_Row04_Col01;
      int _Letter_Row04_Col02;
      int _Letter_Row04_Col03;
      int _Letter_Row04_Col04;
      int _Letter_Row04_Col05;
      int _Letter_Row04_Col06;
      int _Letter_Row04_Col07;
      int _Letter_Row04_Col08;
      int _Letter_Row04_Col09;
      int _Letter_Row04_Col10;
      int _Letter_Row04_Col11;
      int _Letter_Row04_Col12;
      int _Letter_Row04_Col13;
      int _Letter_Row04_Col14;
      int _Letter_Row04_Col15;
      int _Letter_Row04_Col16;
      int _Letter_Row04_Col17;
      int _Letter_Row04_Col18;
      int _Letter_Row04_Col19;
      int _Letter_Row04_Col20;
      int _Letter_Row04_Col21;
      int _Letter_Row05_Col00;
      int _Letter_Row05_Col01;
      int _Letter_Row05_Col02;
      int _Letter_Row05_Col03;
      int _Letter_Row05_Col04;
      int _Letter_Row05_Col05;
      int _Letter_Row05_Col06;
      int _Letter_Row05_Col07;
      int _Letter_Row05_Col08;
      int _Letter_Row05_Col09;
      int _Letter_Row05_Col10;
      int _Letter_Row05_Col11;
      int _Letter_Row05_Col12;
      int _Letter_Row05_Col13;
      int _Letter_Row05_Col14;
      int _Letter_Row05_Col15;
      int _Letter_Row05_Col16;
      int _Letter_Row05_Col17;
      int _Letter_Row05_Col18;
      int _Letter_Row05_Col19;
      int _Letter_Row05_Col20;
      int _Letter_Row05_Col21;
      int _Letter_Row06_Col00;
      int _Letter_Row06_Col01;
      int _Letter_Row06_Col02;
      int _Letter_Row06_Col03;
      int _Letter_Row06_Col04;
      int _Letter_Row06_Col05;
      int _Letter_Row06_Col06;
      int _Letter_Row06_Col07;
      int _Letter_Row06_Col08;
      int _Letter_Row06_Col09;
      int _Letter_Row06_Col10;
      int _Letter_Row06_Col11;
      int _Letter_Row06_Col12;
      int _Letter_Row06_Col13;
      int _Letter_Row06_Col14;
      int _Letter_Row06_Col15;
      int _Letter_Row06_Col16;
      int _Letter_Row06_Col17;
      int _Letter_Row06_Col18;
      int _Letter_Row06_Col19;
      int _Letter_Row06_Col20;
      int _Letter_Row06_Col21;
      int _Letter_Row07_Col00;
      int _Letter_Row07_Col01;
      int _Letter_Row07_Col02;
      int _Letter_Row07_Col03;
      int _Letter_Row07_Col04;
      int _Letter_Row07_Col05;
      int _Letter_Row07_Col06;
      int _Letter_Row07_Col07;
      int _Letter_Row07_Col08;
      int _Letter_Row07_Col09;
      int _Letter_Row07_Col10;
      int _Letter_Row07_Col11;
      int _Letter_Row07_Col12;
      int _Letter_Row07_Col13;
      int _Letter_Row07_Col14;
      int _Letter_Row07_Col15;
      int _Letter_Row07_Col16;
      int _Letter_Row07_Col17;
      int _Letter_Row07_Col18;
      int _Letter_Row07_Col19;
      int _Letter_Row07_Col20;
      int _Letter_Row07_Col21;

      v2f vert (appdata v)
      {
        v2f o;
        o.vertex = UnityObjectToClipPos(v.vertex);
        o.uv = 1.0 - v.uv;
        return o;
      }

      // Write the nth letter in the current cell and return the value of the
      // pixel.
      float2 GetLetter(v2f i, int nth_letter)
      {
        // UV spans from [0,1] to [0,1].
        // 'U' is horizontal; cols.
        // 'V' is vertical; rows.
        //
        // I want to divide the mesh into an m x n grid.
        // I want to know what grid cell I'm in. This is simply u * m, v * n.
        int CHAR_ROWS = 8;
        int CHAR_COLS = 22;

        // OK, I know what cell I'm in. Now I need to know how far across it I
        // am. Produce a float in the range [0, CHAR_COLS).
        float CHAR_FRAC_COL = i.uv.x * CHAR_COLS - floor(i.uv.x * CHAR_COLS);
        float CHAR_FRAC_ROW = i.uv.y * CHAR_ROWS - floor(i.uv.y * CHAR_ROWS);

        // This is the number of rows and columns in the actual texture.
        float LETTER_COLS = 26.6;
        float LETTER_ROWS = 11.4;

        float LETTER_COL = fmod(nth_letter, floor(LETTER_COLS));
        float LETTER_ROW = floor(LETTER_ROWS) - floor(nth_letter / floor(LETTER_COLS));

        float LETTER_UV_ROW = (LETTER_ROW + CHAR_FRAC_ROW - 0.6) / LETTER_ROWS;
        float LETTER_UV_COL = (LETTER_COL + CHAR_FRAC_COL) / LETTER_COLS;

        float2 uv;
        uv.x = LETTER_UV_COL;
        uv.y = LETTER_UV_ROW;

        return uv;
      }

      // Get the value of the parameter for the cell we're in.
      int GetLetterParameter(v2f i)
      {
        float CHAR_ROWS = 8.0;
        float CHAR_COLS = 22.0;
        float CHAR_COL = floor(i.uv.x * CHAR_COLS);
        float CHAR_ROW = floor(i.uv.y * CHAR_ROWS);

        // ok now this is epic
        if (CHAR_ROW == 7) {
          if (CHAR_COL == 0) {
            return _Letter_Row00_Col00;
          } else if (CHAR_COL == 1) {
            return _Letter_Row00_Col01;
          } else if (CHAR_COL == 2) {
            return _Letter_Row00_Col02;
          } else if (CHAR_COL == 3) {
            return _Letter_Row00_Col03;
          } else if (CHAR_COL == 4) {
            return _Letter_Row00_Col04;
          } else if (CHAR_COL == 5) {
            return _Letter_Row00_Col05;
          } else if (CHAR_COL == 6) {
            return _Letter_Row00_Col06;
          } else if (CHAR_COL == 7) {
            return _Letter_Row00_Col07;
          } else if (CHAR_COL == 8) {
            return _Letter_Row00_Col08;
          } else if (CHAR_COL == 9) {
            return _Letter_Row00_Col09;
          } else if (CHAR_COL == 10) {
            return _Letter_Row00_Col10;
          } else if (CHAR_COL == 11) {
            return _Letter_Row00_Col11;
          } else if (CHAR_COL == 12) {
            return _Letter_Row00_Col12;
          } else if (CHAR_COL == 13) {
            return _Letter_Row00_Col13;
          } else if (CHAR_COL == 14) {
            return _Letter_Row00_Col14;
          } else if (CHAR_COL == 15) {
            return _Letter_Row00_Col15;
          } else if (CHAR_COL == 16) {
            return _Letter_Row00_Col16;
          } else if (CHAR_COL == 17) {
            return _Letter_Row00_Col17;
          } else if (CHAR_COL == 18) {
            return _Letter_Row00_Col18;
          } else if (CHAR_COL == 19) {
            return _Letter_Row00_Col19;
          } else if (CHAR_COL == 20) {
            return _Letter_Row00_Col20;
          } else if (CHAR_COL == 21) {
            return _Letter_Row00_Col21;
          }
        } else if (CHAR_ROW == 6) {
          if (CHAR_COL == 0) {
            return _Letter_Row01_Col00;
          } else if (CHAR_COL == 1) {
            return _Letter_Row01_Col01;
          } else if (CHAR_COL == 2) {
            return _Letter_Row01_Col02;
          } else if (CHAR_COL == 3) {
            return _Letter_Row01_Col03;
          } else if (CHAR_COL == 4) {
            return _Letter_Row01_Col04;
          } else if (CHAR_COL == 5) {
            return _Letter_Row01_Col05;
          } else if (CHAR_COL == 6) {
            return _Letter_Row01_Col06;
          } else if (CHAR_COL == 7) {
            return _Letter_Row01_Col07;
          } else if (CHAR_COL == 8) {
            return _Letter_Row01_Col08;
          } else if (CHAR_COL == 9) {
            return _Letter_Row01_Col09;
          } else if (CHAR_COL == 10) {
            return _Letter_Row01_Col10;
          } else if (CHAR_COL == 11) {
            return _Letter_Row01_Col11;
          } else if (CHAR_COL == 12) {
            return _Letter_Row01_Col12;
          } else if (CHAR_COL == 13) {
            return _Letter_Row01_Col13;
          } else if (CHAR_COL == 14) {
            return _Letter_Row01_Col14;
          } else if (CHAR_COL == 15) {
            return _Letter_Row01_Col15;
          } else if (CHAR_COL == 16) {
            return _Letter_Row01_Col16;
          } else if (CHAR_COL == 17) {
            return _Letter_Row01_Col17;
          } else if (CHAR_COL == 18) {
            return _Letter_Row01_Col18;
          } else if (CHAR_COL == 19) {
            return _Letter_Row01_Col19;
          } else if (CHAR_COL == 20) {
            return _Letter_Row01_Col20;
          } else if (CHAR_COL == 21) {
            return _Letter_Row01_Col21;
          }
        } else if (CHAR_ROW == 5) {
          if (CHAR_COL == 0) {
            return _Letter_Row02_Col00;
          } else if (CHAR_COL == 1) {
            return _Letter_Row02_Col01;
          } else if (CHAR_COL == 2) {
            return _Letter_Row02_Col02;
          } else if (CHAR_COL == 3) {
            return _Letter_Row02_Col03;
          } else if (CHAR_COL == 4) {
            return _Letter_Row02_Col04;
          } else if (CHAR_COL == 5) {
            return _Letter_Row02_Col05;
          } else if (CHAR_COL == 6) {
            return _Letter_Row02_Col06;
          } else if (CHAR_COL == 7) {
            return _Letter_Row02_Col07;
          } else if (CHAR_COL == 8) {
            return _Letter_Row02_Col08;
          } else if (CHAR_COL == 9) {
            return _Letter_Row02_Col09;
          } else if (CHAR_COL == 10) {
            return _Letter_Row02_Col10;
          } else if (CHAR_COL == 11) {
            return _Letter_Row02_Col11;
          } else if (CHAR_COL == 12) {
            return _Letter_Row02_Col12;
          } else if (CHAR_COL == 13) {
            return _Letter_Row02_Col13;
          } else if (CHAR_COL == 14) {
            return _Letter_Row02_Col14;
          } else if (CHAR_COL == 15) {
            return _Letter_Row02_Col15;
          } else if (CHAR_COL == 16) {
            return _Letter_Row02_Col16;
          } else if (CHAR_COL == 17) {
            return _Letter_Row02_Col17;
          } else if (CHAR_COL == 18) {
            return _Letter_Row02_Col18;
          } else if (CHAR_COL == 19) {
            return _Letter_Row02_Col19;
          } else if (CHAR_COL == 20) {
            return _Letter_Row02_Col20;
          } else if (CHAR_COL == 21) {
            return _Letter_Row02_Col21;
          }
        } else if (CHAR_ROW == 4) {
          if (CHAR_COL == 0) {
            return _Letter_Row03_Col00;
          } else if (CHAR_COL == 1) {
            return _Letter_Row03_Col01;
          } else if (CHAR_COL == 2) {
            return _Letter_Row03_Col02;
          } else if (CHAR_COL == 3) {
            return _Letter_Row03_Col03;
          } else if (CHAR_COL == 4) {
            return _Letter_Row03_Col04;
          } else if (CHAR_COL == 5) {
            return _Letter_Row03_Col05;
          } else if (CHAR_COL == 6) {
            return _Letter_Row03_Col06;
          } else if (CHAR_COL == 7) {
            return _Letter_Row03_Col07;
          } else if (CHAR_COL == 8) {
            return _Letter_Row03_Col08;
          } else if (CHAR_COL == 9) {
            return _Letter_Row03_Col09;
          } else if (CHAR_COL == 10) {
            return _Letter_Row03_Col10;
          } else if (CHAR_COL == 11) {
            return _Letter_Row03_Col11;
          } else if (CHAR_COL == 12) {
            return _Letter_Row03_Col12;
          } else if (CHAR_COL == 13) {
            return _Letter_Row03_Col13;
          } else if (CHAR_COL == 14) {
            return _Letter_Row03_Col14;
          } else if (CHAR_COL == 15) {
            return _Letter_Row03_Col15;
          } else if (CHAR_COL == 16) {
            return _Letter_Row03_Col16;
          } else if (CHAR_COL == 17) {
            return _Letter_Row03_Col17;
          } else if (CHAR_COL == 18) {
            return _Letter_Row03_Col18;
          } else if (CHAR_COL == 19) {
            return _Letter_Row03_Col19;
          } else if (CHAR_COL == 20) {
            return _Letter_Row03_Col20;
          } else if (CHAR_COL == 21) {
            return _Letter_Row03_Col21;
          }
        } else if (CHAR_ROW == 3) {
          if (CHAR_COL == 0) {
            return _Letter_Row04_Col00;
          } else if (CHAR_COL == 1) {
            return _Letter_Row04_Col01;
          } else if (CHAR_COL == 2) {
            return _Letter_Row04_Col02;
          } else if (CHAR_COL == 3) {
            return _Letter_Row04_Col03;
          } else if (CHAR_COL == 4) {
            return _Letter_Row04_Col04;
          } else if (CHAR_COL == 5) {
            return _Letter_Row04_Col05;
          } else if (CHAR_COL == 6) {
            return _Letter_Row04_Col06;
          } else if (CHAR_COL == 7) {
            return _Letter_Row04_Col07;
          } else if (CHAR_COL == 8) {
            return _Letter_Row04_Col08;
          } else if (CHAR_COL == 9) {
            return _Letter_Row04_Col09;
          } else if (CHAR_COL == 10) {
            return _Letter_Row04_Col10;
          } else if (CHAR_COL == 11) {
            return _Letter_Row04_Col11;
          } else if (CHAR_COL == 12) {
            return _Letter_Row04_Col12;
          } else if (CHAR_COL == 13) {
            return _Letter_Row04_Col13;
          } else if (CHAR_COL == 14) {
            return _Letter_Row04_Col14;
          } else if (CHAR_COL == 15) {
            return _Letter_Row04_Col15;
          } else if (CHAR_COL == 16) {
            return _Letter_Row04_Col16;
          } else if (CHAR_COL == 17) {
            return _Letter_Row04_Col17;
          } else if (CHAR_COL == 18) {
            return _Letter_Row04_Col18;
          } else if (CHAR_COL == 19) {
            return _Letter_Row04_Col19;
          } else if (CHAR_COL == 20) {
            return _Letter_Row04_Col20;
          } else if (CHAR_COL == 21) {
            return _Letter_Row04_Col21;
          }
        } else if (CHAR_ROW == 2) {
          if (CHAR_COL == 0) {
            return _Letter_Row05_Col00;
          } else if (CHAR_COL == 1) {
            return _Letter_Row05_Col01;
          } else if (CHAR_COL == 2) {
            return _Letter_Row05_Col02;
          } else if (CHAR_COL == 3) {
            return _Letter_Row05_Col03;
          } else if (CHAR_COL == 4) {
            return _Letter_Row05_Col04;
          } else if (CHAR_COL == 5) {
            return _Letter_Row05_Col05;
          } else if (CHAR_COL == 6) {
            return _Letter_Row05_Col06;
          } else if (CHAR_COL == 7) {
            return _Letter_Row05_Col07;
          } else if (CHAR_COL == 8) {
            return _Letter_Row05_Col08;
          } else if (CHAR_COL == 9) {
            return _Letter_Row05_Col09;
          } else if (CHAR_COL == 10) {
            return _Letter_Row05_Col10;
          } else if (CHAR_COL == 11) {
            return _Letter_Row05_Col11;
          } else if (CHAR_COL == 12) {
            return _Letter_Row05_Col12;
          } else if (CHAR_COL == 13) {
            return _Letter_Row05_Col13;
          } else if (CHAR_COL == 14) {
            return _Letter_Row05_Col14;
          } else if (CHAR_COL == 15) {
            return _Letter_Row05_Col15;
          } else if (CHAR_COL == 16) {
            return _Letter_Row05_Col16;
          } else if (CHAR_COL == 17) {
            return _Letter_Row05_Col17;
          } else if (CHAR_COL == 18) {
            return _Letter_Row05_Col18;
          } else if (CHAR_COL == 19) {
            return _Letter_Row05_Col19;
          } else if (CHAR_COL == 20) {
            return _Letter_Row05_Col20;
          } else if (CHAR_COL == 21) {
            return _Letter_Row05_Col21;
          }
        } else if (CHAR_ROW == 1) {
          if (CHAR_COL == 0) {
            return _Letter_Row06_Col00;
          } else if (CHAR_COL == 1) {
            return _Letter_Row06_Col01;
          } else if (CHAR_COL == 2) {
            return _Letter_Row06_Col02;
          } else if (CHAR_COL == 3) {
            return _Letter_Row06_Col03;
          } else if (CHAR_COL == 4) {
            return _Letter_Row06_Col04;
          } else if (CHAR_COL == 5) {
            return _Letter_Row06_Col05;
          } else if (CHAR_COL == 6) {
            return _Letter_Row06_Col06;
          } else if (CHAR_COL == 7) {
            return _Letter_Row06_Col07;
          } else if (CHAR_COL == 8) {
            return _Letter_Row06_Col08;
          } else if (CHAR_COL == 9) {
            return _Letter_Row06_Col09;
          } else if (CHAR_COL == 10) {
            return _Letter_Row06_Col10;
          } else if (CHAR_COL == 11) {
            return _Letter_Row06_Col11;
          } else if (CHAR_COL == 12) {
            return _Letter_Row06_Col12;
          } else if (CHAR_COL == 13) {
            return _Letter_Row06_Col13;
          } else if (CHAR_COL == 14) {
            return _Letter_Row06_Col14;
          } else if (CHAR_COL == 15) {
            return _Letter_Row06_Col15;
          } else if (CHAR_COL == 16) {
            return _Letter_Row06_Col16;
          } else if (CHAR_COL == 17) {
            return _Letter_Row06_Col17;
          } else if (CHAR_COL == 18) {
            return _Letter_Row06_Col18;
          } else if (CHAR_COL == 19) {
            return _Letter_Row06_Col19;
          } else if (CHAR_COL == 20) {
            return _Letter_Row06_Col20;
          } else if (CHAR_COL == 21) {
            return _Letter_Row06_Col21;
          }
        } else if (CHAR_ROW == 0) {
          if (CHAR_COL == 0) {
            return _Letter_Row07_Col00;
          } else if (CHAR_COL == 1) {
            return _Letter_Row07_Col01;
          } else if (CHAR_COL == 2) {
            return _Letter_Row07_Col02;
          } else if (CHAR_COL == 3) {
            return _Letter_Row07_Col03;
          } else if (CHAR_COL == 4) {
            return _Letter_Row07_Col04;
          } else if (CHAR_COL == 5) {
            return _Letter_Row07_Col05;
          } else if (CHAR_COL == 6) {
            return _Letter_Row07_Col06;
          } else if (CHAR_COL == 7) {
            return _Letter_Row07_Col07;
          } else if (CHAR_COL == 8) {
            return _Letter_Row07_Col08;
          } else if (CHAR_COL == 9) {
            return _Letter_Row07_Col09;
          } else if (CHAR_COL == 10) {
            return _Letter_Row07_Col10;
          } else if (CHAR_COL == 11) {
            return _Letter_Row07_Col11;
          } else if (CHAR_COL == 12) {
            return _Letter_Row07_Col12;
          } else if (CHAR_COL == 13) {
            return _Letter_Row07_Col13;
          } else if (CHAR_COL == 14) {
            return _Letter_Row07_Col14;
          } else if (CHAR_COL == 15) {
            return _Letter_Row07_Col15;
          } else if (CHAR_COL == 16) {
            return _Letter_Row07_Col16;
          } else if (CHAR_COL == 17) {
            return _Letter_Row07_Col17;
          } else if (CHAR_COL == 18) {
            return _Letter_Row07_Col18;
          } else if (CHAR_COL == 19) {
            return _Letter_Row07_Col19;
          } else if (CHAR_COL == 20) {
            return _Letter_Row07_Col20;
          } else if (CHAR_COL == 21) {
            return _Letter_Row07_Col21;
          }
        }

        return 0;
      }

      fixed4 frag (v2f i) : SV_Target
      {
        int letter = GetLetterParameter(i);
        float2 uv = GetLetter(i, letter);
        fixed4 ret = _MainTex.Sample(sampler_linear_repeat, uv);
        return ret;
      }
      ENDCG
    }
  }
}
