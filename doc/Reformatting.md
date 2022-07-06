It is unlikely the default data format is conducive for a modelling
framework. This repository contains several scripts to convert the
default format into another standard. This section details the
reformatting implementations in this repository, and how they can be
used.

This section assumes the user has followed the previous steps of
aquiring the repository and the data, and that the users current
working directory is the repository root; as mentioned previously:

```bash
$> git clone https://github.com/WadhwaniAI/pest-management-opendata.git
$> cd pest-management-opendata
$> aws s3 sync --no-progress s3://wadhwaniai-agri-opendata/ data/
```

In addition, scripts use the Python logger to report progress. You can
get the most complete set of information from each script by setting
that value to
"[info](https://docs.python.org/3/library/logging.html#logging-levels)":

```bash
$> export PYTHONLOGLEVEL=info
```

Or ignoring information completely by piping stderr to a file.

# Detectron2

[Detectron2](https://github.com/facebookresearch/detectron2) is an
object detection framework maintained by Meta.

## Basic usage

```
$> ./bin/to-detectron2.sh -d data
```

This will create two JSON files corresponding to a train and a
validation set. The location of those files is reported (to stdout) at
the end of the scripts execution.

By default this will use the most recent metadata version. The version
can be explicitly controlled using the `-v` option:

```
$> ls data/metadata/
20220629-1312
$> ./bin/to-detectron2.sh -d data -v 20220629-1312
```

## Advanced usage

For more advanced usage the Python generation script can be run
directly. First, setup your environment:

```
$> ROOT=`git rev-parse --show-toplevel`
$> export PYTHONPATH=$ROOT:$PYTHONPATH
$> export PYTHONLOGLEVEL=info
```

Then run the script:

```bash
$> zcat $ROOT/data/metadata/20220629-1312/dev.csv.gz | \
	python src/detectron2_/build-output.py \
		--data-root $ROOT/data \
		--split train > train.json
```

## Inside the framework

The Detectron2 format manages labels using integers. They support a
means for mapping those integers back to their human-readable
values. We can generate that JSON as follows:

```bash
$> zcat $ROOT/data/metadata/20220629-1312/dev.csv.gz | \
	python src/detectron2_/things.py > things.json
```

Assume that this, and the train/val JSONs are in the following
directory structure:

```bash
> tree /foo/bar/jsons
/foo/bar/jsons
├── data
│   ├── train.json
│   └── val.json
└── things.json

1 directory, 3 files
```

The instructions in the Detectron2
[documentation](https://detectron2.readthedocs.io/en/latest/tutorials/datasets.html#register-a-dataset)
can be augmented as follows:

```python
import json
from pathlib import Path

from detectron2.data import DatasetCatalog, MetadataCatalog

def retreive(path):
    def get():
        with path.open() as fp:
            return json.load(fp)

    return get

sources = Path('/foo/bar/jsons')
things = (sources
          .joinpath('things')
          .with_suffix('.json'))
thing_classes = retrieve(things)

for i in sources.joinpath('data').iterdir():
    DatasetCatalog.register(i.stem, retreive(i))
    MetadataCatalog.get(i.stem).thing_classes = thing_classes()
```

# Wadhwani AI

The object detection framework designed around this data is available
from the Wadhwani Institute for Artificial Intelligence.

## Basic usage

```bash
$> ./bin/to-wadhwaniai.sh -d data > wadhwaniai.json
```

## Advanced usage

For more advanced usage the Python generation script can be run
directly. First, setup your environment:

```
$> ROOT=`git rev-parse --show-toplevel`
$> export PYTHONPATH=$ROOT:$PYTHONPATH
$> export PYTHONLOGLEVEL=info
```

Then run the script:

```bash
$> python src/wadhwaniai_/build-output.py \
	--data-root $ROOT/data \
	--source $ROOT/data/metadata/20220629-1312/dev.csv.gz \
	--source $ROOT/data/metadata/20220629-1312/test.csv.gz > wadhwaniai.json
```

# MMDetection

[MMDetection](https://github.com/open-mmlab/mmdetection) is an object
detection framework developed by OpenMMLab.

## Basic usage

```bash
$> ./bin/to-mmdetection.sh -d data
```

This will create two JSON files corresponding to a train and a
validation set. The location of those files is reported (to stdout) at
the end of the scripts execution.

## Advanced usage

For more advanced usage the Python generation script can be run
directly. First, setup your environment:

```
$> ROOT=`git rev-parse --show-toplevel`
$> export PYTHONPATH=$ROOT:$PYTHONPATH
$> export PYTHONLOGLEVEL=info
```

Then run the script:

```bash
$> zcat $ROOT/data/metadata/20220629-1312/dev.csv.gz | \
	python src/mmdetection_/build-output.py \
		--data-root $ROOT/data \
		--split train > train.json
```
