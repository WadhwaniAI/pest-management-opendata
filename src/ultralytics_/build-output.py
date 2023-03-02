import csv
import collections as cl
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import pandas as pd
from yaml import BaseLoader, load
from pybboxes import BoundingBox

from lib import Logger, ImageInfo, BoxIterator

Flow = cl.namedtuple('Flow', 'source, target')
GroupKey = cl.namedtuple('GroupKey', 'url, split')

class YoloBoxes(BoxIterator):
    _w_h = (
        'width',
        'height',
    )

    def __init__(self, df, info, categories):
        super().__init__(df)

        self.categories = categories
        dimensions = dict(info.shape())
        self.image_size = tuple(map(dimensions.get, self._w_h))

    def extract(self, index, box):
        record = [
            self.categories[box.label],
        ]
        bbox = BoundingBox(*box.geometry.bounds, image_size=self.image_size)
        record.extend(bbox.to_yolo(return_values=True))

        return record

#
#
#
def func(incoming, outgoing, categories, flow):
    (_images, _labels) = ('images', 'labels')
    for i in (_images, _labels):
        flow.target.joinpath(i).mkdir(parents=True, exist_ok=True)

    while True:
        (key, df) = incoming.get()
        Logger.info(' '.join(key))

        info = ImageInfo(key.url, flow.source)
        name = info.path.relative_to(info.path.parents[1])
        target = '-'.join(name.parts)

        # Add the image
        path = flow.target.joinpath(_images, target)
        path.symlink_to(info.path)

        # Create the labels
        dst = flow.target.joinpath(_labels, target).with_suffix('.txt')
        with dst.open('w') as fp:
            boxes = YoloBoxes(df, info, categories)
            writer = csv.writer(fp, delimiter=' ')
            writer.writerows(boxes)

        outgoing.put(key._replace(url=path))

#
#
#
def frames(source, version):
    path = source.joinpath('metadata', version)
    for i in path.iterdir():
        yield pd.read_csv(i, compression='gzip')

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version')
    arguments.add_argument('--data-root', type=Path)
    arguments.add_argument('--yolo-config', type=Path)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    with args.yolo_config.open() as fp:
        config = load(fp, BaseLoader)
    i_o = Flow(args.data_root, Path(config['path']))
    categories = dict(map(reversed, config['names'].items()))

    incoming = Queue()
    outgoing = Queue()
    initargs = (
        outgoing,
        incoming,
        categories,
        i_o,
    )

    with Pool(args.workers, func, initargs):
        groups = (pd
                  .concat(frames(i_o.source, args.version))
                  .groupby(list(GroupKey._fields), sort=False))
        for (i, g) in groups:
            key = GroupKey(*i)
            outgoing.put((key, g))

        records = cl.defaultdict(list)
        for _ in range(groups.ngroups):
            key = incoming.get()
            records[key.split].append(key.url)

    for (k, v) in records.items():
        output = i_o.target.joinpath(config[k])
        with output.open('w') as fp:
            print(*v, sep='\n', file=fp)
