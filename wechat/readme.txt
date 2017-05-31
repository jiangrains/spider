使用说明
1.需要在server安装mitmproxy2.0.2/beautifulsoup4/mongodb/pymongo等，基于python3开发；
2.配置server和测试android手机连接同一个wifi网络；
3.配置android手机的代理服务器为server的ip地址；
4.在android手机浏览器上访问mitm.it，配置安全证书，使mitmproxy可以截获https请求；
5.在server端开启mongod；
6.将spider.py拷贝至server内，并在server终端内执行mitmdump -s spider.py；
7.在android手机上进行微信公众号测试，并在server终端内查看mitmproxy的运行情况。
