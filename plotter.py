import sys
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt

import argparse
parser = argparse.ArgumentParser(description='')
parser.add_argument('csv', help='Input csv file path')
parser.add_argument('--output', default=None)
parser.add_argument('-m', '--mode',
                    required=True,
                    choices=['cwnd', 'process', 'cm'])
parser.add_argument('--width', type=int, default=12)
parser.add_argument('--height', type=int, default=10)
parser.add_argument('--fontsize', default=20)
parser.add_argument('--epoch', type=int, default=1000)
args = parser.parse_args()

class Plotter(object):
    """docstring for Plotter."""

    def cwnd(self):
        plt.rcParams['font.size'] = args.fontsize

        df = pd.read_csv(args.csv)
        df = df[['t', 'cwnd']].rename(columns={'t': 'Time [s]'})
        ax = df.plot(x=df.columns[0],
                     figsize=(args.width, args.height),
                     fontsize=args.fontsize)
        ax.set_ylabel('Window Size [segments]')
        plt.subplots_adjust(left=0.08, right=0.98, bottom=0.1, top=0.98)
        if args.output is not None:
            plt.savefig(args.output)
        else:
            plt.show()

    def process(self):
        df = pd.read_csv(args.csv)
        df = df.query('Epoch <= {}'.format(args.epoch))
        df.plot(x=df.columns[0],
                fontsize=args.fontsize,
                figsize=(args.width, args.height))
        plt.legend(fontsize=args.fontsize)
        plt.xlabel(df.columns[0], fontsize=args.fontsize)
        plt.yticks(np.arange(0, 1.1, 0.1))

        if args.output is not None:
            plt.savefig(args.output)
        else:
            plt.show()

    def cm(self):
        df = pd.read_csv(args.csv, index_col=0)
        plot_confusion_matrix(
            df.values,
            df.columns,
            normalize=True,
            fontsize=args.fontsize,
            figsize=(args.width, args.height)
        )


# https://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html#sphx-glr-auto-examples-model-selection-plot-confusion-matrix-py
def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues,
                          filepath=None,
                          fontsize=20,
                          figsize=(16, 9)):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print('Normalized confusion matrix')
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.figure(figsize=figsize)
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title, fontsize=fontsize)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=fontsize)
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, fontsize=fontsize, rotation=45)
    plt.yticks(tick_marks, classes, fontsize=fontsize)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment='center',
                 color='white' if cm[i, j] > thresh else 'black',
                 fontsize=fontsize)

    plt.ylabel('True', fontsize=fontsize)
    plt.xlabel('Predicted', fontsize=fontsize)
    plt.tight_layout()

    if filepath is not None:
        plt.savefig(filepath)
    else:
        plt.show()


def main():
    plotter = Plotter()

    if args.mode == 'cwnd':
        plotter.cwnd()

    elif args.mode == 'process':
        plotter.process()

    elif args.mode == 'cm':
        plotter.cm()


if __name__ == '__main__':
    main()
