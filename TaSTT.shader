Shader "Unlit/my_shader"
{
  Properties
  {
    _MainTex ("Texture", 2D) = "white" {}
    // software "engineering" LULW
    _Letter_Row00_Col00("_Letter_Row00_Col00", float) = 0
    _Letter_Row00_Col01("_Letter_Row00_Col01", float) = 0
    _Letter_Row00_Col02("_Letter_Row00_Col02", float) = 0
    _Letter_Row00_Col03("_Letter_Row00_Col03", float) = 0
    _Letter_Row00_Col04("_Letter_Row00_Col04", float) = 0
    _Letter_Row00_Col05("_Letter_Row00_Col05", float) = 0
    _Letter_Row00_Col06("_Letter_Row00_Col06", float) = 0
    _Letter_Row00_Col07("_Letter_Row00_Col07", float) = 0
    _Letter_Row00_Col08("_Letter_Row00_Col08", float) = 0
    _Letter_Row00_Col09("_Letter_Row00_Col09", float) = 0
    _Letter_Row00_Col10("_Letter_Row00_Col10", float) = 0
    _Letter_Row00_Col11("_Letter_Row00_Col11", float) = 0
    _Letter_Row00_Col12("_Letter_Row00_Col12", float) = 0
    _Letter_Row00_Col13("_Letter_Row00_Col13", float) = 0
    _Letter_Row00_Col14("_Letter_Row00_Col14", float) = 0
    _Letter_Row00_Col15("_Letter_Row00_Col15", float) = 0
    _Letter_Row01_Col00("_Letter_Row01_Col00", float) = 0
    _Letter_Row01_Col01("_Letter_Row01_Col01", float) = 0
    _Letter_Row01_Col02("_Letter_Row01_Col02", float) = 0
    _Letter_Row01_Col03("_Letter_Row01_Col03", float) = 0
    _Letter_Row01_Col04("_Letter_Row01_Col04", float) = 0
    _Letter_Row01_Col05("_Letter_Row01_Col05", float) = 0
    _Letter_Row01_Col06("_Letter_Row01_Col06", float) = 0
    _Letter_Row01_Col07("_Letter_Row01_Col07", float) = 0
    _Letter_Row01_Col08("_Letter_Row01_Col08", float) = 0
    _Letter_Row01_Col09("_Letter_Row01_Col09", float) = 0
    _Letter_Row01_Col10("_Letter_Row01_Col10", float) = 0
    _Letter_Row01_Col11("_Letter_Row01_Col11", float) = 0
    _Letter_Row01_Col12("_Letter_Row01_Col12", float) = 0
    _Letter_Row01_Col13("_Letter_Row01_Col13", float) = 0
    _Letter_Row01_Col14("_Letter_Row01_Col14", float) = 0
    _Letter_Row01_Col15("_Letter_Row01_Col15", float) = 0
    _Letter_Row02_Col00("_Letter_Row02_Col00", float) = 0
    _Letter_Row02_Col01("_Letter_Row02_Col01", float) = 0
    _Letter_Row02_Col02("_Letter_Row02_Col02", float) = 0
    _Letter_Row02_Col03("_Letter_Row02_Col03", float) = 0
    _Letter_Row02_Col04("_Letter_Row02_Col04", float) = 0
    _Letter_Row02_Col05("_Letter_Row02_Col05", float) = 0
    _Letter_Row02_Col06("_Letter_Row02_Col06", float) = 0
    _Letter_Row02_Col07("_Letter_Row02_Col07", float) = 0
    _Letter_Row02_Col08("_Letter_Row02_Col08", float) = 0
    _Letter_Row02_Col09("_Letter_Row02_Col09", float) = 0
    _Letter_Row02_Col10("_Letter_Row02_Col10", float) = 0
    _Letter_Row02_Col11("_Letter_Row02_Col11", float) = 0
    _Letter_Row02_Col12("_Letter_Row02_Col12", float) = 0
    _Letter_Row02_Col13("_Letter_Row02_Col13", float) = 0
    _Letter_Row02_Col14("_Letter_Row02_Col14", float) = 0
    _Letter_Row02_Col15("_Letter_Row02_Col15", float) = 0
    _Letter_Row03_Col00("_Letter_Row03_Col00", float) = 0
    _Letter_Row03_Col01("_Letter_Row03_Col01", float) = 0
    _Letter_Row03_Col02("_Letter_Row03_Col02", float) = 0
    _Letter_Row03_Col03("_Letter_Row03_Col03", float) = 0
    _Letter_Row03_Col04("_Letter_Row03_Col04", float) = 0
    _Letter_Row03_Col05("_Letter_Row03_Col05", float) = 0
    _Letter_Row03_Col06("_Letter_Row03_Col06", float) = 0
    _Letter_Row03_Col07("_Letter_Row03_Col07", float) = 0
    _Letter_Row03_Col08("_Letter_Row03_Col08", float) = 0
    _Letter_Row03_Col09("_Letter_Row03_Col09", float) = 0
    _Letter_Row03_Col10("_Letter_Row03_Col10", float) = 0
    _Letter_Row03_Col11("_Letter_Row03_Col11", float) = 0
    _Letter_Row03_Col12("_Letter_Row03_Col12", float) = 0
    _Letter_Row03_Col13("_Letter_Row03_Col13", float) = 0
    _Letter_Row03_Col14("_Letter_Row03_Col14", float) = 0
    _Letter_Row03_Col15("_Letter_Row03_Col15", float) = 0
    _Letter_Row04_Col00("_Letter_Row04_Col00", float) = 0
    _Letter_Row04_Col01("_Letter_Row04_Col01", float) = 0
    _Letter_Row04_Col02("_Letter_Row04_Col02", float) = 0
    _Letter_Row04_Col03("_Letter_Row04_Col03", float) = 0
    _Letter_Row04_Col04("_Letter_Row04_Col04", float) = 0
    _Letter_Row04_Col05("_Letter_Row04_Col05", float) = 0
    _Letter_Row04_Col06("_Letter_Row04_Col06", float) = 0
    _Letter_Row04_Col07("_Letter_Row04_Col07", float) = 0
    _Letter_Row04_Col08("_Letter_Row04_Col08", float) = 0
    _Letter_Row04_Col09("_Letter_Row04_Col09", float) = 0
    _Letter_Row04_Col10("_Letter_Row04_Col10", float) = 0
    _Letter_Row04_Col11("_Letter_Row04_Col11", float) = 0
    _Letter_Row04_Col12("_Letter_Row04_Col12", float) = 0
    _Letter_Row04_Col13("_Letter_Row04_Col13", float) = 0
    _Letter_Row04_Col14("_Letter_Row04_Col14", float) = 0
    _Letter_Row04_Col15("_Letter_Row04_Col15", float) = 0
    _Letter_Row05_Col00("_Letter_Row05_Col00", float) = 0
    _Letter_Row05_Col01("_Letter_Row05_Col01", float) = 0
    _Letter_Row05_Col02("_Letter_Row05_Col02", float) = 0
    _Letter_Row05_Col03("_Letter_Row05_Col03", float) = 0
    _Letter_Row05_Col04("_Letter_Row05_Col04", float) = 0
    _Letter_Row05_Col05("_Letter_Row05_Col05", float) = 0
    _Letter_Row05_Col06("_Letter_Row05_Col06", float) = 0
    _Letter_Row05_Col07("_Letter_Row05_Col07", float) = 0
    _Letter_Row05_Col08("_Letter_Row05_Col08", float) = 0
    _Letter_Row05_Col09("_Letter_Row05_Col09", float) = 0
    _Letter_Row05_Col10("_Letter_Row05_Col10", float) = 0
    _Letter_Row05_Col11("_Letter_Row05_Col11", float) = 0
    _Letter_Row05_Col12("_Letter_Row05_Col12", float) = 0
    _Letter_Row05_Col13("_Letter_Row05_Col13", float) = 0
    _Letter_Row05_Col14("_Letter_Row05_Col14", float) = 0
    _Letter_Row05_Col15("_Letter_Row05_Col15", float) = 0
  }
  SubShader
  {
    Tags { "RenderType"="Opaque" }
    LOD 100

    Pass
    {
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

      sampler2D _MainTex;
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
      float _Letter_Row04_Col00;
      float _Letter_Row04_Col01;
      float _Letter_Row04_Col02;
      float _Letter_Row04_Col03;
      float _Letter_Row04_Col04;
      float _Letter_Row04_Col05;
      float _Letter_Row04_Col06;
      float _Letter_Row04_Col07;
      float _Letter_Row04_Col08;
      float _Letter_Row04_Col09;
      float _Letter_Row04_Col10;
      float _Letter_Row04_Col11;
      float _Letter_Row04_Col12;
      float _Letter_Row04_Col13;
      float _Letter_Row04_Col14;
      float _Letter_Row04_Col15;
      float _Letter_Row05_Col00;
      float _Letter_Row05_Col01;
      float _Letter_Row05_Col02;
      float _Letter_Row05_Col03;
      float _Letter_Row05_Col04;
      float _Letter_Row05_Col05;
      float _Letter_Row05_Col06;
      float _Letter_Row05_Col07;
      float _Letter_Row05_Col08;
      float _Letter_Row05_Col09;
      float _Letter_Row05_Col10;
      float _Letter_Row05_Col11;
      float _Letter_Row05_Col12;
      float _Letter_Row05_Col13;
      float _Letter_Row05_Col14;
      float _Letter_Row05_Col15;

      v2f vert (appdata v)
      {
        v2f o;
        o.vertex = UnityObjectToClipPos(v.vertex);
        o.uv = 1.0 - v.uv;
        return o;
      }

      // Write the nth letter in the current cell and return the value of the
      // pixel.
      float2 GetLetter(v2f i, float nth_letter)
      {
        // UV spans from [0,1] to [0,1].
        // 'U' is horizontal; cols.
        // 'V' is vertical; rows.
        //
        // I want to divide the mesh into an m x n grid.
        // Thus given UV, I need to know a few things:
        // 1. What grid cell I'm in. This is simply u * m, v * n.
        float CHAR_ROWS = 6.0;
        float CHAR_COLS = 16.0;
        float CHAR_COL = floor(i.uv.x * CHAR_COLS);
        float CHAR_ROW = floor(i.uv.y * CHAR_ROWS);

        // OK, I know what cell I'm in. Now I need to know how far across it I
        // am.
        float CHAR_FRAC_COL = fmod(i.uv.x, 1.0 / CHAR_COLS) / (1.0 / CHAR_COLS);
        float CHAR_FRAC_ROW = fmod(i.uv.y, 1.0 / CHAR_ROWS) / (1.0 / CHAR_ROWS);

        // TODO(yum_food) figure out what's causing the outlines around letters
        // and remove this. This simply reduces the size of the outlines.
        float kappa = 0.01;
        if (CHAR_FRAC_COL < kappa || CHAR_FRAC_ROW < kappa ||
            CHAR_FRAC_COL > 1 - kappa || CHAR_FRAC_ROW > 1 - kappa) {
          return float2(0, 0);
        }

        float LETTER_COLS = 26.6;
        float LETTER_ROWS = 11.4;
        float LETTER_COL = fmod(nth_letter, floor(LETTER_COLS));
        float LETTER_ROW = floor(LETTER_ROWS) - floor(nth_letter / floor(LETTER_COLS));
        float LETTER_UV_WD = (1.0 / LETTER_COLS);
        float LETTER_UV_COL = (LETTER_UV_WD * LETTER_COL);
        float LETTER_UV_HT = (1.0 / LETTER_ROWS);
        float LETTER_UV_ROW = (LETTER_UV_HT * LETTER_ROW);

        LETTER_UV_ROW += LETTER_UV_HT * CHAR_FRAC_ROW - LETTER_UV_HT * 0.6;
        LETTER_UV_COL += LETTER_UV_WD * CHAR_FRAC_COL;

        float2 uv;
        uv.x = LETTER_UV_COL;
        uv.y = LETTER_UV_ROW;

        return uv;
      }

      // Get the value of the parameter for the cell we're in.
      float GetLetterParameter(v2f i)
      {
        float CHAR_ROWS = 6.0;
        float CHAR_COLS = 16.0;
        float CHAR_COL = floor(i.uv.x * CHAR_COLS);
        float CHAR_ROW = floor(i.uv.y * CHAR_ROWS);

        // ok now this is epic
        if (CHAR_ROW == 5) {
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
          }
        } else if (CHAR_ROW == 4) {
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
          }
        } else if (CHAR_ROW == 3) {
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
          }
        } else if (CHAR_ROW == 2) {
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
          }
        } else if (CHAR_ROW == 1) {
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
          }
        } else if (CHAR_ROW == 0) {
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
          }
        }

        return float2(0, 0);
      }

      fixed4 frag (v2f i) : SV_Target
      {
        float letter = GetLetterParameter(i);
        float2 uv = GetLetter(i, letter);
        fixed4 ret = tex2D(_MainTex, uv);
        if (uv.x == 0 || uv.y == 0 || uv.x == 1 || uv.y == 1) {
          ret.xyz = 0;
          ret.w = 0;
        }
        return ret;
      }
      ENDCG
    }
  }
}
