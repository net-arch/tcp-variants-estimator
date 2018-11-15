import os
import sys
import pandas as pd
import matplotlib.pyplot as plt


def main():
    input = sys.argv[1]

    df = pd.read_csv(input)
    df = df[['ts', 'cwnd']]
    df.plot(x=df.columns[0])

    if len(sys.argv) > 2:
        output = sys.argv[2]
        plt.save(output)
    else:
        plt.show()


if __name__ == '__main__':
    main()
