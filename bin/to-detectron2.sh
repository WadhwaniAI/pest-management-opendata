#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

export PYTHONPATH=$ROOT:$PYTHONPATH
export PYTHONLOGLEVEL=info

while getopts 'd:v:o:h' option; do
    case $option in
	d) data=$OPTARG ;;
        v) version=$OPTARG ;;
	o) output=$OPTARG ;;
        h)
	    cat <<EOF
Usage
./$0 -v [version]
EOF
            exit 0
            ;;
        *) echo -e Unrecognized option \"$option\" ;;
    esac
done

if [ ! $version ]; then
    version=`ls -t $data/metadata/ | head --lines=1`
fi

tmp=`mktemp`

gunzip --to-stdout $data/metadata/$version/dev.csv.gz > $tmp
for i in train val; do
    o=$output/data
    mkdir --parents $o
    python $ROOT/src/detectron2_/build-output.py \
	   --data-root $data \
	   --split $i < $tmp > $o/$i.json
done
python $ROOT/src/detectron2_/things.py < $tmp > $output/things.json

rm $tmp
