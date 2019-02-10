source ./env.sh

for tcp in $TCP_LIST[@]; do
  for i in $(seq $S $E); do
    echo $tcp $i started...
    time python3 cwnd_estimator.py data/dump/$tcp.$i.dump data/estimate/$tcp.$i.csv
    echo $tcp $i end...
    echo
  done
done
