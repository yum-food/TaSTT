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
    Margin_Rounding_Scale("Margin rounding scale", float) = 0.03

    TaSTT_Backplate("TaSTT_Backplate", 2D) = "black" {}
    TaSTT_Indicator_0("TaSTT_Indicator_0", float) = 0
    TaSTT_Indicator_1("TaSTT_Indicator_1", float) = 0

    // BEGIN GENERATED CODE BLOCK
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
    // END GENERATED CODE BLOCK
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

      //#include "UnityCG.cginc"

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
      float Margin_Rounding_Scale;

      // BEGIN GENERATED CODE BLOCK
      #define BYTES_PER_CHAR 2
      #define NROWS 4
      #define NCOLS 48
      // END GENERATED CODE BLOCK

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

      // BEGIN GENERATED CODE BLOCK
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
      // END GENERATED CODE BLOCK

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

      // dist = sqrt(dx^2 + dy^2) = sqrt(<dx,dy> * <dx,dy>)
      bool InRadius2(float2 uv, float2 pos, float radius2)
      {
        float2 delta = uv - pos;
        return dot(delta, delta) < radius2;
      }

      bool InMargin(float2 uv, float2 margin)
      {
        if (uv.x < margin.x ||
            uv.x > 1 - margin.x ||
            uv.y < margin.y ||
            uv.y > 1 - margin.y) {
            return true;
        }

        return false;
      }

      bool InSpeechIndicator(float2 uv, float2 margin)
      {
        if (!Render_Visual_Indicator) {
          return false;
        }

        // Margin is uv_margin/2 wide/tall.
        // We want a circle whose radius is ~80% of that.
        float radius_factor = 0.95;
        float radius = margin.x * radius_factor;
        // We want this circle to be centered halfway through the margin
        // vertically, and at 1.5x the margin width horizontally.
        float2 indicator_center = float2(margin.x + radius, margin.y * 0.5);
        // Finally, translate it to the top of the board instead of the
        // bottom.
        indicator_center.y = 1.0 - indicator_center.y;

        if (InRadius2(uv, indicator_center, radius * radius)) {
          return true;
        }

        return false;
      }

      bool InMarginRounding(float2 uv, float2 margin, float rounding, bool interior)
      {
        if (!interior) {
          rounding += margin.x;
          margin = float2(0, 0);
        }

        // This is the center of a circle whose perimeter touches the
        // upper left corner of the margin.
        float2 c0 = float2(rounding + margin.x, rounding + margin.y);
        if (uv.x < c0.x && uv.y < c0.y && uv.x > margin.x && uv.y > margin.y && !InRadius2(uv, c0, rounding * rounding)) {
            return true;
        }
        c0 = float2(rounding + margin.x, 1 - (rounding + margin.y));
        if (uv.x < c0.x && uv.y > c0.y && uv.x > margin.x && uv.y < 1 - margin.y && !InRadius2(uv, c0, rounding * rounding)) {
            return true;
        }
        c0 = float2(1 - (rounding + margin.x), 1 - (rounding + margin.y));
        if (uv.x > c0.x && uv.y > c0.y && uv.x < 1 - margin.x && uv.y < 1 - margin.y && !InRadius2(uv, c0, rounding * rounding)) {
            return true;
        }
        c0 = float2(1 - (rounding + margin.x), rounding + margin.y);
        if (uv.x > c0.x && uv.y < c0.y && uv.x < 1 - margin.x && uv.y > margin.y && !InRadius2(uv, c0, rounding * rounding)) {
            return true;
        }

        return false;
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
      int GetLetterParameter(float2 uv)
      {
        float CHAR_COL = floor(uv.x * NCOLS);
        float CHAR_ROW = floor(uv.y * NROWS);
        int res = 0;

          // BEGIN GENERATED CODE BLOCK
          [forcecase] switch (CHAR_ROW) {
            case 3:
              [forcecase] switch (CHAR_COL) {
                case 0:
                  res |= ((int) _Letter_Row00_Col00_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col00_Byte1) << (1 * 8);
                  return res;
                case 1:
                  res |= ((int) _Letter_Row00_Col01_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col01_Byte1) << (1 * 8);
                  return res;
                case 2:
                  res |= ((int) _Letter_Row00_Col02_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col02_Byte1) << (1 * 8);
                  return res;
                case 3:
                  res |= ((int) _Letter_Row00_Col03_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col03_Byte1) << (1 * 8);
                  return res;
                case 4:
                  res |= ((int) _Letter_Row00_Col04_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col04_Byte1) << (1 * 8);
                  return res;
                case 5:
                  res |= ((int) _Letter_Row00_Col05_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col05_Byte1) << (1 * 8);
                  return res;
                case 6:
                  res |= ((int) _Letter_Row00_Col06_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col06_Byte1) << (1 * 8);
                  return res;
                case 7:
                  res |= ((int) _Letter_Row00_Col07_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col07_Byte1) << (1 * 8);
                  return res;
                case 8:
                  res |= ((int) _Letter_Row00_Col08_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col08_Byte1) << (1 * 8);
                  return res;
                case 9:
                  res |= ((int) _Letter_Row00_Col09_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col09_Byte1) << (1 * 8);
                  return res;
                case 10:
                  res |= ((int) _Letter_Row00_Col10_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col10_Byte1) << (1 * 8);
                  return res;
                case 11:
                  res |= ((int) _Letter_Row00_Col11_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col11_Byte1) << (1 * 8);
                  return res;
                case 12:
                  res |= ((int) _Letter_Row00_Col12_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col12_Byte1) << (1 * 8);
                  return res;
                case 13:
                  res |= ((int) _Letter_Row00_Col13_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col13_Byte1) << (1 * 8);
                  return res;
                case 14:
                  res |= ((int) _Letter_Row00_Col14_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col14_Byte1) << (1 * 8);
                  return res;
                case 15:
                  res |= ((int) _Letter_Row00_Col15_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col15_Byte1) << (1 * 8);
                  return res;
                case 16:
                  res |= ((int) _Letter_Row00_Col16_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col16_Byte1) << (1 * 8);
                  return res;
                case 17:
                  res |= ((int) _Letter_Row00_Col17_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col17_Byte1) << (1 * 8);
                  return res;
                case 18:
                  res |= ((int) _Letter_Row00_Col18_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col18_Byte1) << (1 * 8);
                  return res;
                case 19:
                  res |= ((int) _Letter_Row00_Col19_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col19_Byte1) << (1 * 8);
                  return res;
                case 20:
                  res |= ((int) _Letter_Row00_Col20_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col20_Byte1) << (1 * 8);
                  return res;
                case 21:
                  res |= ((int) _Letter_Row00_Col21_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col21_Byte1) << (1 * 8);
                  return res;
                case 22:
                  res |= ((int) _Letter_Row00_Col22_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col22_Byte1) << (1 * 8);
                  return res;
                case 23:
                  res |= ((int) _Letter_Row00_Col23_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col23_Byte1) << (1 * 8);
                  return res;
                case 24:
                  res |= ((int) _Letter_Row00_Col24_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col24_Byte1) << (1 * 8);
                  return res;
                case 25:
                  res |= ((int) _Letter_Row00_Col25_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col25_Byte1) << (1 * 8);
                  return res;
                case 26:
                  res |= ((int) _Letter_Row00_Col26_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col26_Byte1) << (1 * 8);
                  return res;
                case 27:
                  res |= ((int) _Letter_Row00_Col27_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col27_Byte1) << (1 * 8);
                  return res;
                case 28:
                  res |= ((int) _Letter_Row00_Col28_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col28_Byte1) << (1 * 8);
                  return res;
                case 29:
                  res |= ((int) _Letter_Row00_Col29_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col29_Byte1) << (1 * 8);
                  return res;
                case 30:
                  res |= ((int) _Letter_Row00_Col30_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col30_Byte1) << (1 * 8);
                  return res;
                case 31:
                  res |= ((int) _Letter_Row00_Col31_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col31_Byte1) << (1 * 8);
                  return res;
                case 32:
                  res |= ((int) _Letter_Row00_Col32_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col32_Byte1) << (1 * 8);
                  return res;
                case 33:
                  res |= ((int) _Letter_Row00_Col33_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col33_Byte1) << (1 * 8);
                  return res;
                case 34:
                  res |= ((int) _Letter_Row00_Col34_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col34_Byte1) << (1 * 8);
                  return res;
                case 35:
                  res |= ((int) _Letter_Row00_Col35_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col35_Byte1) << (1 * 8);
                  return res;
                case 36:
                  res |= ((int) _Letter_Row00_Col36_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col36_Byte1) << (1 * 8);
                  return res;
                case 37:
                  res |= ((int) _Letter_Row00_Col37_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col37_Byte1) << (1 * 8);
                  return res;
                case 38:
                  res |= ((int) _Letter_Row00_Col38_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col38_Byte1) << (1 * 8);
                  return res;
                case 39:
                  res |= ((int) _Letter_Row00_Col39_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col39_Byte1) << (1 * 8);
                  return res;
                case 40:
                  res |= ((int) _Letter_Row00_Col40_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col40_Byte1) << (1 * 8);
                  return res;
                case 41:
                  res |= ((int) _Letter_Row00_Col41_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col41_Byte1) << (1 * 8);
                  return res;
                case 42:
                  res |= ((int) _Letter_Row00_Col42_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col42_Byte1) << (1 * 8);
                  return res;
                case 43:
                  res |= ((int) _Letter_Row00_Col43_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col43_Byte1) << (1 * 8);
                  return res;
                case 44:
                  res |= ((int) _Letter_Row00_Col44_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col44_Byte1) << (1 * 8);
                  return res;
                case 45:
                  res |= ((int) _Letter_Row00_Col45_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col45_Byte1) << (1 * 8);
                  return res;
                case 46:
                  res |= ((int) _Letter_Row00_Col46_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col46_Byte1) << (1 * 8);
                  return res;
                case 47:
                  res |= ((int) _Letter_Row00_Col47_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row00_Col47_Byte1) << (1 * 8);
                  return res;
                default:
                  return 0;
              }
            case 2:
              [forcecase] switch (CHAR_COL) {
                case 0:
                  res |= ((int) _Letter_Row01_Col00_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col00_Byte1) << (1 * 8);
                  return res;
                case 1:
                  res |= ((int) _Letter_Row01_Col01_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col01_Byte1) << (1 * 8);
                  return res;
                case 2:
                  res |= ((int) _Letter_Row01_Col02_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col02_Byte1) << (1 * 8);
                  return res;
                case 3:
                  res |= ((int) _Letter_Row01_Col03_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col03_Byte1) << (1 * 8);
                  return res;
                case 4:
                  res |= ((int) _Letter_Row01_Col04_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col04_Byte1) << (1 * 8);
                  return res;
                case 5:
                  res |= ((int) _Letter_Row01_Col05_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col05_Byte1) << (1 * 8);
                  return res;
                case 6:
                  res |= ((int) _Letter_Row01_Col06_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col06_Byte1) << (1 * 8);
                  return res;
                case 7:
                  res |= ((int) _Letter_Row01_Col07_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col07_Byte1) << (1 * 8);
                  return res;
                case 8:
                  res |= ((int) _Letter_Row01_Col08_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col08_Byte1) << (1 * 8);
                  return res;
                case 9:
                  res |= ((int) _Letter_Row01_Col09_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col09_Byte1) << (1 * 8);
                  return res;
                case 10:
                  res |= ((int) _Letter_Row01_Col10_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col10_Byte1) << (1 * 8);
                  return res;
                case 11:
                  res |= ((int) _Letter_Row01_Col11_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col11_Byte1) << (1 * 8);
                  return res;
                case 12:
                  res |= ((int) _Letter_Row01_Col12_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col12_Byte1) << (1 * 8);
                  return res;
                case 13:
                  res |= ((int) _Letter_Row01_Col13_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col13_Byte1) << (1 * 8);
                  return res;
                case 14:
                  res |= ((int) _Letter_Row01_Col14_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col14_Byte1) << (1 * 8);
                  return res;
                case 15:
                  res |= ((int) _Letter_Row01_Col15_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col15_Byte1) << (1 * 8);
                  return res;
                case 16:
                  res |= ((int) _Letter_Row01_Col16_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col16_Byte1) << (1 * 8);
                  return res;
                case 17:
                  res |= ((int) _Letter_Row01_Col17_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col17_Byte1) << (1 * 8);
                  return res;
                case 18:
                  res |= ((int) _Letter_Row01_Col18_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col18_Byte1) << (1 * 8);
                  return res;
                case 19:
                  res |= ((int) _Letter_Row01_Col19_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col19_Byte1) << (1 * 8);
                  return res;
                case 20:
                  res |= ((int) _Letter_Row01_Col20_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col20_Byte1) << (1 * 8);
                  return res;
                case 21:
                  res |= ((int) _Letter_Row01_Col21_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col21_Byte1) << (1 * 8);
                  return res;
                case 22:
                  res |= ((int) _Letter_Row01_Col22_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col22_Byte1) << (1 * 8);
                  return res;
                case 23:
                  res |= ((int) _Letter_Row01_Col23_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col23_Byte1) << (1 * 8);
                  return res;
                case 24:
                  res |= ((int) _Letter_Row01_Col24_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col24_Byte1) << (1 * 8);
                  return res;
                case 25:
                  res |= ((int) _Letter_Row01_Col25_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col25_Byte1) << (1 * 8);
                  return res;
                case 26:
                  res |= ((int) _Letter_Row01_Col26_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col26_Byte1) << (1 * 8);
                  return res;
                case 27:
                  res |= ((int) _Letter_Row01_Col27_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col27_Byte1) << (1 * 8);
                  return res;
                case 28:
                  res |= ((int) _Letter_Row01_Col28_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col28_Byte1) << (1 * 8);
                  return res;
                case 29:
                  res |= ((int) _Letter_Row01_Col29_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col29_Byte1) << (1 * 8);
                  return res;
                case 30:
                  res |= ((int) _Letter_Row01_Col30_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col30_Byte1) << (1 * 8);
                  return res;
                case 31:
                  res |= ((int) _Letter_Row01_Col31_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col31_Byte1) << (1 * 8);
                  return res;
                case 32:
                  res |= ((int) _Letter_Row01_Col32_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col32_Byte1) << (1 * 8);
                  return res;
                case 33:
                  res |= ((int) _Letter_Row01_Col33_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col33_Byte1) << (1 * 8);
                  return res;
                case 34:
                  res |= ((int) _Letter_Row01_Col34_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col34_Byte1) << (1 * 8);
                  return res;
                case 35:
                  res |= ((int) _Letter_Row01_Col35_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col35_Byte1) << (1 * 8);
                  return res;
                case 36:
                  res |= ((int) _Letter_Row01_Col36_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col36_Byte1) << (1 * 8);
                  return res;
                case 37:
                  res |= ((int) _Letter_Row01_Col37_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col37_Byte1) << (1 * 8);
                  return res;
                case 38:
                  res |= ((int) _Letter_Row01_Col38_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col38_Byte1) << (1 * 8);
                  return res;
                case 39:
                  res |= ((int) _Letter_Row01_Col39_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col39_Byte1) << (1 * 8);
                  return res;
                case 40:
                  res |= ((int) _Letter_Row01_Col40_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col40_Byte1) << (1 * 8);
                  return res;
                case 41:
                  res |= ((int) _Letter_Row01_Col41_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col41_Byte1) << (1 * 8);
                  return res;
                case 42:
                  res |= ((int) _Letter_Row01_Col42_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col42_Byte1) << (1 * 8);
                  return res;
                case 43:
                  res |= ((int) _Letter_Row01_Col43_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col43_Byte1) << (1 * 8);
                  return res;
                case 44:
                  res |= ((int) _Letter_Row01_Col44_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col44_Byte1) << (1 * 8);
                  return res;
                case 45:
                  res |= ((int) _Letter_Row01_Col45_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col45_Byte1) << (1 * 8);
                  return res;
                case 46:
                  res |= ((int) _Letter_Row01_Col46_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col46_Byte1) << (1 * 8);
                  return res;
                case 47:
                  res |= ((int) _Letter_Row01_Col47_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row01_Col47_Byte1) << (1 * 8);
                  return res;
                default:
                  return 0;
              }
            case 1:
              [forcecase] switch (CHAR_COL) {
                case 0:
                  res |= ((int) _Letter_Row02_Col00_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col00_Byte1) << (1 * 8);
                  return res;
                case 1:
                  res |= ((int) _Letter_Row02_Col01_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col01_Byte1) << (1 * 8);
                  return res;
                case 2:
                  res |= ((int) _Letter_Row02_Col02_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col02_Byte1) << (1 * 8);
                  return res;
                case 3:
                  res |= ((int) _Letter_Row02_Col03_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col03_Byte1) << (1 * 8);
                  return res;
                case 4:
                  res |= ((int) _Letter_Row02_Col04_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col04_Byte1) << (1 * 8);
                  return res;
                case 5:
                  res |= ((int) _Letter_Row02_Col05_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col05_Byte1) << (1 * 8);
                  return res;
                case 6:
                  res |= ((int) _Letter_Row02_Col06_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col06_Byte1) << (1 * 8);
                  return res;
                case 7:
                  res |= ((int) _Letter_Row02_Col07_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col07_Byte1) << (1 * 8);
                  return res;
                case 8:
                  res |= ((int) _Letter_Row02_Col08_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col08_Byte1) << (1 * 8);
                  return res;
                case 9:
                  res |= ((int) _Letter_Row02_Col09_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col09_Byte1) << (1 * 8);
                  return res;
                case 10:
                  res |= ((int) _Letter_Row02_Col10_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col10_Byte1) << (1 * 8);
                  return res;
                case 11:
                  res |= ((int) _Letter_Row02_Col11_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col11_Byte1) << (1 * 8);
                  return res;
                case 12:
                  res |= ((int) _Letter_Row02_Col12_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col12_Byte1) << (1 * 8);
                  return res;
                case 13:
                  res |= ((int) _Letter_Row02_Col13_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col13_Byte1) << (1 * 8);
                  return res;
                case 14:
                  res |= ((int) _Letter_Row02_Col14_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col14_Byte1) << (1 * 8);
                  return res;
                case 15:
                  res |= ((int) _Letter_Row02_Col15_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col15_Byte1) << (1 * 8);
                  return res;
                case 16:
                  res |= ((int) _Letter_Row02_Col16_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col16_Byte1) << (1 * 8);
                  return res;
                case 17:
                  res |= ((int) _Letter_Row02_Col17_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col17_Byte1) << (1 * 8);
                  return res;
                case 18:
                  res |= ((int) _Letter_Row02_Col18_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col18_Byte1) << (1 * 8);
                  return res;
                case 19:
                  res |= ((int) _Letter_Row02_Col19_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col19_Byte1) << (1 * 8);
                  return res;
                case 20:
                  res |= ((int) _Letter_Row02_Col20_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col20_Byte1) << (1 * 8);
                  return res;
                case 21:
                  res |= ((int) _Letter_Row02_Col21_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col21_Byte1) << (1 * 8);
                  return res;
                case 22:
                  res |= ((int) _Letter_Row02_Col22_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col22_Byte1) << (1 * 8);
                  return res;
                case 23:
                  res |= ((int) _Letter_Row02_Col23_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col23_Byte1) << (1 * 8);
                  return res;
                case 24:
                  res |= ((int) _Letter_Row02_Col24_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col24_Byte1) << (1 * 8);
                  return res;
                case 25:
                  res |= ((int) _Letter_Row02_Col25_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col25_Byte1) << (1 * 8);
                  return res;
                case 26:
                  res |= ((int) _Letter_Row02_Col26_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col26_Byte1) << (1 * 8);
                  return res;
                case 27:
                  res |= ((int) _Letter_Row02_Col27_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col27_Byte1) << (1 * 8);
                  return res;
                case 28:
                  res |= ((int) _Letter_Row02_Col28_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col28_Byte1) << (1 * 8);
                  return res;
                case 29:
                  res |= ((int) _Letter_Row02_Col29_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col29_Byte1) << (1 * 8);
                  return res;
                case 30:
                  res |= ((int) _Letter_Row02_Col30_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col30_Byte1) << (1 * 8);
                  return res;
                case 31:
                  res |= ((int) _Letter_Row02_Col31_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col31_Byte1) << (1 * 8);
                  return res;
                case 32:
                  res |= ((int) _Letter_Row02_Col32_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col32_Byte1) << (1 * 8);
                  return res;
                case 33:
                  res |= ((int) _Letter_Row02_Col33_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col33_Byte1) << (1 * 8);
                  return res;
                case 34:
                  res |= ((int) _Letter_Row02_Col34_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col34_Byte1) << (1 * 8);
                  return res;
                case 35:
                  res |= ((int) _Letter_Row02_Col35_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col35_Byte1) << (1 * 8);
                  return res;
                case 36:
                  res |= ((int) _Letter_Row02_Col36_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col36_Byte1) << (1 * 8);
                  return res;
                case 37:
                  res |= ((int) _Letter_Row02_Col37_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col37_Byte1) << (1 * 8);
                  return res;
                case 38:
                  res |= ((int) _Letter_Row02_Col38_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col38_Byte1) << (1 * 8);
                  return res;
                case 39:
                  res |= ((int) _Letter_Row02_Col39_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col39_Byte1) << (1 * 8);
                  return res;
                case 40:
                  res |= ((int) _Letter_Row02_Col40_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col40_Byte1) << (1 * 8);
                  return res;
                case 41:
                  res |= ((int) _Letter_Row02_Col41_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col41_Byte1) << (1 * 8);
                  return res;
                case 42:
                  res |= ((int) _Letter_Row02_Col42_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col42_Byte1) << (1 * 8);
                  return res;
                case 43:
                  res |= ((int) _Letter_Row02_Col43_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col43_Byte1) << (1 * 8);
                  return res;
                case 44:
                  res |= ((int) _Letter_Row02_Col44_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col44_Byte1) << (1 * 8);
                  return res;
                case 45:
                  res |= ((int) _Letter_Row02_Col45_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col45_Byte1) << (1 * 8);
                  return res;
                case 46:
                  res |= ((int) _Letter_Row02_Col46_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col46_Byte1) << (1 * 8);
                  return res;
                case 47:
                  res |= ((int) _Letter_Row02_Col47_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row02_Col47_Byte1) << (1 * 8);
                  return res;
                default:
                  return 0;
              }
            case 0:
              [forcecase] switch (CHAR_COL) {
                case 0:
                  res |= ((int) _Letter_Row03_Col00_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col00_Byte1) << (1 * 8);
                  return res;
                case 1:
                  res |= ((int) _Letter_Row03_Col01_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col01_Byte1) << (1 * 8);
                  return res;
                case 2:
                  res |= ((int) _Letter_Row03_Col02_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col02_Byte1) << (1 * 8);
                  return res;
                case 3:
                  res |= ((int) _Letter_Row03_Col03_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col03_Byte1) << (1 * 8);
                  return res;
                case 4:
                  res |= ((int) _Letter_Row03_Col04_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col04_Byte1) << (1 * 8);
                  return res;
                case 5:
                  res |= ((int) _Letter_Row03_Col05_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col05_Byte1) << (1 * 8);
                  return res;
                case 6:
                  res |= ((int) _Letter_Row03_Col06_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col06_Byte1) << (1 * 8);
                  return res;
                case 7:
                  res |= ((int) _Letter_Row03_Col07_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col07_Byte1) << (1 * 8);
                  return res;
                case 8:
                  res |= ((int) _Letter_Row03_Col08_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col08_Byte1) << (1 * 8);
                  return res;
                case 9:
                  res |= ((int) _Letter_Row03_Col09_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col09_Byte1) << (1 * 8);
                  return res;
                case 10:
                  res |= ((int) _Letter_Row03_Col10_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col10_Byte1) << (1 * 8);
                  return res;
                case 11:
                  res |= ((int) _Letter_Row03_Col11_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col11_Byte1) << (1 * 8);
                  return res;
                case 12:
                  res |= ((int) _Letter_Row03_Col12_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col12_Byte1) << (1 * 8);
                  return res;
                case 13:
                  res |= ((int) _Letter_Row03_Col13_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col13_Byte1) << (1 * 8);
                  return res;
                case 14:
                  res |= ((int) _Letter_Row03_Col14_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col14_Byte1) << (1 * 8);
                  return res;
                case 15:
                  res |= ((int) _Letter_Row03_Col15_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col15_Byte1) << (1 * 8);
                  return res;
                case 16:
                  res |= ((int) _Letter_Row03_Col16_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col16_Byte1) << (1 * 8);
                  return res;
                case 17:
                  res |= ((int) _Letter_Row03_Col17_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col17_Byte1) << (1 * 8);
                  return res;
                case 18:
                  res |= ((int) _Letter_Row03_Col18_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col18_Byte1) << (1 * 8);
                  return res;
                case 19:
                  res |= ((int) _Letter_Row03_Col19_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col19_Byte1) << (1 * 8);
                  return res;
                case 20:
                  res |= ((int) _Letter_Row03_Col20_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col20_Byte1) << (1 * 8);
                  return res;
                case 21:
                  res |= ((int) _Letter_Row03_Col21_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col21_Byte1) << (1 * 8);
                  return res;
                case 22:
                  res |= ((int) _Letter_Row03_Col22_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col22_Byte1) << (1 * 8);
                  return res;
                case 23:
                  res |= ((int) _Letter_Row03_Col23_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col23_Byte1) << (1 * 8);
                  return res;
                case 24:
                  res |= ((int) _Letter_Row03_Col24_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col24_Byte1) << (1 * 8);
                  return res;
                case 25:
                  res |= ((int) _Letter_Row03_Col25_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col25_Byte1) << (1 * 8);
                  return res;
                case 26:
                  res |= ((int) _Letter_Row03_Col26_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col26_Byte1) << (1 * 8);
                  return res;
                case 27:
                  res |= ((int) _Letter_Row03_Col27_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col27_Byte1) << (1 * 8);
                  return res;
                case 28:
                  res |= ((int) _Letter_Row03_Col28_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col28_Byte1) << (1 * 8);
                  return res;
                case 29:
                  res |= ((int) _Letter_Row03_Col29_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col29_Byte1) << (1 * 8);
                  return res;
                case 30:
                  res |= ((int) _Letter_Row03_Col30_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col30_Byte1) << (1 * 8);
                  return res;
                case 31:
                  res |= ((int) _Letter_Row03_Col31_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col31_Byte1) << (1 * 8);
                  return res;
                case 32:
                  res |= ((int) _Letter_Row03_Col32_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col32_Byte1) << (1 * 8);
                  return res;
                case 33:
                  res |= ((int) _Letter_Row03_Col33_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col33_Byte1) << (1 * 8);
                  return res;
                case 34:
                  res |= ((int) _Letter_Row03_Col34_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col34_Byte1) << (1 * 8);
                  return res;
                case 35:
                  res |= ((int) _Letter_Row03_Col35_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col35_Byte1) << (1 * 8);
                  return res;
                case 36:
                  res |= ((int) _Letter_Row03_Col36_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col36_Byte1) << (1 * 8);
                  return res;
                case 37:
                  res |= ((int) _Letter_Row03_Col37_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col37_Byte1) << (1 * 8);
                  return res;
                case 38:
                  res |= ((int) _Letter_Row03_Col38_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col38_Byte1) << (1 * 8);
                  return res;
                case 39:
                  res |= ((int) _Letter_Row03_Col39_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col39_Byte1) << (1 * 8);
                  return res;
                case 40:
                  res |= ((int) _Letter_Row03_Col40_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col40_Byte1) << (1 * 8);
                  return res;
                case 41:
                  res |= ((int) _Letter_Row03_Col41_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col41_Byte1) << (1 * 8);
                  return res;
                case 42:
                  res |= ((int) _Letter_Row03_Col42_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col42_Byte1) << (1 * 8);
                  return res;
                case 43:
                  res |= ((int) _Letter_Row03_Col43_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col43_Byte1) << (1 * 8);
                  return res;
                case 44:
                  res |= ((int) _Letter_Row03_Col44_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col44_Byte1) << (1 * 8);
                  return res;
                case 45:
                  res |= ((int) _Letter_Row03_Col45_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col45_Byte1) << (1 * 8);
                  return res;
                case 46:
                  res |= ((int) _Letter_Row03_Col46_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col46_Byte1) << (1 * 8);
                  return res;
                case 47:
                  res |= ((int) _Letter_Row03_Col47_Byte0) << (0 * 8);
                  res |= ((int) _Letter_Row03_Col47_Byte1) << (1 * 8);
                  return res;
                default:
                  return 0;
              }
          }
          // END GENERATED CODE BLOCK
        return res;
      }

      fixed sq_dist(fixed2 p0, fixed2 p1)
      {
        fixed2 delta = p1 - p0;
        //return abs(delta.x) + abs(delta.y);
        return max(abs(delta.x), abs(delta.y));
      }

      fixed4 effect_squares (v2f i)
      {
        const fixed time = _Time.y;

        #define PI 3.1415926535
        fixed theta = PI/4 + sin(time / 4) * 0.1;
        fixed2x2 rot =
          fixed2x2(cos(theta), -1 * sin(theta),
          sin(theta), cos(theta));

        #define NSQ_X 9.0
        #define NSQ_Y 5.0

        // Map uv from [0, 1] to [-.5, .5].
        fixed2 p = i.uv - 0.5;
        p *= fixed2(NSQ_X, NSQ_Y);
        p = mul(rot, p);
        p -= 0.5;

        // See how far we are from the nearest grid point
        fixed2 intra_pos = frac(p);
        fixed2 intra_center = fixed2(0.5, 0.5);
        fixed intra_dist = sq_dist(intra_pos, intra_center);

        fixed st0 = (sin(time) + 1) / 2;
        fixed st1 = (sin(time + PI/8) + 1) / 2;
        fixed st2 = (sin(time + PI/2) + 1) / 2;
        fixed st3 = (sin(time + PI/2 + PI/8) + 1) / 2;

        fixed2 center = fixed2(0, 0);
        center = mul(rot, center);
        center -= 0.5;
        fixed2 rot_lim = fixed2(NSQ_X, NSQ_Y);
        rot_lim = mul(rot, rot_lim);
        rot_lim -= 0.5;

        float v = 0;
        float x = 0;

        if (intra_dist > 0.5 * (0.5 + sin(time * 1.5) * 0.1)) {
          v = intra_dist;
        } else {
          v = 0;
        }

        fixed extra_dist = sq_dist(p, center);
        fixed check = max(rot_lim.x, rot_lim.y) / 2;
        if (extra_dist > check * st0) {
          v = 1.0 - v;
        }
        if (extra_dist > check * st1) {
          v = 1.0 - v;
        }
        if (extra_dist > check * st2) {
          v = 1.0 - v;
        }
        if (extra_dist > check * st3) {
          v = 1.0 - v;
        } else {
          x = 0.50;
        }

        fixed3 hsv;
        hsv[0] = (v * 0.2 * (1 - x * .8) + 0.55) - x;
        hsv[1] = 0.7;
        hsv[2] = 0.8;

        fixed3 col = HSVtoRGB(hsv);

        return fixed4(col, 1.0);
      }

      fixed4 frag (v2f i) : SV_Target
      {
        float2 uv = i.uv;

        // Derived from github.com/pema99/shader-knowledge (MIT license).
        if (unity_CameraProjection[2][0] != 0.0 ||
            unity_CameraProjection[2][1] != 0.0) {
          uv.x = 1.0 - uv.x;
        }

        float2 uv_margin = float2(Margin_Scale, Margin_Scale * 2) / 2;
        if (Render_Margin) {
          if (Margin_Rounding_Scale > 0.0) {
            if (InMarginRounding(uv, uv_margin, Margin_Rounding_Scale, /*interior=*/true)) {
              return effect_squares(i);
            }
            if (InMarginRounding(uv, uv_margin, Margin_Rounding_Scale, /*interior=*/false)) {
              return fixed4(0, 0, 0, 0);
            }
          }
          if (InMargin(uv, uv_margin)) {
            if (InSpeechIndicator(uv, uv_margin)) {
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

            if (Render_Margin) {
              return effect_squares(i);
            }
          }
        }

        uv_margin *= 4;
        float2 uv_with_margin = AddMarginToUV(uv, uv_margin);

        int letter = GetLetterParameter(uv_with_margin);

        float texture_cols;
        float texture_rows;
        float2 letter_uv;
        if (letter < 0xE000) {
          texture_cols = 128.0;
          texture_rows = 64.0;
          letter_uv = GetLetter(uv_with_margin, letter, texture_cols, texture_rows, NCOLS, NROWS);
        } else {
          texture_cols = 8.0;
          texture_rows = 8.0;
          letter_uv = GetLetter(uv_with_margin, letter, texture_cols, texture_rows, 8, 4);
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