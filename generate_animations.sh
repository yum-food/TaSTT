#!/usr/bin/env bash

# One animation per slot, per letter.
# For upper-lower + a few symbols, this is roughly
# 6 * 14 * 128 \approx 8000 animations.
# Hopefully we don't hit some limit, lmao

set -o errexit
set -o pipefail

[ -d generated/animations ] && rm -rf generated || true
mkdir -p generated/animations

for row in `seq 0 5`; do
  ROW_PADDED=$(printf '%02d' $row)
  for col in `seq 0 13`; do
    COL_PADDED=$(printf '%02d' $col)
    LETTER_SHADER_PARAM=_Letter_Row${ROW_PADDED}_Col${COL_PADDED}
    for letter in `seq 0 128`; do
      LETTER_PADDED=$(printf '%02d' $letter)
      ANIM_NAME=${LETTER_SHADER_PARAM}_Letter${LETTER_PADDED}
      FILENAME=generated/animations/${ANIM_NAME}.anim
      cat template.anim | \
        sed \
            -e "s/%LETTER_VALUE%/$letter/g" \
            -e "s/%LETTER_SHADER_PARAM%/$LETTER_SHADER_PARAM/g" \
            -e "s/%ANIMATION_NAME%/$ANIM_NAME/g" \
            > $FILENAME
    done
  done
done
