import os
import sys
import numpy as np
import pandas as pd


class CwndSplitter(object):
    def __init__(self, df):
        self.df = df
        self.dfs = []

    def split(self):
        df = self.df
        retransmits = np.where(df['retransmit'] == 1)[0]

        s = 0
        for e in retransmits:
            self.dfs.append(df[s:e])
            s = e
        return self.dfs


def main():
    input = sys.argv[1]
    output = sys.argv[2]

    df = pd.read_csv(input)

    splitter = CwndSplitter(df)
    dfs = splitter.split()
    for i, d in enumerate(dfs):
        d.to_csv('{}.{}.csv'.format(output, i), float_format='%.6f', index=False)


if __name__ == '__main__':
    main()
