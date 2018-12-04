import os
import sys
import numpy as np
import pandas as pd


class CwndSplitter(object):
    def split(self, df):
        retransmits = np.where(df['retransmit'] == 1)[0]

        dfs = []

        s = 0
        for e in retransmits:
            dfs.append(df[s:e])
            s = e
        return dfs


def main():
    input = sys.argv[1]
    output = sys.argv[2]

    df = pd.read_csv(input)

    splitter = CwndSplitter()
    dfs = splitter.split(df)
    for i, d in enumerate(dfs):
        d.to_csv('{}.{}.csv'.format(output, i), float_format='%.6f', index=False)


if __name__ == '__main__':
    main()
