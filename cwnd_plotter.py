import os
import sys
import pandas as pd
import matplotlib.pyplot as plt


def main():
    estimate_path = sys.argv[1]

    plt.rcParams['font.size'] = 20

    df = pd.read_csv(estimate_path)
    df = df[['t', 'cwnd']].rename(columns={'t': 'Time [s]'})
    ax = df.plot(x=df.columns[0], figsize=(16, 10), fontsize=20)
    ax.set_ylabel('Window Size [segments]')

    if len(sys.argv) > 2:
        figure_path = sys.argv[2]
        plt.savefig(figure_path)
    else:
        plt.show()


if __name__ == '__main__':
    main()
