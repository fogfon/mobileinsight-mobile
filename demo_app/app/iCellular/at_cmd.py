#!/usr/bin/python
# Filename: at_cmd.py

"""

An interface for AT commands

Author: Yuanjie Li

"""

import sys
import subprocess
import codecs

ANDROID_SHELL = "/system/bin/sh"
at_log_file = "/sdcard/at_tmp.txt"

class AtCmd(object):
    
    def __init__(self, at_device):

        '''
        Initialize the at command interface. Disable the echo mode

        :param at_device: the serial port name for AT command
        :types at_device: string
        '''

        # self._run_shell_cmd("su -c chown root "+at_device,True)
        # self._run_shell_cmd("su -c chgrp sdcard_rw "+at_device,True)
        self._run_shell_cmd("su -c chmod 777 " + at_device, True)

        # self.phy_ser = open(at_device,"rw")
        self.at_device = at_device

        at_res_cmd = "su -c cat " + at_device + ">" + at_log_file
        self.at_proc = subprocess.Popen(at_res_cmd, executable = ANDROID_SHELL, shell = True)

        self.cmd_count = 0  #succesful command execution

        #disable echo mode
        self.run_cmd("ATE0")

    def _run_shell_cmd(self, cmd, wait = False):
        p = subprocess.Popen(cmd, executable = ANDROID_SHELL, shell = True)
        if wait:
            p.wait()
            return p.returncode
        else:
            return None


    def is_running(self):
        '''
        Test if an AT command is running

        :returns: True if an AT command is running, False otherwise
        '''

        #Current implementation: compare the count of successful execution and available counts in list
        #If they are equal, it means no command is running
        #TODO: optimize this code to avoid redundant scanning
        while True:
            res = ""
            count = 0
            with codecs.open(at_log_file, encoding = 'utf8') as fp:
                while True:
                    s = fp.readline()
                    if not s:
                        break
                    res += s
                    if len(res) > 2 and res[-2] == "\r" and res[-1] == "\n":
                        #Read next line until the end
                        count = count + 1
                        res = ""
            if count>self.cmd_count:
                #A new record is included, so no command is running
                #Update the command count
                self.cmd_count = self.cmd_count + 1
                return False
            else:
                return True




    def run_cmd(self, cmd, wait = False):
        '''
        Send an AT command, return responses

        :param cmd: the command to be sent
        :type cmd: string
        :param wait: whether to wait for the responses of AT command
        :type wait: boolean
        :returns: the return value of AT command if wait==True, otherwise empty string
        '''
        full_cmd = 'su -c \"echo -e \'' + cmd + '\\r\\n\' > ' + self.at_device + "\""
        p = subprocess.Popen(full_cmd, executable = ANDROID_SHELL, shell = True)
        p.wait()

        if not wait:
            return ""
        
        while True:
            res = ""
            count = 0
            with codecs.open(at_log_file, encoding = 'utf8') as fp:
                while True:
                    s = fp.readline()
                    if not s:
                        break
                    res += s
                    if len(res) > 2 and res[-2] == "\r" and res[-1] == "\n":
                        if count == self.cmd_count:
                            break
                        else:
                            count = count + 1
                            res = ""
            if res:
                self.cmd_count = self.cmd_count + 1
                return res

if __name__=="__main__":
    # at_cmd = AtCmd("/dev/smd11")
    at_cmd = AtCmd(at_device)
    print at_cmd.run_cmd("ATD3106148922")