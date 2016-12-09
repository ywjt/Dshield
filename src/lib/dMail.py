#!/usr/bin/env python
# encoding=utf-8
"""
* @ Dshield for Python
##############################################################################
# Author: YWJT / Sunshine Koo                                                #
# Modify: 2016-12-08                                                         #
##############################################################################
# This program is distributed under the "Artistic License" Agreement         #
# The LICENSE file is located in the same directory as this program. Please  #
# read the LICENSE file before you make copies or distribute this program    #
##############################################################################
"""

import sys
sys.path.append("..")
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from lib.dLog import save_log
from lib import Dshield


class PyEmail(Dshield):
    sender = ''     #发送者
    
    """
    @name: 构造函数
    @desc: 读取配置文件,初始化变量
    """
    def __init__(self):
        Dshield.__init__(self)

        if not self.avr['username'].find('@'):
            self.sender = self.avr['smtpserver'].replace(self.avr['smtpserver'].split('.')[0]+'.',self.avr['username']+'@')
        else:
            self.sender = self.avr['username']  
        

    """
    @name: 普通发信模式
    @desc: 不需要SSl认证
    """
    def nonsend(self,subject,msg):
        self.__init__()
        msg = MIMEText(msg,'plain','utf-8') #中文需参数‘utf-8’，单字节字符不需要
        msg['Subject'] = subject
        smtp = smtplib.SMTP()
        smtp.connect(self.avr['smtpserver'])
        smtp.login(self.avr['username'], self.avr['password'])
        smtp.sendmail(self.sender, self.avr['receiver'], msg.as_string())
        smtp.quit()
        
    """
    @name: SSL发信模式
    @desc: 支持google邮箱
    """
    def sslsend(self,subject,msg):
        self.__init__()
        msg = MIMEText(msg,'plain','utf-8') #中文需参数‘utf-8’，单字节字符不需要
        msg['Subject'] = Header(subject, 'utf-8')
        smtp = smtplib.SMTP()
        smtp.connect(self.avr['smtpserver'])
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.set_debuglevel(1)
        smtp.login(self.avr['username'], self.avr['password'])
        smtp.sendmail(self.sender, self.avr['receiver'], msg.as_string())
        smtp.quit()
        
    """
    @name: 发送邮件
    """    
    def sendto(self,subject,msg):
        if str(self.avr['type']) == 'ssl':
            try:
                self.sslsend(subject,msg)
                save_log('MAIL','Send mail Success.')
            except Exception, e:
                save_log('MAIL','Send mail failed to: %s' % e)
        else:
            try:
                self.nonsend(subject,msg)
                save_log('MAIL','Send mail Success.')
            except Exception, e:
                save_log('MAIL','Send mail failed to: %s' % e)
    
