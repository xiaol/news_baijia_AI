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
    # text = codecs.open('/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/text/01.txt', 'r', 'utf-8').read()
    text2 = codecs.open('/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/text/02.txt', 'r', 'utf-8').read()
    text3 = codecs.open('/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/text/02.txt', 'r', 'utf-8').read()
    # stop_words_file='/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/stopword.data'
    # tr4w = TextRank4Keyword(stop_words_file)  # 导入停止词
    # #使用词性过滤，文本小写，窗口为2
    # tr4w.train(text=text, speech_tag_filter=True, lower=True, window=2)
    # # 20个关键词且每个的长度最小为1
    # wresult = ' '.join(tr4w.get_keywords(20, word_min_len=1))
    # # 20个关键词去构造短语，短语在原文本中出现次数最少为2
    # presult = ' '.join(tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2))
    # tr4s = TextRank4Sentence(stop_words_file)
    # # 使用词性过滤，文本小写，使用words_all_filters生成句子之间的相似性
    # tr4s.train(text=text, speech_tag_filter=True, lower=True, source = 'all_filters')
    # gresult = ' '.join(tr4s.get_key_sentences(num=3)) # 重要性最高的三个句子

    def __init__(self, stop_words_file='/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/stopword.data'):
            self.stop_words_file=stop_words_file

    def get_keyword(self, text):
            self.tr4w = TextRank4Keyword(self.stop_words_file)  # 导入停止词
            #使用词性过滤，文本小写，窗口为2
            self.tr4w.train(text=text, speech_tag_filter=True, lower=True, window=2)
            # 20个关键词且每个的长度最小为1
            self.wresult = ' '.join(self.tr4w.get_keywords(20, word_min_len=1))
            return self.wresult

    def get_keyphrase(self):
            # 20个关键词去构造短语，短语在原文本中出现次数最少为2
            self.presult = ' '.join(self.tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2))
            self.tr4s = TextRank4Sentence(self.stop_words_file)
            return self.presult

    def get_gist(self, text):
            self.tr4w = TextRank4Keyword(self.stop_words_file)  # 导入停止词
            #使用词性过滤，文本小写，窗口为2
            self.tr4w.train(text=text, speech_tag_filter=True, lower=True, window=2)
            # 20个关键词且每个的长度最小为1
            self.wresult = ' '.join(self.tr4w.get_keywords(20, word_min_len=1))
            # 20个关键词去构造短语，短语在原文本中出现次数最少为2
            self.presult = ' '.join(self.tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2))
            self.tr4s = TextRank4Sentence(self.stop_words_file)
            # 使用词性过滤，文本小写，使用words_all_filters生成句子之间的相似性
            self.tr4s.train(text=text, speech_tag_filter=True, lower=True, source = 'all_filters')
            self.gresult = ' '.join(self.tr4s.get_key_sentences(num=3)) # 重要性最高的三个句子
            return self.gresult


def cal_sim(textList):

    dictionary = corpora.Dictionary(textList)
    dictionary.save('/Users/Gavin/work/news_baijia_AI/para_sim/gist.dict') # store the dictionary, for future reference
    corpus = [dictionary.doc2bow(text) for text in textList]
    corpora.MmCorpus.serialize('/Users/Gavin/work/news_baijia_AI/para_sim/gist.mm', corpus) # store to disk, for later use
    corpus = corpora.MmCorpus('/Users/Gavin/work/news_baijia_AI/para_sim/gist.mm')
    tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
    corpus_tfidf = tfidf[corpus]
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2) # initialize an LSI transformation
    corpus_lsi = lsi[corpus_tfidf] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi
    lsi.save('/Users/Gavin/work/news_baijia_AI/para_sim/model.lsi') # same for tfidf, lda, ...
    lsi = models.LsiModel.load('/Users/Gavin/work/news_baijia_AI/para_sim/model.lsi')
    index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it
    index.save('/Users/Gavin/work/news_baijia_AI/para_sim/gist.index')
    index = similarities.MatrixSimilarity.load('/Users/Gavin/work/news_baijia_AI/para_sim/gist.index')
    sims_list =[]
    for x in range(len(textList)):
        vec_lsi = lsi[corpus[x]]
        sims = index[vec_lsi]
        sims_list.append(list(enumerate(sims)))
    r = {}
    w = []
    for sl in sims_list:
        for v,k in sl:
            r[v] = k
        w.append(r)
    dl = [dict(t) for t in sims_list]
    # for m in dl:
    #     if min()
    mdl = []
    # min_val = min(u.iteritems())
    # min_val_d = {k:v for k, v in u.iteritems() if v == min_val}

    for x in dl:
        min_v = min(x.itervalues())
        mdlo = {k:v for k,v in x.iteritems() if v == min_v}
        # mdl.append(min_v)
        mdl.append(mdlo)
    smdl = sorted(mdl, key = lambda k:k)
    # fr = sorted(dl)

    print smdl
    print sims_list

    # vec_lsi = lsi[corpus[0]]
    # sims = index[vec_lsi]



    # sims = sorted(enumerate(index), key=lambda item: item[1])
    # print list(enumerate(index))
    # print(list(enumerate(index)))
    # return lsi.print_topics(2)
    # for d print simsoc in corpus_lsi:
    # return list(enumerate(sims))


# def get_one_doc_gist(content):
#     gist = ''
#     return gist

if __name__ == "__main__":
    a = Gist().get_gist(codecs.open('/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/text/01.txt', 'r', 'utf-8').read())
    b = Gist().get_gist(codecs.open('/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/text/02.txt', 'r', 'utf-8').read())
    c = Gist().get_gist(codecs.open('/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/text/05.txt', 'r', 'utf-8').read())

    ag = list(jieba.cut(a))
    bg = list(jieba.cut(b))
    cg = list(jieba.cut(c))
    textList = []
    textList.append(ag)
    textList.append(bg)
    textList.append(cg)
    # print cal_sim(textList)
    print a
    print cal_sim(textList)
    # get_one_doc_gist("中国人是这样的")










