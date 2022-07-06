import sys
import json
import uuid
import getpass
import functools as ft
import collections as cl
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

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

class EntryGenerator:
    def __init__(self, args):
        self.args = args
        self._categories = None

    def __iter__(self):
        incoming = Queue()
        outgoing = Queue()
        initargs = (
            outgoing,
            incoming,
            self.args,
        )

        with Pool(self.args.workers, self.func, initargs):
            df = pd.concat(self.frames(), ignore_index=True)
            self._categories = Categories(df)
            cats = dict(self._categories.records())

            groups = df.groupby('url', sort=False)
            for i in groups:
                outgoing.put((*i, cats))

            for _ in range(groups.ngroups):
                entry = incoming.get()
                yield entry

    def frames(self):
        for i in self.args.source:
            yield pd.read_csv(i, compression='gzip')

    @property
    def categories(self):
        if self._categories is None:
            raise AttributeError()

        return list(self._categories)

    @staticmethod
    def func(incoming, outgoing, args):
        while True:
            (image, df, categories) = incoming.get()
            Logger.info(image)

            pests = PestBoxes(df, categories)
            idx = int(pests)
            box_annotations = list(pests)

            info = ImageInfo(image, args.data_root)
            images = {
                'id': idx,
                'file_path': str(info),
                's3_url': image,
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

            entry = Entry(images, box_annotations, caption_annotations, splits)
            outgoing.put(entry)

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--data-root', type=Path)
    arguments.add_argument('--source', type=Path, action='append')
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    ec = EntryCollection()
    eg = EntryGenerator(args)
    for i in eg:
        ec.update(i)

    info = {
        'version': str(uuid.uuid4()),
        'description': 'Wadhwani AI pest management model input',
        'contributor': getpass.getuser(),
        'url': None,
        'date_created': str(pd.Timestamp.today()),
    }
    ec.to_json(sys.stdout, info=info, categories=eg.categories)
