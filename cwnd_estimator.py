# -*- coding: utf-8 -*-

import sys
from datetime import datetime
from socket import inet_ntoa
from binascii import hexlify
import dpkt

client = '192.168.2.2'
server = '192.168.1.2'
mss = 1500

def is_ack(p):
    return p['src'] == server

def search_data(packets, ack_tsval):
    for i, p in enumerate(packets):
        if p['src'] == client and p['tsecr'] == ack_tsval:
            return p

def search_acks(packets, fs_seq):
    pre = None
    for i, p in enumerate(packets):
        if p['src'] != server:
            continue

        if p['ack'] >= fs_seq:
            return pre, p

        pre = p

def calc_cwnd(packets):
    cwnd = '0'
    for i, p in enumerate(packets):
        if not is_ack(p):
            continue

        ack1 = p

        data1 = search_data(packets[i:], ack1['tsval'])
        if data1 is None:
            continue

        ack1_dash, ack2 = search_acks(packets[i:], data1['seq'])
        if ack1_dash is None:
            continue

        data2 = search_data(packets[i:], ack2['tsval'])
        if data2 is None:
            continue

        cwnd = int((data2['seq'] - ack1_dash['ack']) / mss)
        print '{1},{2}'.format(i, ack1['ts'], cwnd)


def parse_timestamp_opts(opts):
    for type, raw_data in opts:
        if type != dpkt.tcp.TCP_OPT_TIMESTAMP:
            continue

        d = hexlify(raw_data)
        return d[:8], d[8:]
    return None, None

def main():
    filepath = sys.argv[1]
    p = dpkt.pcap.Reader(open(filepath,'rb'))

    packets = []
    syn = 0

    for t, buf in p:
        eth = dpkt.ethernet.Ethernet(buf)

        ip = eth.data
        src = ip.src
        dst = ip.dst
        src_a = inet_ntoa(src)
        dst_a = inet_ntoa(dst)

        tcp = ip.data

        options = dpkt.tcp.parse_opts ( tcp.opts )
        tsval, tsecr = parse_timestamp_opts(dpkt.tcp.parse_opts ( tcp.opts ))

        # iperf3 の最初のコネクション構築は対象外
        if tcp.flags & dpkt.tcp.TH_SYN != 0:
            syn += 1
            start = datetime.utcfromtimestamp(t)

        ts = datetime.utcfromtimestamp(t) - start
        if syn > 2:
            packets.append({
                'ts': '{}.{}'.format(ts.seconds, ts.microseconds),
                'src': src_a,
                'dst': dst_a,
                'seq': tcp.seq,
                'ack': tcp.ack,
                'tsval': tsval,
                'tsecr': tsecr
            })

    # print(packets)
    calc_cwnd(packets)

if __name__ == '__main__':
    main()
