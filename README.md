## TaSTT: A deliciously free STT

TaSTT (pronounced "tasty") is a free speech-to-text tool for VRChat. It uses
local machine translation to turn your voice into text, then sends it into
VRChat via OSC. A few parameters, a machine-generated FX layer, and a
custom shader display the text in game.

Features:
* Free as in beer.
* Free as in freedom.
* Privacy respecting. Speech-to-text done locally using an open source language
  model.
* Low-latency.
* Stable.
* Configurable.
* 6x14 display grid, 80 characters per slot.
  * Each parameter - grid size, characters per slot, may be dialed up or down
    as desired.
* 100% from-scratch implementation.
* Permissive MIT license.

### Motivation

Many VRChat players choose not to use their mics, but as a practical matter,
occasionally have to communicate. I want this to be as simple, efficient, and
reliable as possible.

There are existing tools which help here, but they are all imperfect for one
reason or another:

1. RabidCrab's STT costs money and relies on cloud-based translation. I have
   struggled with latency, quality, and reliability issues. It's also
   closed-source, and uses quite a few parameters.
2. The in-game text box is only visible to your friends list, making it
   useless for those who like to make new friends.

Thus I believe that a free alternative is both needed and justified.

I hope that this codebase aids and motivates the creation of better, more
expressive communication tools for mutes.

### Design overview

There are roughly 4 important pieces here:

1. TaSTT.shader. A simple CG shader. Has one parameter per cell in the display.
2. generate\_animations.sh. Generates one animation per (row, column, letter).
   These animations allow us to write the shader's parameters from an FX layer.
3. generate\_fx.py. Generates a colossal FX layer which maps (row, column,
   letter, active) to exactly one of TaSTT.shader's parameters.
4. osc\_ctrl.py. Sends OSC messages to VRChat, which it dutifully passes along
   to the generated FX layer.

### Backlog

1. Better Unity integrations
1.1. Port all scripts to Unity-native C# scripts.
1.2. Support appending to existing FX layers.
1.3. Use VRCSDK to generate FX layer instead of generating the serialized files.
1.4. Optimize FX layer. Unity takes quite a while to load in the current one.
     Some redesign is likely needed.
2. In-game usability features.
2.1. Resizing (talk to friends far away).
2.2. Basic toggles (hide it when not needed).
2.3. World mounting (leave it in a fixed position in world space).
2.4. Avatar mounting (attach it to your hand).
2.5. Controller triggers (avoid having to use the radial menu every time you
     want to speak).
3. General usability features.
3.1. Error detection & correction.
3.2. Text-to-text interface. Type in terminal, show in game.

Made with love by yum\_food.
