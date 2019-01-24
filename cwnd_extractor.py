import sys
import pandas as pd
from cwnd_splitter import CwndSplitter
from cwnd_filter import CwndFilter
from cwnd_normalizer import CwndNormalizer

seq_len = 128

def extract(df):
    splitter = CwndSplitter()
    dfs = splitter.split(df)

    filter = CwndFilter()
    dfs = filter.first(dfs)
    return dfs


def main():
    algo = sys.argv[1]
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    output = sys.argv[4]

    dfs = []

    for i in range(start, end):
        filepath = "data/estimate/{}.{}.csv".format(algo, i)
        df = pd.read_csv(filepath)
        _dfs = extract(df)
        dfs.extend(_dfs)

    dfs.sort(key=lambda df: len(df), reverse=True)

    ndfs = []
    normalizer = CwndNormalizer(seq_len)
    for d in dfs:
        ndfs.append(normalizer.normalize(d))

    seq_df = pd.DataFrame(columns=[i for i in range(seq_len)])
    for d in ndfs:
        tmp = pd.Series(d['cwnd'], index=seq_df.columns)
        seq_df = seq_df.append(tmp, ignore_index=True)

    seq_df.to_csv(output, header=False, index=False)


if __name__ == '__main__':
    main()
