# Dshield

Dshield is a lightweight tool for defending DDoS, which has good performance on defending DDoS attacks of CC, pressure measurement softwares and other DDoS tools . but actually it does not has the ability to intercept attacks. It is based on IPtables firewall, using SS command to filter suspicious IPs and acting together with IPtables firewall to defend. When DDos attacking, this tool will analyse the purpose of origin of these links in real time and add the origin ips to the DROP chain of IPtables. Meanwhile these IPs will be added to the database. But we will unblock the IP until preset ttl. It performs quite well on the basic tests of the concurrent attacks, cc attacks of single IP. It is not suitable for the truly big stream attacks, but it can handle the lightweight DDoS as long as the flow does not excess the maximum bandwidth of server which may crash the service. Dshield may be the easiest and simplest software-level DDoS defense solution. It is developed with python which is easy to read and convenient for further modifying.

Dshield has been updated for 4 versions which origin name is “DDos-defender”, v4.0.0 adds GUI based on web visualization and was reconstructed totally on code-level. Dshield adapts influxDB+grafana on the basic constructure because of web visualized orientation. You can run it without installing any extra http services, because grafana has integrated a set of http service within, and the GUI is user-definable. It is very easy to use and hope you enjoy it. 

Dshield是一个轻量型的DDos防护工具，它在受到如CC、压测工具等拒绝服务攻击时，能进行比较有效的防御。实际上它并不具备阻截能力，它是基于IPtables防火墙，利用类似于SS命令过滤出可疑IP，与IPtables防火墙实现联动。在发生恶意拒绝服务攻击时，本工具会实时分析连接来源的企图，并自动将其加入iptables防火墙的DROP链表中进行阻截。同时将攻击IP记录数据库中，当达到预定时间后，工具自动从IPtables防火墙中解封对应IP。在基本测试过程中，应付单IP并发连接攻击、cc攻击等效果明显。但它并不适合于真正的大流量攻击，只要攻击流量不超过服务器的最高带宽一般不会造成服务宕机，能对抗轻量DDOS。它也许是在软件级别上安装最方便和最简单的一个解决方案。本工具完全由python开发，程序简单易读，方便后期修改。

本工具经过了4次更新，原名叫“DDoS-Defender”，本版本V4.0.0中新增了基于web可视化的图形界面,代码层基本上全部进行了重构。由于面向web可视化，所以底层架构上采用了influxDB + grafana的结合，你可以不需要安装任何额外的http服务来支持它的运行，因为grafana工具已集成了一套http服务，且图形是可自定义配置的。使用起来相当容易。保证你会喜欢上它！

## Constructure
* Dshield/conf     Configure files
* Dshield/data     Data buffer storage
* Dshield/lib      Library of modules
* Dshield/sbin     Main program
* Dshield/logs     Logs directory
* Dshield/test     Test cases

## Installation

Install Dshield with root user:

(1) Install grafana
```shell
yum -y install https://grafanarel.s3.amazonaws.com/builds/grafana-4.0.2-1481203731.x86_64.rpm
service grafana-server start
```
or install it by adding yum source, vi /etc/yum.repos.d/grafana.repo and add the content below.
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

Then install it by yum and start grafana-server by service command.
```shell
yum install grafana
service grafana-server start
```

(2) Install Dshield
```shell
wget https://github.com/ywjt/Dshield/archive/master.zip
unzip master.zip
cd Dshield-master/
sh install.sh
```

Installation finished and you can start it now!
```shell
service grafana-server restart
/usr/local/Dshield/sbin/dshield all start
```
Now you can log in the administration backend by URL http://{your_ip}:3000
username: admin
password: admin

<img src="https://github.com/ywjt/Dshield/blob/master/demo.png">

## Help

**command usage**
```shell
# /usr/local/Dshield/sbin/dshield all {start|stop|restart}    #Start all service
# /usr/local/Dshield/sbin/dshield cc {start|stop|restart}     #Start cc process
# /usr/local/Dshield/sbin/dshield sniff {start|stop|restart}  #Start ttl modle
# /usr/local/Dshield/sbin/inflctl {start|stop|restart}        #Only start InfluxDB process
```

**modified configure file**

Open File: /usr/local/Dshield/conf/default.ini


**white list**

support CIRD format
> whitelisted_ips = "10.10.10.0/24,172.16.0.0/16"

> whitel_ttl_ips = "10.10.10.0/24,172.16.0.0/16"

**monitor interface**
> mont_interface = "eth0"

**monitor port**
> mont_port = "80,22"

**listen mode**
false means active defense, true means only record IP and ttl but not block
> mont_listen = false

**monitor interval**
specified in seconds
> rexec_time = 5

**block connections**
this parameter can assign the sensitivity of monitoring, 100 is recommanded
> no_of_connections = 100

**ip block time**
support 1d/1h/1m format
> block_period_ip = "1m"

**monitor protocol**
it is available for TTL monitor module, tcp-tcp only, udp-udp only, ‘’-all protocols are monitored
> mont_protocol = "tcp"

**block connections**
this parameter can assign the sensitivity of monitoring, 20000~100000 is recommanded
> no_ttl_connections = 20000

**ttl unblock time**
surpport 1d/1h/1m format
> block_period_ttl = "1m"


## About

**Original Author:** YWJT http://www.ywjt.org/ (Copyright (C) 2016)

**Maintainer:** Sunshine Koo <350311204@qq.com>

<img src="http://www.ywjt.org/ywjtshare.png" width="200px">
