import os
import sys
import pandas as pd


class CwndNormalizer(object):
    def __init__(self, seq_len):
        self.seq_len = seq_len

    def normalize(self, df):
        df = df.astype(float)
        ndf = (df - df.min()) / (df.max() - df.min())
        ndf['retransmit'] = df['retransmit']

        ts = []
        cwnd = []

        seq_len = self.seq_len
        ratio = len(df) / seq_len

        t = 0
        for t in range(seq_len):
            i = int(t * ratio)
            ts.append(ndf['ts'][i])
            cwnd.append(ndf['cwnd'][i])

        data = {'ts': ts, 'cwnd': cwnd}
        return pd.DataFrame(data)


def main():
    input = sys.argv[1]
    output = sys.argv[2]
    df = pd.read_csv(input)
    normalizer = CwndNormalizer(128)
    ndf = normalizer.normalize(df)
    ndf.to_csv(output)


if __name__ == '__main__':
    main()
