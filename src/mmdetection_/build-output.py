import sys
import json
import functools as ft
import collections as cl
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import pandas as pd
from shapely import wkt
from geopandas import GeoDataFrame

from lib import Logger, ImageInfo, LabelClass

Ann = cl.namedtuple('Ann', 'bboxes, labels')

class PandasEncoder(json.JSONEncoder):
    @ft.singledispatchmethod
    def default(self, o):
        return super().default(o)

    @default.register
    def _(self, o: pd.Series):
        return o.tolist()

    @default.register
    def _(self, o: pd.DataFrame):
        return o.to_numpy().tolist()

#
#
#
def func(incoming, outgoing, args):
    while True:
        (image, df, categories) = incoming.get()
        Logger.info(image)

        info = ImageInfo(image, args.data_root)
        record = dict(info.shape(), filename=str(info))

        view = df.dropna(subset=['geometry'])
        if view.empty:
            ann = Ann([], [])
        else:
            geometry = view['geometry'].apply(wkt.loads)
            gdf = GeoDataFrame(view, geometry=geometry)
            ann = Ann(
                gdf.geometry.bounds,
                gdf['label'].replace(categories),
            )
        record['ann'] = ann._asdict()

        outgoing.put(record)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--data-root', type=Path)
    arguments.add_argument('--split', action='append')
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        args,
    )

    with Pool(args.workers, func, initargs):
        df = pd.read_csv(sys.stdin)

        lc = LabelClass(df)
        categories = dict(lc.l2c())
        if args.split:
            df = df.query('split in @args.split')

        groups = df.groupby('url', sort=False)
        for i in groups:
            outgoing.put((*i, categories))

        data = []
        for _ in range(groups.ngroups):
            record = incoming.get()
            data.append(record)
        json.dump(data, sys.stdout, cls=PandasEncoder)
