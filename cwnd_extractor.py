import sys
import pandas as pd
from cwnd_estimator import CwndEstimator
from cwnd_splitter import CwndSplitter
from cwnd_filter import CwndFilter
from cwnd_normalizer import CwndNormalizer

seq_len = 128

def main():
    input = sys.argv[1]
    output = sys.argv[2]

    estimator = CwndEstimator()
    df = estimator.estimate(input)

    splitter = CwndSplitter()
    dfs = splitter.split(df)

    filter = CwndFilter()
    dfs = filter.first(dfs)

    ndfs = []
    normalizer = CwndNormalizer(seq_len)
    for d in dfs:
        ndfs.append(normalizer.normalize(d))

    seq_df = pd.DataFrame(columns=[i for i in range(seq_len)])
    for d in ndfs:
        tmp = pd.Series(d['cwnd'], index=seq_df.columns)
        seq_df = seq_df.append(tmp, ignore_index=True)

    seq_df.to_csv(output, mode='a', header=False, index=False)

if __name__ == '__main__':
    main()
