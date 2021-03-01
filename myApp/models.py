import datetime

from django.db import models

# Create your models here.
from django.utils import timezone


class LPGRecord(models.Model):
    transaction_no = models.IntegerField(verbose_name='流水号')
    side = models.IntegerField(verbose_name='充装数据机器号')
    proportion = models.CharField(max_length=20, verbose_name='比例')
    bay = models.IntegerField(verbose_name='车道')
    bl_no = models.IntegerField(verbose_name='提单号')
    customer_no = models.IntegerField(verbose_name='客户号')
    drive_no = models.IntegerField(verbose_name='车牌号')
    preset = models.IntegerField(verbose_name='预装数量')
    gross = models.IntegerField(verbose_name='实际数量')
    started = models.DateTimeField(verbose_name='开始时间')
    stopped = models.DateTimeField(verbose_name='结束时间')
    fill_time = models.IntegerField(default=0, verbose_name='充装时间(分钟)')
    # auto_now_add=True
    load_database_time = models.DateTimeField(default=timezone.now,
                                              verbose_name='入库时间')
    butane = models.IntegerField(verbose_name='C4 数量')
    propane = models.IntegerField(verbose_name='C3 数量')

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_no': self.transaction_no,
            'proportion': self.proportion,
            'bay': self.bay,
            'bl_no': self.bl_no,
            'customer_no': self.customer_no,
            'drive_no': self.drive_no,
            'preset': self.preset,
            'gross': self.gross,
            'started': self.started,
            'stopped': self.stopped,
            'fill_time': self.fill_time,
            'load_database_time': self.load_database_time,
            'butane': self.butane,
            'propane': self.propane
        }

    class Meta:
        # db_table = 'LPGRecord_table'
        # managed = False
        ordering = ['-started']
