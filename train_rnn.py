import tensorflow as tf
from build_rnn import AFD_RNN
from utils import parser_cfg_file
from load_data import LoadData

def train_rnn():
    train_content = parser_cfg_file('./config/train.cfg')
    learing_rate = float(train_content['learning_rate'])
    train_iterior = int(train_content['train_iteration'])

    rnn_net = AFD_RNN()
    predict = rnn_net.build_net_graph()
    label = tf.placeholder(tf.float32, [None, rnn_net.time_step, rnn_net.class_num])

    with tf.name_scope('loss'):
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=label, logits=predict))
        train_op = tf.train.AdamOptimizer(learing_rate).minimize(loss)

    with tf.name_scope('accuracy'):
        correct_pred = tf.equal(tf.argmax(label, 1), tf.argmax(predict, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

    dataset = LoadData('./dataset/train/', time_step=rnn_net.time_step, class_num= rnn_net.class_num)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        current_epoch = dataset.epoch

        for step in range(train_iterior):
            x, y = dataset.get_next_batch(rnn_net.batch_size)
            if step == 0:
                feed_dict = {rnn_net.x:x, label:y}
            else:
                feed_dict = {rnn_net.x: x, label: y, rnn_net.cell_state:state}
            _, compute_loss, state = sess.run([train_op, loss, rnn_net.cell_state], feed_dict=feed_dict)

            if step%10 == 0:
                compute_accuracy = sess.run(accuracy, feed_dict=feed_dict)
                print('train step = %d,loss = %f,accuracy = %f'%(step, compute_loss, compute_accuracy))
            if current_epoch != dataset.epoch:
                current_epoch = dataset.epoch
                compute_accuracy = sess.run(accuracy, feed_dict=feed_dict)
                print('train epoch = %d,loss = %f,accuracy = %f' % (current_epoch, compute_loss, compute_accuracy))

train_rnn()