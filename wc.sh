ALGO_LIST="reno cubic bbr bic westwood htcp vegas veno scalable highspeed "

# CHECK
for algo in $ALGO_LIST; do
	wc -l data/train/$algo.csv
	wc -l data/test/$algo.csv
	echo
done
