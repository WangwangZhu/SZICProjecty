#! /usr/bin/env python3
###############################################################################################################
###############################################################################################################
# 文件名称：kavser_test.py
# 文件功能：CAN 总线测试程序
# 备注信息：
##############################################################################################################
##############################################################################################################

import sys 
sys.path.append('/usr/local/lib/python3.5/dist-packages/')
import canlib.canlib as canlib
#  cl = canlib.canlib()
num_channels = canlib.getNumberOfChannels()
print("Found %d channels" % num_channels)
for ch in range(0, num_channels):
    #  print("%d. %s (%s / %s)" % (ch, cl.getChannelData_Name(ch),
    print("%d. %s (%s / %s)" % (ch, canlib.ChannelData(ch).channel_name,
        canlib.ChannelData(ch).card_upc_no,
        canlib.ChannelData(ch).card_serial_no))
