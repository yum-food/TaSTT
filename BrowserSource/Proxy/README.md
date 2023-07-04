This is a Linux server. It receives transcripts from TaSTT and serves them to
peers using a session identifier. It serves the use case where a mute player
wishes to show their transcript on a friend's stream.

Dependencies:
* clang-15
* cmake
* fmtlib/fmt

To build:
./build-foss.sh
make
