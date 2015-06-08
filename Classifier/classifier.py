# -*- coding: utf-8 -*-
"""
Created on May 08, 2015
@author: Gavin
"""

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
from math import sqrt
import gensim
from sklearn.svm import SVC
import os
import jieba
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import math
import numpy as np



def vec2dense(vec, num_terms):

    '''Convert from sparse gensim format to dense list of numbers'''
    return list(gensim.matutils.corpus2dense([vec], num_terms=num_terms).T[0])

#training_data can be a a dictionary of different paragraphs,data_to_classify can be a
# a dictionary of different commnents to be classified to those paragraphs.
def doc_classify(training_data, data_to_classify):
    #Load in corpus, remove newlines, make strings lower-case
    docs = {}
    docs.update(training_data)
    docs.update(data_to_classify)
    names = docs.keys()

    preprocessed_docs = {}
    for name in names:
        preprocessed_docs[name] = list(jieba.cut(docs[name]))

    #Build the dictionary and filter out rare terms
    #Perform Chinese words segmentation.
    dct = gensim.corpora.Dictionary(preprocessed_docs.values())
    unfiltered = dct.token2id.keys()
    dct.filter_extremes(no_below=2)
    filtered = dct.token2id.keys()
    filtered_out = set(unfiltered) - set(filtered)

    print "\nThe following super common/rare words were filtered out..."
    print list(filtered_out), '\n'

    print "Vocabulary after filtering..."
    print dct.token2id.keys(), '\n'

    #Build Bag of Words Vectors out of preprocessed corpus
    print "---Bag of Words Corpus---"

    bow_docs = {}
    for name in names:

        sparse = dct.doc2bow(preprocessed_docs[name])
        bow_docs[name] = sparse
        dense = vec2dense(sparse, num_terms=len(dct))
        print name, ":", dense

    #Dimensionality reduction using LSI. Go from 6D to 2D.
    print "\n---LSI Model---"

    lsi_docs = {}
    num_topics = 2
    lsi_model = gensim.models.LsiModel(bow_docs.values(),
                                       num_topics=num_topics)
    for name in names:

        vec = bow_docs[name]
        sparse = lsi_model[vec]
        dense = vec2dense(sparse, num_topics)
        lsi_docs[name] = sparse
        print name, ':', dense

    #Normalize LSI vectors by setting each vector to unit length
    print "\n---Unit Vectorization---"

    unit_vecs = {}

    for name in names:

        vec = vec2dense(lsi_docs[name], num_topics)
        print vec
        norm = sqrt(sum(num ** 2 for num in vec))
        with np.errstate(invalid='ignore'):
            unit_vec = [num / norm for num in vec]
        if math.isnan(unit_vec[0]) | math.isnan(unit_vec[1]):
            unit_vec = [0.0,0.0]

        unit_vecs[name] = unit_vec
        print name, ':', unit_vec
    #Take cosine distances between docs and show best matches
    print "\n---Document Similarities---"

    index = gensim.similarities.MatrixSimilarity(lsi_docs.values())
    for i, name in enumerate(names):

        vec = lsi_docs[name]
        sims = index[vec]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        #Similarities are a list of tuples of the form (doc #, score)
        #In order to extract the doc # we take first value in the tuple
        #Doc # is stored in tuple as numpy format, must cast to int

        if int(sims[0][0]) != i:
            match = int(sims[0][0])
        else:
            match = int(sims[1][0])

        match = names[match]
        print name, "is most similar to...", match

    print "\n---Classification---"

    train = [unit_vecs[key] for key in training_data.keys()]


    labels = [(num+1) for num in range(len(training_data.keys()))]
    label_to_name = dict(zip(labels, training_data.keys()))
    classifier = SVC()
    classifier.fit(train, labels)
    result = {}
    for name in names:

        vec = unit_vecs[name]
        label = classifier.predict([vec])[0]
        cls = label_to_name[label]
        if name in data_to_classify.keys():
            result[name]= cls
    print result
    print r'\xe5\xbe\xae\xe8\xbd\xaf' + " is " + '\xe5\xbe\xae\xe8\xbd\xaf'
    print r'\xe8\xb0\xb7\xe6\xad\x8c' + " is " + '\xe8\xb0\xb7\xe6\xad\x8c'
    return result
    print '\n'



