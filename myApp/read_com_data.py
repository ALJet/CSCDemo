import datetime
import serial
import time
import threading


# 把线程改成了进程 但是 没有加上进程锁
# 不能该成进程啊 进程不能修改model django框架定的 好像也不能读com口


# ser.baudrate＝9600#设置波特率
# ser.bytesize＝8#字节大小
# ser.bytesize＝serial.EiGHTBITS#8位数据位
#
# ser.parity=serial.PARITY_EVEN#偶校验
# ser.parity=serial.PARITY_NONE#无校验
# ser.parity=serial.PARITY_ODD#奇校验
#
# ser.stopbits＝1#停止位
# ser.timeout＝0.5#读超时设置
# ser.writeTimeout＝0.5#写超时
# ser.xonxoff#软件流控
# ser.rtscts#硬件流控
# ser.dsrdtr#硬件流控
# ser.interCharTimeout#字符间隔超时
# com口的一些相关参数说明
# Port='COM3',Baudrate=4800,Prity=serial.PARITY_EVEN,StopBits=serial.STOPBITS_ONE

class ComThread:
    file = None

    def __init__(self, Port='COM3', Baudrate=4800, Prity=serial.PARITY_NONE, Stopbits=serial.STOPBITS_ONE,
                 Bytesize=serial.EIGHTBITS, AB=True):
        self.l_serial = None
        self.alive = False
        self.waitEnd = None
        self.port = Port
        self.baurate = Baudrate
        self.prity = Prity
        self.stopbits = Stopbits
        self.bytesize = Bytesize
        self.ab = AB
        # 我觉得 少了个Data bits
        self.ID = None
        self.data = None

    def waiting(self):
        if not self.waitEnd is None:
            self.waitEnd.wait()

    def SetStopEvent(self):
        if not self.waitEnd is None:
            self.waitEnd.set()
        self.alive = False
        self.stop()

    def start(self):
        self.l_serial = serial.Serial()
        self.l_serial.port = self.port
        self.l_serial.baudrate = self.baurate
        self.l_serial.parity = self.prity
        self.l_serial.stopbits = self.stopbits
        self.l_serial.bytesize = self.bytesize
        # self.l_serial.timeout = 5
        # 设置缓冲区 默认4096  可能需要更小
        #Linux下没有改属性 需要重新编写
        #self.l_serial.set_buffer_size(16)
        self.l_serial.open()
        if self.l_serial.isOpen():
            self.waitEnd = threading.Event()
            self.alive = True
            self.thread_read = None
            self.thread_read = threading.Thread(target=self.FirstReader)
            self.thread_read.setDaemon(1)
            self.thread_read.start()

            return True
        else:
            return False

    def FirstReader(self):

        while self.alive:
            '''测试了许多时间估计最终编码是用ISO-8859-1 
            '''
            # 编码格式 ISO-8859-1  ASCII   UTF-8   Unicode  UTF-16  UTF-32  gbk
            data = ''
            #data = data.encode('ASCII')
            data = data.encode('ISO-8859-1')

            while(True):
                lock = threading.Lock()
                lock.acquire()
                data = self.l_serial.read()
                #data = data.encode('ISO-8859-1')
                #data = data.decode('ASCII')
                filename = writeFile(self.ab)
                filename.write(data)
                #filename.write(data.encode('ISO-8859-1'))
                filename.close()
                lock.release()
        self.waitEnd.set()
        self.alive = False

    def stop(self):
        self.alive = False
        self.thread_read.join()
        # self.p.join()
        if self.l_serial.isOpen():
            self.l_serial.close()


# 写入文件 'a+'没有创建 有覆盖 指针在最后
def writeFile(ab):
    if ab:
        filename = time.strftime("%Y-%m-%d", time.localtime()) + 'A.cmt'
    else:
        filename = time.strftime("%Y-%m-%d", time.localtime()) + 'B.cmt'
    #out = open('./ComData/' + filename, 'a+',encoding='ASCII')
    out = open('./ComData/' + filename, 'ab+')
    return out
