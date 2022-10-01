#!/usr/bin/env bash

set -o pipefail
set -o errexit
set -o xtrace

echo 'Generating animations'

./generate_animations

echo 'Tab into unity and wait for it to import animations, then press enter.'
echo
echo 'This is necessary because the FX layer will reference animations by '
echo 'their Unity GUID which is generated during import.'
read -r line

echo 'Generating FX layer'

./generate_fx.py > TaSTT_fx.controller

echo 'Generating parameters'

./generate_params.py > TaSTT_params.asset

echo 'Done! Assign the parameters and fx layer, then upload.'


