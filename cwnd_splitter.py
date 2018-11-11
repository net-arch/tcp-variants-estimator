import os, sys, csv

header = ['ts', 'cwnd', 'delta', 'retransmit']
i = 0


def write(rows, filepath):
    global i

    base = os.path.basename(filepath)
    name, ext = os.path.splitext(base)
    with open('split/{}.{}.csv'.format(name, i), 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)

    i += 1


def main():
    filepath = sys.argv[1]

    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)

        rows = []
        for row in reader:
            if row[3] == '1':
                write(rows, filepath)
                rows = []

            rows.append(row)


if __name__ == '__main__':
    main()
