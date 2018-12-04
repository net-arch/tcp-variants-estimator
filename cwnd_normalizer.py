import os
import sys
import pandas as pd


class CwndNormalizer(object):
    def __init__(self, seq_len):
        self.seq_len = seq_len

    def normalize(self, df):
        df = df.astype(float).reset_index(drop=True)
        dn = (df - df.min()) / (df.max() - df.min())
        dn['retransmit'] = df['retransmit']

        ts = []
        cwnd = []

        seq_len = self.seq_len
        ratio = len(df) / seq_len

        t = 0
        for t in range(seq_len):
            i = int(t * ratio)
            ts.append(dn['ts'][i])
            cwnd.append(dn['cwnd'][i])

        data = {'ts': ts, 'cwnd': cwnd}
        return pd.DataFrame(data)


def main():
    input = sys.argv[1]
    output = sys.argv[2]
    df = pd.read_csv(input)
    normalizer = CwndNormalizer(128)
    dn = normalizer.normalize(df)
    dn.to_csv(output)


if __name__ == '__main__':
    main()
