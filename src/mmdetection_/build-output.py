import sys
import json
import logging
import itertools as it
import collections as cl
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool

import pandas as pd
from shapely import wkt
from geopandas import GeoDataFrame

from lib import Logger, ImageInfo, LabelClass

Ann = cl.namedtuple('Ann', 'bboxes, labels')

#
#
#
def func(args):
    (image, df, categories) = args
    Logger.info(image)

    info = ImageInfo(image)
    record = dict(info.shape(), filename=str(info))

    view = df.dropna(subset=['geometry'])
    if view.empty:
        ann = Ann([], [])
    else:
        geometry = view['geometry'].apply(wkt.loads)
        gdf = GeoDataFrame(view, geometry=geometry)
        ann = Ann(
            gdf.geometry.bounds.to_numpy(),
            gdf['label'].replace(categories).to_numpy(),
        )
    record['ann'] = ann._asdict()

    return record

def each(fp, args):
    df = pd.read_csv(fp)

    lc = LabelClass(df)
    categories = dict(lc.l2c())
    if args.split:
        df = df.query('split in @args.split')

    for (i, g) in df.groupby('path', sort=False):
        if args.image_root is not None:
            i = args.image_root.joinpath(i)
        yield (i, g, categories)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--image-root', type=Path)
    arguments.add_argument('--split', action='append')
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        data = pool.imap_unordered(func, each(sys.stdin, args))
        json.dump(list(data), sys.stdout)
