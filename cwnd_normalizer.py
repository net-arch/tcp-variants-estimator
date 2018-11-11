import os, sys
import pandas as pd

seq_len = 128


def min_max(x):
    min = x.min()
    max = x.max()
    result = (x-min)/(max-min)#
    return result


def main():
    filepath = sys.argv[1]

    print('ts,cwnd')

    df = pd.read_csv(filepath)

    ts = min_max(df['ts'].values)
    cwnd = min_max(df['cwnd'].values)

    i, t = 0, 0
    for t in range(seq_len):
        if (t-1)/seq_len < ts[i] <= t / seq_len:
            print('{},{}'.format(ts[i], cwnd[i]))
            i += 1
        else:
            print('{},{}'.format(ts[i], cwnd[i]))


if __name__ == '__main__':
    main()
