Data can be aquired using the [AWS CLI](https://aws.amazon.com/cli/):

```bash
$> aws s3 sync --no-progress s3://wadhwaniai-agri-opendata/ data/
```

The data directory will consists of images, along with metadata
(compressed CSVs) containing information about pest locations in those
images.

In the AWS sync command, the target does not have to be `data`. This
documentation assumes, however, that `data` was used. Please keep this
in mind as you go through the documentation if you decide to deviate
from this convention.

# Images

Most images (`data/images/*`) were captured using the pest management
mobile application during actual app deployments. This means the
images come with a range of characteristics, both with respect to the
number of pests they contain, and to their contents overall.

Image EXIF information has been generated using
[ExifTool](https://exiftool.org/). Aside from the default values it
generates, EXIF info in this data set includes:

* Date the image was captured ("DateTimeOriginal")
* Copyright ("Copyright")
* Image license ("UserComment")

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

The CSV files are GZIP'd, containing one line per bounding box
(pest). The files are structured as follows:

| Header | In "dev" | In "test" | Description
|---     | ---   | ---    | ---
| url | Yes | Yes | S3 URL of the image
| split | Yes | Yes | Split for which the image is meant
| label | Yes | No | The pest contained in this box
| geometry | Yes | No | The bounding box of the pest, as [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry)

Some rows in the dev CSV contain empty label and geometry
values. These images come from user user submissions that did not
contain pests.

### Manipulation

The metadata format is designed to be minimal. It only assumes that
potential downstream pipelines require bounding boxes and
corresponding box labels. Example of potential manipulations:

* __Information not in the metadata__: If additional information about
  the image is required, the image can be read to obtain it:

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

* __Pest counts__: To train models based on pest counts instead of
  bounding boxes, the file can be manipulated as follows:

  ```python
  import pandas as pd

  df = (pd
		.read_csv('data/metadata/dev.csv.gz', compression='gzip')
		.groupby(['path', 'label', 'split'], sort=False, dropna=False)['geometry']
		.count()
		.reset_index())
  ```

This minimal approach to data formatting makes it unlikely that a
modelling framework will be able to work with the files directly. For
convenience, we provide scripts to go from our minimal format to other
frameworks. See our documentation on how to use those tools; pay
attention to their source code (Python scripts in `src/`) for further
guidance.
