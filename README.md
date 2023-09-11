## TaSTT: A deliciously free STT

TaSTT (pronounced "tasty") is a free speech-to-text tool for VRChat. It uses
[a GPU-based transcription algorithm](https://github.com/openai/whisper) to
turn your voice into text, then sends it into VRChat via OSC.

To get started, download the latest .zip from [the releases page](https://github.com/yum-food/TaSTT/releases/latest).

[![Speech-to-text demo](https://img.youtube.com/vi/tUO1MXN64Mo/0.jpg)](https://youtube.com/watch?v=tUO1MXN64Mo)

Contents:

0. [Usage and setup](#usage-and-setup)
1. [Features](#features)
2. [Requirements](#requirements)
3. [Motivation](#motivation)
4. [Design overview](#design-overview)
5. [Contributing](#contributing)
6. [Roadmap](#Roadmap)
7. [Backlog](#backlog)

Made with love by yum\_food.

## Usage and setup

Download the latest .zip from [the releases page](https://github.com/yum-food/TaSTT/releases/latest).

Please [join the discord](https://discord.gg/YWmCvbCRyn) to share feedback and
get technical help.

To build your own package from source, see GUI/README.md.

Basic controls:
* Short click to toggle transcription.
* Medium click to hide the text box.
* Hold to update text box without unlocking from worldspace.
* Medium click + hold to type using STT.
* Scale up/down in the radial menu.

## Design philosophy

* All language services are performed on the client. No network hops in the
  critical path.
* Priorities (descending order): reliability, latency, accuracy, performance,
  aesthetics.
* No telemetry of any kind in the app. github and discord are the only means I
  have to estimate usage and triage bugs.
* Permissive licensing. Users should be legally entitled to hack, extend,
  relicense, and profit from this codebase.

## Features

* Works with the built-in chatbox (usable with public avatars!)
* Customizable board resolution, [up to ridiculous sizes](https://www.youtube.com/watch?v=u5h-ivkwS0M).
* Lighweight design:
  * Custom textbox requires as few as 65 parameter bits
  * Transcription doesn't affect VRChat framerate much, since VRC is heavily
    CPU-bound. Performance impact when not speaking is negligible.
* Browser source. Use with OBS!
* Multi-language support.
  * Japanese, Korean, and Chinese glyphs included, among many other languages.
    * Full list of Unicode blocks is defined in
      [generate_fonts.py](https://github.com/yum-food/TaSTT/blob/master/Scripts/generate_fonts.py#L43-L109).
  * Whisper natively supports transcription in [100 languages](
    https://github.com/openai/whisper/blob/main/whisper/tokenizer.py#L10).
* Customizable:
  * Control button may be set to left/right a/b/joystick.
  * Text color, background color, and border color are customizable in the shader.
  * Text background may be customized with PBR textures: base color, normal,
    metallic, roughness, and emission are all implemented.
  * Border width and rounding are customizable.
  * Shader supports physically based shading: smoothness, metallic, and emissive.
* Many optional quality-of-life features:
  * Audio feedback: hear distinct beeps when transcription starts and stops.
  * May also enable in-game noise indicator, to grab others' attention.
  * Visual transcription indicator.
  * Resize with a blendtree in your radial menu.
* Locks to world space when done speaking.
* Privacy-respecting: transcription is done on your GPU, not in the cloud.
* Hackable.
* From-scratch implementation.
* Free as in beer.
* Free as in freedom.
* MIT license.

## Requirements

System requirements:

* ~2GB disk space
* NVIDIA GPU with at least 2GB of spare VRAM.
  * You *can* run it in CPU mode, but it's really slow and lags you a
    lot more, so I wouldn't recommend it.
  * I've tested on a 1080 Ti and a 3090 and saw comparable latency.
* SteamVR.
* No write defaults on your avatar if you're using the custom text box.

Avatar resources used:

* Tris: 4
* Material slots: 1
* Texture memory: 340 KB (English), 130 MB (international)
* Parameter bits: 65-217 (configurable; more bits == faster paging)
* Menu slots: 1

## Motivation

Many VRChat players choose not to use their mics, but as a practical matter,
occasionally have to communicate. I want this to be as simple, efficient, and
reliable as possible.

There are existing tools which help here, but they are all imperfect for one
reason or another:

1. RabidCrab's STT costs money and relies on cloud-based transcription.
   Because of the reliance on cloud-based transcription services, it's
   typically slower and less reliable than local transcription.
2. The in-game text box is not visible in streamer mode, and limits you to one
   update every ~2 seconds, making it a poor choice for latency-sensitive
   communication.
3. [KillFrenzy's AvatarText](https://github.com/killfrenzy96/KillFrenzyAvatarText)
   only supports text-to-text. It's an excellent product with high-quality
   source code, but it lacks integration with a client-side STT engine.
4. [I5UCC's VRCTextboxSTT](https://github.com/I5UCC/VRCTextboxSTT) makes
   KillFrenzy's AvatarText and Whisper kiss. It's the closest spiritual cousin
   to this repository. The author has made incredible sustained progress on
   the problem. Definitely take a look!
5. [VRCWizard's TTS-Voice-Wizard](https://github.com/VRCWizard/TTS-Voice-Wizard)
   also uses Whisper, but they rely on the C# interface to Const-Me's
   CUDA-enabled Whisper implementation. This implementation does not support
   beam search decoding and waits for pauses to segment your voice. Thus it's
   less accurate and higher latency than this project's Python-based
   transcription engine, but it's more performant. It supports more feature
   (like cloud-based TTS), so you might want to check it out.

Why should you pick this project over the alternatives? This project has
the lowest latency (measured <500ms end-to-end on mid-range hardware), most
reliable transcriptions of any STT in VRChat, period. There is no network hop
to worry about and no subscription to manage. Just download and go.

## Design overview

These are the important bits:

1. `TaSTT_template.shader`. A simple unlit shader template. Contains the
   business logic for the shader that shows text in game.
2. `generate_shader.py`. Adds parameters and an accessor function to the
   shader template.
3. `libunity.py`. Contains the logic required to generate and manipulate Unity
   YAML files. Works well enough on YAMLs up to ~40k documents, 1M lines.
4. `libtastt.py`. Contains the logic to generate TaSTT-specific Unity files,
   namely the animations and the animator.
5. `osc_ctrl.py`. Sends OSC messages to VRChat, which it dutifully passes along
   to the generated FX layer.
6. `transcribe.py`. Uses OpenAI's whisper neural network to transcribe audio
   and sends it to the board using osc_ctrl.

#### Parameters & board indexing

I divide the board into several regions and use a single int parameter,
`TaSTT_Select`, to select the active region. For each byte of data
in the active region, I use a float parameter to blend between two
animations: one with value 0, and one with value 255.

To support wide character sets, I support 2 bytes per character. This
can be configured down to 1 byte per character to save parameter bits.

#### FX controller design

The FX controller (AKA animator) is pretty simple. There is one layer for each
sync parameter (i.e. each character byte). The layer has to work out which
region it's in, then write a byte to the correct shader parameter.

![One FX layer with 16 regions](Images/tastt_anim.png)

From top down, we first check if updating the board is enabled. If no, we stay
in the first state. Then we check which region we're in. Finally, we drive a
shader parameter to one of 256 possible values using a blendtree.

![An 8-bit blendtree](Images/tastt_blend.png)

The blendtree trick lets us represent wide character sets efficiently. The
number of animations required increases logarithmically with the size of the
character set:

```
(N bytes per character) = ceil(log2(size of character set))
(total animations) =
    (2 animations per byte) *
    (N bytes per character) *
    (M characters per region)
```

## Contributing

Contributions welcome. Send a pull request to this repository.

See GUI/README.md for instructions on building the GUI.

Ping the discord if you need help getting set up.

## Roadmap

### Milestone 1: STT Personally usable

Status: COMPLETE.

Scope: The speech-to-text may be used by one developer intimately familiar with
its inner workings. Environment is not encapsulated.

Completed at commit 8326dee0bf01956.

### Milestone 2: STT Generally usable

Status: COMPLETE.

Scope: The speech-to-text is used by at least one user not familiar with its
inner workings. Dependency management is mostly handled mechanically. The app
can be controlled using a GUI.

Completed at commit 1f15133dd985442, AKA release 0.10.0.

### Milestone 3: STT Generally performant

Status: COMPLETE.

Scope: The speech-to-text may be used on resource constrained systems.

I'm looking at Const-Me/Whisper as the transcription
backend. I have measured terrible accuracy when using the VAD-segmented
transcription path vs. using the file-based non-VAD-segmented transcription
path (~15x higher edit distance on the same recording of the Bill of Rights).
Beam search has not measurably improved the file-based transcription path.
It remains to be seen if VAD segmentation is the failure source, or if
it's caused by the inference layer being unable to "second guess" itself
(previous transcriptions cannot be edited in the current architecture),
or something else.

Completed at commit 1f2e5c6cf16e7e7, AKA release 0.11.2.

### Milestone 4: Enable non-VRChat use cases

Status: COMPLETE.

Scope: The speech-to-text may be used as a tool for usecases outside of VRChat.

Streamers could use the STT as an OBS browser source. VR players could use it
to type into arbitrary text fields (voice-driven keyboard device). MMO players
could also use the voice-driven keyboard (speak -> preview -> rapid commit?)
while raiding.

Completed at commit 7a576bcac1c37c3, AKA release 0.13.1.

### Milestone 5: Integration into other tools

Status: NOT STARTED.

Scope: Integrate performant client-side transcription into other STT tools.

Once performant client-side transcription is implemented, there is no reason
to keep it locked away inside one project. Other projects making different
tradeoffs (such as relying on cloud services for TTS) could benefit from this
functionality, driving down costs and latency for users. In particular, I think
that there is value in integrating with TTS-Voice-Wizard.

TaSTT is about providing performant, commoditized, user-owned STT services. I
have no interest in using cloud services to provide any functionality.
Instead of extending this project to do that, the best way to spread the love
is to partner with (contribute to) projects that do.

### Completion

This project will probably reach a stable state and then go into maintenance.
The efforts described above are the major milestones I plan to implement. Small
features and bugfixes will likely continue in the "completed" state.

## Backlog

1. Better Unity integrations
   1. Port all scripts to Unity-native C# scripts.
   2. ~~Support appending to existing FX layers.~~ DONE
   3. Use VRCSDK to generate FX layer instead of generating the serialized files.
2. In-game usability features.
   1. ~~Resizing (talk to friends far away).~~ DONE
   2. ~~Basic toggles (hide it when not needed).~~ DONE
   3. ~~World mounting (leave it in a fixed position in world space).~~ DONE
   4. ~~Avatar mounting (attach it to your hand)~~ DONE.
   5. ~~Controller triggers (avoid having to use the radial menu every time you
     want to speak).~~ DONE
3. General usability features.
   1. ~~Error detection & correction.~~ DONE
   2. ~~Text-to-text interface. Type in terminal, show in game.~~ DONE
   3. ~~Speech-to-text interface. Speak out loud, show in game.~~ DONE
   4. ~~Translation into non-English. Whisper natively supports translating N
      languages into English, but not the other way around.~~ DONE
   5. Display text in overlay. Enables (1) lower latency view of TaSTT's
      transcription state; (2) checking transcriptions ahead of time; (3)
      checking transcriptions without having to see the board in game.
   6. TTS. Multiple people have requested this. See if there are open source
      algorithms available; or, figure out how to integrate with
   7. ~~Save UI input fields to config file. Persist across process exit. It's
      annoying having to re-enter the config every time I use the STT.~~ DONE
   8. ~~Customizable controller bindings. Someone mentioned they use left click
      to unmute. Let's work around users, not make them change their existing
      keybinds.~~ DONE
   9. One-click upgrade. Fetch latest stable release, copy over virtual env and
      UI configs, relaunch.
   10. ~~Browser source for OBS. Blocker: the transcription layer doesn't handle
      long pauses well.~~ DONE
   11. Test suite. Some long representative transcripts with mechanical word
       error rate (WER) calculation.
4. Optimization
   1. ~~Utilize the avatar 3.0 SDK's ability to drive parameters to reduce the
     total # of parameters (and therefore OSC messages & sync events). Note
     that the parameter memory usage may not decrease.~~ DONE
   2. ~~Optimize FX layer. We have 14k animations and a 1.2 million line FX
      layer. Something must be rethought to bring these numbers down.~~ DONE
   3. ~~Implement multicore YAML parsing. This will make working with large
      animators much more practical.~~ DONE
   4. ~~Transcription engine sleep interval increases exponentially up to 1-2
      seconds, then jumps back to a short interval once speech is detected.
      This should significantly cut down on idle resource consumption. Perhaps
      there's even a more efficient way to detect the odds that anything is
      being said, which we could use to gate transcription.~~ DONE
   5. There are ~64k words in the English language. We could encode each word
      using a 16-bit int. On the other hand, suppose you represented each
      character using 7 bits per character and transmitted words
      character-by-character. The average word length is 4.7 characters, and we
      send ~1 space character per word. Thus the expected bits per word in an
      optimized version of today's encoding scheme is (5.7 * 7) == 39.9 bits.
      The other encoding scheme is thus ~2.5 times more efficient. This could
      be used to significantly speed up sync times. (Thanks, Noppers for the
      idea!)
   6. ~~Use Const-Me/Whisper for transcription.~~ WON'T DO
   7. ~~Implement beam search in Const-Me/Whisper.~~ WON'T DO
5. Bugfixes
   1. ~~The whisper STT says "Thank you." when there's no audio?~~ DONE
   2. JP and CN transcription does not work in the GUI due to encoding issues.
6. Shine
   1. Smooth scrolling.
   2. ~~Infinite scrolling.~~ DONE
   3. ~~Sound indicator, maybe like animal crossing :)~~ DONE
   4. ~~Support texture-based PBR shading~~ DONE

