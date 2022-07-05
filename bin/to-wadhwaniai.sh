#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

export PYTHONPATH=$ROOT:$PYTHONPATH
export PYTHONLOGLEVEL=info

meta=( `readlink --canonicalize $ROOT/data/metadata/*` )
source=`sed -e's/ / --source /g' <<< ${sources[@]}`

python $ROOT/src/wadhwaniai_/build-output.py \
    --image-root $ROOT/data \
    --source $source
