使用说明
1.需要在server安装mitmproxy2.0.2/beautifulsoup4/mongodb/pymongo等，基于python3开发；
2.配置server和测试android手机连接同一个wifi网络；
3.配置android手机的代理服务器为server的ip地址；
4.在android手机浏览器上访问mitm.it，配置安全证书，使mitmproxy可以截获https请求；
5.在server端开启mongod；
6.将spider.py拷贝至server内，并在server终端内执行mitmdump -s spider.py；
7.在android手机上进行微信公众号测试，并在server终端内查看mitmproxy的运行情况；

关于数据库
8.数据库的名字为"wechat",可通过dbname变量指定；
9.存放文章的表为"articles",可通过collection_articles变量指定；
10.存放公众号的表为"official_accounts"，可通过collection_official_accounts变量指定，公众号表单还存放最新10篇文章列表；
