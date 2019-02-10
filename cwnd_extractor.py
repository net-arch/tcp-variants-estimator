import sys
import pandas as pd

seq_len = 128

def CwndEXtractor(object):
    def __init__(self, seq_len):
        self.seq_len = seq_len

    def split(self, df):
        retransmits = np.where(df['retransmit'] == 1)[0]
        dfs = []

        s = 0
        for e in retransmits:
            dfs.append(df[s:e].reset_index(drop=True))
            s = e
        return dfs

    def drop_first(self, dfs):
        return dfs[1:]

    def normalize(df):
        df = df.astype(float)
        ndf = (df - df.min()) / (df.max() - df.min())
        ndf['retransmit'] = df['retransmit']

        t = []
        cwnd = []

        seq_len = seq_len
        ratio = len(df) / seq_len

        i = 0
        for i in range(seq_len):
            index = int(i * ratio)
            t.append(ndf['t'][index])
            cwnd.append(ndf['cwnd'][index])

        data = {'t': t, 'cwnd': cwnd}
        return pd.DataFrame(data)

    def extract


def main():
    tcp = sys.argv[1]
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    output = sys.argv[4]

    extractor = CwndEXtractor(seq_len)

    dfs = []

    for i in range(start, end):
        filepath = "data/estimate/{}.{}.csv".format(tcp, i)
        df = pd.read_csv(filepath)
        tmp = extractor.split(df)
        tmp = extractor.drop_first(tmp)
        dfs.extend(tmp)

    dfs.sort(key=lambda df: len(df), reverse=True)

    ndfs = []
    for d in dfs:
        ndfs.append(extractor.normalize(d))

    seq_df = pd.DataFrame(columns=[i for i in range(seq_len)])
    for d in ndfs:
        tmp = pd.Series(d['cwnd'], index=seq_df.columns)
        seq_df = seq_df.append(tmp, ignore_index=True)

    seq_df.to_csv(output, header=False, index=False)


if __name__ == '__main__':
    main()
