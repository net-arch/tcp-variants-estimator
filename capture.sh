ALGO_LIST="reno cubic bbr bic westwood htcp vegas veno scalable highspeed "

for ALGO in $ALGO_LIST; do
  for i in {0..19}; do
    FILEPATH="data/dump/${ALGO}.${i}.dump"
    rm -f $FILEPATH

    echo
    echo [ $ALGO $i ]
    echo

    sleep 2
    tcpdump host 192.168.1.2 -i enp0s25 -w $FILEPATH &
    PID=$!
    echo capture started... PID:$PID

    sleep 2
    iperf3 -c 192.168.1.2 -t 600 -C ${ALGO}
    kill ${PID}
    echo capture stopped... PID:$PID
  done
done
