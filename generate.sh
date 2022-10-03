#!/usr/bin/env bash

set -o pipefail
set -o errexit
set -o xtrace

echo 'Generating animations'

./generate_animations.sh

set +o xtrace
echo 'Tab into unity and wait for it to import animations, then press enter.'
echo
echo 'This is necessary because the FX layer will reference animations by '
echo 'their Unity GUID, which is generated during import.'
set -o xtrace
read -r line

set +o xtrace
echo 'Now that animations have been generated, close Unity again.'
echo 'Unity can only really handle importing the generated FX layer at startup.'
echo 'If it reimports it at runtime, it hangs for a long time. No idea why!'
echo
echo 'Press enter once Unity is closed again.'
set -o xtrace
read -r line

echo 'Generating FX layer'

./generate_fx.py > TaSTT_fx.controller

echo 'Generating parameters'

./generate_params.py > TaSTT_params.asset

echo 'Done! Assign the parameters and fx layer, then upload.'


