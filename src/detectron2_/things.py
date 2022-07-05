import sys
import json
import operator as op

import pandas as pd

from lib import Logger, LabelClass

if __name__ == '__main__':
    df = pd.read_csv(sys.stdin, usecols=['label'])
    lc = LabelClass(df)

    json.dump(list(map(op.itemgetter(1), lc)), sys.stdout)
