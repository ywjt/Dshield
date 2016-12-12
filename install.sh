#!/bin/bash
#
# @ Dshield for Python
##############################################################################
# Author: YWJT / Sunshine Koo                                                #
# Modify: 2016-12-10                                                         #
##############################################################################
# This program is distributed under the "Artistic License" Agreement         #
# The LICENSE file is located in the same directory as this program. Please  #
# read the LICENSE file before you make copies or distribute this program    #
##############################################################################
#


# Check if user is root
if [ $(id -u) != "0" ]; then
    echo "Error: You must be root to run this script, use sudo sh $0"
    exit 1
fi

SHELL_DIR=$(cd "$(dirname "$0")"; pwd)
BASEDIR=$(dirname $SHELL_DIR)
if [ `cat ~/.bash_profile|grep 'Dshield'|wc -l` -eq 0 ];then
    echo "PATH="$PATH:$SHELL_DIR >> ~/.bash_profile
    echo "export PATH" >> ~/.bash_profile
    export PATH=$PATH:$SHELL_DIR
fi


cd $SHELL_DIR
function header()
{
	echo 
	echo "==========================================================================="
	echo "| Dshield v4.0.0 For Python"
	echo "| Copyright (C)2016,YWJT.org."
	echo "| Author: YWJT / Sunshine Koo"
	echo "| Github: https://github.com/ywjt/Dshield"
	echo "| AuBlog: http://www.ywjt.org"
	echo "==========================================================================="
	echo
	echo "[$(date)] Setup Begin >>>"
}

function option_irq() {
  if [ ! -f /var/log/irq_tmp ]
  then
      if [ ! -z ${MONT_INTERFACE} ]
      then
          /etc/init.d/irqbalance stop 1>/dev/null 2>&1
          IrqID=$(cat /proc/interrupts |grep ${MONT_INTERFACE}|awk -F ':' '{print $1}'|xargs)
          Nx=0
          for Cid in ${IrqID}
          do
              Mex=$(echo $((2**${Nx})))
              Hex=$(printf "%x" ${Mex})
              echo ${Hex} > /proc/irq/${Cid}/smp_affinity
              Nx=$((${Nx}+1))
          done
          echo 1 >> /var/log/irq_tmp
      fi
  fi
}


function chk_iptables() {
	echo "| Check iptables env ... "
	if ! rpm -qa iptables|grep 'iptables' >/dev/null
	then
		yum -y install iptables
	else
	    /sbin/service iptables status 1>/dev/null 2>&1
	    if [ $? -ne 0 ]; then
	        #/etc/init.d/iptables start
	        echo "你的iptables没有启动,请手工执行启动后再跑一次!"
	        echo "/etc/init.d/iptables start"
	        read -p "跳过请按'y', 退出按'n':" act
	        if [[ "${act}" == "n" || "${act}" == "N" ]]
	        then
	        		exit 1
	        fi
	    fi
	fi
}


function chk_tcpdump() {
	echo "| Check tcpdump env ... "
	if [ ! -x /usr/sbin/tcpdump ]
		then
			yum -y install tcpdump
	fi
}


function chk_pyenv() {
	echo "| Check python env ... "
	i=1
	for dir in $(find / -name "site-packages" -type d|grep -E '*/lib/python2.[0-9]/site-packages$')
	do
		echo "Python Env ($i):" $dir
		/bin/cp -rf site-packages/* $dir/
		let i=$i+1
	done
}

function grafana_init() {
	echo "| Install grafana ..."
	if ! rpm -qa grafana|grep 'grafana' >/dev/null
	then
		yum -y install https://grafanarel.s3.amazonaws.com/builds/grafana-4.0.2-1481203731.x86_64.rpm
	fi
	service grafana-server start
}


function dshield_init() {
	echo "| Install dshield ..."
	#if [ ! -f Dshield.zip ]
	#then
	#	wget https://github.com/ywjt/Dshield/archive/master.zip -O Dshield.zip
	#	[ -d Dshield ] && rm -rf Dshield
	#	unzip Dshield.zip
	#	cd Dshield
	#fi
	/bin/cp -rf src /usr/local/Dshield
	/bin/cp -f grafana.db /var/lib/grafana/
	chk_pyenv
	chown root:root /usr/local/Dshield
	chmod 775 -R /usr/local/Dshield
}

####### >>>>>>>>>>>>>>>>>>>
header
chk_iptables
chk_tcpdump
option_irq
grafana_init
dshield_init
####### >>>>>>>>>>>>>>>>>>>
echo
echo "==========================================================================="
echo "| 首先: service grafana-server restart"
echo "| 然后: /usr/local/Dshield/sbin/dshield all start"
echo "| 现在: 打开 http://your_ip:3000/ 输入用户名/密码: admin /admin"
echo "| 尽情: Enjoy!"
echo "==========================================================================="
echo 
