import os, sys
import pandas as pd
import matplotlib.pyplot as plt


def main():
    filepath = sys.argv[1]
    df = pd.read_csv(filepath)
    df = df[['ts', 'cwnd']]
    df.plot(x=df.columns[0])
    # plt.save('images/{}.png')
    plt.show()


if __name__ == '__main__':
    main()
