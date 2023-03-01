import csv
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, JoinableQueue

import pandas as pd
from yaml import BaseLoader, load
from pybboxes import BoundingBox

from lib import Logger, ImageInfo, BoxIterator

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

class TargetManager:
    def __init__(self, root):
        self.root = root

    def create(self, *args):
        path = self.root.joinpath(*args)
        path.parent.mkdir(parents=True, exist_ok=True)

        return path

#
#
#
def func(queue, args):
    tm = TargetManager(args.output_root)
    with args.yolo_config.open() as fp:
        config = load(fp, BaseLoader)
    categories = dict(map(reversed, config['names'].items()))

    while True:
        (image, df) = queue.get()
        Logger.info(image)

        info = ImageInfo(image, args.data_root)

        split = df['split'].unique().item()
        name = info.path.relative_to(info.path.parents[1])
        target = Path(split, '-'.join(name.parts))

        # Add the image
        tm.create('images', target).symlink_to(info.path)

        # Create the labels
        dst = tm.create('labels', target.with_suffix('.txt'))
        with dst.open('w') as fp:
            boxes = YoloBoxes(df, info, categories)
            writer = csv.writer(fp, delimiter=' ')
            writer.writerows(boxes)

        queue.task_done()

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--version')
    arguments.add_argument('--data-root', type=Path)
    arguments.add_argument('--yolo-config', type=Path)
    arguments.add_argument('--output-root', type=Path)
    arguments.add_argument('--workers', type=int)
    args = arguments.parse_args()

    queue = JoinableQueue()
    initargs = (
        queue,
        args,
    )

    with Pool(args.workers, func, initargs):
        data = (args
                .data_root
                .joinpath('metadata', args.version)
                .iterdir())
        df = pd.concat(pd.read_csv(x, compression='gzip') for x in data)
        for i in df.groupby('url', sort=False):
            queue.put(i)
        queue.join()
