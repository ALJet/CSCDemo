import datetime
import threading
import time
from .models import LPGRecord
from pathlib import Path
from django.db.models import Q


class WriteDB:
    def __init__(self, AB=True):
        self.ab = AB
        # if AB:
        #     self.filename = time.strftime("%Y-%m-%d", time.localtime()) + 'A.txt'
        # else:
        #     self.filename = time.strftime("%Y-%m-%d", time.localtime()) + 'B.txt'
        # self.path = './ComData/' + self.filename
        self.alive = False

    def start(self):
        self.alive = True
        self.thread_read = threading.Thread(target=self.read2db)
        self.thread_read.setDaemon(1)
        self.thread_read.start()

    def stop(self):
        self.alive = False
        # self.p.join()
        self.thread_read.join()

    # 要确保数据的完整性 什么意思呢 txt里面 Batch Summary 中的字段必须从头到尾 数据要完整 不然会报错 因为截取不到一下字符串的数据 summarys数组从1开始
    def read2db(self):
        while self.alive:
            # 觉得有必要设置一下线程休息 好让数据完全写入到txt在读取 设置3到5秒
            time.sleep(5)
            # print('read2db')
            self.path = './ComData/' + read_file(self.ab)
            my_file = Path(self.path)
            if my_file.exists():
                # print('打开ComData里面的文件')
                # print(self.path)
                self.file = open(self.path, 'r', encoding='ISO-8859-1')
                recoder = self.file.read()

                self.file.close()
                summarys = recoder.split('Batch Summary')
                # if len(summarys) == 1:
                # print('没有匹配到Batch Summary')

                if len(summarys) != 1:

                    if len(summarys[-1]) >= 520:
                        summarys = summarys[1:]
                    else:
                        summarys = summarys[1:-1]
                    for summary_value in summarys:
                        try:
                            summary = summary_value[:550]

                            transaction = summary[13:18].strip()
                            if (is_number(transaction)):
                                transaction = int(transaction)
                            else:
                                transaction = -1
                            side = summary[24:25]
                            if (is_number(side)):
                                side = int(side)
                            else:
                                side = -1
                            #
                            # # 暂时没有mix在处理
                            mix = summary[27:31]
                            property = summary[27:34]
                            mix_value = summary[31:35]
                            bay = summary[53].strip()
                            if (is_number(bay)):
                                bay = int(bay)
                            else:
                                bay = -1
                            bl_no = summary[81:86].strip()
                            if (is_number(bl_no)):
                                bl_no = int(bl_no)
                            else:
                                bl_no = -1

                            # # # customer 是否需要4位数
                            customer_no = summary[124:128].strip()
                            if (is_number(customer_no)):
                                customer_no = int(customer_no)
                            else:
                                customer_no = -1
                            drive_no = summary[163:171].strip()
                            if (is_number(drive_no)):
                                drive_no = int(drive_no)
                            else:
                                drive_no = -1
                            preset = summary[190:197].strip()
                            if (is_number(preset)):
                                preset = int(preset)
                            else:
                                preset = -1
                            gross = summary[204:211].strip()
                            if (is_number(gross)):
                                gross = int(gross)
                            else:
                                gross = -1
                            started = summary[231:248]

                            if (is_valid_date(started)):
                                started_af = datetime.datetime.strptime(started, '%d-%m-%y %H:%M:%S')
                            else:
                                started_af = -1

                            stopped = summary[258:275]
                            if (is_valid_date(stopped)):
                                stopped_af = datetime.datetime.strptime(stopped, '%d-%m-%y %H:%M:%S')
                            else:
                                started_af = -1

                            butane = summary[453:461].strip()
                            if (is_number(butane)):
                                butane = int(butane)
                            else:
                                butane = -1
                            propane = summary[511:518].strip()
                            if (is_number(propane)):
                                propane = int(propane)
                            else:
                                propane = -1
                            fill_time = -1
                            if (is_valid_date(started) and is_valid_date(stopped)):
                                fill_time_str = stopped_af - started_af
                                fill_time = int(str(fill_time_str)[2:4].strip())


                        except ValueError or TypeError:
                            raise Exception

                        if mix == 'Mix ' or mix == 'Mix':
                            # mix_value = 'MIX ' + mix_value
                            mix_value = mix_value.strip() + '%'
                        else:
                            mix_value = 'Propane'

                        if gross > 100:
                            count = LPGRecord.objects.filter(
                                Q(transaction_no=transaction) & Q(bay=bay) & Q(bl_no=bl_no) & Q(
                                    customer_no=customer_no)).count()
                            if count == 0:
                                LPGRecord.objects.create(transaction_no=transaction, side=side,
                                                         proportion=mix_value,
                                                         bay=bay,
                                                         bl_no=bl_no,
                                                         customer_no=customer_no, drive_no=drive_no,
                                                         preset=preset,
                                                         gross=gross,
                                                         started=started_af, stopped=stopped_af,
                                                         fill_time=fill_time, butane=butane,
                                                         propane=propane)


def read_file(a):
    if a:
        return time.strftime("%Y-%m-%d", time.localtime()) + 'A.cmt'
    else:
        return time.strftime("%Y-%m-%d", time.localtime()) + 'B.cmt'


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def is_valid_date(str):
    '''判断是否是一个有效的日期字符串'''
    try:
        datetime.datetime.strptime(str, '%d-%m-%y %H:%M:%S')
        # time.strptime(str, '%d-%m-%y %H:%M:%S')
        return True
    except:
        return False
