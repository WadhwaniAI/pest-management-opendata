import sys
import json
import uuid
import getpass
import functools as ft
import collections as cl
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool

import pandas as pd

from lib import Logger, ImageInfo, BoxIterator

#
#
#
class PestBoxes(BoxIterator):
    def __init__(self, df, categories):
        super().__init__(df)
        self.categories = categories
        self.image_id = int(self)

    def extract(self, index, box):
        (minx, miny, maxx, maxy) = box.geometry.bounds
        bbox = [
            minx,
            miny,
            maxx - minx,
            maxy - miny,
        ]

        return {
            'id': index,
            'image_id': self.image_id,
            'category_id': self.categories[box.label],
            'bbox': bbox,
        }

#
#
#
Entry = cl.namedtuple('Entry', [
    'images',
    'box_annotations',
    'caption_annotations',
    'splits',
])

class EntryCollection:
    def __init__(self):
        self.collection = { x: [] for x in Entry._fields }

    def __iter__(self):
        yield from self.collection.items()

    def update(self, entry):
        for (k, v) in entry._asdict().items():
            self.push(v, k)

    def to_json(self, fp, **kwargs):
        json.dump(dict(self, **kwargs), fp)

    @ft.singledispatchmethod
    def push(self, item, target):
        raise TypeError(type(item))

    @push.register
    def _(self, item: dict, target):
        self.collection[target].append(item)

    @push.register
    def _(self, item: list, target):
        self.collection[target].extend(item)

#
#
#
Category = cl.namedtuple('Category', 'name, supercategory')

class Categories:
    _trap = 'is_trap'

    def __init__(self, df):
        self.categories = [
            Category(self._trap, 'Image Level Categorical Label'),
        ]
        labels = df['label'].dropna().unique()
        self.categories.extend(Category(x, 'bounding box') for x in labels)

    def __iter__(self):
        for (i, j) in enumerate(self.categories):
            yield dict(j._asdict(), id=i)

    def records(self):
        for i in self:
            yield (i['name'], i['id'])

class MyImageInfo(ImageInfo):
    def __init__(self, image, root=None):
        if root is not None:
            image = root.joinpath(image)
        super().__init__(image)

#
#
#
def func(args):
    (image, df, categories) = args
    Logger.info(image)

    pests = PestBoxes(df, categories)
    idx = int(pests)
    box_annotations = list(pests)

    info = MyImageInfo(image)
    images = {
        'id': idx,
        'file_path': str(info),
        's3_url': None,
        'date_captured': str(info.time()),
    }
    images.update(info.shape())

    splits = {
        'image_id': idx,
        'split': df['split'].unique().item(),
    }

    caption_annotations = {
        'id': idx,
        'image_id': idx,
        'category_id': categories[Categories._trap],
        'caption': str(int(df['geometry'].notnull().all())),
    }

    return Entry(images, box_annotations, caption_annotations, splits)

def each(df, categories):
    cats = dict(categories.records())
    for (i, g) in df.groupby('path', sort=False):
        if args.image_root is not None:
            i = args.image_root.joinpath(i)
        yield (i, g, cats)

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--image-root', type=Path)
    arguments.add_argument('--source', type=Path, action='append')
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with Pool(args.workers) as pool:
        objs = (pd.read_csv(x, compression='gzip') for x in args.source)
        df = pd.concat(objs, ignore_index=True)
        categories = Categories(df)

        ec = EntryCollection()
        for i in pool.imap_unordered(func, each(df, categories)):
            ec.update(i)

    info = {
        'version': str(uuid.uuid4()),
        'description': 'Wadhwani AI pest management model input',
        'contributor': getpass.getuser(),
        'url': None,
        'date_created': str(pd.Timestamp.today()),
    }
    ec.to_json(sys.stdout, info=info, categories=list(categories))
