#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

export PYTHONPATH=$ROOT:$PYTHONPATH
export PYTHONLOGLEVEL=info

splits=(
    train
    validation
)

tmp=`mktemp --directory`
for i in ${splits[@]}; do
    python $ROOT/src/detectron2_/build-output.py \
	   --image-root $ROOT/data \
	   --split $i > $tmp/$i.json
done
echo $tmp
