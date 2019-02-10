source ./env.sh

for tcp in ${TCP_LIST[@]}; do
  echo $tcp
  python3 plotter.py --mode cwnd data/estimate_for_graph/$tcp.csv --output data/img/estimate/$tcp.pdf --fontsize 24 --width 16 --height 10
done
