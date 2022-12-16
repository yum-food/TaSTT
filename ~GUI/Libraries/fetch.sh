#!/usr/bin/env bash

set -o errexit
set -o xtrace

WX_3_2_1_URL=https://github.com/wxWidgets/wxWidgets/releases/download/v3.2.1/wxWidgets-3.2.1.zip
WX_URL=$WX_3_2_1_URL

mkdir wx
pushd wx >/dev/null
wget $WX_URL
unzip $(basename $WX_URL)
popd >/dev/null

