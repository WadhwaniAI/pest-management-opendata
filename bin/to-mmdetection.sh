#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

export PYTHONPATH=$ROOT:$PYTHONPATH
export PYTHONLOGLEVEL=info

while getopts 'd:v:h' option; do
    case $option in
	d) data=$OPTARG ;;
        v) version=$OPTARG ;;
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

tmp=`mktemp --directory`
for i in train val; do
    zcat $data/metadata/$version/dev.csv.gz | \
	python $ROOT/src/mmdetection_/build-output.py \
	       --data-root $data \
	       --split $i > $tmp/$i.json
done
echo $tmp
