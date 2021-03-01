import datetime
import os
import threading
import time
from io import BytesIO

import xlwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView

from myApp.misc import get_query
from .models import LPGRecord

from .start_loading import loading
from django.db.models import Q
from .forms import LPGForm, LoginForm

# Create your views here.

# django项目启动时，一起执行  读取com口数据写入txt文本 在从txt读取写入数据库中
loading()

User = get_user_model()

Excel_query = None

page = 1


def get_default_ordering():
    return getattr(settings, 'LPG_DEFAULT_STARTED_ORDERING', '-started')


def get_lpg_ordering(request):
    query_order = request.GET.get('order', '')
    if query_order in ['-started', 'started', '-transaction_no', 'transaction_no']:
        return query_order
    return get_default_ordering()


class Index(ListView):
    model = LPGRecord
    paginate_by = settings.PAGINATE_BY
    template_name = 'list.html'
    context_object_name = 'lpg_list'

    def get_queryset(self):
        global Excel_query
        Excel_query = LPGRecord.objects.all().order_by(
            get_lpg_ordering(self.request)
        )
        global page
        page = self.kwargs.get('page')
        return LPGRecord.objects.all().order_by(
            get_lpg_ordering(self.request)
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['show_order'] = True
        context['title'] = '首页'
        context['panel_title'] = '充装记录'
        return context


class SearchView(ListView):
    model = LPGRecord
    paginate_by = settings.PAGINATE_BY
    template_name = 'search.html'
    context_object_name = 'lpg_list'

    def get_queryset(self):
        keywords = self.kwargs.get('keyword')
        keywords = keywords.strip()
        print('keywords = ', keywords)
        global Excel_query

        global page
        page = self.kwargs.get('page')
        # query = get_query(keywords,['transaction_no','bl_no','drive_no'])
        if 'date=' in keywords and 'bay=' in keywords:
            bayIndex = keywords.find('bay')
            bay = keywords[bayIndex + 4: bayIndex + 5]
            dateIndex = keywords.find('date')
            date = keywords[dateIndex + 5:dateIndex + 17]
            query = Q(started__icontains=date) & Q(bay__icontains=bay)

        elif 'bay=' in keywords:
            bayIndex = keywords.find('bay')
            bay = keywords[bayIndex + 4: bayIndex + 5]
            # query = 'bay=%s ' %bay
            query = Q(bay__icontains=bay)


        elif 'date=' in keywords:
            dateIndex = keywords.find('date')
            date = keywords[dateIndex + 5:dateIndex + 17]
            query = Q(started__icontains=date)
            # query = 'started=%s' %date
        else:
            query = Q(bay__icontains=keywords) | Q(started__icontains=keywords)
        Excel_query = LPGRecord.objects.filter(query).order_by(get_lpg_ordering(self.request))
        return LPGRecord.objects.filter(query).order_by(get_lpg_ordering(self.request))

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['show_order'] = True
        context['title'] = '搜索'
        context['panel_title'] = '搜索----模糊搜索(格式如下：bay=? date=?)'
        return context


class overload(ListView):
    model = LPGRecord
    paginate_by = settings.PAGINATE_BY
    template_name = 'list.html'
    context_object_name = 'lpg_list'

    def get_queryset(self):
        global Excel_query
        query = Q(gross__gt=25499) | Q(fill_time__gt=69)
        Excel_query = LPGRecord.objects.filter(query).order_by(
            get_lpg_ordering(self.request)
        )
        global page
        page = self.kwargs.get('page')
        return LPGRecord.objects.filter(query).order_by(
            get_lpg_ordering(self.request)
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['show_order'] = True
        context['title'] = '充装'
        context['panel_title'] = '超载记录'
        return context


@login_required
def edit_lpg(request, pk):
    lpg = LPGRecord.objects.get(pk=pk)
    form = None

    if request.method == 'POST':
        form = LPGForm(request.POST, instance=lpg)
        if form.is_valid():
            l = form.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = LPGForm(instance=lpg)
    return render(request, 'edit.html', {'form': form, 'pk': pk, 'title': '详细'})


def login_view(request):
    # if request.method == 'GET':
    #     return render(request, 'login.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        valid = True
        obj = LoginForm(request.POST)
        res = obj.is_valid()
        if not res:
            return render(request, 'login.html', {'obj': obj})

        lock = threading.Lock()
        lock.acquire()
        user = User.objects.filter(username=username).first()
        lock.release()
        if not user:
            valid = False
            messages.add_message(request, messages.INFO, '用户不存在')
            return render(request, 'login.html')
        user = authenticate(username=username, password=password)
        if (user is not None) and valid:
            if user.is_active:
                lock = threading.Lock()
                lock.acquire()
                login(request, user)
                lock.release()
                return HttpResponseRedirect(reverse('index'))
            else:
                valid = False
                return HttpResponseRedirect(reverse('login'))
        else:
            valid = False
            messages.add_message(request, messages.INFO, '密码错误')
    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


# 导出Excel数据
@login_required
def export_excel(request):
    # if page is None:
    #     page = 1

    # 设置HTTPResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=lpgrecord.xls'
    # 创建一个文件对象
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)

    # 设置文件头的样式,这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
                font:
                    name Arial,
                    colour_index white,
                    bold on,
                    height 0xA0;
                align:
                    wrap off,
                    vert center,
                    horiz center;
                pattern:
                    pattern solid,
                    fore-colour 0x19;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """)
    # 写入文件标题
    sheet.write(0, 0, '序号ID', style_heading)
    sheet.write(0, 1, '流水号', style_heading)
    sheet.write(0, 2, '比例', style_heading)
    sheet.write(0, 3, '车道', style_heading)
    sheet.write(0, 4, '提单号', style_heading)
    sheet.write(0, 5, '客户号', style_heading)
    sheet.write(0, 6, '车牌号', style_heading)
    sheet.write(0, 7, '预装数量', style_heading)
    sheet.write(0, 8, '实际数量', style_heading)
    sheet.write(0, 9, '开始时间', style_heading)
    sheet.write(0, 10, '结束时间', style_heading)
    sheet.write(0, 11, '充装时间(分钟)', style_heading)
    sheet.write(0, 12, '入库时间', style_heading)
    sheet.write(0, 13, 'C4数量', style_heading)
    sheet.write(0, 14, 'C3数量', style_heading)

    # 尝试设置一下列宽
    sheet.col(9).width = 5500
    sheet.col(10).width = 5500
    sheet.col(11).width = 4500
    sheet.col(12).width = 5500

    # 写入数据
    data_row = 1
    paginate_by = int(settings.PAGINATE_BY)
    global Excel_query
    excel_list = Excel_query
    # global page
    # if page == None:
    #     page = 1
    # if page == 1:
    #     excel_list = Excel_query[:paginate_by * page]
    # else:
    #     excel_list = Excel_query[(page - 1) * paginate_by:paginate_by * page]
    # print('page: ',page)
    for i in excel_list:
        sheet.write(data_row, 0, i.id)
        sheet.write(data_row, 1, i.transaction_no)
        sheet.write(data_row, 2, i.proportion)
        sheet.write(data_row, 3, i.bay)
        sheet.write(data_row, 4, i.bl_no)
        sheet.write(data_row, 5, i.customer_no)
        sheet.write(data_row, 6, i.drive_no)
        sheet.write(data_row, 7, i.preset)
        sheet.write(data_row, 8, i.gross)
        sheet.write(data_row, 9, i.started.strftime('%Y-%m-%d %H:%M:%S'))
        sheet.write(data_row, 10, i.stopped.strftime('%Y-%m-%d %H:%M:%S'))
        sheet.write(data_row, 11, i.fill_time)
        sheet.write(data_row, 12, i.load_database_time.strftime('%Y-%m-%d %H:%M:%S'))
        sheet.write(data_row, 13, i.butane)
        sheet.write(data_row, 14, i.propane)
        data_row = data_row + 1

        # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


@login_required
def upload_file(request):
    return render(request, 'upload_file.html')


@login_required
def upload_data(request):
    if request.method == "POST":
        myFile = request.FILES.get('myfile', None)
        if not myFile:
            return render(request, 'info.html', {'info': '没有选择文件，请重新选择！'})
        os.makedirs('./upload/' + date_folder(), exist_ok=True)
        destination = open('./upload/' + date_folder() + '/' + myFile.name, 'wb+')
        print(destination)
        for chunk in myFile.chunks():
            destination.write(chunk)
        destination.close()
        try:
            is_complete = write_db(request, myFile.name)
        except Exception:
            return render(request, 'info.html', {'info': '文件格式出错，请重新导入！'})
        if is_complete:
            return render(request, 'info.html', {'info': '写入成功！请返回首页!'})
        else:
            return render(request, 'info.html', {'info': '数据不完整!'})


def write_db(request, file_name):
    destination = open('./upload/' + date_folder() + '/' + file_name, 'r')
    recoder = destination.read()
    destination.close()
    summarys = recoder.split('Batch Summary')
    is_true = len(summarys)
    print(type(is_true))
    if len(summarys) == 1:
        return False
    if len(summarys) != 1:
        if len(summarys[-1]) >= 520:
            summarys = summarys[1:]
        else:
            summarys = summarys[1:-1]
        for summary_value in summarys:
            summary = summary_value[:550]
            transaction = int(summary[13:18].strip())
            side = int(summary[24:25])
            #
            # # 暂时没有mix在处理
            mix = summary[27:31]
            property = summary[27:34]
            mix_value = summary[31:35]
            #
            bay = summary[53].strip()

            bl_no = int(summary[81:86].strip())
            # # # customer 是否需要4位数
            customer_no = int(summary[124:128].strip())
            drive_no = summary[163:171].strip()
            batch = int(summary[176:183].strip())
            preset = int(summary[190:197].strip())
            gross = int(summary[204:211].strip())

            started = summary[231:248]
            started = datetime.datetime.strptime(started, '%d-%m-%y %H:%M:%S')
            stopped = summary[258:275]
            stopped = datetime.datetime.strptime(stopped, '%d-%m-%y %H:%M:%S')

            butane = int(summary[453:461].strip())
            propane = int(summary[511:518].strip())

            fill_time_str = stopped - started
            fill_time = int(str(fill_time_str)[2:4].strip())

            if mix == 'Mix':
                mix_value = 'MIX ' + mix_value
                mix_value = mix_value + '%'
            else:
                mix_value = 'Propane'
            if gross > 100:
                data = LPGRecord.objects.get_or_create(transaction_no=transaction, side=side,
                                                       proportion=mix_value,
                                                       bay=bay,
                                                       bl_no=bl_no,
                                                       customer_no=customer_no, drive_no=drive_no,
                                                       preset=preset,
                                                       gross=gross,
                                                       started=started, stopped=stopped, fill_time=fill_time,
                                                       butane=butane,
                                                       propane=propane)
        return True


def date_folder():
    return time.strftime("%Y%m%d", time.localtime())
