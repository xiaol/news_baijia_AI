#-*- encoding:utf-8 -*-
"""
Created on May 30, 2015
@author: Gavin
"""

import sys
import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence
reload(sys)
sys.setdefaultencoding('utf-8')
import jieba
from gensim import corpora, models, similarities

class Gist:

    def __init__(self, stop_words_file='stopword.data'):
            self.stop_words_file=stop_words_file
            self.tr4w = TextRank4Keyword(self.stop_words_file)  # 导入停止词

    def get_keyword(self, text):
            self.tr4w = TextRank4Keyword(self.stop_words_file)  # Import stopwords
            #Use word class filtering，decapitalization of text，window is 2.
            self.tr4w.train(text=text, speech_tag_filter=True, lower=True, window=2)
            # 20 keywords The min length of each word is 1.
            self.wresult = ' '.join(self.tr4w.get_keywords(20, word_min_len=1))
            return self.wresult

    def get_keyphrase(self):
            #Use 20 keywords for contructing phrase, the phrase occurrence in original text is at least 2.
            self.presult = ' '.join(self.tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2))
            self.tr4s = TextRank4Sentence(self.stop_words_file)
            return self.presult

    def get_gist(self, text):
            # self.tr4w = TextRank4Keyword(self.stop_words_file)  # 导入停止词
            #使用词性过滤，文本小写，窗口为2
            self.tr4w.train(text=text, speech_tag_filter=True, lower=True, window=2)
            # 20个关键词且每个的长度最小为1
            self.wresult = ' '.join(self.tr4w.get_keywords(20, word_min_len=1))
            # 20个关键词去构造短语，短语在原文本中出现次数最少为2
            self.presult = ' '.join(self.tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2))
            self.tr4s = TextRank4Sentence(self.stop_words_file)
            # 使用词性过滤，文本小写，使用words_all_filters生成句子之间的相似性
            self.tr4s.train(text=text, speech_tag_filter=True, lower=True, source = 'all_filters')
            self.gresult = ' '.join(self.tr4s.get_key_sentences(num=1)) # 重要性最高的三个句子
            return self.gresult

#query is a string, textList is a list of strings.
#If a query only compares itself against itself or only one another document, the result is always 1.
def cal_sim(query, textList):

    textList = [list(jieba.cut(text)) for text in textList]

    dictionary = corpora.Dictionary(textList)
    corpus = [dictionary.doc2bow(text) for text in textList]
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2) # initialize an LSI transformation
    query_bow = dictionary.doc2bow(list(jieba.cut(query)))


    query_lsi = lsi[query_bow]
    index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it
    sims = index[query_lsi]
    print sims
    return sims

if __name__ == "__main__":
    a = Gist().get_gist(codecs.open('/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/text/01.txt', 'r', 'utf-8').read())
    b = Gist().get_gist(codecs.open('/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/text/02.txt', 'r', 'utf-8').read())
    c = Gist().get_gist(codecs.open('/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/text/05.txt', 'r', 'utf-8').read())

    x = '上个周末，吉林农业科技学院经济管理学院赵同学，本来是因为得到了一张长春市的演出邀请券，从吉林市到长春市玩，不想在重庆路逛街的途中竟看到了一个正在行窃的小偷，并用手机拍下了小偷行窃的全过程。 '
    y = '这小偷还挺有职业道德，只偷钱，又把钱包放回去了，钱包里都是各种卡啊身份证啥的，补办起来很麻烦，很体贴的小偷，赞一个。'
    z = '这小偷还挺有职业道德，只偷钱，又把钱包放回去了，钱包里都是各种卡啊身份证啥的，补办起来很麻烦。'
    textList = []
    textList.append(x)
    textList.append(x)
    textList.append(y)
    textList.append(z)
    cal_sim(x, textList)











