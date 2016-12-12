# Dshield

Dshield是一个轻量型的DDos防护工具，它在受到如CC、压测工具等拒绝服务攻击时，能进行比较有效的防御。实际上它并不具备阻截能力，它是基于IPtables防火墙，利用类似于SS命令过滤出可疑IP，与IPtables防火墙实现联动。在发生恶意拒绝服务攻击时，本工具会实时分析连接来源的企图，并自动将其加入iptables防火墙的DROP链表中进行阻截。同时将攻击IP记录数据库中，当达到预定时间后，工具自动从IPtables防火墙中解封对应IP。在基本测试过程中，应付单IP并发连接攻击、cc攻击等效果明显。但它并不适合于真正的大流量攻击，只要攻击流量不超过服务器的最高带宽一般不会造成服务宕机，能对抗轻量DDOS。它也许是在软件级别上安装最方便和最简单的一个解决方案。本工具完全由python开发，程序简单易读，方便后期修改。

本工具经过了4次更新，原名叫“DDoS-Defender”，本版本V4.0.0中新增了基于web可视化的图形界面,代码层基本上全部进行了重构。由于面向web可视化，所以底层架构上采用了influxDB + grafana的结合，你可以不需要安装任何额外的http服务来支持它的运行，因为grafana工具已集成了一套http服务，且图形是可自定义配置的。使用起来相当容易。保证你会喜欢上它！

### 程序结构
* Dshield/conf     配置文件
* Dshield/data     存放数据缓存
* Dshield/lib      功能模块实例
* Dshield/sbin     主程序
* Dshield/logs     日志输出记录
* Dshield/test     测试用例

##  安装 Installation

使用root用户来进行安装(<del>要求你本机使用python2.6 Centos系统</del>):

(1)安装grafana
```shell
yum -y install https://grafanarel.s3.amazonaws.com/builds/grafana-4.0.2-1481203731.x86_64.rpm
```

或者添加YUM源的方式，使用vi /etc/yum.repos.d/grafana.repo 将以下内容追加到文件里：
```shell
[grafana]
name=grafana
baseurl=https://packagecloud.io/grafana/stable/el/6/$basearch
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packagecloud.io/gpg.key https://grafanarel.s3.amazonaws.com/RPM-GPG-KEY-grafana
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
```
然后执行YUM安装以及使用service命令启动
```shell
yum install grafana
```

(2) 安装Dshield
```shell
wget https://github.com/ywjt/Dshield/archive/master.zip
unzip master.zip
cd Dshield-master/
sh install.sh
```

安装完成，现在可以启动Dshield工具！
```shell
service grafana-server restart
/usr/local/Dshield/sbin/dshield all start
```
赶紧打开 http://{your_ip}:3000/ 看看。

用户名/密码：admin /admin 

<img src="https://github.com/ywjt/Dshield/blob/master/demo.png">

## 使用帮助

**命令使用**
```shell
# /usr/local/Dshield/sbin/dshield all {start|stop|restart}    #启动全部服务
# /usr/local/Dshield/sbin/dshield cc {start|stop|restart}     #启动主进程
# /usr/local/Dshield/sbin/dshield sniff {start|stop|restart}  #启动ttl模块
# /usr/local/Dshield/sbin/inflctl {start|stop|restart}        #独立启动数据缓存
```

**修改配置文件**

打开 /usr/local/Dshield/conf/default.ini


**白名单列表**

支持CIRD格式 
> whitelisted_ips = "10.10.10.0/24,172.16.0.0/16"

> whitel_ttl_ips = "10.10.10.0/24,172.16.0.0/16"

**监控接口**
> mont_interface = "eth0"

**监控端口**
> mont_port = "80,22"

**监听模式**
false 表示主动防御
true  表示只作记录不会锁IP,ttl
> mont_listen = false

**监控密度,单位为秒**
> rexec_time = 5

**锁定连接数,该项能确定监控的敏感度**
建议：100
> no_of_connections = 100

**ip封锁时间**
支持1d/1h/1m格式
> block_period_ip = "1m"

**监控协议**
对TTL监控模块生效
tcp 模式
udp 模式
''  表示所有协议
> mont_protocol = "tcp"

**锁定连接数,该项能确定监控的敏感度**
建议：100000
> no_ttl_connections = 100000

**ttl封锁时间**
支持1d/1h/1m格式
> block_period_ttl = "1m"


