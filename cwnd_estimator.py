# -*- coding: utf-8 -*-
import sys
from datetime import datetime
from socket import inet_ntoa
from binascii import hexlify
import dpkt


client = '192.168.2.2'
server = '192.168.1.2'
mss = 1480


# pritn packet
def pp(p, msg=None):
    display = ""
    if msg is not None:
        display += msg + "\n"
    display += "ts: {}, src: {}, dst: {}, seq: {}, ack: {}, tsval: {}, tsecr: {}" \
                .format(p['ts'], p['src'], p['dst'], p['seq'], p['ack'], int(p['tsval'], 16), int(p['tsecr'], 16))

    print(display)


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

        if p['ack'] > fs_seq:
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
            # pp(ack1, 'data1 not found')
            continue

        ack1_dash, ack2 = search_acks(packets[i:], data1['seq'])
        if ack1_dash is None:
            # pp(ack1, 'ack1_dash not found')
            continue

        if ack2 is None:
            pp(ack1, 'ack2 not found')
            continue

        data2 = search_data(packets[i:], ack2['tsval'])
        if data2 is None:
            # pp(ack1, 'data2 not found')
            continue

        cwnd = int((data2['seq'] - ack1_dash['ack']) / mss)
        print( '{1},{2}'.format(i, ack1['ts'], cwnd))


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
    start = None

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

        if start is None:
            start = datetime.utcfromtimestamp(t)

        td = datetime.utcfromtimestamp(t) - start
        packets.append({
            'ts': '{}.{:06}'.format(td.seconds, td.microseconds),
            'src': src_a,
            'dst': dst_a,
            'seq': tcp.seq,
            'ack': tcp.ack,
            'tsval': tsval,
            'tsecr': tsecr
        })

    calc_cwnd(packets)


if __name__ == '__main__':
    main()
