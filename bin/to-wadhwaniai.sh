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
for i in $data/metadata/$version/*; do
    src=( ${src[@]} --source $i )
done

python $ROOT/src/wadhwaniai_/build-output.py ${src[@]} --data-root $data
