import random
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.contrib import rnn

random.seed(777)
np.random.seed(777)
tf.set_random_seed(777)

# パラメーター
N_CLASSES = 3  # クラス数
N_INPUTS = 1  # 1ステップに入力されるデータ数
N_STEPS = 2000  # 学習ステップ数
SEQ_LEN = 128  # 系列長
N_NODES = 128  # ノード数
N_DATA = 200  # 各クラスの学習用データ数
N_TEST = 200  # テスト用データ数
BATCH_SIZE = 128  # バッチサイズ


def read_dataframe(tcp, l, n):
    path = 'result/{}.csv'.format(tcp)
    df = pd.read_csv(path).dropna()[-1*n:]    # 前から / 後ろから
    label = np.full([n, 1], l)
    return np.hstack((df.values, label)).reshape(-1, SEQ_LEN+1, 1)

def gen_dataset(seq_len, n_data):
    class_01_data = read_dataframe('cubic', 0, n_data)
    class_02_data = read_dataframe('reno', 1, n_data)
    class_03_data = read_dataframe('bbr', 2, n_data)
    dataset = np.r_[class_01_data, class_02_data, class_03_data]
    np.random.shuffle(dataset)
    x_ = dataset[:, :seq_len]
    t_ = dataset[:, seq_len].reshape(-1)
    return x_, t_


x_train, t_train = gen_dataset(SEQ_LEN, N_DATA)  # 学習用データセット
x_test, t_test = gen_dataset(SEQ_LEN, N_TEST)  # テスト用データセット

# モデルの構築
x = tf.placeholder(tf.float32, [None, SEQ_LEN, N_INPUTS])  # 入力データ
t = tf.placeholder(tf.int32, [None])  # 教師データ
t_on_hot = tf.one_hot(t, depth=N_CLASSES, dtype=tf.float32)  # 1-of-Kベクトル
cell = rnn.LSTMCell(num_units=N_NODES, activation=tf.nn.tanh)  # 中間層のセル
# RNNに入力およびセル設定する
outputs, states = tf.nn.dynamic_rnn(
    cell=cell, inputs=x, dtype=tf.float32, time_major=False)
# [ミニバッチサイズ,系列長,出力数]→[系列長,ミニバッチサイズ,出力数]
outputs = tf.transpose(outputs, perm=[1, 0, 2])

w = tf.Variable(tf.random_normal([N_NODES, N_CLASSES], stddev=0.01))
b = tf.Variable(tf.zeros([N_CLASSES]))
logits = tf.matmul(outputs[-1], w) + b  # 出力層
pred = tf.nn.softmax(logits)  # ソフトマックス

cross_entropy = tf.nn.softmax_cross_entropy_with_logits(
    labels=t_on_hot, logits=logits)
loss = tf.reduce_mean(cross_entropy)  # 誤差関数
train_step = tf.train.AdamOptimizer().minimize(loss)  # 学習アルゴリズム

correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(t_on_hot, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))  # 精度

# 学習の実行
sess = tf.Session()
sess.run(tf.global_variables_initializer())
i = 0
for _ in range(N_STEPS):
    cycle = int(N_DATA * 3 / BATCH_SIZE)
    begin = int(BATCH_SIZE * (i % cycle))
    end = begin + BATCH_SIZE
    x_batch, t_batch = x_train[begin:end], t_train[begin:end]
    sess.run(train_step, feed_dict={x: x_batch, t: t_batch})
    i += 1
    if i % 10 == 0:
        loss_, acc_ = sess.run([loss, accuracy], feed_dict={
                               x: x_batch, t: t_batch})
        loss_test_, acc_test_ = sess.run(
            [loss, accuracy], feed_dict={x: x_test, t: t_test})
        print("[TRAIN] loss : %f, accuracy : %f" % (loss_, acc_))
        print("[TEST loss : %f, accuracy : %f" % (loss_test_, acc_test_))
sess.close()
