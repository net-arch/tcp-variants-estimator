./env.sh

for tcp in $TCP_LIST; do
  for i in $(seq $start $end); do
    FILEPATH="data/dump/$tcp.$i.dump"
    rm -f $FILEPATH

    echo
    echo [ $tcp $i ]
    echo

    sleep 2
    tcpdump host 192.168.1.2 -i enp0s25 -w $FILEPATH &
    PID=$!
    echo capture started... PID:$PID

    sleep 2
    iperf3 -c 192.168.1.2 -t 600 -C $tcp
    kill $PID
    echo capture stopped... PID:$PID
  done
done
