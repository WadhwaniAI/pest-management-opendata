import sys
import json
import logging
import itertools as it
import collections as cl
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool

import pandas as pd
from detectron2.structures import BoxMode

from lib import Logger, ImageInfo, LabelClass, BoxIterator

from things import read_things

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
def func(args):
    (image, df, categories) = args
    Logger.info(image)

    info = ImageInfo(image)
    boxes = DetectronBoxes(df, categories)
    record = {
        'image_id': int(boxes),
        'file_name': str(info),
        'annotations': list(boxes),
    }
    record.update(info.shape())

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
