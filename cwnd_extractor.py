# -*- coding: utf-8 -*-

# python cwnd_extractor.py "path/to/dumpfile"

import sys
import matplotlib.pyplot as plt
from datetime import datetime
from socket import inet_ntoa
from binascii import hexlify
import dpkt


client = '192.168.2.2'
server = '192.168.1.2'
mss = 1448              # iperf3 mss: 1460　となり, 1460 - 12 (options) = 1448
port = 0


def stdout(results):
    print('ts,cwnd,delta,retransmit')
    for i, p in enumerate(results):
        print('{},{},{},{}'.format(
            results[i]['ts'],
            results[i]['cwnd'],
            results[i]['delta'],
            results[i]['retransmit']))


def plot(results, filepath):
    plt.plot(results['ts'], results['cwnd'])
    plt.savefig('images/'+filepath[filepath.rfind('/')+1:filepath.rfind('.')+1]+'png')
    # plt.show()


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
    """
    ack の tsval を tsecr に持つ packet を返す
    """

    for p in packets:
        if p['src'] == client and p['tsecr'] >= ack_tsval:
            return p


def search_acks(packets, fs_seq):
    """
    data の seq に対応する ack の ack を持つ packet とその前の packet を返す
    """

    pre = None
    for p in packets:
        if p['src'] != server:
            continue

        if p['ack'] > fs_seq:
            # sequence 32bit 一巡対策　かなりいい加減
            if abs(p['ack'] - fs_seq) < 2 ** 31:
                return pre, p

        pre = p

    return None, None


def check_retransmit(packets, data1, ack1_dash):
    pre_ack = None

    for p in packets:
        if float(p['ts']) < float(data1['ts']):
            continue

        if float(p['ts']) > float(ack1_dash['ts']):
            break

        if not is_ack(p):
            continue

        if pre_ack is None:
            pre_ack = p
            continue

        if pre_ack['ack'] == p['ack']:
            return True

        pre_ack = p

    return False


def extract_cwnd(packets):
    results = []

    pre_cwnd = 0
    cwnd = 0
    ack2 = None
    retransmit = False

    for i, p in enumerate(packets):
        if not is_ack(p):
            continue
        ack1 = p

        if ack2 is not None and ack1 is not ack2:
            continue

        data1 = search_data(packets[i:], ack1['tsval'])
        if data1 is None:
            # pp(ack1, 'data1 not found')
            continue

        ack1_dash, ack2 = search_acks(packets[i:], data1['seq'])
        if ack1_dash is None:
            # pp(ack1, 'ack1_dash not found')
            continue

        if ack2 is None:
            # pp(ack1, 'ack2 not found')
            continue

        data2 = search_data(packets[i:], ack2['tsval'])
        if data2 is None:
            # pp(ack1, 'data2 not found')
            continue

        if check_retransmit(packets[i:], data1, ack1_dash):
            retransmit = True
            # pp(ack1, 'retransmit detected')
            continue

        pre_cwnd = cwnd

        snd_bytes = (data2['seq'] - ack1_dash['ack'])
        if snd_bytes < 0:
            snd_bytes += 2 ** 32

        cwnd = int(snd_bytes / mss)

        result = {}
        result['ts'] = float(ack1['ts'])
        result['cwnd'] = cwnd
        result['delta'] = cwnd - pre_cwnd
        result['retransmit'] = int(retransmit)
        results.append(result)

        retransmit = False

    return results


def parse_timestamp_opts(opts):
    for _type, raw_data in opts:
        if _type != dpkt.tcp.TCP_OPT_TIMESTAMP:
            continue

        d = hexlify(raw_data)
        return d[:8], d[8:]
    return None, None


def main():
    global port

    filepath = sys.argv[1]
    p = dpkt.pcap.Reader(open(filepath,'rb'))

    packets = []
    start_ts = None

    for t, buf in p:
        eth = dpkt.ethernet.Ethernet(buf)

        ip = eth.data
        src = ip.src
        dst = ip.dst
        src_a = inet_ntoa(src)
        dst_a = inet_ntoa(dst)

        tcp = ip.data

        options = dpkt.tcp.parse_opts(tcp.opts)
        tsval, tsecr = parse_timestamp_opts(options)

        # キャプチャファイルと同じタイムスタンプ表示
        if start_ts is None:
            start_ts = datetime.utcfromtimestamp(t)

        # iperf3 の制御ストリームは除外
        if port == 0:
            port = tcp.sport

        if tcp.sport == port or tcp.dport == port:
            continue

        if tcp.flags & dpkt.tcp.TH_RST:
            break

        td = datetime.utcfromtimestamp(t) - start_ts
        packets.append({
            'ts': '{}.{:06}'.format(td.seconds, td.microseconds),
            'src': src_a,
            'dst': dst_a,
            'seq': tcp.seq,
            'ack': tcp.ack,
            'tsval': tsval,
            'tsecr': tsecr
        })

    results = extract_cwnd(packets)
    stdout(results)
    # plot(results, filepath)


if __name__ == '__main__':
    main()
