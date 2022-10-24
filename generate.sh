#!/usr/bin/env bash

set -o pipefail
set -o errexit
set -o xtrace

echo 'Generating animations'

./libtastt.py gen_anims

echo 'Generating FX layer'

./libtastt.py gen_fx > TaSTT_fx.controller

echo 'Generating parameters'

./generate_params.py > TaSTT_params.asset

echo 'Done! Assign the parameters and fx layer, then upload.'


