#!/usr/bin/env python
# encoding=utf-8


import ConfigParser
import sys, os
sys.path.append("..")

PROC_DIR =  os.path.abspath('..')

class LoadConfig:
    cf = ''
    filepath = PROC_DIR + "/conf/default.ini"

    def __init__(self):
        try:
            f = open(self.filepath, 'r')
        except IOError, e:
            print "\"%s\" Config file not found." % (self.filepath)
            sys.exit(1)
        f.close()

        self.cf = ConfigParser.ConfigParser()
        self.cf.read(self.filepath)

    def getSectionValue(self, section, key):
        return self.getFormat(self.cf.get(section, key))

    def getSectionOptions(self, section):
        return self.cf.options(section)

    def getSectionItems(self, section):
        return self.cf.items(section)

    def getFormat(self, string):
        return string.strip("'").strip('"').replace(" ","")