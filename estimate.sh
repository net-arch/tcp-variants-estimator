source venv/bin/activate

ALGO_LIST="reno cubic bbr bic westwood htcp vegas veno scalable highspeed "

for algo in $ALGO_LIST; do
  for i in {10..19}; do
    echo $algo $i
    time python3 cwnd_estimator.py data/dump/$algo.$i.dump data/estimate/$algo.$i.csv
  done
done
