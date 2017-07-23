# coding=utf-8
from tornado import httpclient, gen, ioloop
from lxml import etree
import re
import time
import csv

http_asy = httpclient.AsyncHTTPClient(max_clients=100)
category = "21"
url = 'http://www.anyv.net/index.php/category-{0}-page-{1}'

header = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "zh-CN,zh;q=0.8",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
"Host": "www.anyv.net",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
}

categorys = {"2":u'新闻类',"51":u'财经',"19":u'科技',"25":u'阅读',\
"3":u'搞笑',"20":u'趣玩',"22":u'时尚',"23":u'生活',"26":u'健康',\
"27":u'旅游',"28":u'运动',"29":u'影音',"21":u'教育',"70":u'品牌',\
"80":u'购物',"1":u'明星',"18":u'名人',"24":u'美女'}

@gen.coroutine
def get():
    with open('wxh.csv', 'w+') as f:
        ff = csv.writer(f)
        for key in categorys.keys():
            count = 0
            for i in range(1, 210):
                try:
                    response = yield http_asy.fetch(url.format(key, i), headers=header)
                    print url.format(key, i)
                    root = etree.HTML(response.body.decode('gbk'))
                    url_list = root.xpath('//div[@class="newpicsmall_list"]/a/@href')
                    if not url_list:
                        print "not found url."
                        count += 1
                    if count == 4:
                        print "not found url, we will break."
                        break
                    response = yield [http_asy.fetch(ur, headers=header, connect_timeout=40, request_timeout=40, raise_error=False) for ur in url_list]
                    for res in response:
                        if res.body:
                            num = re.findall(u'微信号:(.*)', res.body.decode('gbk'))
                            name = re.findall(u'<h1>(.*)</h1>', res.body.decode('gbk'))
                            if num and name and len(name) == 1 :
                                print name[0].encode('utf8'), num[0].replace('<br> ', '').encode('utf8')
                                #ff.writerow([name[0].encode('utf8'), num[0].replace('<br> ', '').encode('utf8')])
                                ff.writerow([name[0].encode('gbk'), num[0].replace('<br> ', '').encode('utf8')])
                except Exception, e:
                    print i
                    print e
                    continue




ioloop.IOLoop.current().run_sync(get)
