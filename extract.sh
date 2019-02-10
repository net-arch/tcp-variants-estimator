./env.sh


for tcp in $TCP_LIST[@]; do
  echo Extract : Train $tcp
  python3 cwnd_extractor.py $tcp $TRAIN_S $TRAIN_E data/train/$tcp.csv
done

for tcp in $TCP_LIST[@]; do
  echo Extract : Test $tcp
  python3 cwnd_extractor.py $tcp $TEST_S $TEST_E data/test/$tcp.csv
done

# check
for tcp in ${TCP_LIST[@]}; do
  wc -l data/train/$tcp.csv
  wc -l data/test/$tcp.csv
done
