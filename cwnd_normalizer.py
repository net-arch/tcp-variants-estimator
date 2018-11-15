import os
import sys
import pandas as pd


class CwndNormalizer(object):
    def __init__(self, df, seq_len):
        self.df = df
        self.seq_len = seq_len

    def normalize(self):
        df = self.df
        dn = (df - df.min()) / (df.max() - df.min())
        dn['retransmit'] = df['retransmit']

        ts = []
        cwnd = []

        seq_len = self.seq_len
        width = 1 / seq_len
        t, i = 0, 0
        for t in range(seq_len):
            if t <= dn['ts'][i] / width < (t + 1):
                ts.append(dn['ts'][i])
                cwnd.append(dn['cwnd'][i])
                i += 1
            else:
                ts.append(dn['ts'][i])
                cwnd.append(dn['cwnd'][i])

        data = {'ts': ts, 'cwnd': cwnd}
        return pd.DataFrame(data)


def main():
    input = sys.argv[1]
    output = sys.argv[2]
    df = pd.read_csv(input)
    normalizer = CwndNormalizer(df, 128)
    dn = normalizer.normalize()
    dn.to_csv(output)


if __name__ == '__main__':
    main()
