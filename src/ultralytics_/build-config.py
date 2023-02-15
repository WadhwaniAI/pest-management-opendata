from pathlib import Path
from argparse import ArgumentParser

import yaml
import pandas as pd

def ipaths(df, root='images'):
    for i in df['split'].unique():
        path = Path(root, i)
        yield (i, str(path))

#
#
#
if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--metadata', action='append', type=Path)
    arguments.add_argument('--output-root', type=Path)
    args = arguments.parse_args()

    df = pd.concat(pd.read_csv(x, compression='gzip') for x in args.metadata)
    labels = df['label'].dropna().unique()

    config = {
        'path': str(args.output_root),
        'names': dict(enumerate(sorted(labels))),
    }
    config.update(ipaths(df))

    print(yaml.dump(config), end='')
