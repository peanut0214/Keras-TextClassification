# -*- coding: UTF-8 -*-
# !/usr/bin/python
# @time     :2019/6/3 10:51
# @author   :Mo
# @function :train of fast text with baidu-qa-2019 in question title


# 适配linux
import pathlib
import sys
import os

project_path = str(pathlib.Path(os.path.abspath(__file__)).parent.parent.parent)
sys.path.append(project_path)
# 地址
from keras_textclassification.conf.path_config import path_model, path_fineture, \
                                                      path_model_dir, path_hyper_parameters
# 训练验证数据地址
from keras_textclassification.conf.path_config import path_baidu_qa_2019_train, path_baidu_qa_2019_valid, path_root

# 数据预处理, 删除文件目录下文件
from keras_textclassification.data_preprocess.text_preprocess import PreprocessText, PreprocessSim, delete_file
# 模型图
from keras_textclassification.m10_DeepMoji.graph import DeepMojiGraph as Graph
# 计算时间
import time




# fast_text config
# 模型目录
path_model_dir =  path_root + "/data/model/ccks_2020_el_cls_deepmoji/"
# 语料地址
path_model = path_model_dir + 'model_fast_text.h5'
# 超参数保存地址
path_hyper_parameters =  path_model_dir + 'hyper_parameters.json'
# embedding微调保存地址
path_fineture = path_model_dir + "embedding_trainable.h5"

if not os.path.exists(path_model_dir):
    os.mkdir(path_model_dir)

def train(hyper_parameters=None, rate=1.0):
    """
        训练函数
    :param hyper_parameters: json, 超参数
    :param rate: 比率, 抽出rate比率语料取训练
    :return: None
    """
    if not hyper_parameters:
        hyper_parameters = {
            'len_max': 1376,  # 句子最大长度, 固定 推荐20-50
            'embed_size': 300,  # 字/词向量维度
            'vocab_size': 20000,  # 这里随便填的，会根据代码里修改
            'trainable': True,  # embedding是静态的还是动态的, 即控制可不可以微调
            'level_type': 'char',  # 级别, 最小单元, 字/词, 填 'char' or 'word'
            'embedding_type': 'random',  # 级别, 嵌入类型, 还可以填'xlnet'、'random'、 'bert'、 'albert' or 'word2vec"
            'gpu_memory_fraction': 0.8,  # gpu使用率
            'model': {'label': 23,  # 类别数
                      'batch_size': 16,  # 批处理尺寸, 感觉原则上越大越好,尤其是样本不均衡的时候, batch_size设置影响比较大
                      'dropout': 0.5,  # 随机失活, 概率
                      'decay_step': 100,  # 学习率衰减step, 每N个step衰减一次
                      'decay_rate': 0.999,  # 学习率衰减系数, 乘法
                      'epochs': 20,  # 训练最大轮次
                      'patience': 6,  # 早停,2-3就好
                      'lr': 1e-3,  # 学习率, 对训练会有比较大的影响, 如果准确率一直上不去,可以考虑调这个参数
                      'l2': 1e-6,  # l2正则化
                      'activate_classify': 'softmax',  # 最后一个layer, 即分类激活函数
                      'loss': 'categorical_crossentropy',  # 损失函数
                      'metrics': 'accuracy',  # 保存更好模型的评价标准
                      'is_training': True,  # 训练后者是测试模型
                      'model_path': path_model,  # 模型地址, loss降低则保存的依据, save_best_only=True, save_weights_only=True
                      'path_hyper_parameters': path_hyper_parameters,  # 模型(包括embedding)，超参数地址,
                      'path_fineture': path_fineture,  # 保存embedding trainable地址, 例如字向量、词向量、bert向量等
                      'rnn_type': 'GRU', # type of rnn, select 'LSTM', 'GRU', 'Bidirectional-GRU'
                      'rnn_units': 150,  # RNN隐藏层,
                      },
            'embedding': {'layer_indexes': [12],  # bert取的层数,
                          # 'corpus_path': '',     # embedding预训练数据地址,不配则会默认取conf里边默认的地址, keras-bert可以加载谷歌版bert,百度版ernie(需转换，https://github.com/ArthurRizar/tensorflow_ernie),哈工大版bert-wwm(tf框架，https://github.com/ymcui/Chinese-BERT-wwm)
                          },
            'data': {'train_data': path_ccks_2020_el_cls_train,  # 训练数据
                     'val_data': path_ccks_2020_el_cls_dev  # 验证数据
                     },
        }

    # 删除先前存在的模型\embedding微调模型等
    # delete_file(path_model_dir)
    time_start = time.time()
    # graph初始化
    graph = Graph(hyper_parameters)
    print("graph init ok!")
    ra_ed = graph.word_embedding
    # 数据预处理
    pt = PreprocessSim(path_model_dir)
    x_train, y_train = pt.preprocess_label_ques_to_idx(hyper_parameters['embedding_type'],
                                                       hyper_parameters['data']['train_data'],
                                                       ra_ed, rate=rate, shuffle=True)
    x_val, y_val = pt.preprocess_label_ques_to_idx(hyper_parameters['embedding_type'],
                                                   hyper_parameters['data']['val_data'],
                                                   ra_ed, rate=rate, shuffle=True)
    print("data propress ok!")
    print(len(y_train))
    # 训练
    graph.fit(x_train, y_train, x_val, y_val)
    print("耗时:" + str(time.time() - time_start))


if __name__ == "__main__":
    train(rate=1)
