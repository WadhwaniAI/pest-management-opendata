import sys
import json
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import pandas as pd
from detectron2.structures import BoxMode

from lib import Logger, ImageInfo, LabelClass, BoxIterator

class DetectronBoxes(BoxIterator):
    def __init__(self, df, categories):
        super().__init__(df)
        self.categories = categories

    def extract(self, index, box):
        bbox = list(box.geometry.bounds)
        category_id = self.categories[box.label]

        return {
            'bbox': bbox,
            'bbox_mode': BoxMode.XYXY_ABS,
            'category_id': category_id,
        }

#
#
#
def func(incoming, outgoing, args):
    while True:
        (image, df, categories) = incoming.get()
        Logger.info(image)

        info = ImageInfo(image, args.data_root)
        boxes = DetectronBoxes(df, categories)
        record = {
            'image_id': int(boxes),
            'file_name': str(info),
            'annotations': list(boxes),
        }
        record.update(info.shape())

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
        json.dump(data, sys.stdout)
