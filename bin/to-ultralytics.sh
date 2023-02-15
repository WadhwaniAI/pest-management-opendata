#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

export PYTHONPATH=$ROOT:$PYTHONPATH
export PYTHONLOGLEVEL=info

while getopts 'd:v:o:h' option; do
    case $option in
	d) _data=$OPTARG ;;
        v) _version=$OPTARG ;;
	o) _output=$OPTARG ;;
        h)
	    cat <<EOF
Usage
$0 -v [version]
EOF
            exit 0
            ;;
        *) echo -e Unrecognized option \"$option\" ;;
    esac
done

if [ ! $_version ]; then
    _version=`ls -t $_data/metadata/ | head --lines=1`
fi
mkdir --parents $_output

for i in $_data/metadata/$_version/*; do
    data=( ${data[@]} --metadata $i )
done
python $ROOT/src/ultralytics_/build-config.py ${data[@]} \
       --output-root $_output > $_output/config
python $ROOT/src/ultralytics_/build-output.py \
       --data-root $_data \
       --version $_version \
       --yolo-config $_output/config \
       --output-root $_output
