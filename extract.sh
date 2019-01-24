source venv/bin/activate

ALGO_LIST="reno cubic bbr bic westwood htcp vegas veno scalable highspeed "

for algo in $ALGO_LIST; do
	echo Extract : Train $algo
	python3 cwnd_extractor.py $algo 0 9 data/train/$algo.csv
done

for algo in $ALGO_LIST; do
	echo Extract : Test $algo
	python3 cwnd_extractor.py $algo 10 19 data/test/$algo.csv
done

./wc.sh