if __name__ == '__main__':

    # a = {"M": "公司于1975年由比尔·盖茨和保罗·艾伦创立。初期主要为阿尔塔8800发展和销售BASIC解释器，在1980年代中期凭借MS-DOS在家用电脑操作系统市场上获取长足进步，后来出现的Windows使得微软逐渐统治了家用桌面电脑操作系统市场。同时微软也开始扩张业务，进军其他行业和市场：创建MSN门户网站；计算机硬件市场上，微软商标及Xbox、Xbox 360、Surface、Zune和MSN TV家庭娱乐设备也在不同的年份出现在市场上[3]。微软于1986年首次公开募股，此后不断走高的股价为微软缔造了四位亿万富翁和12,000位百万富翁[5][6][7]。",
    #      "G": "是一家美国的跨国科技企业，业务范围涵盖互联网搜索、云计算、广告技术等领域，开发并提供大量基于互联网的产品与服务，[8]其主要利润来自于AdWords等广告服务。[9][10] Google由当时在斯坦福大学攻读理工博士的拉里·佩奇和谢尔盖·布林共同创建，因此两人也被称为“Google Guys”。[11][12][13]1998年9月4日，Google以私营公司的形式创立，设计并管理一个互联网搜索引擎“Google搜索”；Google网站则于1999年下半年启用。2004年8月19日，Google公司的股票在纳斯达克上市，后来被称为“三驾马车”的公司两位共同创始人与出任首席执行官的埃里克·施密特在当时承诺：共同在Google工作至少二十年，即至2024年止。[14]创始之初，Google官方的公司使命为“集成全球范围的信息，使人人皆可访问并从中受益”（To organize the world's information and make it universally accessible and useful）；[15]而非正式的口号则为“不作恶”（Don't be evil），由工程师阿米特·帕特尔（Amit Patel）所创，[16]并得到了保罗·布赫海特的支持。[17][18] Google公司的总部称为“Googleplex”，位于美国加州圣克拉拉县的芒廷维尤。2011年4月，佩奇接替施密特担任首席执行官[19]。",
    # }
    # b = {"微软": "微软公司于1975年由比尔·盖茨和保罗·艾伦创立。他们是小时候认识的朋友及高中同学，并对在计算机编程充满激情。利用其演讲技能，追求一个成功的企业。在1975年01月发布MITS公司的牛郎星8800大众化微电脑和遥测系统令他们注意到，他们可以编写一个BASIC解释器赚钱，他致电给Altair 8800的发明者（MITS），提出示范在该系统中运行BASIC。[10]完成后，MITS公司感到兴趣，更要求艾伦和盖茨进行示范。之后MITS公司聘请艾伦为“牛郎星”进行模拟器（解释器中的组件）的开发工作，而盖茨则开发解释器。它们的工作十分完美，在1975年3月MITS公司同意贩买出售牛郎星BASIC解释器[11]。然后他们顺利赚了第一桶金。于是，盖茨离开哈佛大学，并搬到MITS在新墨西哥州阿布奎基的总部。1975年04月04日，微软正式成立，盖茨为微软首席运行官。原名“Micro-Soft”是艾伦想出来的，之后更改为“Microsoft”[12]。在1995年《财富》杂志的一篇文章中回忆，在1977年08月，公司和日本ASCII杂志签署了一个协议，成立了其首个国际办事处“ASCII Microsoft”[13]。在1979年01月，公司搬迁到在华盛顿州的比尔维尤的新办公室。微软在1981年06月25日于华盛顿州改组成注册公司（“Microsoft,Inc.”）。盖茨于改组中成为公司的总裁和董事长，保罗·艾伦则成为运行副总裁。",
    #      "Microsoft": "微软公司于1975年由比尔·盖茨和保罗·艾伦创立。他们是小时候认识的朋友及高中同学，并对在计算机编程充满激情。利用其演讲技能，追求一个成功的企业。在1975年01月发布MITS公司的牛郎星8800大众化微电脑和遥测系统令他们注意到，他们可以编写一个BASIC解释器赚钱，他致电给Altair 8800的发明者（MITS），提出示范在该系统中运行BASIC。[10]完成后，MITS公司感到兴趣，更要求艾伦和盖茨进行示范。之后MITS公司聘请艾伦为“牛郎星”进行模拟器（解释器中的组件）的开发工作，而盖茨则开发解释器。它们的工作十分完美，在1975年3月MITS公司同意贩买出售牛郎星BASIC解释器[11]。然后他们顺利赚了第一桶金。于是，盖茨离开哈佛大学，并搬到MITS在新墨西哥州阿布奎基的总部。1975年04月04日，微软正式成立，盖茨为微软首席运行官。原名“Micro-Soft”是艾伦想出来的，之后更改为“Microsoft”[12]。在1995年《财富》杂志的一篇文章中回忆，在1977年08月，公司和日本ASCII杂志签署了一个协议，成立了其首个国际办事处“ASCII Microsoft”[13]。在1979年01月，公司搬迁到在华盛顿州的比尔维尤的新办公室。微软在1981年06月25日于华盛顿州改组成注册公司（“Microsoft,Inc.”）。盖茨于改组中成为公司的总裁和董事长，保罗·艾伦则成为运行副总裁。",
    #      "谷歌": "据估计，Google在全世界的数据中心内运营着超过百万台的服务器，[20]每天处理数以亿计的搜索请求[21]和约二十四PB用户生成的数据。[22][23][24][25] Google自创立起开始的快速成长同时也带动了一系列的产品研发、并购事项与合作关系，而不仅仅是公司核心的网络搜索业务。Google公司提供丰富的线上软件服务，如云硬盘、Gmail电子邮件，包括Orkut、Google Buzz以及Google+在内的社交网络服务。Google的产品同时也以应用软件的形式进入用户桌面，例如Google Chrome网页浏览器、Picasa图片整理与编辑软件、Google Talk即时通讯工具等。另外，Google还进行了移动设备的Android操作系统以及上网本的Google Chrome OS操作系统的开发。",
    #      "Google":"1996年1月，身为加州斯坦福大学理学博士生的拉里·佩奇和谢尔盖·布林在学校开始一项关于搜索的研究项目。[30]区别于传统的搜索靠搜索字眼在页面中出现次数来进行结果排序的方法，两人开发了一个对网站之间的关系做精确分析的搜寻引擎。[31]这个名为PageRank的引擎通过检查网页中的反向链接以评估站点的重要性，此引擎的精确度胜于当时的基本搜索技术。[32][33]最初，佩奇和布林将这个搜索引擎命名为‘BackRub’，直到后来改为‘Google’。[34][35][36]这个新名字来源于一个数学大数googol（数字1后有100个0，即自然数10100）单词错误的拼写方式，[37][38]象征着为人们提供搜索海量优质信息的决心。[39] Google搜索引擎在斯坦福大学的网站上启用，域名为google.stanford.edu。[40]"
    # }
    a = {0: u'\u3010\u73af\u7403\u519b\u4e8b\u62a5\u9053\u3011 \u4e2d\u56fd \u519b\u961f\u4ece\u4eca\u5929\u8d77\u5728\u4e2d\u7f05\u8fb9\u754c\u6211\u65b9\u5883\u5185\u7ec4\u7ec7\u9646\u7a7a\u8054\u5408\u5b9e\u5175\u5b9e\u5f39\u6f14\u4e60\u30026\u67081\u65e5\u4e0a\u5348\uff0c\u6210\u90fd\u519b\u533a\u65b0\u95fb\u53d1\u8a00\u4eba\u8d75\u4e15\u806a\u5927\u6821\u5bf9\u5916\u53d1\u5e03\u6210\u90fd\u519b\u533a\u5c06\u5728\u4e91\u5357\u65b9\u5411\u7ec4\u7ec7\u9646\u7a7a\u8054\u5408\u6f14\u4e60\u901a\u544a\u3002\u4e2d\u65b9\u4e3e\u884c\u519b\u4e8b\u6f14\u4e60\u7684\u4e2d\u7f05\u8fb9\u5883\u5bf9\u9762 \u7f05\u7538 \u4e00\u8fb9\u662f\u7f05\u7538\u679c\u6562\u5730\u533a\u3002\u4eca\u5e74\u4ee5\u6765\uff0c\u8be5\u5730\u533a\u51b2\u7a81\u4e0d\u65ad\u5e76\u6b83\u53ca\u4e91\u5357\u5730\u533a\uff0c\u9020\u6210\u4e2d\u56fd\u5883\u5185\u8fb9\u6c11\u6570\u4eba\u4f24\u4ea1\u3002\u4e2d\u56fd\u5916\u4ea4\u90e8\u591a\u6b21\u6566\u4fc3\u7f05\u7538\u6709\u5173\u5404\u65b9\u4fdd\u6301\u514b\u5236\u3002\u5bf9\u6b64\u6b21\u519b\u6f14\uff0c\u6709\u56fd\u9645\u5a92\u4f53\u731c\u6d4b\u201c\u4e2d\u56fd\u88ab\u6fc0\u6012\u4e86\u201d\u3002\u4e2d\u56fd\u5916\u4ea4\u90e8\u53d1\u8a00\u4eba\u534e\u6625\u83b91\u65e5\u5728\u8bb0\u8005\u4f1a\u4e0a\u8868\u793a\uff0c\u8fd9\u662f\u519b\u961f\u4efb\u52a1\u8303\u56f4\u5185\u7684\u6b63\u5e38\u7684\u6d3b\u52a8\u3002\u5bf9\u4e8e\u7f05\u5317\u5c40\u52bf\u6d89\u53ca\u4e2d\u7f05\u8fb9\u5883\u5730\u533a \u548c\u5e73 \u4e0e\u5b89\u5b81\uff0c\u534e\u6625\u83b9\u5f3a\u8c03\uff0c\u5e0c\u671b\u7f05\u65b9\u4e0e\u4e2d\u65b9\u5171\u540c\u52aa\u529b\uff0c\u7ef4\u62a4\u597d\u4e2d\u7f05\u8fb9\u5883\u5730\u533a\u7684\u5b89\u5b81\uff0c\u63a8\u52a8\u4e2d\u7f05\u5173\u7cfb\u6301\u7eed\u5065\u5eb7\u7a33\u5b9a\u53d1\u5c55\u3002',
         1: u'\u4e2d\u56fd\u56fd\u9632\u90e8\u7f51\u7ad9\u663e\u793a\uff0c\u6210\u90fd\u519b\u533a\u65b0\u95fb\u53d1\u8a00\u4eba\u8d75\u4e15\u806a\u5927\u68211\u65e5\u5bf9\u5916\u53d1\u5e03\u4e86\u6210\u90fd\u519b\u533a\u5c06\u5728\u4e91\u5357\u65b9\u5411\u7ec4\u7ec7\u9646\u7a7a\u8054\u5408\u6f14\u4e60\u7684\u901a\u544a\uff1a6\u67082\u65e5\u8d77\u5728\u4e2d\u7f05\u8fb9\u5883\u6211\u65b9\u5883\u5185\u7ec4\u7ec7\u9646\u7a7a\u8054\u5408\u5b9e\u5175\u5b9e\u5f39\u6f14\u4e60\uff0c\u6f14\u4e60\u7ed3\u675f\u65f6\u95f4\u5c06\u53e6\u884c\u901a\u544a\u3002\u6f14\u4e60\u671f\u95f4\uff0c\u5404\u7c7b\u98de\u884c\u5668\u672a\u7ecf\u6279\u51c6\u4e0d\u5f97\u8fdb\u5165\u8be5\u7a7a\u57df\uff0c\u8f66\u8f86\u3001\u4eba\u5458\u8bf7\u670d\u4ece\u4ea4\u901a\u7ba1\u5236\uff0c\u672a\u7ecf\u6279\u51c6\u4e0d\u5f97\u8fdb\u5165\u6f14\u4e60\u7ba1\u5236\u533a\u57df\u3002\u6f14\u4e60\u4e0d\u5f71\u54cd\u7fa4\u4f17\u6b63\u5e38\u7684\u751f\u4ea7\u751f\u6d3b\u3002\u901a\u544a\u79f0\uff0c\u4f9d\u636e\u56fd\u9645\u901a\u884c\u505a\u6cd5\u548c\u4e2d\u7f05\u4e24\u56fd\u4e24\u519b\u76f8\u5173\u534f\u8bae\uff0c\u6211\u6709\u5173\u90e8\u95e8\u5411\u7f05\u65b9\u901a\u62a5\u4e86\u6211\u7ec4\u7ec7\u519b\u4e8b\u6f14\u4e60\u4e8b\u5b9c\u3002',
         2: u'\u8fd9\u662f\u81ea2\u67089\u65e5\u7f05\u5317\u6218\u4e8b\u7206\u53d1\u4ee5\u6765\uff0c\u4e2d\u56fd\u5b98\u65b9\u9996\u6b21\u5ba3\u5e03\u5728\u4e2d\u7f05\u8fb9\u5883\u6211\u65b9\u5883\u5185\u8fdb\u884c\u5b9e\u5f39\u6f14\u4e60\u3002\u6839\u636e\u516c\u5f00\u62a5\u9053\uff0c\u622a\u81f3\u76ee\u524d\u7f05\u7538\u65b9\u9762\u70ae\u5f39\u5df2\u7ecf\u6709\u4e94\u6b21\u843d\u5165\u4e2d\u56fd\u5883\u5185\uff0c\u4e24\u6b21\u9020\u6210\u4eba\u5458\u4f24\u4ea1\u3002\u4eca\u5e743\u670813\u65e5\uff0c\u7f05\u7538\u519b\u673a\u70b8\u5f39\u66fe\u843d\u5165\u4e2d\u65b9\u5883\u5185\uff0c\u9020\u6210\u4e2d\u65b95\u6b7b8\u4f24\u30023\u670814\u65e5\uff0c\u4e2d\u592e\u519b\u59d4\u526f\u4e3b\u5e2d\u8303\u957f\u9f99\u4e0e\u7f05\u7538\u56fd\u9632\u519b\u603b\u53f8\u4ee4\u7d27\u6025\u901a\u8bdd\u3002\u8303\u957f\u9f99\u8981\u6c42\uff0c\u201c\u7f05\u519b\u9ad8\u5c42\u8981\u4e25\u683c\u7ba1\u63a7\u7ea6\u675f\u90e8\u961f\uff0c\u7edd\u4e0d\u80fd\u518d\u6b21\u53d1\u751f\u6b64\u7c7b\u4e8b\u4ef6\u3002\u5426\u5219\uff0c\u4e2d\u56fd\u519b\u961f\u5c06\u91c7\u53d6\u575a\u51b3\u679c\u65ad\u63aa\u65bd\uff0c\u4fdd\u62a4\u4e2d\u56fd\u4eba\u6c11\u751f\u547d\u8d22\u4ea7\u5b89\u5168\u201d\u3002\u968f\u540e\uff0c\u5728\u4e8b\u53d1\u8fb9\u5883\u5730\u533a\u4e2d\u56fd\u519b\u961f\u91c7\u53d6\u4e86\u4e00\u7cfb\u5217\u8fb9\u5883\u9632\u63a7\u8b66\u6212\u63aa\u65bd\uff0c\u5305\u62ec\u9632\u7a7a\u90e8\u961f\u8fdb\u9a7b\uff0c\u6218\u6597\u673a\u5e26\u5f39\u5de1\u903b\u7b49\u30025\u670814\u65e5\uff0c\u6765\u81ea\u7f05\u7538\u65b9\u5411\u76842\u679a\u70ae\u5f39\u843d\u5165\u4e91\u5357\u7701\u4e34\u6ca7\u5e02\u9547\u5eb7\u53bf\u5357\u4f1e\u9547\uff0c\u81f45\u4eba\u53d7\u4f24\u3002',
         3: u'\u6839\u636e\u901a\u544a\u663e\u793a\u7684\u6f14\u4e60\u8303\u56f4\uff0c\u8fd9\u6b21\u6f14\u4e60\u5730\u57df\u5305\u62ec\u4e91\u5357\u803f\u9a6c\u53bf\u3001\u9547\u5eb7\u53bf\u6cbf\u8fb9\u5730\u533a\u3002\u8fd9\u4e24\u4e2a\u5730\u533a\u5747\u53d1\u751f\u8fc7\u7f05\u7538\u65b9\u5411\u70ae\u5f39\u4f24\u4eba\u4e8b\u4ef6\uff0c\u5bf9\u9762\u662f\u7f05\u5317\u51b2\u7a81\u6700\u6fc0\u70c8\u7684\u533a\u57df\u3002\u4ece\u7f05\u5317\u6218\u4e8b\u7206\u53d1\u81f3\u4eca\uff0c\u5f53\u5730\u201c\u8fd8\u80fd\u542c\u5230\u8fb9\u754c\u5bf9\u9762\u70ae\u5f39\u7206\u70b8\u58f0\u4e0d\u65ad\uff0c\u5c40\u52bf\u4ecd\u65e7\u5f88\u7d27\u5f20\u3002\u201d\u4e00\u4f4d\u751f\u6d3b\u5728\u4e8b\u53d1\u5730\u7684\u4eba\u58eb1\u65e5\u544a\u8bc9\u300a\u73af\u7403\u65f6\u62a5\u300b\u8bb0\u8005\u3002', 4: u''}
    b = {0: u'\u72af\u6211\u4e2d\u534e\u8005\uff0c\u867d\u8fdc\u5fc5\u9a82',
         1: u'\u6709\u5fc5\u8981\u9707\u6151\u4e00\u4e0b\u7f05\u7538\u4eba\uff0c\u8ba9\u4ed6\u4eec\u77e5\u9053\u624b\u4f38\u7684\u592a\u957f\u662f\u8981\u88ab\u5241\u6389\u7684\u3002\u601d\u8003',
         2: u'\u7ed9\u4ea4\u6218\u53cc\u65b9\u65bd\u52a0\u538b\u529b\uff0c\u6218\u4e89\u5230\u6b64\u4e3a\u6b62\uff0c\u4e0d\u51c6\u518d\u95f9\uff0c\u5426\u5219\u540e\u679c\u81ea\u8d1f\u3002',
         3: u'\u7f05\u7538\u653f\u5e9c\u8ba4\u4e3a\u53ea\u8981\u8ddf\u4e2d\u56fd\u4ea4\u6076\uff0c\u7f8e\u56fd\u548c\u65e5\u672c\u4f1a\u7ed9\u4ed6\u597d\u5904\uff1b\u679c\u6562\u4ee5\u4e3a\u53ea\u8981\u6253\u6c11\u65cf\u724c\uff0c\u4e2d\u56fd\u5c31\u4f1a\u65e0\u6761\u4ef6\u6551\u52a9\u4ed6\u3002\u5176\u5b9e\uff0c\u4e2d\u56fd\u9700\u8981\u5b89\u5b9a\u7684\u897f\u90e8\u73af\u5883\uff0c\u9700\u8981\u5370\u5ea6\u6d0b\u51fa\u6d77\u53e3\uff0c\u4e2d\u56fd\u591a\u6b21\u5f3a\u8c03\uff0c\u65e0\u4eba\u7406\u4f1a\uff0c\u53ea\u597d\u62bd\u51fa\u5927\u68d2\u6765\u4e86\u3002\u4e2d\u56fd\u771f\u52a8\u624b\u7684\u8bdd\uff0c\u7f8e\u65e5\u4e5f\u5c31\u662f\u653e\u51e0\u4e2a\u5c41\u800c\u5df2\u3002',
         4: u'\u81f3\u4ece\u6709\u4e86\u90a3\u4e2a\u897f\u65b9\u79f0\u4f5c\u5973\u6597\u58eb\u7684\u4ec0\u4e48\u9e21[\u6316\u9f3b\u5c4e]\uff0c\u73b0\u5728\u7f05\u7538\u592a\u8ddf\u7740\u7f8e\u56fd\u8f6c\u4e86\uff0c\u4e2d\u56fd\u4e3a\u4e86\u8fb9\u754c\u5b89\u5b81\uff0c\u5df2\u7ecf\u518d\u4e09\u8981\u6c42\u7f05\u7538\u653f\u5e9c\u548c\u5e73\u89e3\u51b3\u5185\u90e8\u4e89\u7aef\uff0c\u4f46\u662f\u7f05\u7538\u81ea\u4ee5\u4e3a\u73b0\u5728\u4e2d\u56fd\u5fd9\u4e8e\u7ecf\u6d4e\uff0c\u5fd9\u4e8e\u5357\u6d77\uff0c\u4e1c\u6d77\uff0c\u81ea\u5df1\u53c8\u6709\u7f8e\u56fd\u6491\u8170\uff0c\u5df2\u591a\u6b21\u8ba9\u4e2d\u56fd\u6ca1\u9762\u5b50\uff01\u5fc5\u987b\u6709\u52a8\u4f5c\uff0c\u5fc5\u987b\u8b66\u544a\uff0c\u4e25\u60e9\uff01',
         5: u'\u5fcd\u65e0\u53ef\u5fcd\u65f6\uff0c\u65e0\u9700\u518d\u5fcd\u3002', 6: u'\u5176\u5b9e\u6211\u4e0d\u662f\u55b7\u5b50\uff0c\u4f46\u6211\u66f4\u5e0c\u671b\u6765\u4e00\u573a\u6218\u4e89\uff0c\u8ba9\u70ae\u706b\u5728\u4eba\u4eec\u5934\u4e0a\u5212\u8fc7\uff0c\u8ba9\u5b50\u5f39\u5728\u4eba\u7fa4\u4e2d\u7a7f\u68ad\uff0c\u90a3\u4e9b\u50bb\u903c\u55b7\u5b50\u81ea\u7136\u800c\u7136\u77e5\u9053\u56fd\u5bb6\u4e43\u662f\u6839\u672c', 7: u'\u54ce\uff0c\u8c01\u7ed9\u4f60\u4eec\u7684\u52c7\u6c14\u5462\uff1f\u628a\u6218\u4e89\u513f\u620f\u822c\u6302\u5728\u5634\u8fb9\u3002\u8be5\u4e0d\u8be5\u6253\u81ea\u7136\u6709\u6700\u9ad8\u7684\u51b3\u7b56\u673a\u6784\u4e0e\u667a\u56ca\u56e2\u7efc\u5408\u5404\u65b9\u8003\u8651\uff0c\u4e0d\u662f\u8857\u89d2\u762a\u4e09\u6b3a\u8f6f\u6015\u786c\u6216\u773c\u9ad8\u4e8e\u9876\u4e89\u4e00\u65f6\u4e4b\u6c14\u3002',
         8: u'\u56fd\u5185\u5a92\u4f53\u5462\uff0c\u600e\u4e48\u5c31\u62a5\u9053\u8fd9\u4e00\u70b9\u3002\u771f\u5e0c\u671b\u6709\u5929\u56fd\u5185\u5a92\u4f53\u80fd\u6709\u4efb\u4f55\u7684\u62a5\u9053\u6743\u3002', 9: u'\u56de\u590d@\u4e09\u4e09\u4e0d\u8981\u518d\u71ac\u591c:\u5f53\u65f6\u5927\u9646\u641e\u519b\u6f14\u4e3b\u8981\u662f\u9488\u5bf9\u53f0\u72ec\u52bf\u529b\u7684\uff0c\u4e5f\u662f\u5bf9\u53f0\u6e7e\u5f53\u5c40\u7684\u5a01\u6151\uff0c\u5982\u679c\u53f0\u6e7e\u6ca1\u6709\u4e8b\u5b9e\u4e0a\u7684\u72ec\u7acb\uff0c\u5927\u9646\u4e5f\u5c31\u7b97\u4e86\uff0c\u8fd9\u5c31\u662f\u7ed3\u5c40\uff0c\u4e00\u70b9\u4e5f\u4e0d\u610f\u5916\uff0c\u56e0\u4e3a\u5927\u9646\u73b0\u5728\u6839\u672c\u5c31\u6ca1\u6709\u6253\u7b97\u8981\u7528\u6b66\u529b\u6765\u6536\u590d\u53f0\u6e7e\u3002\u4eca\u540e\u53f0\u6e7e\u5c9b\u5185\u53c8\u5f00\u59cb\u53f0\u72ec\u6d3b\u52a8\uff0c\u5927\u9646\u80af\u5b9a\u6bd4\u524d\u6b21\u66f4\u5927\u89c4\u6a21\u7684\u519b\u6f14\u3002',
         10: u'\u522b\u5439\u725b\u4e86\uff0c\u8fd8\u662f\u63a5\u7740\u8c34\u8d23\u5427........', 11: u'\u6f14\u7684\u8fde\u81ea\u5df1\u90fd\u5206\u4e0d\u6e05\u771f\u5047\u4e86\uff0c\u624d\u662f\u6700\u9ad8\u5883\u754c.......',
         12: u'\u519b\u6f14\uff0c\u8bf4\u7a7f\u4e86\u5c31\u662f\u6f14\u7ed9\u89c2\u4f17\u770b\u7684\u3002\u4e00\u662f\u5e73\u606f\u56fd\u5185\u6028\u6c14\uff0c\u4e8c\u662f\u7ed9\u7f05\u7538\u4e00\u70b9\u8b66\u793a\uff0c\u5982\u6b64\u800c\u5df2\uff01', 13: u'\u94c1\u8840\u5434\u732b\u53c8YY\u9ad8\u6f6e\u4e86\u3002', 14: u'\u5ba6\u7403\u5c4e\u62a5\uff01\uff01', 15: u'\u6ce8\u610f\uff1a\u697c\u4e0a\u662f\u4f2a\u88c5\u6210\u4e2d\u56fd\u4eba\u7684\u65e5\u672c\u4eba\u4e00\u5934\uff0c\u6709\u7f8e\u56fd\u9ed1\u4eba\u5927\u5175\u8840\u7edf\uff0c\u5c0a\u79f0\u502d\u755c\uff0c\u4fd7\u79f0\u65e5\u672c\u755c\u7272\u9274\u8d4f\u5b8c\u6bd5', 16: u'\u8bf4\u5f97\u597d\uff0c\U0001f436\u7cae\u4e00\u7f50\u7ed9\u4f60', 17: u'\u679c\u6562\u9aa8\u8089\u76f8\u8fde\u7684\u5144\u5f1f\uff0c\u4e0d\u662f\u5417\uff1f\u8fd8\u662f\u8c34\u8d23\u6297\u8bae\u5427\uff01',
         18: u'\u4e16\u754c\u7b2c\u4e00\u725b13zF\uff0c\u4e16\u754c\u7b2c\u4e00\u9760\u725b13\u5439\u5f3a\u7684\u56fd\u5bb6\uff0c\u5439\uff0c\u7ee7\u7eed\u5439\uff01', 19: u'\u6211\u5c31\u6ca1\u89c1\u8fc7\u771f\u6b63\u6253\u8fc7', 20: u'\u626f\uff01', 21: u'\u5982\u679c\u518d\u6709\u6d41\u5f39\u8fdb\u5165\uff0c\u4e2d\u56fd\u5c06\u534f\u52a9\u7f05\u7538\uff0c\u534a\u4e2a\u5c0f\u65f6\u5185\u5b8c\u6210\u6218\u6597', 22: u'\u5728\u679c\u6562\u6c49\u4eba\u8eab\u4e0a\uff0c\u6211\u770b\u5230\u4e86\u4e00\u4e2a\u4f1f\u5927\u6c11\u65cf\u7684\u4e0d\u5c48\u4e0d\u6320\uff01\u5728\u7f05\u7538\u6c49\u65cf\u8981\u8981\u906d\u53d7\u6b67\u89c6\uff0c\u5728\u4e2d\u56fd\u6c49\u65cf\u8fd8\u662f\u8981\u906d\u53d7\u6b67\u89c6\uff01\u4f46\u662f\u7f05\u7538\u6c49\u65cf\u80fd\u591f\u4e3a\u6b64\u6297\u4e89\uff01\u800c\u4f5c\u4e3a\u4e2d\u56fd\u7684\u6c49\u65cf\u53ea\u80fd\u547c\u5401\u5b9e\u73b0\u6c11\u65cf\u5e73\u7b49\uff0c\u4f7f\u6c49\u65cf\u4eab\u6709\u548c\u5176\u4ed6\u6c11\u65cf\u540c\u7b49\u7684\u4e0d\u53d7\u6b67\u89c6\u7684\u6743\u5229\u3002', 23: u'\u8fd9\u5e74\u5934\u4e0d\u6b7b\u4e0a\u51e0\u4e2a\u4eba\uff0c\u4e0d\u559d\u4e0a\u51e0\u53e3\u519c\u836f\u4ec0\u4e48\u7684\uff0c\u66f9\u53bfzF\u5c31\u4e00\u76f4\u88c5\u6b7b\uff01\u547d\u8d31\u554a\u3002', 24: u'\u4e3a\u4e2d\u56fd\u5229\u76ca\u800c\u6218\uff01\u4e3a\u548c\u5e73\u800c\u6218\uff01\u4e3a\u7956\u56fd\u800c\u6218\uff01\u4e3a\u4e2d\u56fd\u767e\u59d3\u800c\u6218\uff01\u4e3a\u5c0a\u4e25\u800c\u6218\uff01\u8fd9\u662f\u4e2d\u56fd\u519b\u4eba\u7684\u5929\u804c\uff01\u662f13\u4ebf\u56fd\u4eba\u7684\u671f\u76fc\uff01\u4e2d\u56fd\u4e0d\u60f9\u8c01\uff0c\u8c01\u4e5f\u522b\u60f3\u4e3b\u5bb0\u4eca\u5929\u7684\u4e2d\u56fd\uff01', 25: u'\u90a3\u4f60\u4e0a\u5427\uff0c\u4f60\u8001\u5a46\u5973\u513f\u6211\u7167\u987e', 26: u'\u8d4f\u4f60\u4e00\u5768\u5c4e\uff0c\u4e94\u6ee1\U0001f436', 27: u'\u76f8\u4fe1\u6211\uff0c\u5230\u4e86\u6781\u9650\u80af\u5b9a\u4f1a\u8c34\u8d23\u7684\uff01',
         28: u'\u89e3\u653e\u519b\u8fd9\u4e2a\u50bb\u903c\u6562\u5417', 29: u'\u5c31\u662f\uff0c\u4e0d\u53ef\u80fd\u4ecb\u5165\u7684\uff0c\u4e07\u4e00\u6253\u4e0d\u8fc7\u4eba\u5bb6\uff0c\u4e0d\u8981\u88ab\u7b11\u6b7b', 30: u'\u4e00\u7eb8\u8001\u864e\u51fa\u6765\u5413\u4eba\u4e86', 31: u'2015\u5e74\u4e0a\u534a\u5e74\uff0c\u6562\u52a8\u4e2d\u56fd\u6392\u884c\u699c\uff1a\u5927\u7f05\u7538\u5e1d\u56fd\u76f4\u63a5\u70ae\u51fb\u548c\u8f70\u70b8\u673a\u5230\u4e2d\u56fd\u5883\u5185\u70b8\u6b7b\u70b8\u6b7b\u591a\u4eba\uff0c\u7b2c\u4e8c\u540d\u5927\u5317\u97e9\u5e1d\u56fd\u8d8a\u5883\u6740\u5bb3\u4e2d\u56fd\u8fb9\u6c11\u591a\u4eba\uff0c\u7b2c\u4e09\u540d\u5370\u5c3c\u70b8\u6bc1\u4e2d\u56fd\u6e14\u8239\uff0c\u7b2c\u56db\u540d\u5927\u8d8a\u5357\u5e1d\u56fd\uff0c\uff0c\uff0c\uff0c\uff0c\uff0c\uff0c', 32: u'\u522b\u50bb\u903c\u4e86\uff0c\u6218\u4e89\u7684\u5173\u952e\u5728\u4e8e\u9009\u5bf9\u4e86\u5bf9\u624b\u3002\u6d88\u706d\u7f05\u7538\u519b\u6536\u590d\u679c\u6562\u4e5f\u8bb8\u662f\u4e00\u4e2a\u660e\u667a\u7684\u9009\u62e9\u3002\u5982\u679c\u88c5\u903c\u548c\u65e5\u7f8e\u6b7b\u78d5\u6700\u7ec8\u53ea\u80fd\u662f\u60f9\u7978\u4e0a\u8eab\u3002', 33: u'\u9b3c\u5b50\uff01\u4f60\u7ad9\u5230\u5927\u8857\u6765\u653e\u72d7\u5c41\uff01\u4f60\u6562\u5417\uff1f\u4e0d\u51fa\u4e00\u5206\u949f\u5c31\u80fd\u8ba9\u4f60\u53ea\u6709\u51fa\u6c14\u6ca1\u8fdb\u6c14\uff01\u4e0d\u4fe1\uff1f\u4f60\u8bd5\u8bd5\uff01',
         34: u'\u5c71\u59c6\u60f3\u641e\u4e71\u7f05\u7538\uff0c\u963b\u6b62\u4e1d\u7ef8\u4e4b\u8def',
         35: u'\u660e\u767d\u4eba', 36: u'\u679c\u6562\u90fd\u6253\u5b8c\u4e86\uff0c\u7f05\u519b\u90fd\u64a4\u56de\u4e86\u3002\u4f60\u7ec8\u4e8e\u6562\u9732\u5934\u6f14\u4e60\u4e86\u3002', 37: u'\u9519\uff01\u662f\u9001\u7ed9\u5927\u7f05\u7538\u7684\u3002', 38: u'\u5916\u5a92\u53c8\u51fa\u6765\u9020\u8c23\u4e86\uff0c\u72d7\u6742\u4eec\u53c8\u5f00\u59cb\u9ad8\u6f6e\u4e86\u3002', 39: u'\u4e00\u6b21\u4e34\u65f6\u6f14\u4e60\uff0c\u4e0d\u8981\u523b\u610f\u8fc7\u5ea6\u89e3\u8bfb\u3002', 40: u'\u5e9f\u96641960\u5e74\u4e0e\u7f05\u7538\u7b7e\u8ba2\u7684\u8fb9\u754c\u534f\u5b9a\u6761\u7ea6\uff08\u4e16\u754c\u4e0a\u6700\u65e0\u80fd\u7684\u6761\u7ea6\uff09\uff0c\u4e5f\u5c31\u662f\u5426\u5b9a\u6bdb\u5f53\u5e74\u7684\u51b3\u5b9a\u3002', 41: u'\u697c\u4e0a\u4eca\u65e5\u8fdb\u5e10\u4e94\u89d2', 42: u'\u53eb\u4e0a\u90a3\u4e24\u4f4d\u5728\u8c34\u8d23\u3001\u6297\u8bae\u4e00\u4e0b\u5c31\u884c\u4e86\uff0c\u6f14\u620f\u662f\u8981\u82b1\u7eb3\u7a0e\u4eba\u94b1\u7684\uff01\uff01', 43: u'\u516c\u6c11\u7684\u4e49\u52a1\u5c31\u662f\uff1a1\u3001\u6211\u8bf4\u4ec0\u4e48\u4f60\u7167\u505a\uff0c2\u3001\u770b\u61c2\u4e86\u4e5f\u522b\u8bf4\u7a7f\u3002', 44: u'\u5982\u6b64\u8fd8\u4e0d\u591f\u5417\uff0c\u96be\u9053\u4f60\u8fd8\u60f3\u6253\u6218\uff0c\u518d\u8fc7\u4e0a\u82e6\u65e5\u5b50\uff1f\uff1f', 45: u'\u5c3c\u739b\u6bd4', 46: u'\u62ff\u7f05\u7538\u7ec3\u7ec3\u5175\u591a\u597d\u5440\uff0c\u600e\u4e48\u5c31\u4e0d\u6562\u52a8\u5462', 47: u'\u8fd8\u8981\u7b49\u7740\u4eba\u5bb6\u5f80\u4f60\u5403\u996d\u7684\u7897\u91cc\u62c9\u7b2c\u4e09\u6b21\u5417\uff1f', 48: u'\u4e0a\u4e16\u7eaa60\u5e74\u4ee3\u6253\u8fc7\uff0c\u8054\u5408\u7f05\u519b\u6253\u56fd\u519b\uff0c\u6e05\u527f\u8fc7\u540e\u6c5f\u5fc3\u5761\u9001\u7ed9\u7f05\u7538\u3002', 49: u'\u53bb\u533b\u9662\u67e5\u67e5\u4f60\u662f\u4e0d\u662f\u6709\u9ed1\u4eba\u7684\u57fa\u56e0~\u636e\u8bf4\u5e7f\u5dde\u90a3\u9ed1\u4eba\u6210\u707e\u554a~\u4e0d\u662f\u4f60\u5988\u51fa\u53bb\u561a\u745f\u4e00\u5708~\u6709\u4e86\u4f60\u554a\uff1f'}
    print a.values()
    doc_classify(a,b)


