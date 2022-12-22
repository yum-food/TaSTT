Shader "Unlit/TaSTT"
{
  Properties
  {
    _Font_0x0000_0x1FFF ("Font 0 (unicode 0x0000 - 0x1FFFF)", 2D) = "white" {}
    _Font_0x2000_0x3FFF ("Font 1 (unicode 0x2000 - 0x3FFFF)", 2D) = "white" {}
    _Font_0x4000_0x5FFF ("Font 2 (unicode 0x4000 - 0x5FFFF)", 2D) = "white" {}
    _Font_0x6000_0x7FFF ("Font 3 (unicode 0x6000 - 0x7FFFF)", 2D) = "white" {}
    _Font_0x8000_0x9FFF ("Font 4 (unicode 0x8000 - 0x9FFFF)", 2D) = "white" {}
    _Font_0xA000_0xBFFF ("Font 5 (unicode 0xA000 - 0xBFFFF)", 2D) = "white" {}
    _Font_0xC000_0xDFFF ("Font 6 (unicode 0xC000 - 0xDFFFF)", 2D) = "white" {}
    _Img_0xE000_0xE03F  ("Images 0", 2D) = "white" {}

    [MaterialToggle] Render_Margin("Render margin", float) = 1
    [MaterialToggle] Render_Visual_Indicator("Render visual speech indicator", float) = 1
    Margin_Scale("Margin scale", float) = 0.03

    TaSTT_Backplate("TaSTT_Backplate", 2D) = "black" {}

    TaSTT_Indicator_0("TaSTT_Indicator_0", float) = 0
    TaSTT_Indicator_1("TaSTT_Indicator_1", float) = 0

    // software "engineering" LULW
    _Letter_Row00_Col00_Byte0("_Letter_Row00_Col00_Byte0", float) = 0
    _Letter_Row00_Col01_Byte0("_Letter_Row00_Col01_Byte0", float) = 0
    _Letter_Row00_Col02_Byte0("_Letter_Row00_Col02_Byte0", float) = 0
    _Letter_Row00_Col03_Byte0("_Letter_Row00_Col03_Byte0", float) = 0
    _Letter_Row00_Col04_Byte0("_Letter_Row00_Col04_Byte0", float) = 0
    _Letter_Row00_Col05_Byte0("_Letter_Row00_Col05_Byte0", float) = 0
    _Letter_Row00_Col06_Byte0("_Letter_Row00_Col06_Byte0", float) = 0
    _Letter_Row00_Col07_Byte0("_Letter_Row00_Col07_Byte0", float) = 0
    _Letter_Row00_Col08_Byte0("_Letter_Row00_Col08_Byte0", float) = 0
    _Letter_Row00_Col09_Byte0("_Letter_Row00_Col09_Byte0", float) = 0
    _Letter_Row00_Col10_Byte0("_Letter_Row00_Col10_Byte0", float) = 0
    _Letter_Row00_Col11_Byte0("_Letter_Row00_Col11_Byte0", float) = 0
    _Letter_Row00_Col12_Byte0("_Letter_Row00_Col12_Byte0", float) = 0
    _Letter_Row00_Col13_Byte0("_Letter_Row00_Col13_Byte0", float) = 0
    _Letter_Row00_Col14_Byte0("_Letter_Row00_Col14_Byte0", float) = 0
    _Letter_Row00_Col15_Byte0("_Letter_Row00_Col15_Byte0", float) = 0
    _Letter_Row00_Col16_Byte0("_Letter_Row00_Col16_Byte0", float) = 0
    _Letter_Row00_Col17_Byte0("_Letter_Row00_Col17_Byte0", float) = 0
    _Letter_Row00_Col18_Byte0("_Letter_Row00_Col18_Byte0", float) = 0
    _Letter_Row00_Col19_Byte0("_Letter_Row00_Col19_Byte0", float) = 0
    _Letter_Row00_Col20_Byte0("_Letter_Row00_Col20_Byte0", float) = 0
    _Letter_Row00_Col21_Byte0("_Letter_Row00_Col21_Byte0", float) = 0
    _Letter_Row00_Col22_Byte0("_Letter_Row00_Col22_Byte0", float) = 0
    _Letter_Row00_Col23_Byte0("_Letter_Row00_Col23_Byte0", float) = 0
    _Letter_Row00_Col24_Byte0("_Letter_Row00_Col24_Byte0", float) = 0
    _Letter_Row00_Col25_Byte0("_Letter_Row00_Col25_Byte0", float) = 0
    _Letter_Row00_Col26_Byte0("_Letter_Row00_Col26_Byte0", float) = 0
    _Letter_Row00_Col27_Byte0("_Letter_Row00_Col27_Byte0", float) = 0
    _Letter_Row00_Col28_Byte0("_Letter_Row00_Col28_Byte0", float) = 0
    _Letter_Row00_Col29_Byte0("_Letter_Row00_Col29_Byte0", float) = 0
    _Letter_Row00_Col30_Byte0("_Letter_Row00_Col30_Byte0", float) = 0
    _Letter_Row00_Col31_Byte0("_Letter_Row00_Col31_Byte0", float) = 0
    _Letter_Row00_Col32_Byte0("_Letter_Row00_Col32_Byte0", float) = 0
    _Letter_Row00_Col33_Byte0("_Letter_Row00_Col33_Byte0", float) = 0
    _Letter_Row00_Col34_Byte0("_Letter_Row00_Col34_Byte0", float) = 0
    _Letter_Row00_Col35_Byte0("_Letter_Row00_Col35_Byte0", float) = 0
    _Letter_Row00_Col36_Byte0("_Letter_Row00_Col36_Byte0", float) = 0
    _Letter_Row00_Col37_Byte0("_Letter_Row00_Col37_Byte0", float) = 0
    _Letter_Row00_Col38_Byte0("_Letter_Row00_Col38_Byte0", float) = 0
    _Letter_Row00_Col39_Byte0("_Letter_Row00_Col39_Byte0", float) = 0
    _Letter_Row00_Col40_Byte0("_Letter_Row00_Col40_Byte0", float) = 0
    _Letter_Row00_Col41_Byte0("_Letter_Row00_Col41_Byte0", float) = 0
    _Letter_Row00_Col42_Byte0("_Letter_Row00_Col42_Byte0", float) = 0
    _Letter_Row00_Col43_Byte0("_Letter_Row00_Col43_Byte0", float) = 0
    _Letter_Row00_Col44_Byte0("_Letter_Row00_Col44_Byte0", float) = 0
    _Letter_Row00_Col45_Byte0("_Letter_Row00_Col45_Byte0", float) = 0
    _Letter_Row00_Col46_Byte0("_Letter_Row00_Col46_Byte0", float) = 0
    _Letter_Row00_Col47_Byte0("_Letter_Row00_Col47_Byte0", float) = 0
    _Letter_Row01_Col00_Byte0("_Letter_Row01_Col00_Byte0", float) = 0
    _Letter_Row01_Col01_Byte0("_Letter_Row01_Col01_Byte0", float) = 0
    _Letter_Row01_Col02_Byte0("_Letter_Row01_Col02_Byte0", float) = 0
    _Letter_Row01_Col03_Byte0("_Letter_Row01_Col03_Byte0", float) = 0
    _Letter_Row01_Col04_Byte0("_Letter_Row01_Col04_Byte0", float) = 0
    _Letter_Row01_Col05_Byte0("_Letter_Row01_Col05_Byte0", float) = 0
    _Letter_Row01_Col06_Byte0("_Letter_Row01_Col06_Byte0", float) = 0
    _Letter_Row01_Col07_Byte0("_Letter_Row01_Col07_Byte0", float) = 0
    _Letter_Row01_Col08_Byte0("_Letter_Row01_Col08_Byte0", float) = 0
    _Letter_Row01_Col09_Byte0("_Letter_Row01_Col09_Byte0", float) = 0
    _Letter_Row01_Col10_Byte0("_Letter_Row01_Col10_Byte0", float) = 0
    _Letter_Row01_Col11_Byte0("_Letter_Row01_Col11_Byte0", float) = 0
    _Letter_Row01_Col12_Byte0("_Letter_Row01_Col12_Byte0", float) = 0
    _Letter_Row01_Col13_Byte0("_Letter_Row01_Col13_Byte0", float) = 0
    _Letter_Row01_Col14_Byte0("_Letter_Row01_Col14_Byte0", float) = 0
    _Letter_Row01_Col15_Byte0("_Letter_Row01_Col15_Byte0", float) = 0
    _Letter_Row01_Col16_Byte0("_Letter_Row01_Col16_Byte0", float) = 0
    _Letter_Row01_Col17_Byte0("_Letter_Row01_Col17_Byte0", float) = 0
    _Letter_Row01_Col18_Byte0("_Letter_Row01_Col18_Byte0", float) = 0
    _Letter_Row01_Col19_Byte0("_Letter_Row01_Col19_Byte0", float) = 0
    _Letter_Row01_Col20_Byte0("_Letter_Row01_Col20_Byte0", float) = 0
    _Letter_Row01_Col21_Byte0("_Letter_Row01_Col21_Byte0", float) = 0
    _Letter_Row01_Col22_Byte0("_Letter_Row01_Col22_Byte0", float) = 0
    _Letter_Row01_Col23_Byte0("_Letter_Row01_Col23_Byte0", float) = 0
    _Letter_Row01_Col24_Byte0("_Letter_Row01_Col24_Byte0", float) = 0
    _Letter_Row01_Col25_Byte0("_Letter_Row01_Col25_Byte0", float) = 0
    _Letter_Row01_Col26_Byte0("_Letter_Row01_Col26_Byte0", float) = 0
    _Letter_Row01_Col27_Byte0("_Letter_Row01_Col27_Byte0", float) = 0
    _Letter_Row01_Col28_Byte0("_Letter_Row01_Col28_Byte0", float) = 0
    _Letter_Row01_Col29_Byte0("_Letter_Row01_Col29_Byte0", float) = 0
    _Letter_Row01_Col30_Byte0("_Letter_Row01_Col30_Byte0", float) = 0
    _Letter_Row01_Col31_Byte0("_Letter_Row01_Col31_Byte0", float) = 0
    _Letter_Row01_Col32_Byte0("_Letter_Row01_Col32_Byte0", float) = 0
    _Letter_Row01_Col33_Byte0("_Letter_Row01_Col33_Byte0", float) = 0
    _Letter_Row01_Col34_Byte0("_Letter_Row01_Col34_Byte0", float) = 0
    _Letter_Row01_Col35_Byte0("_Letter_Row01_Col35_Byte0", float) = 0
    _Letter_Row01_Col36_Byte0("_Letter_Row01_Col36_Byte0", float) = 0
    _Letter_Row01_Col37_Byte0("_Letter_Row01_Col37_Byte0", float) = 0
    _Letter_Row01_Col38_Byte0("_Letter_Row01_Col38_Byte0", float) = 0
    _Letter_Row01_Col39_Byte0("_Letter_Row01_Col39_Byte0", float) = 0
    _Letter_Row01_Col40_Byte0("_Letter_Row01_Col40_Byte0", float) = 0
    _Letter_Row01_Col41_Byte0("_Letter_Row01_Col41_Byte0", float) = 0
    _Letter_Row01_Col42_Byte0("_Letter_Row01_Col42_Byte0", float) = 0
    _Letter_Row01_Col43_Byte0("_Letter_Row01_Col43_Byte0", float) = 0
    _Letter_Row01_Col44_Byte0("_Letter_Row01_Col44_Byte0", float) = 0
    _Letter_Row01_Col45_Byte0("_Letter_Row01_Col45_Byte0", float) = 0
    _Letter_Row01_Col46_Byte0("_Letter_Row01_Col46_Byte0", float) = 0
    _Letter_Row01_Col47_Byte0("_Letter_Row01_Col47_Byte0", float) = 0
    _Letter_Row02_Col00_Byte0("_Letter_Row02_Col00_Byte0", float) = 0
    _Letter_Row02_Col01_Byte0("_Letter_Row02_Col01_Byte0", float) = 0
    _Letter_Row02_Col02_Byte0("_Letter_Row02_Col02_Byte0", float) = 0
    _Letter_Row02_Col03_Byte0("_Letter_Row02_Col03_Byte0", float) = 0
    _Letter_Row02_Col04_Byte0("_Letter_Row02_Col04_Byte0", float) = 0
    _Letter_Row02_Col05_Byte0("_Letter_Row02_Col05_Byte0", float) = 0
    _Letter_Row02_Col06_Byte0("_Letter_Row02_Col06_Byte0", float) = 0
    _Letter_Row02_Col07_Byte0("_Letter_Row02_Col07_Byte0", float) = 0
    _Letter_Row02_Col08_Byte0("_Letter_Row02_Col08_Byte0", float) = 0
    _Letter_Row02_Col09_Byte0("_Letter_Row02_Col09_Byte0", float) = 0
    _Letter_Row02_Col10_Byte0("_Letter_Row02_Col10_Byte0", float) = 0
    _Letter_Row02_Col11_Byte0("_Letter_Row02_Col11_Byte0", float) = 0
    _Letter_Row02_Col12_Byte0("_Letter_Row02_Col12_Byte0", float) = 0
    _Letter_Row02_Col13_Byte0("_Letter_Row02_Col13_Byte0", float) = 0
    _Letter_Row02_Col14_Byte0("_Letter_Row02_Col14_Byte0", float) = 0
    _Letter_Row02_Col15_Byte0("_Letter_Row02_Col15_Byte0", float) = 0
    _Letter_Row02_Col16_Byte0("_Letter_Row02_Col16_Byte0", float) = 0
    _Letter_Row02_Col17_Byte0("_Letter_Row02_Col17_Byte0", float) = 0
    _Letter_Row02_Col18_Byte0("_Letter_Row02_Col18_Byte0", float) = 0
    _Letter_Row02_Col19_Byte0("_Letter_Row02_Col19_Byte0", float) = 0
    _Letter_Row02_Col20_Byte0("_Letter_Row02_Col20_Byte0", float) = 0
    _Letter_Row02_Col21_Byte0("_Letter_Row02_Col21_Byte0", float) = 0
    _Letter_Row02_Col22_Byte0("_Letter_Row02_Col22_Byte0", float) = 0
    _Letter_Row02_Col23_Byte0("_Letter_Row02_Col23_Byte0", float) = 0
    _Letter_Row02_Col24_Byte0("_Letter_Row02_Col24_Byte0", float) = 0
    _Letter_Row02_Col25_Byte0("_Letter_Row02_Col25_Byte0", float) = 0
    _Letter_Row02_Col26_Byte0("_Letter_Row02_Col26_Byte0", float) = 0
    _Letter_Row02_Col27_Byte0("_Letter_Row02_Col27_Byte0", float) = 0
    _Letter_Row02_Col28_Byte0("_Letter_Row02_Col28_Byte0", float) = 0
    _Letter_Row02_Col29_Byte0("_Letter_Row02_Col29_Byte0", float) = 0
    _Letter_Row02_Col30_Byte0("_Letter_Row02_Col30_Byte0", float) = 0
    _Letter_Row02_Col31_Byte0("_Letter_Row02_Col31_Byte0", float) = 0
    _Letter_Row02_Col32_Byte0("_Letter_Row02_Col32_Byte0", float) = 0
    _Letter_Row02_Col33_Byte0("_Letter_Row02_Col33_Byte0", float) = 0
    _Letter_Row02_Col34_Byte0("_Letter_Row02_Col34_Byte0", float) = 0
    _Letter_Row02_Col35_Byte0("_Letter_Row02_Col35_Byte0", float) = 0
    _Letter_Row02_Col36_Byte0("_Letter_Row02_Col36_Byte0", float) = 0
    _Letter_Row02_Col37_Byte0("_Letter_Row02_Col37_Byte0", float) = 0
    _Letter_Row02_Col38_Byte0("_Letter_Row02_Col38_Byte0", float) = 0
    _Letter_Row02_Col39_Byte0("_Letter_Row02_Col39_Byte0", float) = 0
    _Letter_Row02_Col40_Byte0("_Letter_Row02_Col40_Byte0", float) = 0
    _Letter_Row02_Col41_Byte0("_Letter_Row02_Col41_Byte0", float) = 0
    _Letter_Row02_Col42_Byte0("_Letter_Row02_Col42_Byte0", float) = 0
    _Letter_Row02_Col43_Byte0("_Letter_Row02_Col43_Byte0", float) = 0
    _Letter_Row02_Col44_Byte0("_Letter_Row02_Col44_Byte0", float) = 0
    _Letter_Row02_Col45_Byte0("_Letter_Row02_Col45_Byte0", float) = 0
    _Letter_Row02_Col46_Byte0("_Letter_Row02_Col46_Byte0", float) = 0
    _Letter_Row02_Col47_Byte0("_Letter_Row02_Col47_Byte0", float) = 0
    _Letter_Row03_Col00_Byte0("_Letter_Row03_Col00_Byte0", float) = 0
    _Letter_Row03_Col01_Byte0("_Letter_Row03_Col01_Byte0", float) = 0
    _Letter_Row03_Col02_Byte0("_Letter_Row03_Col02_Byte0", float) = 0
    _Letter_Row03_Col03_Byte0("_Letter_Row03_Col03_Byte0", float) = 0
    _Letter_Row03_Col04_Byte0("_Letter_Row03_Col04_Byte0", float) = 0
    _Letter_Row03_Col05_Byte0("_Letter_Row03_Col05_Byte0", float) = 0
    _Letter_Row03_Col06_Byte0("_Letter_Row03_Col06_Byte0", float) = 0
    _Letter_Row03_Col07_Byte0("_Letter_Row03_Col07_Byte0", float) = 0
    _Letter_Row03_Col08_Byte0("_Letter_Row03_Col08_Byte0", float) = 0
    _Letter_Row03_Col09_Byte0("_Letter_Row03_Col09_Byte0", float) = 0
    _Letter_Row03_Col10_Byte0("_Letter_Row03_Col10_Byte0", float) = 0
    _Letter_Row03_Col11_Byte0("_Letter_Row03_Col11_Byte0", float) = 0
    _Letter_Row03_Col12_Byte0("_Letter_Row03_Col12_Byte0", float) = 0
    _Letter_Row03_Col13_Byte0("_Letter_Row03_Col13_Byte0", float) = 0
    _Letter_Row03_Col14_Byte0("_Letter_Row03_Col14_Byte0", float) = 0
    _Letter_Row03_Col15_Byte0("_Letter_Row03_Col15_Byte0", float) = 0
    _Letter_Row03_Col16_Byte0("_Letter_Row03_Col16_Byte0", float) = 0
    _Letter_Row03_Col17_Byte0("_Letter_Row03_Col17_Byte0", float) = 0
    _Letter_Row03_Col18_Byte0("_Letter_Row03_Col18_Byte0", float) = 0
    _Letter_Row03_Col19_Byte0("_Letter_Row03_Col19_Byte0", float) = 0
    _Letter_Row03_Col20_Byte0("_Letter_Row03_Col20_Byte0", float) = 0
    _Letter_Row03_Col21_Byte0("_Letter_Row03_Col21_Byte0", float) = 0
    _Letter_Row03_Col22_Byte0("_Letter_Row03_Col22_Byte0", float) = 0
    _Letter_Row03_Col23_Byte0("_Letter_Row03_Col23_Byte0", float) = 0
    _Letter_Row03_Col24_Byte0("_Letter_Row03_Col24_Byte0", float) = 0
    _Letter_Row03_Col25_Byte0("_Letter_Row03_Col25_Byte0", float) = 0
    _Letter_Row03_Col26_Byte0("_Letter_Row03_Col26_Byte0", float) = 0
    _Letter_Row03_Col27_Byte0("_Letter_Row03_Col27_Byte0", float) = 0
    _Letter_Row03_Col28_Byte0("_Letter_Row03_Col28_Byte0", float) = 0
    _Letter_Row03_Col29_Byte0("_Letter_Row03_Col29_Byte0", float) = 0
    _Letter_Row03_Col30_Byte0("_Letter_Row03_Col30_Byte0", float) = 0
    _Letter_Row03_Col31_Byte0("_Letter_Row03_Col31_Byte0", float) = 0
    _Letter_Row03_Col32_Byte0("_Letter_Row03_Col32_Byte0", float) = 0
    _Letter_Row03_Col33_Byte0("_Letter_Row03_Col33_Byte0", float) = 0
    _Letter_Row03_Col34_Byte0("_Letter_Row03_Col34_Byte0", float) = 0
    _Letter_Row03_Col35_Byte0("_Letter_Row03_Col35_Byte0", float) = 0
    _Letter_Row03_Col36_Byte0("_Letter_Row03_Col36_Byte0", float) = 0
    _Letter_Row03_Col37_Byte0("_Letter_Row03_Col37_Byte0", float) = 0
    _Letter_Row03_Col38_Byte0("_Letter_Row03_Col38_Byte0", float) = 0
    _Letter_Row03_Col39_Byte0("_Letter_Row03_Col39_Byte0", float) = 0
    _Letter_Row03_Col40_Byte0("_Letter_Row03_Col40_Byte0", float) = 0
    _Letter_Row03_Col41_Byte0("_Letter_Row03_Col41_Byte0", float) = 0
    _Letter_Row03_Col42_Byte0("_Letter_Row03_Col42_Byte0", float) = 0
    _Letter_Row03_Col43_Byte0("_Letter_Row03_Col43_Byte0", float) = 0
    _Letter_Row03_Col44_Byte0("_Letter_Row03_Col44_Byte0", float) = 0
    _Letter_Row03_Col45_Byte0("_Letter_Row03_Col45_Byte0", float) = 0
    _Letter_Row03_Col46_Byte0("_Letter_Row03_Col46_Byte0", float) = 0
    _Letter_Row03_Col47_Byte0("_Letter_Row03_Col47_Byte0", float) = 0
    _Letter_Row00_Col00_Byte1("_Letter_Row00_Col00_Byte1", float) = 0
    _Letter_Row00_Col01_Byte1("_Letter_Row00_Col01_Byte1", float) = 0
    _Letter_Row00_Col02_Byte1("_Letter_Row00_Col02_Byte1", float) = 0
    _Letter_Row00_Col03_Byte1("_Letter_Row00_Col03_Byte1", float) = 0
    _Letter_Row00_Col04_Byte1("_Letter_Row00_Col04_Byte1", float) = 0
    _Letter_Row00_Col05_Byte1("_Letter_Row00_Col05_Byte1", float) = 0
    _Letter_Row00_Col06_Byte1("_Letter_Row00_Col06_Byte1", float) = 0
    _Letter_Row00_Col07_Byte1("_Letter_Row00_Col07_Byte1", float) = 0
    _Letter_Row00_Col08_Byte1("_Letter_Row00_Col08_Byte1", float) = 0
    _Letter_Row00_Col09_Byte1("_Letter_Row00_Col09_Byte1", float) = 0
    _Letter_Row00_Col10_Byte1("_Letter_Row00_Col10_Byte1", float) = 0
    _Letter_Row00_Col11_Byte1("_Letter_Row00_Col11_Byte1", float) = 0
    _Letter_Row00_Col12_Byte1("_Letter_Row00_Col12_Byte1", float) = 0
    _Letter_Row00_Col13_Byte1("_Letter_Row00_Col13_Byte1", float) = 0
    _Letter_Row00_Col14_Byte1("_Letter_Row00_Col14_Byte1", float) = 0
    _Letter_Row00_Col15_Byte1("_Letter_Row00_Col15_Byte1", float) = 0
    _Letter_Row00_Col16_Byte1("_Letter_Row00_Col16_Byte1", float) = 0
    _Letter_Row00_Col17_Byte1("_Letter_Row00_Col17_Byte1", float) = 0
    _Letter_Row00_Col18_Byte1("_Letter_Row00_Col18_Byte1", float) = 0
    _Letter_Row00_Col19_Byte1("_Letter_Row00_Col19_Byte1", float) = 0
    _Letter_Row00_Col20_Byte1("_Letter_Row00_Col20_Byte1", float) = 0
    _Letter_Row00_Col21_Byte1("_Letter_Row00_Col21_Byte1", float) = 0
    _Letter_Row00_Col22_Byte1("_Letter_Row00_Col22_Byte1", float) = 0
    _Letter_Row00_Col23_Byte1("_Letter_Row00_Col23_Byte1", float) = 0
    _Letter_Row00_Col24_Byte1("_Letter_Row00_Col24_Byte1", float) = 0
    _Letter_Row00_Col25_Byte1("_Letter_Row00_Col25_Byte1", float) = 0
    _Letter_Row00_Col26_Byte1("_Letter_Row00_Col26_Byte1", float) = 0
    _Letter_Row00_Col27_Byte1("_Letter_Row00_Col27_Byte1", float) = 0
    _Letter_Row00_Col28_Byte1("_Letter_Row00_Col28_Byte1", float) = 0
    _Letter_Row00_Col29_Byte1("_Letter_Row00_Col29_Byte1", float) = 0
    _Letter_Row00_Col30_Byte1("_Letter_Row00_Col30_Byte1", float) = 0
    _Letter_Row00_Col31_Byte1("_Letter_Row00_Col31_Byte1", float) = 0
    _Letter_Row00_Col32_Byte1("_Letter_Row00_Col32_Byte1", float) = 0
    _Letter_Row00_Col33_Byte1("_Letter_Row00_Col33_Byte1", float) = 0
    _Letter_Row00_Col34_Byte1("_Letter_Row00_Col34_Byte1", float) = 0
    _Letter_Row00_Col35_Byte1("_Letter_Row00_Col35_Byte1", float) = 0
    _Letter_Row00_Col36_Byte1("_Letter_Row00_Col36_Byte1", float) = 0
    _Letter_Row00_Col37_Byte1("_Letter_Row00_Col37_Byte1", float) = 0
    _Letter_Row00_Col38_Byte1("_Letter_Row00_Col38_Byte1", float) = 0
    _Letter_Row00_Col39_Byte1("_Letter_Row00_Col39_Byte1", float) = 0
    _Letter_Row00_Col40_Byte1("_Letter_Row00_Col40_Byte1", float) = 0
    _Letter_Row00_Col41_Byte1("_Letter_Row00_Col41_Byte1", float) = 0
    _Letter_Row00_Col42_Byte1("_Letter_Row00_Col42_Byte1", float) = 0
    _Letter_Row00_Col43_Byte1("_Letter_Row00_Col43_Byte1", float) = 0
    _Letter_Row00_Col44_Byte1("_Letter_Row00_Col44_Byte1", float) = 0
    _Letter_Row00_Col45_Byte1("_Letter_Row00_Col45_Byte1", float) = 0
    _Letter_Row00_Col46_Byte1("_Letter_Row00_Col46_Byte1", float) = 0
    _Letter_Row00_Col47_Byte1("_Letter_Row00_Col47_Byte1", float) = 0
    _Letter_Row01_Col00_Byte1("_Letter_Row01_Col00_Byte1", float) = 0
    _Letter_Row01_Col01_Byte1("_Letter_Row01_Col01_Byte1", float) = 0
    _Letter_Row01_Col02_Byte1("_Letter_Row01_Col02_Byte1", float) = 0
    _Letter_Row01_Col03_Byte1("_Letter_Row01_Col03_Byte1", float) = 0
    _Letter_Row01_Col04_Byte1("_Letter_Row01_Col04_Byte1", float) = 0
    _Letter_Row01_Col05_Byte1("_Letter_Row01_Col05_Byte1", float) = 0
    _Letter_Row01_Col06_Byte1("_Letter_Row01_Col06_Byte1", float) = 0
    _Letter_Row01_Col07_Byte1("_Letter_Row01_Col07_Byte1", float) = 0
    _Letter_Row01_Col08_Byte1("_Letter_Row01_Col08_Byte1", float) = 0
    _Letter_Row01_Col09_Byte1("_Letter_Row01_Col09_Byte1", float) = 0
    _Letter_Row01_Col10_Byte1("_Letter_Row01_Col10_Byte1", float) = 0
    _Letter_Row01_Col11_Byte1("_Letter_Row01_Col11_Byte1", float) = 0
    _Letter_Row01_Col12_Byte1("_Letter_Row01_Col12_Byte1", float) = 0
    _Letter_Row01_Col13_Byte1("_Letter_Row01_Col13_Byte1", float) = 0
    _Letter_Row01_Col14_Byte1("_Letter_Row01_Col14_Byte1", float) = 0
    _Letter_Row01_Col15_Byte1("_Letter_Row01_Col15_Byte1", float) = 0
    _Letter_Row01_Col16_Byte1("_Letter_Row01_Col16_Byte1", float) = 0
    _Letter_Row01_Col17_Byte1("_Letter_Row01_Col17_Byte1", float) = 0
    _Letter_Row01_Col18_Byte1("_Letter_Row01_Col18_Byte1", float) = 0
    _Letter_Row01_Col19_Byte1("_Letter_Row01_Col19_Byte1", float) = 0
    _Letter_Row01_Col20_Byte1("_Letter_Row01_Col20_Byte1", float) = 0
    _Letter_Row01_Col21_Byte1("_Letter_Row01_Col21_Byte1", float) = 0
    _Letter_Row01_Col22_Byte1("_Letter_Row01_Col22_Byte1", float) = 0
    _Letter_Row01_Col23_Byte1("_Letter_Row01_Col23_Byte1", float) = 0
    _Letter_Row01_Col24_Byte1("_Letter_Row01_Col24_Byte1", float) = 0
    _Letter_Row01_Col25_Byte1("_Letter_Row01_Col25_Byte1", float) = 0
    _Letter_Row01_Col26_Byte1("_Letter_Row01_Col26_Byte1", float) = 0
    _Letter_Row01_Col27_Byte1("_Letter_Row01_Col27_Byte1", float) = 0
    _Letter_Row01_Col28_Byte1("_Letter_Row01_Col28_Byte1", float) = 0
    _Letter_Row01_Col29_Byte1("_Letter_Row01_Col29_Byte1", float) = 0
    _Letter_Row01_Col30_Byte1("_Letter_Row01_Col30_Byte1", float) = 0
    _Letter_Row01_Col31_Byte1("_Letter_Row01_Col31_Byte1", float) = 0
    _Letter_Row01_Col32_Byte1("_Letter_Row01_Col32_Byte1", float) = 0
    _Letter_Row01_Col33_Byte1("_Letter_Row01_Col33_Byte1", float) = 0
    _Letter_Row01_Col34_Byte1("_Letter_Row01_Col34_Byte1", float) = 0
    _Letter_Row01_Col35_Byte1("_Letter_Row01_Col35_Byte1", float) = 0
    _Letter_Row01_Col36_Byte1("_Letter_Row01_Col36_Byte1", float) = 0
    _Letter_Row01_Col37_Byte1("_Letter_Row01_Col37_Byte1", float) = 0
    _Letter_Row01_Col38_Byte1("_Letter_Row01_Col38_Byte1", float) = 0
    _Letter_Row01_Col39_Byte1("_Letter_Row01_Col39_Byte1", float) = 0
    _Letter_Row01_Col40_Byte1("_Letter_Row01_Col40_Byte1", float) = 0
    _Letter_Row01_Col41_Byte1("_Letter_Row01_Col41_Byte1", float) = 0
    _Letter_Row01_Col42_Byte1("_Letter_Row01_Col42_Byte1", float) = 0
    _Letter_Row01_Col43_Byte1("_Letter_Row01_Col43_Byte1", float) = 0
    _Letter_Row01_Col44_Byte1("_Letter_Row01_Col44_Byte1", float) = 0
    _Letter_Row01_Col45_Byte1("_Letter_Row01_Col45_Byte1", float) = 0
    _Letter_Row01_Col46_Byte1("_Letter_Row01_Col46_Byte1", float) = 0
    _Letter_Row01_Col47_Byte1("_Letter_Row01_Col47_Byte1", float) = 0
    _Letter_Row02_Col00_Byte1("_Letter_Row02_Col00_Byte1", float) = 0
    _Letter_Row02_Col01_Byte1("_Letter_Row02_Col01_Byte1", float) = 0
    _Letter_Row02_Col02_Byte1("_Letter_Row02_Col02_Byte1", float) = 0
    _Letter_Row02_Col03_Byte1("_Letter_Row02_Col03_Byte1", float) = 0
    _Letter_Row02_Col04_Byte1("_Letter_Row02_Col04_Byte1", float) = 0
    _Letter_Row02_Col05_Byte1("_Letter_Row02_Col05_Byte1", float) = 0
    _Letter_Row02_Col06_Byte1("_Letter_Row02_Col06_Byte1", float) = 0
    _Letter_Row02_Col07_Byte1("_Letter_Row02_Col07_Byte1", float) = 0
    _Letter_Row02_Col08_Byte1("_Letter_Row02_Col08_Byte1", float) = 0
    _Letter_Row02_Col09_Byte1("_Letter_Row02_Col09_Byte1", float) = 0
    _Letter_Row02_Col10_Byte1("_Letter_Row02_Col10_Byte1", float) = 0
    _Letter_Row02_Col11_Byte1("_Letter_Row02_Col11_Byte1", float) = 0
    _Letter_Row02_Col12_Byte1("_Letter_Row02_Col12_Byte1", float) = 0
    _Letter_Row02_Col13_Byte1("_Letter_Row02_Col13_Byte1", float) = 0
    _Letter_Row02_Col14_Byte1("_Letter_Row02_Col14_Byte1", float) = 0
    _Letter_Row02_Col15_Byte1("_Letter_Row02_Col15_Byte1", float) = 0
    _Letter_Row02_Col16_Byte1("_Letter_Row02_Col16_Byte1", float) = 0
    _Letter_Row02_Col17_Byte1("_Letter_Row02_Col17_Byte1", float) = 0
    _Letter_Row02_Col18_Byte1("_Letter_Row02_Col18_Byte1", float) = 0
    _Letter_Row02_Col19_Byte1("_Letter_Row02_Col19_Byte1", float) = 0
    _Letter_Row02_Col20_Byte1("_Letter_Row02_Col20_Byte1", float) = 0
    _Letter_Row02_Col21_Byte1("_Letter_Row02_Col21_Byte1", float) = 0
    _Letter_Row02_Col22_Byte1("_Letter_Row02_Col22_Byte1", float) = 0
    _Letter_Row02_Col23_Byte1("_Letter_Row02_Col23_Byte1", float) = 0
    _Letter_Row02_Col24_Byte1("_Letter_Row02_Col24_Byte1", float) = 0
    _Letter_Row02_Col25_Byte1("_Letter_Row02_Col25_Byte1", float) = 0
    _Letter_Row02_Col26_Byte1("_Letter_Row02_Col26_Byte1", float) = 0
    _Letter_Row02_Col27_Byte1("_Letter_Row02_Col27_Byte1", float) = 0
    _Letter_Row02_Col28_Byte1("_Letter_Row02_Col28_Byte1", float) = 0
    _Letter_Row02_Col29_Byte1("_Letter_Row02_Col29_Byte1", float) = 0
    _Letter_Row02_Col30_Byte1("_Letter_Row02_Col30_Byte1", float) = 0
    _Letter_Row02_Col31_Byte1("_Letter_Row02_Col31_Byte1", float) = 0
    _Letter_Row02_Col32_Byte1("_Letter_Row02_Col32_Byte1", float) = 0
    _Letter_Row02_Col33_Byte1("_Letter_Row02_Col33_Byte1", float) = 0
    _Letter_Row02_Col34_Byte1("_Letter_Row02_Col34_Byte1", float) = 0
    _Letter_Row02_Col35_Byte1("_Letter_Row02_Col35_Byte1", float) = 0
    _Letter_Row02_Col36_Byte1("_Letter_Row02_Col36_Byte1", float) = 0
    _Letter_Row02_Col37_Byte1("_Letter_Row02_Col37_Byte1", float) = 0
    _Letter_Row02_Col38_Byte1("_Letter_Row02_Col38_Byte1", float) = 0
    _Letter_Row02_Col39_Byte1("_Letter_Row02_Col39_Byte1", float) = 0
    _Letter_Row02_Col40_Byte1("_Letter_Row02_Col40_Byte1", float) = 0
    _Letter_Row02_Col41_Byte1("_Letter_Row02_Col41_Byte1", float) = 0
    _Letter_Row02_Col42_Byte1("_Letter_Row02_Col42_Byte1", float) = 0
    _Letter_Row02_Col43_Byte1("_Letter_Row02_Col43_Byte1", float) = 0
    _Letter_Row02_Col44_Byte1("_Letter_Row02_Col44_Byte1", float) = 0
    _Letter_Row02_Col45_Byte1("_Letter_Row02_Col45_Byte1", float) = 0
    _Letter_Row02_Col46_Byte1("_Letter_Row02_Col46_Byte1", float) = 0
    _Letter_Row02_Col47_Byte1("_Letter_Row02_Col47_Byte1", float) = 0
    _Letter_Row03_Col00_Byte1("_Letter_Row03_Col00_Byte1", float) = 0
    _Letter_Row03_Col01_Byte1("_Letter_Row03_Col01_Byte1", float) = 0
    _Letter_Row03_Col02_Byte1("_Letter_Row03_Col02_Byte1", float) = 0
    _Letter_Row03_Col03_Byte1("_Letter_Row03_Col03_Byte1", float) = 0
    _Letter_Row03_Col04_Byte1("_Letter_Row03_Col04_Byte1", float) = 0
    _Letter_Row03_Col05_Byte1("_Letter_Row03_Col05_Byte1", float) = 0
    _Letter_Row03_Col06_Byte1("_Letter_Row03_Col06_Byte1", float) = 0
    _Letter_Row03_Col07_Byte1("_Letter_Row03_Col07_Byte1", float) = 0
    _Letter_Row03_Col08_Byte1("_Letter_Row03_Col08_Byte1", float) = 0
    _Letter_Row03_Col09_Byte1("_Letter_Row03_Col09_Byte1", float) = 0
    _Letter_Row03_Col10_Byte1("_Letter_Row03_Col10_Byte1", float) = 0
    _Letter_Row03_Col11_Byte1("_Letter_Row03_Col11_Byte1", float) = 0
    _Letter_Row03_Col12_Byte1("_Letter_Row03_Col12_Byte1", float) = 0
    _Letter_Row03_Col13_Byte1("_Letter_Row03_Col13_Byte1", float) = 0
    _Letter_Row03_Col14_Byte1("_Letter_Row03_Col14_Byte1", float) = 0
    _Letter_Row03_Col15_Byte1("_Letter_Row03_Col15_Byte1", float) = 0
    _Letter_Row03_Col16_Byte1("_Letter_Row03_Col16_Byte1", float) = 0
    _Letter_Row03_Col17_Byte1("_Letter_Row03_Col17_Byte1", float) = 0
    _Letter_Row03_Col18_Byte1("_Letter_Row03_Col18_Byte1", float) = 0
    _Letter_Row03_Col19_Byte1("_Letter_Row03_Col19_Byte1", float) = 0
    _Letter_Row03_Col20_Byte1("_Letter_Row03_Col20_Byte1", float) = 0
    _Letter_Row03_Col21_Byte1("_Letter_Row03_Col21_Byte1", float) = 0
    _Letter_Row03_Col22_Byte1("_Letter_Row03_Col22_Byte1", float) = 0
    _Letter_Row03_Col23_Byte1("_Letter_Row03_Col23_Byte1", float) = 0
    _Letter_Row03_Col24_Byte1("_Letter_Row03_Col24_Byte1", float) = 0
    _Letter_Row03_Col25_Byte1("_Letter_Row03_Col25_Byte1", float) = 0
    _Letter_Row03_Col26_Byte1("_Letter_Row03_Col26_Byte1", float) = 0
    _Letter_Row03_Col27_Byte1("_Letter_Row03_Col27_Byte1", float) = 0
    _Letter_Row03_Col28_Byte1("_Letter_Row03_Col28_Byte1", float) = 0
    _Letter_Row03_Col29_Byte1("_Letter_Row03_Col29_Byte1", float) = 0
    _Letter_Row03_Col30_Byte1("_Letter_Row03_Col30_Byte1", float) = 0
    _Letter_Row03_Col31_Byte1("_Letter_Row03_Col31_Byte1", float) = 0
    _Letter_Row03_Col32_Byte1("_Letter_Row03_Col32_Byte1", float) = 0
    _Letter_Row03_Col33_Byte1("_Letter_Row03_Col33_Byte1", float) = 0
    _Letter_Row03_Col34_Byte1("_Letter_Row03_Col34_Byte1", float) = 0
    _Letter_Row03_Col35_Byte1("_Letter_Row03_Col35_Byte1", float) = 0
    _Letter_Row03_Col36_Byte1("_Letter_Row03_Col36_Byte1", float) = 0
    _Letter_Row03_Col37_Byte1("_Letter_Row03_Col37_Byte1", float) = 0
    _Letter_Row03_Col38_Byte1("_Letter_Row03_Col38_Byte1", float) = 0
    _Letter_Row03_Col39_Byte1("_Letter_Row03_Col39_Byte1", float) = 0
    _Letter_Row03_Col40_Byte1("_Letter_Row03_Col40_Byte1", float) = 0
    _Letter_Row03_Col41_Byte1("_Letter_Row03_Col41_Byte1", float) = 0
    _Letter_Row03_Col42_Byte1("_Letter_Row03_Col42_Byte1", float) = 0
    _Letter_Row03_Col43_Byte1("_Letter_Row03_Col43_Byte1", float) = 0
    _Letter_Row03_Col44_Byte1("_Letter_Row03_Col44_Byte1", float) = 0
    _Letter_Row03_Col45_Byte1("_Letter_Row03_Col45_Byte1", float) = 0
    _Letter_Row03_Col46_Byte1("_Letter_Row03_Col46_Byte1", float) = 0
    _Letter_Row03_Col47_Byte1("_Letter_Row03_Col47_Byte1", float) = 0
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

      SamplerState sampler_linear_repeat;

      Texture2D _Font_0x0000_0x1FFF;
      Texture2D _Font_0x2000_0x3FFF;
      Texture2D _Font_0x4000_0x5FFF;
      Texture2D _Font_0x6000_0x7FFF;
      Texture2D _Font_0x8000_0x9FFF;
      Texture2D _Font_0xA000_0xBFFF;
      Texture2D _Font_0xC000_0xDFFF;
      Texture2D _Img_0xE000_0xE03F;

      float Render_Margin;
      float Render_Visual_Indicator;
      float Margin_Scale;

      float3 HUEtoRGB(in float H)
      {
        float R = abs(H * 6 - 3) - 1;
        float G = 2 - abs(H * 6 - 2);
        float B = 2 - abs(H * 6 - 4);
        return saturate(float3(R, G, B));
      }

      float3 HSVtoRGB(in float3 HSV)
      {
        float3 RGB = HUEtoRGB(HSV.x);
        return ((RGB - 1) * HSV.y + 1) * HSV.z;
      }

      float TaSTT_Indicator_0;
      float TaSTT_Indicator_1;
      static const float3 TaSTT_Indicator_Color_0 = HSVtoRGB(float3(0.00, 0.7, 1.0));
      static const float3 TaSTT_Indicator_Color_1 = HSVtoRGB(float3(0.07, 0.7, 1.0));
      static const float3 TaSTT_Indicator_Color_2 = HSVtoRGB(float3(0.30, 0.7, 1.0));

      fixed4 float3tofixed4(in float3 f3, in float alpha)
      {
        return fixed4(
          f3.r,
          f3.g,
          f3.b,
          alpha);
      }

      Texture2D TaSTT_Backplate;

      float _Letter_Row00_Col00_Byte0;
      float _Letter_Row00_Col01_Byte0;
      float _Letter_Row00_Col02_Byte0;
      float _Letter_Row00_Col03_Byte0;
      float _Letter_Row00_Col04_Byte0;
      float _Letter_Row00_Col05_Byte0;
      float _Letter_Row00_Col06_Byte0;
      float _Letter_Row00_Col07_Byte0;
      float _Letter_Row00_Col08_Byte0;
      float _Letter_Row00_Col09_Byte0;
      float _Letter_Row00_Col10_Byte0;
      float _Letter_Row00_Col11_Byte0;
      float _Letter_Row00_Col12_Byte0;
      float _Letter_Row00_Col13_Byte0;
      float _Letter_Row00_Col14_Byte0;
      float _Letter_Row00_Col15_Byte0;
      float _Letter_Row00_Col16_Byte0;
      float _Letter_Row00_Col17_Byte0;
      float _Letter_Row00_Col18_Byte0;
      float _Letter_Row00_Col19_Byte0;
      float _Letter_Row00_Col20_Byte0;
      float _Letter_Row00_Col21_Byte0;
      float _Letter_Row00_Col22_Byte0;
      float _Letter_Row00_Col23_Byte0;
      float _Letter_Row00_Col24_Byte0;
      float _Letter_Row00_Col25_Byte0;
      float _Letter_Row00_Col26_Byte0;
      float _Letter_Row00_Col27_Byte0;
      float _Letter_Row00_Col28_Byte0;
      float _Letter_Row00_Col29_Byte0;
      float _Letter_Row00_Col30_Byte0;
      float _Letter_Row00_Col31_Byte0;
      float _Letter_Row00_Col32_Byte0;
      float _Letter_Row00_Col33_Byte0;
      float _Letter_Row00_Col34_Byte0;
      float _Letter_Row00_Col35_Byte0;
      float _Letter_Row00_Col36_Byte0;
      float _Letter_Row00_Col37_Byte0;
      float _Letter_Row00_Col38_Byte0;
      float _Letter_Row00_Col39_Byte0;
      float _Letter_Row00_Col40_Byte0;
      float _Letter_Row00_Col41_Byte0;
      float _Letter_Row00_Col42_Byte0;
      float _Letter_Row00_Col43_Byte0;
      float _Letter_Row00_Col44_Byte0;
      float _Letter_Row00_Col45_Byte0;
      float _Letter_Row00_Col46_Byte0;
      float _Letter_Row00_Col47_Byte0;
      float _Letter_Row01_Col00_Byte0;
      float _Letter_Row01_Col01_Byte0;
      float _Letter_Row01_Col02_Byte0;
      float _Letter_Row01_Col03_Byte0;
      float _Letter_Row01_Col04_Byte0;
      float _Letter_Row01_Col05_Byte0;
      float _Letter_Row01_Col06_Byte0;
      float _Letter_Row01_Col07_Byte0;
      float _Letter_Row01_Col08_Byte0;
      float _Letter_Row01_Col09_Byte0;
      float _Letter_Row01_Col10_Byte0;
      float _Letter_Row01_Col11_Byte0;
      float _Letter_Row01_Col12_Byte0;
      float _Letter_Row01_Col13_Byte0;
      float _Letter_Row01_Col14_Byte0;
      float _Letter_Row01_Col15_Byte0;
      float _Letter_Row01_Col16_Byte0;
      float _Letter_Row01_Col17_Byte0;
      float _Letter_Row01_Col18_Byte0;
      float _Letter_Row01_Col19_Byte0;
      float _Letter_Row01_Col20_Byte0;
      float _Letter_Row01_Col21_Byte0;
      float _Letter_Row01_Col22_Byte0;
      float _Letter_Row01_Col23_Byte0;
      float _Letter_Row01_Col24_Byte0;
      float _Letter_Row01_Col25_Byte0;
      float _Letter_Row01_Col26_Byte0;
      float _Letter_Row01_Col27_Byte0;
      float _Letter_Row01_Col28_Byte0;
      float _Letter_Row01_Col29_Byte0;
      float _Letter_Row01_Col30_Byte0;
      float _Letter_Row01_Col31_Byte0;
      float _Letter_Row01_Col32_Byte0;
      float _Letter_Row01_Col33_Byte0;
      float _Letter_Row01_Col34_Byte0;
      float _Letter_Row01_Col35_Byte0;
      float _Letter_Row01_Col36_Byte0;
      float _Letter_Row01_Col37_Byte0;
      float _Letter_Row01_Col38_Byte0;
      float _Letter_Row01_Col39_Byte0;
      float _Letter_Row01_Col40_Byte0;
      float _Letter_Row01_Col41_Byte0;
      float _Letter_Row01_Col42_Byte0;
      float _Letter_Row01_Col43_Byte0;
      float _Letter_Row01_Col44_Byte0;
      float _Letter_Row01_Col45_Byte0;
      float _Letter_Row01_Col46_Byte0;
      float _Letter_Row01_Col47_Byte0;
      float _Letter_Row02_Col00_Byte0;
      float _Letter_Row02_Col01_Byte0;
      float _Letter_Row02_Col02_Byte0;
      float _Letter_Row02_Col03_Byte0;
      float _Letter_Row02_Col04_Byte0;
      float _Letter_Row02_Col05_Byte0;
      float _Letter_Row02_Col06_Byte0;
      float _Letter_Row02_Col07_Byte0;
      float _Letter_Row02_Col08_Byte0;
      float _Letter_Row02_Col09_Byte0;
      float _Letter_Row02_Col10_Byte0;
      float _Letter_Row02_Col11_Byte0;
      float _Letter_Row02_Col12_Byte0;
      float _Letter_Row02_Col13_Byte0;
      float _Letter_Row02_Col14_Byte0;
      float _Letter_Row02_Col15_Byte0;
      float _Letter_Row02_Col16_Byte0;
      float _Letter_Row02_Col17_Byte0;
      float _Letter_Row02_Col18_Byte0;
      float _Letter_Row02_Col19_Byte0;
      float _Letter_Row02_Col20_Byte0;
      float _Letter_Row02_Col21_Byte0;
      float _Letter_Row02_Col22_Byte0;
      float _Letter_Row02_Col23_Byte0;
      float _Letter_Row02_Col24_Byte0;
      float _Letter_Row02_Col25_Byte0;
      float _Letter_Row02_Col26_Byte0;
      float _Letter_Row02_Col27_Byte0;
      float _Letter_Row02_Col28_Byte0;
      float _Letter_Row02_Col29_Byte0;
      float _Letter_Row02_Col30_Byte0;
      float _Letter_Row02_Col31_Byte0;
      float _Letter_Row02_Col32_Byte0;
      float _Letter_Row02_Col33_Byte0;
      float _Letter_Row02_Col34_Byte0;
      float _Letter_Row02_Col35_Byte0;
      float _Letter_Row02_Col36_Byte0;
      float _Letter_Row02_Col37_Byte0;
      float _Letter_Row02_Col38_Byte0;
      float _Letter_Row02_Col39_Byte0;
      float _Letter_Row02_Col40_Byte0;
      float _Letter_Row02_Col41_Byte0;
      float _Letter_Row02_Col42_Byte0;
      float _Letter_Row02_Col43_Byte0;
      float _Letter_Row02_Col44_Byte0;
      float _Letter_Row02_Col45_Byte0;
      float _Letter_Row02_Col46_Byte0;
      float _Letter_Row02_Col47_Byte0;
      float _Letter_Row03_Col00_Byte0;
      float _Letter_Row03_Col01_Byte0;
      float _Letter_Row03_Col02_Byte0;
      float _Letter_Row03_Col03_Byte0;
      float _Letter_Row03_Col04_Byte0;
      float _Letter_Row03_Col05_Byte0;
      float _Letter_Row03_Col06_Byte0;
      float _Letter_Row03_Col07_Byte0;
      float _Letter_Row03_Col08_Byte0;
      float _Letter_Row03_Col09_Byte0;
      float _Letter_Row03_Col10_Byte0;
      float _Letter_Row03_Col11_Byte0;
      float _Letter_Row03_Col12_Byte0;
      float _Letter_Row03_Col13_Byte0;
      float _Letter_Row03_Col14_Byte0;
      float _Letter_Row03_Col15_Byte0;
      float _Letter_Row03_Col16_Byte0;
      float _Letter_Row03_Col17_Byte0;
      float _Letter_Row03_Col18_Byte0;
      float _Letter_Row03_Col19_Byte0;
      float _Letter_Row03_Col20_Byte0;
      float _Letter_Row03_Col21_Byte0;
      float _Letter_Row03_Col22_Byte0;
      float _Letter_Row03_Col23_Byte0;
      float _Letter_Row03_Col24_Byte0;
      float _Letter_Row03_Col25_Byte0;
      float _Letter_Row03_Col26_Byte0;
      float _Letter_Row03_Col27_Byte0;
      float _Letter_Row03_Col28_Byte0;
      float _Letter_Row03_Col29_Byte0;
      float _Letter_Row03_Col30_Byte0;
      float _Letter_Row03_Col31_Byte0;
      float _Letter_Row03_Col32_Byte0;
      float _Letter_Row03_Col33_Byte0;
      float _Letter_Row03_Col34_Byte0;
      float _Letter_Row03_Col35_Byte0;
      float _Letter_Row03_Col36_Byte0;
      float _Letter_Row03_Col37_Byte0;
      float _Letter_Row03_Col38_Byte0;
      float _Letter_Row03_Col39_Byte0;
      float _Letter_Row03_Col40_Byte0;
      float _Letter_Row03_Col41_Byte0;
      float _Letter_Row03_Col42_Byte0;
      float _Letter_Row03_Col43_Byte0;
      float _Letter_Row03_Col44_Byte0;
      float _Letter_Row03_Col45_Byte0;
      float _Letter_Row03_Col46_Byte0;
      float _Letter_Row03_Col47_Byte0;
      float _Letter_Row00_Col00_Byte1;
      float _Letter_Row00_Col01_Byte1;
      float _Letter_Row00_Col02_Byte1;
      float _Letter_Row00_Col03_Byte1;
      float _Letter_Row00_Col04_Byte1;
      float _Letter_Row00_Col05_Byte1;
      float _Letter_Row00_Col06_Byte1;
      float _Letter_Row00_Col07_Byte1;
      float _Letter_Row00_Col08_Byte1;
      float _Letter_Row00_Col09_Byte1;
      float _Letter_Row00_Col10_Byte1;
      float _Letter_Row00_Col11_Byte1;
      float _Letter_Row00_Col12_Byte1;
      float _Letter_Row00_Col13_Byte1;
      float _Letter_Row00_Col14_Byte1;
      float _Letter_Row00_Col15_Byte1;
      float _Letter_Row00_Col16_Byte1;
      float _Letter_Row00_Col17_Byte1;
      float _Letter_Row00_Col18_Byte1;
      float _Letter_Row00_Col19_Byte1;
      float _Letter_Row00_Col20_Byte1;
      float _Letter_Row00_Col21_Byte1;
      float _Letter_Row00_Col22_Byte1;
      float _Letter_Row00_Col23_Byte1;
      float _Letter_Row00_Col24_Byte1;
      float _Letter_Row00_Col25_Byte1;
      float _Letter_Row00_Col26_Byte1;
      float _Letter_Row00_Col27_Byte1;
      float _Letter_Row00_Col28_Byte1;
      float _Letter_Row00_Col29_Byte1;
      float _Letter_Row00_Col30_Byte1;
      float _Letter_Row00_Col31_Byte1;
      float _Letter_Row00_Col32_Byte1;
      float _Letter_Row00_Col33_Byte1;
      float _Letter_Row00_Col34_Byte1;
      float _Letter_Row00_Col35_Byte1;
      float _Letter_Row00_Col36_Byte1;
      float _Letter_Row00_Col37_Byte1;
      float _Letter_Row00_Col38_Byte1;
      float _Letter_Row00_Col39_Byte1;
      float _Letter_Row00_Col40_Byte1;
      float _Letter_Row00_Col41_Byte1;
      float _Letter_Row00_Col42_Byte1;
      float _Letter_Row00_Col43_Byte1;
      float _Letter_Row00_Col44_Byte1;
      float _Letter_Row00_Col45_Byte1;
      float _Letter_Row00_Col46_Byte1;
      float _Letter_Row00_Col47_Byte1;
      float _Letter_Row01_Col00_Byte1;
      float _Letter_Row01_Col01_Byte1;
      float _Letter_Row01_Col02_Byte1;
      float _Letter_Row01_Col03_Byte1;
      float _Letter_Row01_Col04_Byte1;
      float _Letter_Row01_Col05_Byte1;
      float _Letter_Row01_Col06_Byte1;
      float _Letter_Row01_Col07_Byte1;
      float _Letter_Row01_Col08_Byte1;
      float _Letter_Row01_Col09_Byte1;
      float _Letter_Row01_Col10_Byte1;
      float _Letter_Row01_Col11_Byte1;
      float _Letter_Row01_Col12_Byte1;
      float _Letter_Row01_Col13_Byte1;
      float _Letter_Row01_Col14_Byte1;
      float _Letter_Row01_Col15_Byte1;
      float _Letter_Row01_Col16_Byte1;
      float _Letter_Row01_Col17_Byte1;
      float _Letter_Row01_Col18_Byte1;
      float _Letter_Row01_Col19_Byte1;
      float _Letter_Row01_Col20_Byte1;
      float _Letter_Row01_Col21_Byte1;
      float _Letter_Row01_Col22_Byte1;
      float _Letter_Row01_Col23_Byte1;
      float _Letter_Row01_Col24_Byte1;
      float _Letter_Row01_Col25_Byte1;
      float _Letter_Row01_Col26_Byte1;
      float _Letter_Row01_Col27_Byte1;
      float _Letter_Row01_Col28_Byte1;
      float _Letter_Row01_Col29_Byte1;
      float _Letter_Row01_Col30_Byte1;
      float _Letter_Row01_Col31_Byte1;
      float _Letter_Row01_Col32_Byte1;
      float _Letter_Row01_Col33_Byte1;
      float _Letter_Row01_Col34_Byte1;
      float _Letter_Row01_Col35_Byte1;
      float _Letter_Row01_Col36_Byte1;
      float _Letter_Row01_Col37_Byte1;
      float _Letter_Row01_Col38_Byte1;
      float _Letter_Row01_Col39_Byte1;
      float _Letter_Row01_Col40_Byte1;
      float _Letter_Row01_Col41_Byte1;
      float _Letter_Row01_Col42_Byte1;
      float _Letter_Row01_Col43_Byte1;
      float _Letter_Row01_Col44_Byte1;
      float _Letter_Row01_Col45_Byte1;
      float _Letter_Row01_Col46_Byte1;
      float _Letter_Row01_Col47_Byte1;
      float _Letter_Row02_Col00_Byte1;
      float _Letter_Row02_Col01_Byte1;
      float _Letter_Row02_Col02_Byte1;
      float _Letter_Row02_Col03_Byte1;
      float _Letter_Row02_Col04_Byte1;
      float _Letter_Row02_Col05_Byte1;
      float _Letter_Row02_Col06_Byte1;
      float _Letter_Row02_Col07_Byte1;
      float _Letter_Row02_Col08_Byte1;
      float _Letter_Row02_Col09_Byte1;
      float _Letter_Row02_Col10_Byte1;
      float _Letter_Row02_Col11_Byte1;
      float _Letter_Row02_Col12_Byte1;
      float _Letter_Row02_Col13_Byte1;
      float _Letter_Row02_Col14_Byte1;
      float _Letter_Row02_Col15_Byte1;
      float _Letter_Row02_Col16_Byte1;
      float _Letter_Row02_Col17_Byte1;
      float _Letter_Row02_Col18_Byte1;
      float _Letter_Row02_Col19_Byte1;
      float _Letter_Row02_Col20_Byte1;
      float _Letter_Row02_Col21_Byte1;
      float _Letter_Row02_Col22_Byte1;
      float _Letter_Row02_Col23_Byte1;
      float _Letter_Row02_Col24_Byte1;
      float _Letter_Row02_Col25_Byte1;
      float _Letter_Row02_Col26_Byte1;
      float _Letter_Row02_Col27_Byte1;
      float _Letter_Row02_Col28_Byte1;
      float _Letter_Row02_Col29_Byte1;
      float _Letter_Row02_Col30_Byte1;
      float _Letter_Row02_Col31_Byte1;
      float _Letter_Row02_Col32_Byte1;
      float _Letter_Row02_Col33_Byte1;
      float _Letter_Row02_Col34_Byte1;
      float _Letter_Row02_Col35_Byte1;
      float _Letter_Row02_Col36_Byte1;
      float _Letter_Row02_Col37_Byte1;
      float _Letter_Row02_Col38_Byte1;
      float _Letter_Row02_Col39_Byte1;
      float _Letter_Row02_Col40_Byte1;
      float _Letter_Row02_Col41_Byte1;
      float _Letter_Row02_Col42_Byte1;
      float _Letter_Row02_Col43_Byte1;
      float _Letter_Row02_Col44_Byte1;
      float _Letter_Row02_Col45_Byte1;
      float _Letter_Row02_Col46_Byte1;
      float _Letter_Row02_Col47_Byte1;
      float _Letter_Row03_Col00_Byte1;
      float _Letter_Row03_Col01_Byte1;
      float _Letter_Row03_Col02_Byte1;
      float _Letter_Row03_Col03_Byte1;
      float _Letter_Row03_Col04_Byte1;
      float _Letter_Row03_Col05_Byte1;
      float _Letter_Row03_Col06_Byte1;
      float _Letter_Row03_Col07_Byte1;
      float _Letter_Row03_Col08_Byte1;
      float _Letter_Row03_Col09_Byte1;
      float _Letter_Row03_Col10_Byte1;
      float _Letter_Row03_Col11_Byte1;
      float _Letter_Row03_Col12_Byte1;
      float _Letter_Row03_Col13_Byte1;
      float _Letter_Row03_Col14_Byte1;
      float _Letter_Row03_Col15_Byte1;
      float _Letter_Row03_Col16_Byte1;
      float _Letter_Row03_Col17_Byte1;
      float _Letter_Row03_Col18_Byte1;
      float _Letter_Row03_Col19_Byte1;
      float _Letter_Row03_Col20_Byte1;
      float _Letter_Row03_Col21_Byte1;
      float _Letter_Row03_Col22_Byte1;
      float _Letter_Row03_Col23_Byte1;
      float _Letter_Row03_Col24_Byte1;
      float _Letter_Row03_Col25_Byte1;
      float _Letter_Row03_Col26_Byte1;
      float _Letter_Row03_Col27_Byte1;
      float _Letter_Row03_Col28_Byte1;
      float _Letter_Row03_Col29_Byte1;
      float _Letter_Row03_Col30_Byte1;
      float _Letter_Row03_Col31_Byte1;
      float _Letter_Row03_Col32_Byte1;
      float _Letter_Row03_Col33_Byte1;
      float _Letter_Row03_Col34_Byte1;
      float _Letter_Row03_Col35_Byte1;
      float _Letter_Row03_Col36_Byte1;
      float _Letter_Row03_Col37_Byte1;
      float _Letter_Row03_Col38_Byte1;
      float _Letter_Row03_Col39_Byte1;
      float _Letter_Row03_Col40_Byte1;
      float _Letter_Row03_Col41_Byte1;
      float _Letter_Row03_Col42_Byte1;
      float _Letter_Row03_Col43_Byte1;
      float _Letter_Row03_Col44_Byte1;
      float _Letter_Row03_Col45_Byte1;
      float _Letter_Row03_Col46_Byte1;
      float _Letter_Row03_Col47_Byte1;

      v2f vert (appdata v)
      {
        v2f o;
        o.vertex = UnityObjectToClipPos(v.vertex);
        o.uv = 1.0 - v.uv;
        return o;
      }

      float2 AddMarginToUV(float2 uv, float2 margin)
      {
        float2 lo = float2(-margin.x / 2, -margin.y / 2);
        float2 hi = float2(1.0 + margin.x / 2, 1.0 + margin.y / 2);

        return clamp(lerp(lo, hi, uv), 0.0, 1.0);
      }

      bool InMargin(float2 uv, float2 margin)
      {
        return uv.x < margin.x / 2 ||
            uv.x > 1 - margin.x / 2 ||
            uv.y < margin.y / 2 ||
            uv.y > 1 - margin.y / 2;
      }

      // dist = sqrt(dx^2 + dy^2) = sqrt(<dx,dy> * <dx,dy>)
      bool InRadius2(float2 uv, float2 pos, float radius2)
      {
        float2 delta = uv - pos;
        return dot(delta, delta) < radius2;
      }

      // Write the nth letter in the current cell and return the value of the
      // pixel.
      // `texture_rows` and `texture_cols` indicate how many rows and columns are
      // in the texture being sampled.
      float2 GetLetter(float2 uv, int nth_letter,
          float texture_cols, float texture_rows,
          float board_cols, float board_rows)
      {
        // UV spans from [0,1] to [0,1].
        // 'U' is horizontal; cols.
        // 'V' is vertical; rows.
        //
        // I want to divide the mesh into an m x n grid.
        // I want to know what grid cell I'm in. This is simply u * m, v * n.

        // OK, I know what cell I'm in. Now I need to know how far across it I
        // am. Produce a float in the range [0, 1).
        float CHAR_FRAC_COL = uv.x * board_cols - floor(uv.x * board_cols);
        float CHAR_FRAC_ROW = uv.y * board_rows - floor(uv.y * board_rows);

        // Avoid rendering pixels right on the edge of the slot. If we were to
        // do this, then that value would get stretched due to clamping
        // (AddMarginToUV), resulting in long lines on the edge of the display.
        if (CHAR_FRAC_ROW < 0.01 ||
            CHAR_FRAC_COL < 0.01 ||
            CHAR_FRAC_ROW > 0.99 ||
            CHAR_FRAC_COL > 0.99) {
          return float2(0, 0);
        }

        float LETTER_COL = fmod(nth_letter, floor(texture_cols));
        float LETTER_ROW = floor(texture_rows) - floor(nth_letter / floor(texture_cols));

        float LETTER_UV_ROW = (LETTER_ROW + CHAR_FRAC_ROW - 1.00) / texture_rows;
        float LETTER_UV_COL = (LETTER_COL + CHAR_FRAC_COL) / texture_cols;

        float2 result;
        result.x = LETTER_UV_COL;
        result.y = LETTER_UV_ROW;

        return result;
      }

      Texture2D GetTexture(int which_letter) {
        int which_texture = (int) floor(which_letter / (64 * 64));

        [forcecase] switch (which_letter)
        {
          case 0:
            return _Font_0x0000_0x1FFF;
          case 1:
            return _Font_0x2000_0x3FFF;
          case 2:
            return _Font_0x4000_0x5FFF;
          case 3:
            return _Font_0x6000_0x7FFF;
          case 4:
            return _Font_0x8000_0x9FFF;
          case 5:
            return _Font_0xA000_0xBFFF;
          case 6:
            return _Font_0xC000_0xDFFF;
          default:
            return _Font_0x0000_0x1FFF;
        }
      }

      // Get the value of the parameter for the cell we're in.
      float2 GetLetterParameter(float2 uv)
      {
        float CHAR_ROWS = 4.0;
        float CHAR_COLS = 48.0;
        float CHAR_COL = floor(uv.x * CHAR_COLS);
        float CHAR_ROW = floor(uv.y * CHAR_ROWS);

        [forcecase] switch (CHAR_ROW)
        {
          case 3:
            [forcecase] switch (CHAR_COL) {
              case 0:
                return float2(_Letter_Row00_Col00_Byte0, _Letter_Row00_Col00_Byte1);
              case 1:
                return float2(_Letter_Row00_Col01_Byte0, _Letter_Row00_Col01_Byte1);
              case 2:
                return float2(_Letter_Row00_Col02_Byte0, _Letter_Row00_Col02_Byte1);
              case 3:
                return float2(_Letter_Row00_Col03_Byte0, _Letter_Row00_Col03_Byte1);
              case 4:
                return float2(_Letter_Row00_Col04_Byte0, _Letter_Row00_Col04_Byte1);
              case 5:
                return float2(_Letter_Row00_Col05_Byte0, _Letter_Row00_Col05_Byte1);
              case 6:
                return float2(_Letter_Row00_Col06_Byte0, _Letter_Row00_Col06_Byte1);
              case 7:
                return float2(_Letter_Row00_Col07_Byte0, _Letter_Row00_Col07_Byte1);
              case 8:
                return float2(_Letter_Row00_Col08_Byte0, _Letter_Row00_Col08_Byte1);
              case 9:
                return float2(_Letter_Row00_Col09_Byte0, _Letter_Row00_Col09_Byte1);
              case 10:
                return float2(_Letter_Row00_Col10_Byte0, _Letter_Row00_Col10_Byte1);
              case 11:
                return float2(_Letter_Row00_Col11_Byte0, _Letter_Row00_Col11_Byte1);
              case 12:
                return float2(_Letter_Row00_Col12_Byte0, _Letter_Row00_Col12_Byte1);
              case 13:
                return float2(_Letter_Row00_Col13_Byte0, _Letter_Row00_Col13_Byte1);
              case 14:
                return float2(_Letter_Row00_Col14_Byte0, _Letter_Row00_Col14_Byte1);
              case 15:
                return float2(_Letter_Row00_Col15_Byte0, _Letter_Row00_Col15_Byte1);
              case 16:
                return float2(_Letter_Row00_Col16_Byte0, _Letter_Row00_Col16_Byte1);
              case 17:
                return float2(_Letter_Row00_Col17_Byte0, _Letter_Row00_Col17_Byte1);
              case 18:
                return float2(_Letter_Row00_Col18_Byte0, _Letter_Row00_Col18_Byte1);
              case 19:
                return float2(_Letter_Row00_Col19_Byte0, _Letter_Row00_Col19_Byte1);
              case 20:
                return float2(_Letter_Row00_Col20_Byte0, _Letter_Row00_Col20_Byte1);
              case 21:
                return float2(_Letter_Row00_Col21_Byte0, _Letter_Row00_Col21_Byte1);
              case 22:
                return float2(_Letter_Row00_Col22_Byte0, _Letter_Row00_Col22_Byte1);
              case 23:
                return float2(_Letter_Row00_Col23_Byte0, _Letter_Row00_Col23_Byte1);
              case 24:
                return float2(_Letter_Row00_Col24_Byte0, _Letter_Row00_Col24_Byte1);
              case 25:
                return float2(_Letter_Row00_Col25_Byte0, _Letter_Row00_Col25_Byte1);
              case 26:
                return float2(_Letter_Row00_Col26_Byte0, _Letter_Row00_Col26_Byte1);
              case 27:
                return float2(_Letter_Row00_Col27_Byte0, _Letter_Row00_Col27_Byte1);
              case 28:
                return float2(_Letter_Row00_Col28_Byte0, _Letter_Row00_Col28_Byte1);
              case 29:
                return float2(_Letter_Row00_Col29_Byte0, _Letter_Row00_Col29_Byte1);
              case 30:
                return float2(_Letter_Row00_Col30_Byte0, _Letter_Row00_Col30_Byte1);
              case 31:
                return float2(_Letter_Row00_Col31_Byte0, _Letter_Row00_Col31_Byte1);
              case 32:
                return float2(_Letter_Row00_Col32_Byte0, _Letter_Row00_Col32_Byte1);
              case 33:
                return float2(_Letter_Row00_Col33_Byte0, _Letter_Row00_Col33_Byte1);
              case 34:
                return float2(_Letter_Row00_Col34_Byte0, _Letter_Row00_Col34_Byte1);
              case 35:
                return float2(_Letter_Row00_Col35_Byte0, _Letter_Row00_Col35_Byte1);
              case 36:
                return float2(_Letter_Row00_Col36_Byte0, _Letter_Row00_Col36_Byte1);
              case 37:
                return float2(_Letter_Row00_Col37_Byte0, _Letter_Row00_Col37_Byte1);
              case 38:
                return float2(_Letter_Row00_Col38_Byte0, _Letter_Row00_Col38_Byte1);
              case 39:
                return float2(_Letter_Row00_Col39_Byte0, _Letter_Row00_Col39_Byte1);
              case 40:
                return float2(_Letter_Row00_Col40_Byte0, _Letter_Row00_Col40_Byte1);
              case 41:
                return float2(_Letter_Row00_Col41_Byte0, _Letter_Row00_Col41_Byte1);
              case 42:
                return float2(_Letter_Row00_Col42_Byte0, _Letter_Row00_Col42_Byte1);
              case 43:
                return float2(_Letter_Row00_Col43_Byte0, _Letter_Row00_Col43_Byte1);
              case 44:
                return float2(_Letter_Row00_Col44_Byte0, _Letter_Row00_Col44_Byte1);
              case 45:
                return float2(_Letter_Row00_Col45_Byte0, _Letter_Row00_Col45_Byte1);
              case 46:
                return float2(_Letter_Row00_Col46_Byte0, _Letter_Row00_Col46_Byte1);
              case 47:
                return float2(_Letter_Row00_Col47_Byte0, _Letter_Row00_Col47_Byte1);
              default:
                return float2(0, 0);
            }
          case 2:
            [forcecase] switch (CHAR_COL) {
              case 0:
                return float2(_Letter_Row01_Col00_Byte0, _Letter_Row01_Col00_Byte1);
              case 1:
                return float2(_Letter_Row01_Col01_Byte0, _Letter_Row01_Col01_Byte1);
              case 2:
                return float2(_Letter_Row01_Col02_Byte0, _Letter_Row01_Col02_Byte1);
              case 3:
                return float2(_Letter_Row01_Col03_Byte0, _Letter_Row01_Col03_Byte1);
              case 4:
                return float2(_Letter_Row01_Col04_Byte0, _Letter_Row01_Col04_Byte1);
              case 5:
                return float2(_Letter_Row01_Col05_Byte0, _Letter_Row01_Col05_Byte1);
              case 6:
                return float2(_Letter_Row01_Col06_Byte0, _Letter_Row01_Col06_Byte1);
              case 7:
                return float2(_Letter_Row01_Col07_Byte0, _Letter_Row01_Col07_Byte1);
              case 8:
                return float2(_Letter_Row01_Col08_Byte0, _Letter_Row01_Col08_Byte1);
              case 9:
                return float2(_Letter_Row01_Col09_Byte0, _Letter_Row01_Col09_Byte1);
              case 10:
                return float2(_Letter_Row01_Col10_Byte0, _Letter_Row01_Col10_Byte1);
              case 11:
                return float2(_Letter_Row01_Col11_Byte0, _Letter_Row01_Col11_Byte1);
              case 12:
                return float2(_Letter_Row01_Col12_Byte0, _Letter_Row01_Col12_Byte1);
              case 13:
                return float2(_Letter_Row01_Col13_Byte0, _Letter_Row01_Col13_Byte1);
              case 14:
                return float2(_Letter_Row01_Col14_Byte0, _Letter_Row01_Col14_Byte1);
              case 15:
                return float2(_Letter_Row01_Col15_Byte0, _Letter_Row01_Col15_Byte1);
              case 16:
                return float2(_Letter_Row01_Col16_Byte0, _Letter_Row01_Col16_Byte1);
              case 17:
                return float2(_Letter_Row01_Col17_Byte0, _Letter_Row01_Col17_Byte1);
              case 18:
                return float2(_Letter_Row01_Col18_Byte0, _Letter_Row01_Col18_Byte1);
              case 19:
                return float2(_Letter_Row01_Col19_Byte0, _Letter_Row01_Col19_Byte1);
              case 20:
                return float2(_Letter_Row01_Col20_Byte0, _Letter_Row01_Col20_Byte1);
              case 21:
                return float2(_Letter_Row01_Col21_Byte0, _Letter_Row01_Col21_Byte1);
              case 22:
                return float2(_Letter_Row01_Col22_Byte0, _Letter_Row01_Col22_Byte1);
              case 23:
                return float2(_Letter_Row01_Col23_Byte0, _Letter_Row01_Col23_Byte1);
              case 24:
                return float2(_Letter_Row01_Col24_Byte0, _Letter_Row01_Col24_Byte1);
              case 25:
                return float2(_Letter_Row01_Col25_Byte0, _Letter_Row01_Col25_Byte1);
              case 26:
                return float2(_Letter_Row01_Col26_Byte0, _Letter_Row01_Col26_Byte1);
              case 27:
                return float2(_Letter_Row01_Col27_Byte0, _Letter_Row01_Col27_Byte1);
              case 28:
                return float2(_Letter_Row01_Col28_Byte0, _Letter_Row01_Col28_Byte1);
              case 29:
                return float2(_Letter_Row01_Col29_Byte0, _Letter_Row01_Col29_Byte1);
              case 30:
                return float2(_Letter_Row01_Col30_Byte0, _Letter_Row01_Col30_Byte1);
              case 31:
                return float2(_Letter_Row01_Col31_Byte0, _Letter_Row01_Col31_Byte1);
              case 32:
                return float2(_Letter_Row01_Col32_Byte0, _Letter_Row01_Col32_Byte1);
              case 33:
                return float2(_Letter_Row01_Col33_Byte0, _Letter_Row01_Col33_Byte1);
              case 34:
                return float2(_Letter_Row01_Col34_Byte0, _Letter_Row01_Col34_Byte1);
              case 35:
                return float2(_Letter_Row01_Col35_Byte0, _Letter_Row01_Col35_Byte1);
              case 36:
                return float2(_Letter_Row01_Col36_Byte0, _Letter_Row01_Col36_Byte1);
              case 37:
                return float2(_Letter_Row01_Col37_Byte0, _Letter_Row01_Col37_Byte1);
              case 38:
                return float2(_Letter_Row01_Col38_Byte0, _Letter_Row01_Col38_Byte1);
              case 39:
                return float2(_Letter_Row01_Col39_Byte0, _Letter_Row01_Col39_Byte1);
              case 40:
                return float2(_Letter_Row01_Col40_Byte0, _Letter_Row01_Col40_Byte1);
              case 41:
                return float2(_Letter_Row01_Col41_Byte0, _Letter_Row01_Col41_Byte1);
              case 42:
                return float2(_Letter_Row01_Col42_Byte0, _Letter_Row01_Col42_Byte1);
              case 43:
                return float2(_Letter_Row01_Col43_Byte0, _Letter_Row01_Col43_Byte1);
              case 44:
                return float2(_Letter_Row01_Col44_Byte0, _Letter_Row01_Col44_Byte1);
              case 45:
                return float2(_Letter_Row01_Col45_Byte0, _Letter_Row01_Col45_Byte1);
              case 46:
                return float2(_Letter_Row01_Col46_Byte0, _Letter_Row01_Col46_Byte1);
              case 47:
                return float2(_Letter_Row01_Col47_Byte0, _Letter_Row01_Col47_Byte1);
              default:
                return float2(0, 0);
            }
          case 1:
            [forcecase] switch (CHAR_COL) {
              case 0:
                return float2(_Letter_Row02_Col00_Byte0, _Letter_Row02_Col00_Byte1);
              case 1:
                return float2(_Letter_Row02_Col01_Byte0, _Letter_Row02_Col01_Byte1);
              case 2:
                return float2(_Letter_Row02_Col02_Byte0, _Letter_Row02_Col02_Byte1);
              case 3:
                return float2(_Letter_Row02_Col03_Byte0, _Letter_Row02_Col03_Byte1);
              case 4:
                return float2(_Letter_Row02_Col04_Byte0, _Letter_Row02_Col04_Byte1);
              case 5:
                return float2(_Letter_Row02_Col05_Byte0, _Letter_Row02_Col05_Byte1);
              case 6:
                return float2(_Letter_Row02_Col06_Byte0, _Letter_Row02_Col06_Byte1);
              case 7:
                return float2(_Letter_Row02_Col07_Byte0, _Letter_Row02_Col07_Byte1);
              case 8:
                return float2(_Letter_Row02_Col08_Byte0, _Letter_Row02_Col08_Byte1);
              case 9:
                return float2(_Letter_Row02_Col09_Byte0, _Letter_Row02_Col09_Byte1);
              case 10:
                return float2(_Letter_Row02_Col10_Byte0, _Letter_Row02_Col10_Byte1);
              case 11:
                return float2(_Letter_Row02_Col11_Byte0, _Letter_Row02_Col11_Byte1);
              case 12:
                return float2(_Letter_Row02_Col12_Byte0, _Letter_Row02_Col12_Byte1);
              case 13:
                return float2(_Letter_Row02_Col13_Byte0, _Letter_Row02_Col13_Byte1);
              case 14:
                return float2(_Letter_Row02_Col14_Byte0, _Letter_Row02_Col14_Byte1);
              case 15:
                return float2(_Letter_Row02_Col15_Byte0, _Letter_Row02_Col15_Byte1);
              case 16:
                return float2(_Letter_Row02_Col16_Byte0, _Letter_Row02_Col16_Byte1);
              case 17:
                return float2(_Letter_Row02_Col17_Byte0, _Letter_Row02_Col17_Byte1);
              case 18:
                return float2(_Letter_Row02_Col18_Byte0, _Letter_Row02_Col18_Byte1);
              case 19:
                return float2(_Letter_Row02_Col19_Byte0, _Letter_Row02_Col19_Byte1);
              case 20:
                return float2(_Letter_Row02_Col20_Byte0, _Letter_Row02_Col20_Byte1);
              case 21:
                return float2(_Letter_Row02_Col21_Byte0, _Letter_Row02_Col21_Byte1);
              case 22:
                return float2(_Letter_Row02_Col22_Byte0, _Letter_Row02_Col22_Byte1);
              case 23:
                return float2(_Letter_Row02_Col23_Byte0, _Letter_Row02_Col23_Byte1);
              case 24:
                return float2(_Letter_Row02_Col24_Byte0, _Letter_Row02_Col24_Byte1);
              case 25:
                return float2(_Letter_Row02_Col25_Byte0, _Letter_Row02_Col25_Byte1);
              case 26:
                return float2(_Letter_Row02_Col26_Byte0, _Letter_Row02_Col26_Byte1);
              case 27:
                return float2(_Letter_Row02_Col27_Byte0, _Letter_Row02_Col27_Byte1);
              case 28:
                return float2(_Letter_Row02_Col28_Byte0, _Letter_Row02_Col28_Byte1);
              case 29:
                return float2(_Letter_Row02_Col29_Byte0, _Letter_Row02_Col29_Byte1);
              case 30:
                return float2(_Letter_Row02_Col30_Byte0, _Letter_Row02_Col30_Byte1);
              case 31:
                return float2(_Letter_Row02_Col31_Byte0, _Letter_Row02_Col31_Byte1);
              case 32:
                return float2(_Letter_Row02_Col32_Byte0, _Letter_Row02_Col32_Byte1);
              case 33:
                return float2(_Letter_Row02_Col33_Byte0, _Letter_Row02_Col33_Byte1);
              case 34:
                return float2(_Letter_Row02_Col34_Byte0, _Letter_Row02_Col34_Byte1);
              case 35:
                return float2(_Letter_Row02_Col35_Byte0, _Letter_Row02_Col35_Byte1);
              case 36:
                return float2(_Letter_Row02_Col36_Byte0, _Letter_Row02_Col36_Byte1);
              case 37:
                return float2(_Letter_Row02_Col37_Byte0, _Letter_Row02_Col37_Byte1);
              case 38:
                return float2(_Letter_Row02_Col38_Byte0, _Letter_Row02_Col38_Byte1);
              case 39:
                return float2(_Letter_Row02_Col39_Byte0, _Letter_Row02_Col39_Byte1);
              case 40:
                return float2(_Letter_Row02_Col40_Byte0, _Letter_Row02_Col40_Byte1);
              case 41:
                return float2(_Letter_Row02_Col41_Byte0, _Letter_Row02_Col41_Byte1);
              case 42:
                return float2(_Letter_Row02_Col42_Byte0, _Letter_Row02_Col42_Byte1);
              case 43:
                return float2(_Letter_Row02_Col43_Byte0, _Letter_Row02_Col43_Byte1);
              case 44:
                return float2(_Letter_Row02_Col44_Byte0, _Letter_Row02_Col44_Byte1);
              case 45:
                return float2(_Letter_Row02_Col45_Byte0, _Letter_Row02_Col45_Byte1);
              case 46:
                return float2(_Letter_Row02_Col46_Byte0, _Letter_Row02_Col46_Byte1);
              case 47:
                return float2(_Letter_Row02_Col47_Byte0, _Letter_Row02_Col47_Byte1);
              default:
                return float2(0, 0);
            }
          case 0:
            [forcecase] switch (CHAR_COL) {
              case 0:
                return float2(_Letter_Row03_Col00_Byte0, _Letter_Row03_Col00_Byte1);
              case 1:
                return float2(_Letter_Row03_Col01_Byte0, _Letter_Row03_Col01_Byte1);
              case 2:
                return float2(_Letter_Row03_Col02_Byte0, _Letter_Row03_Col02_Byte1);
              case 3:
                return float2(_Letter_Row03_Col03_Byte0, _Letter_Row03_Col03_Byte1);
              case 4:
                return float2(_Letter_Row03_Col04_Byte0, _Letter_Row03_Col04_Byte1);
              case 5:
                return float2(_Letter_Row03_Col05_Byte0, _Letter_Row03_Col05_Byte1);
              case 6:
                return float2(_Letter_Row03_Col06_Byte0, _Letter_Row03_Col06_Byte1);
              case 7:
                return float2(_Letter_Row03_Col07_Byte0, _Letter_Row03_Col07_Byte1);
              case 8:
                return float2(_Letter_Row03_Col08_Byte0, _Letter_Row03_Col08_Byte1);
              case 9:
                return float2(_Letter_Row03_Col09_Byte0, _Letter_Row03_Col09_Byte1);
              case 10:
                return float2(_Letter_Row03_Col10_Byte0, _Letter_Row03_Col10_Byte1);
              case 11:
                return float2(_Letter_Row03_Col11_Byte0, _Letter_Row03_Col11_Byte1);
              case 12:
                return float2(_Letter_Row03_Col12_Byte0, _Letter_Row03_Col12_Byte1);
              case 13:
                return float2(_Letter_Row03_Col13_Byte0, _Letter_Row03_Col13_Byte1);
              case 14:
                return float2(_Letter_Row03_Col14_Byte0, _Letter_Row03_Col14_Byte1);
              case 15:
                return float2(_Letter_Row03_Col15_Byte0, _Letter_Row03_Col15_Byte1);
              case 16:
                return float2(_Letter_Row03_Col16_Byte0, _Letter_Row03_Col16_Byte1);
              case 17:
                return float2(_Letter_Row03_Col17_Byte0, _Letter_Row03_Col17_Byte1);
              case 18:
                return float2(_Letter_Row03_Col18_Byte0, _Letter_Row03_Col18_Byte1);
              case 19:
                return float2(_Letter_Row03_Col19_Byte0, _Letter_Row03_Col19_Byte1);
              case 20:
                return float2(_Letter_Row03_Col20_Byte0, _Letter_Row03_Col20_Byte1);
              case 21:
                return float2(_Letter_Row03_Col21_Byte0, _Letter_Row03_Col21_Byte1);
              case 22:
                return float2(_Letter_Row03_Col22_Byte0, _Letter_Row03_Col22_Byte1);
              case 23:
                return float2(_Letter_Row03_Col23_Byte0, _Letter_Row03_Col23_Byte1);
              case 24:
                return float2(_Letter_Row03_Col24_Byte0, _Letter_Row03_Col24_Byte1);
              case 25:
                return float2(_Letter_Row03_Col25_Byte0, _Letter_Row03_Col25_Byte1);
              case 26:
                return float2(_Letter_Row03_Col26_Byte0, _Letter_Row03_Col26_Byte1);
              case 27:
                return float2(_Letter_Row03_Col27_Byte0, _Letter_Row03_Col27_Byte1);
              case 28:
                return float2(_Letter_Row03_Col28_Byte0, _Letter_Row03_Col28_Byte1);
              case 29:
                return float2(_Letter_Row03_Col29_Byte0, _Letter_Row03_Col29_Byte1);
              case 30:
                return float2(_Letter_Row03_Col30_Byte0, _Letter_Row03_Col30_Byte1);
              case 31:
                return float2(_Letter_Row03_Col31_Byte0, _Letter_Row03_Col31_Byte1);
              case 32:
                return float2(_Letter_Row03_Col32_Byte0, _Letter_Row03_Col32_Byte1);
              case 33:
                return float2(_Letter_Row03_Col33_Byte0, _Letter_Row03_Col33_Byte1);
              case 34:
                return float2(_Letter_Row03_Col34_Byte0, _Letter_Row03_Col34_Byte1);
              case 35:
                return float2(_Letter_Row03_Col35_Byte0, _Letter_Row03_Col35_Byte1);
              case 36:
                return float2(_Letter_Row03_Col36_Byte0, _Letter_Row03_Col36_Byte1);
              case 37:
                return float2(_Letter_Row03_Col37_Byte0, _Letter_Row03_Col37_Byte1);
              case 38:
                return float2(_Letter_Row03_Col38_Byte0, _Letter_Row03_Col38_Byte1);
              case 39:
                return float2(_Letter_Row03_Col39_Byte0, _Letter_Row03_Col39_Byte1);
              case 40:
                return float2(_Letter_Row03_Col40_Byte0, _Letter_Row03_Col40_Byte1);
              case 41:
                return float2(_Letter_Row03_Col41_Byte0, _Letter_Row03_Col41_Byte1);
              case 42:
                return float2(_Letter_Row03_Col42_Byte0, _Letter_Row03_Col42_Byte1);
              case 43:
                return float2(_Letter_Row03_Col43_Byte0, _Letter_Row03_Col43_Byte1);
              case 44:
                return float2(_Letter_Row03_Col44_Byte0, _Letter_Row03_Col44_Byte1);
              case 45:
                return float2(_Letter_Row03_Col45_Byte0, _Letter_Row03_Col45_Byte1);
              case 46:
                return float2(_Letter_Row03_Col46_Byte0, _Letter_Row03_Col46_Byte1);
              case 47:
                return float2(_Letter_Row03_Col47_Byte0, _Letter_Row03_Col47_Byte1);
              default:
                return float2(0, 0);
            }
        }

        return float2(0, 0);
      }

      fixed4 frag (v2f i) : SV_Target
      {
        float2 uv = i.uv;

        // Derived from github.com/pema99/shader-knowledge (MIT license).
        if (unity_CameraProjection[2][0] != 0.0 ||
            unity_CameraProjection[2][1] != 0.0) {
          uv.x = 1.0 - uv.x;
        }

        float2 uv_margin = float2(Margin_Scale, Margin_Scale * 2);
        if (InMargin(uv, uv_margin)) {
          // Margin is uv_margin/2 wide/tall.
          // We want a circle whose radius is ~80% of that.
          if (Render_Visual_Indicator) {
            float radius_factor = 0.95;
            float radius = (uv_margin.x / 2) * radius_factor;
            // We want this circle to be centered halfway through the margin
            // vertically, and at 1.5x the margin width horizontally.
            float2 indicator_center = float2(
                uv_margin.x * 0.5 + radius,
                uv_margin.y * 0.5 * 0.5
                );
            // Finally, translate it to the top of the board instead of the
            // bottom.
            indicator_center.y = 1.0 - indicator_center.y;

            if (InRadius2(uv, indicator_center, radius * radius)) {
              if (floor(TaSTT_Indicator_0) == 1.0) {
                // Actively speaking
                return float3tofixed4(TaSTT_Indicator_Color_2, 1.0);
              } else if (floor(TaSTT_Indicator_1) == 1.0) {
                // Done speaking, waiting for paging.
                return float3tofixed4(TaSTT_Indicator_Color_1, 1.0);
              } else {
                // Neither speaking nor paging.
                return float3tofixed4(TaSTT_Indicator_Color_0, 1.0);
              }
            }
          }
          if (Render_Margin) {
            return fixed4(1,1,1,1);
          }
        }

        float2 uv_with_margin = AddMarginToUV(uv, uv_margin);
        uv_margin *= 2;
        float2 uv_with_margin2 = AddMarginToUV(uv, uv_margin);

        int2 letter_bytes = (int2) floor(GetLetterParameter(uv_with_margin2));
        int letter = letter_bytes[0] | (letter_bytes[1] << 8);

        float texture_cols;
        float texture_rows;
        float2 letter_uv;
        if (letter < 0xE000) {
          texture_cols = 128.0;
          texture_rows = 64.0;
          letter_uv = GetLetter(uv_with_margin2, letter, texture_cols, texture_rows, 48, 4);
        } else {
          texture_cols = 8.0;
          texture_rows = 8.0;
          letter_uv = GetLetter(uv_with_margin2, letter, texture_cols, texture_rows, 8, 4);
        }

        fixed4 background = TaSTT_Backplate.Sample(sampler_linear_repeat, uv);
        fixed4 text;

        int which_texture = (int) floor(letter / (64 * 128));
        [forcecase] switch (which_texture)
        {
          case 0:
            text = _Font_0x0000_0x1FFF.Sample(sampler_linear_repeat, letter_uv);
            break;
          case 1:
            text = _Font_0x2000_0x3FFF.Sample(sampler_linear_repeat, letter_uv);
            break;
          case 2:
            text = _Font_0x4000_0x5FFF.Sample(sampler_linear_repeat, letter_uv);
            break;
          case 3:
            text = _Font_0x6000_0x7FFF.Sample(sampler_linear_repeat, letter_uv);
            break;
          case 4:
            text = _Font_0x8000_0x9FFF.Sample(sampler_linear_repeat, letter_uv);
            break;
          case 5:
            text = _Font_0xA000_0xBFFF.Sample(sampler_linear_repeat, letter_uv);
            break;
          case 6:
            text = _Font_0xC000_0xDFFF.Sample(sampler_linear_repeat, letter_uv);
            break;
          default:
            text = _Img_0xE000_0xE03F.Sample(sampler_linear_repeat, letter_uv);
            break;
        }
        fixed4 black = fixed4(0,0,0,1);
        if (text.r == black.r && text.g == black.g && text.b == black.b && text.a == black.a) {
          return background;
        } else {
          return text;
        }
      }
      ENDCG
    }
  }
}
