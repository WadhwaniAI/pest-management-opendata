import warnings
import collections as cl
from pathlib import Path
from urllib.parse import urlparse

import cv2
import piexif
import pandas as pd
from shapely import wkt

__all__ = [
    'ImageInfo',
    'BoxIterator',
]

# Pandas.DataFrame.itertuples does not mix well with multiprocessing
# (https://github.com/pandas-dev/pandas/issues/11791)
def itertuples(df):
    Frame = cl.namedtuple('Frame', df.columns)
    for (i, *j) in df.itertuples(name=None):
        yield (i, Frame(*j))

class ImageInfo:
    _exif_date = '%Y:%m:%d %H:%M:%S'

    def __init__(self, source, target):
        url = urlparse(source)
        path = Path(url.path)
        if path.is_absolute():
            path = path.relative_to(path.root)

        self.path = target.joinpath(path)

    def __str__(self):
        return str(self.path)

    def shape(self):
        img = cv2.imread(str(self.path), cv2.IMREAD_IGNORE_ORIENTATION)
        yield from zip(('height', 'width'), img.shape)

    def time(self):
        try:
            tstamp = (piexif
                      .load(str(self.path))
                      .get('Exif')
                      .get(piexif.ExifIFD.DateTimeOriginal)
                      .decode())
            dt = pd.to_datetime(tstamp, format=self._exif_date)
        except piexif.InvalidImageDataError:
            warnings.warn(f'{self}: Bad EXIF')
            dt = pd.NaT

        return pd.Timestamp.min if pd.isnull(dt) else dt

class BoxIterator:
    def __init__(self, df):
        self.df = df

    def __int__(self):
        return int(self.df.index.min())

    def __iter__(self):
        for (i, df) in itertuples(self.df):
            if pd.notnull(df.geometry):
                geometry = wkt.loads(df.geometry)
                df = df._replace(geometry=geometry)
                yield self.extract(i, df)

    def extract(self, index, box):
        raise NotImplementedError()
