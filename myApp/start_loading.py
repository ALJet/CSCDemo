from .read_com_data import ComThread
from .com_to_db import WriteDB
from django.conf import settings
import serial


def read_com():
    com1 = ComThread(settings.PORT1, settings.BAUDRATE, settings.PRITY, settings.STOPBITS, settings.BYTESIZE, True)
    com1.start()

    com2 = ComThread(settings.PORT2, settings.BAUDRATE, settings.PRITY, settings.STOPBITS, settings.BYTESIZE, False)
    com2.start()


def write_db():
    write_com1_db = WriteDB(True)
    write_com1_db.start()

    write_com2_db = WriteDB(False)
    write_com2_db.start()


def loading():
    try:
        read_com()
        write_db()
    #except serial.SerialException:
        #print('com空异常，请检查！是否有两个com口')
    except UnicodeEncodeError:
        print('数据异常，编码异常，估计哪条车道数据乱码！')
    except UnicodeDecodeError:
        print('数据异常，解码异常，估计哪条车道数据乱码！')
