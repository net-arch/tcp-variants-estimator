# -*- coding: utf-8 -*-

# python cwnd_estimator.py "path/to/dumpfile" "path/to/estimatefile.csv"

import sys
from datetime import datetime
from socket import inet_ntoa
from binascii import hexlify
import dpkt
import pandas as pd


class CwndEstimator(object):
    def __init__(self, client, server, mss, port=None):
        self.client = client
        self.server = server
        self.mss = mss
        self.port = port

    # print packet
    def pp(self, p, msg=None):
        display = ''
        if msg is not None:
            display += msg + '\n'
        display += 't: {}, '.format(p['t'])
        display += 'src: {}, '.format(p['src'])
        display += 'dst: {}, '.format(p['dst'])
        display += 'seq: {}, '.format(p['seq'])
        display += 'ack: {}, '.format(p['ack'])
        display += 'tsval: {}, '.format(int(p['tsval'], 16))
        display += 'tsecr: {}'.format(int(p['tsecr'], 16))

        print(display)

    def is_ack(self, p):
        return p['src'] == self.server

    def search_data(self, packets, ack_tsval):
        """
        ack の tsval を tsecr に持つ packet を返す
        """

        for p in packets:
            if p['src'] == self.client and p['tsecr'] >= ack_tsval:
                return p

    def search_acks(self, packets, data_seq):
        """
        data の seq に対応する ack を持つ packet とその前の packet を返す
        """

        pre = None
        for p in packets:
            if p['src'] != self.server:
                continue

            if p['ack'] > data_seq:
                # sequence 32bit 一巡対策　かなりいい加減
                if abs(p['ack'] - data_seq) < 2 ** 31:
                    return pre, p

            pre = p

        return None, None

    def check_retransmit(self, packets, data1, ack1_dash):
        pre_ack = None

        for p in packets:
            if float(p['t']) < float(data1['t']):
                continue

            if float(p['t']) > float(ack1_dash['t']):
                break

            if not self.is_ack(p):
                continue

            if pre_ack is None:
                pre_ack = p
                continue

            if pre_ack['ack'] == p['ack']:
                return True

            pre_ack = p

        return False

    def estimate_cwnd(self, packets):
        results = []

        pre_cwnd = 0
        cwnd = 0
        ack2 = None
        retransmit = False

        for i, p in enumerate(packets):
            if not self.is_ack(p):
                continue
            ack1 = p

            if ack2 is not None and ack1 is not ack2:
                continue

            data1 = self.search_data(packets[i:], ack1['tsval'])
            if data1 is None:
                # pp(ack1, 'data1 not found')
                continue

            ack1_dash, ack2 = self.search_acks(packets[i:], data1['seq'])
            if ack1_dash is None:
                # pp(ack1, 'ack1_dash not found')
                continue

            if ack2 is None:
                # pp(ack1, 'ack2 not found')
                continue

            data2 = self.search_data(packets[i:], ack2['tsval'])
            if data2 is None:
                # pp(ack1, 'data2 not found')
                continue

            if self.check_retransmit(packets[i:], data1, ack1_dash):
                retransmit = True
                # pp(ack1, 'retransmit detected')
                continue

            pre_cwnd = cwnd

            snd_bytes = (data2['seq'] - ack1_dash['ack'])
            if snd_bytes < 0:
                snd_bytes += 2 ** 32

            cwnd = int(snd_bytes / self.mss)

            result = [
                ack1['t'],
                cwnd,
                cwnd - pre_cwnd,
                int(retransmit)
            ]
            results.append(result)

            retransmit = False

        return results

    def parse_timestamp_opts(self, opts):
        for _type, raw_data in opts:
            if _type != dpkt.tcp.TCP_OPT_TIMESTAMP:
                continue

            d = hexlify(raw_data)
            return d[:8], d[8:]
        return None, None

    def estimate(self, filepath):
        with open(filepath, 'rb') as f:
            p = dpkt.pcap.Reader(f)

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
                tsval, tsecr = self.parse_timestamp_opts(options)

                # キャプチャファイルと同じタイムスタンプ表示
                if start_ts is None:
                    start_ts = datetime.utcfromtimestamp(t)

                # iperf3 の制御ストリームは除外
                if self.port == None:
                    self.port = tcp.sport

                if tcp.sport == self.port or tcp.dport == self.port:
                    continue

                if tcp.flags & dpkt.tcp.TH_RST:
                    break

                td = datetime.utcfromtimestamp(t) - start_ts
                packets.append({
                    't': '{}.{:06}'.format(td.seconds, td.microseconds),
                    'src': src_a,
                    'dst': dst_a,
                    'seq': tcp.seq,
                    'ack': tcp.ack,
                    'tsval': tsval,
                    'tsecr': tsecr
                })

            results = self.estimate_cwnd(packets)
            columns = ['t', 'cwnd', 'delta', 'retransmit']
            df = pd.DataFrame(results, columns=columns)
            return df


def main():
    dump_path = sys.argv[1]
    estimate_path = sys.argv[2]

    client = '192.168.2.2'
    server = '192.168.1.2'
    mss = 1448  # iperf3 mss: 1460 となり, 1460 - 12 (options) = 1448

    estimator = CwndEstimator(client, server, mss)
    df = estimator.estimate(dump_path)
    df.to_csv(estimate_path, index=False)


if __name__ == '__main__':
    main()
