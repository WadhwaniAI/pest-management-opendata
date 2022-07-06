Data can be aquired using the [AWS CLI](https://aws.amazon.com/cli/):

```bash
$> aws s3 sync --no-progress s3://wadhwaniai-agri-opendata/ data/
```

Data consists of images, along with metadata that contains information
about pest locations in those images.

# Images

Most images (`data/images/*`) were captured using the pest management
mobile application during actual app deployments. This means the
images come with a range of characteristics, both with respect to the
number of pests they contain, and to their contents overall.

# Metadata

Images meant for both model development and model testing are present
in this dataset. There are two CSV files to describe each. Pest
locations are only present in the development CSV, acting as a
resource for training pipelines. The test CSV is meant only to
idenfity which images are part of the test set. It is void of any pest
information.

## Versioning

The metadata folder is divided into sub-directories, below each are
the development and test CSVs previously described:

```bash
$> tree data/metadata/
data/metadata/
└── 20220629-1312
    ├── dev.csv.gz
    └── test.csv.gz

1 directory, 2 files
```

In this case, the development and test CSVs would be considered to be
under version 20220629-1312.

## Format

### Overview

The CSV files are GZIP'd, containing one line per pest (box). The
files are structured as follows:

| Header | Present in "dev" | Present in "test" | Description
|---     | ---   | ---    | ---
| path | Yes | Yes | Path to the image file assuming the current working directory is `data`
| split | Yes | Yes | Split for which the image is meant; values include `train`, `validation`, or `test`
| label | Yes | No | The pest contained in this box; values include `abw` or `pbw`
| geometry | Yes | No | The bounding box of the pest, as [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry)

### Manipulation

The metadata format is designed to be minimal. The only thing it
assumes about potential downstream pipelines are that bounding boxes
and corresponding box labels are required. If, for example, training
models based on pest counts instead of bounding boxes is required, the
file can be easily manipulated:

```python
import pandas as pd

df = (pd
      .read_csv('data/metadata/dev.csv.gz', compression='gzip')
      .groupby(['path', 'label', 'split'], sort=False, dropna=False)['geometry']
      .count()
      .reset_index())
```

If additional information about the image is required, the image can
be read to obtain it:

```python
import cv2
import pandas as pd

def get_shapes(df):
    for i in df['path'].unique():
        img = cv2.imread(img, cv2.IMREAD_IGNORE_ORIENTATION)
        shape = zip(('height', 'width'), img.shape)
        yield dict(shape, path=i)

df = pd.read_csv('data/metadata/dev.csv.gz', compression='gzip')
shapes = pd.DataFrame.from_records(get_shapes(df))
```

This approach to formatting makes it unlikely that a modelling
framework will be able to work with the files directly. For
convenience, we provide scripts to go from our minimal format to other
frameworks.
