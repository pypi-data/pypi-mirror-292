"""
本项目基于pytest-html3.1.1
1. 关于中文乱码: 修改pytest-html的plugin源码，self.node_id去掉编解码
2. 关于钩子函数：除了以下外其它的直接调
pytest_runtest_makereport用法：
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    self = yield
    conf.pytest_runtest_makereport(item, self)
"""

import json
import shutil

import pyecharts
import re
import time
import os
import random
from py.xml import html
from PIL import ImageGrab, Image
from datetime import datetime, timedelta
from lxml import etree
from itertools import zip_longest
from functools import reduce


class _Utils:
    cur_time = property(lambda self: datetime.now().strftime('%Y%m%d%H%M%S%f'))

    @staticmethod
    def clear_by_mtime(dir_path, days=4, count=0):
        files_date = [(file, datetime.fromtimestamp(os.stat(os.path.join(dir_path, file)).st_mtime))
                      for file in os.listdir(dir_path)]
        sorted_file = [(os.path.join(dir_path, x[0]), x[1]) for x in
                       sorted(files_date, key=lambda x: x[1], reverse=True)]
        if count:
            sorted_file = sorted_file[count:]

        for i in sorted_file:
            file, date = i
            if date < datetime.today() - timedelta(days=days) or count:
                try:
                    os.remove(file)
                except PermissionError:
                    shutil.rmtree(file)

    def clear_by_count(self, dir_path, count=10):
        return self.clear_by_mtime(dir_path=dir_path, count=count)

    @staticmethod
    def clear_by_type(dir_path, end='.jpg'):
        for i in [os.path.join(dir_path, i) for i in os.listdir(dir_path)]:
            if i.endswith(end):
                os.remove(i)

    def preset(self, dir_path):
        """输出文件夹清理 + 报告备份"""
        for i in os.listdir(dir_path):
            i_path = os.path.join(dir_path, i)
            if 'report' == i:
                bake_report_path = os.path.join(dir_path, 'report' + self.cur_time[4:-6])
                shutil.copytree(i_path, bake_report_path)
                # shutil.rmtree(i_path)  # 有时是grid并行在跑，一个跑完了一个没跑完，把它删了会影响另一个的报告。优化为不删仅复制，删除超过一天的截图
                screenshot_path = os.path.join(i_path, 'screenshots')
                if os.path.exists(screenshot_path):
                    self.clear_by_mtime(screenshot_path, days=1)
                break
        self.clear_by_count(dir_path)  # 根据数量清理


class Conftest:
    def __init__(self, base_path: str, view=pyecharts, driver=...,
                 replace_js='', index_url='please input url here.', user='None', pwd='None', browser='chrome'):
        """
        :param base_path: 当前工程路径
        :param view: pyecharts对象或pyplot对象，import pyechars或者import matplotlib.pyplot as plt，传入
        """
        base_path = os.path.abspath(base_path)
        self.output_dir = os.path.join(base_path, "output")
        self.report_path = os.path.join(self.output_dir, "report")
        self.html_report_path = os.path.join(self.report_path, "report.html")
        self.e1_html_path = os.path.join(self.report_path, "assets", "e1.html")
        self.e2_html_path = os.path.join(self.report_path, "assets", "e2.html")
        self.pfs_json = os.path.join(self.report_path, "assets", "pfs.json")
        self.replace_js_bake = os.path.join(self.report_path, "assets", "e.js")
        self.summary_pic_path = os.path.join(self.report_path, "summary.jpg")
        self.summary_module_pic_path = os.path.join(self.report_path, "summary2.jpg")
        self.log_dir = os.path.join(self.output_dir, "logs")
        self.driver = driver
        self.index_url = index_url
        self.user = user
        self.pwd = pwd
        self.view = view
        self.screenshot_dir = os.path.join(self.report_path, "screenshots")
        self.replace_js = replace_js  # echarts需要联网，为True可以避免内网环境时加载不了js
        self.browser = browser
        self.module_num = 0
        for _ in [self.report_path, self.screenshot_dir, self.log_dir]:
            if not os.path.exists(_):
                os.makedirs(_)

        _Utils.clear_by_type(self.report_path)

    mds = []
    summary2 = False
    __color__ = ['6cb1e1', 'ffb06a', '74d974', 'cb91ff', 'ff8ddc', 'ff8a8a', 'feff00', '17becf',
                 '32cd99', '7093db', '8af38a', 'd4ed31']
    __pfs_color__ = ['#74d974', '#fd5a3e', '#ffd050']
    cl = random.choice(__color__)

    def pytest_runtest_makereport(self, item, _self_):
        pytest_html = item.config.pluginmanager.getplugin("html")
        report = _self_.get_result()
        extra = getattr(report, 'extra', [])
        if report.when == 'call' or report.when == 'setup':
            xfail = hasattr(report, 'wasxfail')
            if (report.skipped and xfail) or (report.failed and not xfail):
                file_name = report.nodeid.replace("::", "_") + ".png"
                if file_name:
                    screen_img = self._screenshot_()
                    html_ = (
                            '<div><img src="%s" alt="screenshot" style="width:465px;height:245px;" '
                            'onclick="window.open(this.src)" align="right"/></div>' % screen_img
                    )
                    extra.append(pytest_html.extras.html(html_))
        doc = str(item.function.__doc__)
        if len(doc) > 180:
            doc = doc[:177] + '...'
        report.description = doc
        report.extra = extra

    def pytest_html_results_table_row(self, report, cells):
        try:
            cells.insert(2, html.td(report.description))
        except AttributeError:
            ...
        cells.insert(3, html.td(self.c_time(report.start), class_='col-time'))
        cells.pop()
        for i in range(len(cells)):
            cells[i].attr.__setattr__('style', 'border:0.2px solid #%s' % self.cl)

    def c_time(self, star):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(star))

    def pytest_html_results_table_header(self, cells):
        cells[0].attr.width = '10%'
        cells[1].attr.width = '30%'
        cells.insert(2, html.th("Description", width='35%'))
        cells.insert(3, html.th("Time", class_="sortable time", col="time", width='13%'))
        cells[4].attr.width = '12%'
        cells.pop()
        for i in range(len(cells)):
            cells[i].attr.__setattr__('style', 'border:3px solid #%s' % self._color_())

    @staticmethod
    def pytest_html_report_title(report):
        report.title = 'Test Report'

    def pytest_html_results_summary(self, prefix):
        if 'pyplot' in str(self.view):
            prefix.extend([html.div(html.img(
                src=r'./summary.jpg', alt='', style="width:280px;height:250px;margin:-220px 0px 0px 43%"),
            )])
            prefix.extend([html.div(html.img(
                src=r'./summary2.jpg', alt='', style="width:280px;height:250px;margin:-220px 0px 0px 73%"),
            )])

    def pytest_sessionfinish(self):
        _Utils.clear_by_mtime(self.screenshot_dir)
        _Utils.clear_by_mtime(self.log_dir)
        self._sub_html_()

        self._get_pfs_data_()
        with open(self.pfs_json, "r", encoding="utf-8") as ff:
            data = json.loads(ff.read())

        if self.replace_js:
            shutil.copy(self.replace_js, self.replace_js_bake)
        if 'pyplot' in str(self.view):
            self._draw_by_matplotlib_(data)
            self._draw_by_matplotlib2_(data)
        elif 'pyecharts' in str(self.view):
            self._draw_by_echarts_(data)
            self._draw_by_echarts2_(data)
            self._replace_js_()
        else:
            raise TypeError("传入 pyecharts 对象或者 matplotlib-pyplot 对象")
        _Utils().preset(self.output_dir)  # 报告备份，grid并行运行必须在结束时备份，开始时备份不行

    @staticmethod
    def _get_view1_data(data):
        p = f = s = 0
        for k, v in data.items():
            v1, v2, v3 = v
            p = p + v1
            f = f + v2
            s = s + v3
        x = [p, f]
        label = ['成功', '失败']
        if s:
            x.append(s)
            label.append('跳过')
        return p, f, s, x, label

    def _get_pfs_data_(self):
        with open(self.html_report_path, 'r', encoding='utf-8') as f:
            con = f.read()
        con = etree.HTML(con)
        pfs_xpath = '//tbody[contains(@class,"%s")]//td[@class="col-name"]'
        p = con.xpath(pfs_xpath % 'passed')
        f = con.xpath(pfs_xpath % 'failed')
        s = con.xpath(pfs_xpath % 'skipped')

        def _cal_(pfs):
            _md = dict()
            if not pfs:
                return _md
            for _ in pfs:
                e = _.text.rindex('/')
                try:
                    md = _.text[_.text.rindex('/', 0, e) + 1:e]
                except ValueError:
                    md = _.text[e + 1:_.text.rindex('.')]
                if _md.get(md):
                    _md[md] += 1
                else:
                    _md[md] = 1
            return _md

        pmd = _cal_(p)
        fmd = _cal_(f)
        smd = _cal_(s)
        self.module_num = max(len(pmd), len(fmd))
        rates = dict()  # 各模块的pfs
        for p, f, s in zip_longest(pmd, fmd, smd):
            key = p or f or s
            pp = pmd.get(key, 0)
            ff = fmd.get(key, 0)
            ss = smd.get(key, 0)
            try:
                rates[key] = (pp, ff, ss)
            except ZeroDivisionError:
                rates[p] = 100

        with open(self.pfs_json, "w", encoding="utf-8") as f:
            f.write(json.dumps(rates))

    def pytest_collection_modifyitems(self, items):
        for item in items:
            nid = item._nodeid
            if not nid.count('/') >= 2:
                return
            i2 = nid.rindex('/')
            i1 = nid.rindex('/', 0, i2) + 1
            md = nid[i1:i2]
            self.mds.append(md)
        self.mds = list(set(self.mds))

    def _color_(self):
        _ = random.choice(self.__color__)
        if len(self.__color__) > 1:
            self.__color__.remove(_)
        return _

    def _sub_html_(self):
        with open(self.html_report_path, 'r', encoding='utf-8') as f:
            con = f.read()
        res = re.sub('<p>Report generated.*</p>', '', con)
        re_waste = r'<p>\d+ tests ran in*.*</p>'
        waste = re.findall(re_waste, res)
        if not waste:
            re_waste = r'</span>\d+ tests ran in*.*</div>'
            waste = re.findall(re_waste, res)
        waste = waste[0][3:-4]
        res = re.sub(re_waste, '', res)
        res = re.sub(r'<p>*.*\(Un\)check the boxes .+\.</p>', '', res)
        res = re.sub(r'<input checked="true"',
                     '<span style="height:40px; color:black; font-weight:bold; font-size:120%">Filter : </span>'
                     '<input checked="true"',
                     res, count=1)
        res = re.sub(r'0 errors</span>*.*unexpected passes</span>', '0 errors</span>', res)
        res = re.sub(r'<h2>Results</h2>', '', res)
        link = f'<div style="height:30px; color:green; padding:15px 0px 0px 0px">' \
               f'<span style="color:black;font-weight:bold; font-size:120%">Test Url : </span>' \
               f'<a href={self.index_url} style="color:green">{self.index_url}</a></div>' \
               f'<div style="height:30px; color:green">' \
               f'<span style="color:black;font-weight:bold; font-size:120%">Test By : </span>' \
               f'name: {self.user} &nbsp &nbsp | &nbsp &nbsp password: {self.pwd} </div>' \
               f'<div style="height:30px; color:green">' \
               f'<span style="color:black;font-weight:bold; font-size:120%">Test Browser : </span>{self.browser}</div>' \
               f'<div style="height:30px; color:green">' \
               f'<span style="color:black;font-weight:bold; font-size:120%">Test Consuming : </span>{waste}</div>'
        res = re.sub('<h2>Summary</h2>', link, res)
        with open(self.html_report_path, 'w', encoding='utf-8') as f:
            f.write(res)

    def _replace_js_(self):
        if self.replace_js:
            js_name = self.replace_js.rsplit(os.sep)[-1]
            for i in (self.e1_html_path, self.e2_html_path):
                with open(i, 'r', encoding='utf-8') as f:
                    con = f.read()
                res = re.sub('https://assets.pyecharts.org/assets/v5/echarts.min.js', js_name, con)
                with open(i, 'w', encoding='utf-8') as f:
                    f.write(res)

        with open(self.html_report_path, 'r', encoding='utf-8') as f:
            con = f.read()
        res = re.sub('seconds. </div>',
                     'seconds. </div>'
                     '<iframe style="width:30%;height:300px;margin:-215px 0px 0px 30.5%" width="100%" height="100%" '
                     'frameborder="no" border="0" src="assets/e1.html"></iframe>'
                     f'<iframe style="width:33%;height:{300+self.module_num*10}px;margin:-290px 0px 0px 59.5%" width="100%" height="100%" '
                     'frameborder="no" border="0" src="assets/e2.html"></iframe>'  # 33% 兼容了小屏
                     '<div style="margin:-80px 0px 0px 0px"></div>',  # 上下部分缝合
                     con)
        with open(self.html_report_path, 'w', encoding='utf-8') as f:
            f.write(res)

    def _draw_by_matplotlib_(self, data):
        plt = self.view
        p, f, s, x, label = self._get_view1_data(data)
        if s:
            x.append(s)
        label = [i + f":{j}" for i, j in zip(label, x)]
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.figure(figsize=(3.3, 3.3))
        plt.pie(
            x=x,
            labels=label,
            pctdistance=1.2,
            textprops={'fontsize': 10},
            colors=self.__pfs_color__,
            wedgeprops={'width': 0.35},
        )
        plt.text(-0.36, -0.05, f'{round(p / (p + f + s) * 100, 2)}%', fontsize=20)
        plt.tight_layout()
        plt.savefig(self.summary_pic_path, dpi=250)

        img = Image.open(self.summary_pic_path)
        c_img = img.crop((0, 0, img.width, img.height - 100))
        c_img.save(self.summary_pic_path)

    def _draw_by_echarts_(self, data):
        p, f, s, x, label = self._get_view1_data(data)
        try:
            rate = round(p / (p + f + s) * 100, 2)
        except ZeroDivisionError:
            rate = 0
        c = (
            self.view.charts.Pie(init_opts=self.view.options.InitOpts(width="380px", height="280px"))
            .add(
                "",
                [list(z) for z in zip(label, x)],
                radius=["35%", "55%"], center=["45%", "55%"],
            )
            .set_global_opts(
                title_opts=self.view.options.TitleOpts(title=f"{rate} %", pos_right="45%", pos_top="48%"),
                legend_opts=self.view.options.LegendOpts(is_show=False)
            )
            .set_series_opts(label_opts=self.view.options.LabelOpts(formatter="{b}: {c}"))
            .set_colors(self.__pfs_color__)
        )
        c.page_title = '成功率'
        c.render(path=self.e1_html_path)

    def _draw_by_echarts2_(self, data):
        """
        :param data: {"Demo": (8, 1), "结构化": (9, 3), "零部件": (12, 0)}
        """

        def radius(color_index: int, border_radius: list):
            return {
                "normal": {
                    "color": self.view.commons.utils.JsCode(
                        """new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'%s'},{offset:1,color:'%s'}],false)""" % (
                            self.__pfs_color__[color_index], self.__pfs_color__[color_index])
                    ),
                    "barBorderRadius": border_radius,
                }
            }

        x, y1, y2, y3 = [], [], [], []
        for k, v in data.items():
            x.append(k)
            v1, v2, v3 = v
            if not v1:
                v1 = ""
            if not v2:
                v2 = ""
            if not v3:
                v3 = ""
            y1.append(v1)  # 所有的成功
            y2.append(v2)  # 所有的失败
            y3.append(v3)  # 所有的跳过

        # 后面的height高度值配置iframe的高度调整，7个模块没问题，再往上会不好看
        bar = self.view.charts.Bar(init_opts=self.view.options.InitOpts(width="500px", height=f"{195 + len(x) * 22}px"))
        bar.add_xaxis(x)

        bar.add_yaxis(series_name='成功', y_axis=y1, stack="stack1", color=self.__pfs_color__[0], category_gap="33%",
                      itemstyle_opts=radius(0, [6, 3, 3, 6]), label_opts={"show": True, "color": "black"})
        bar.add_yaxis(series_name='跳过', y_axis=y3, stack="stack1", color=self.__pfs_color__[2], category_gap="33%",
                      itemstyle_opts=radius(2, [0, 0, 0, 0]), label_opts={"show": True, "color": "black"})
        bar.add_yaxis(series_name='失败', y_axis=y2, stack="stack1", color=self.__pfs_color__[1], category_gap="33%",
                      itemstyle_opts=radius(1, [3, 6, 6, 3]), label_opts={"show": True, "color": "black"})

        try:
            max_ = sum(data.values())
        except TypeError:  # 多模块运行情况
            max_ = []
            for i in list(data.values()):
                max_.append(sum(i))
            max_ = max(max_)

        bar.set_global_opts(
            # min/max 控制长短，inverse：左右对调，调试时把show打开。min最多为-2，最少为-0.2；max为总数
            xaxis_opts={"show": False, "inverse": False, "min": -0.2 - max_ / 5, "max": max_},
            yaxis_opts={"show": True, "splitLine": {"show": False}, "axisLine": {"show": False}, "axisTick": {
                "show": False}, "offset": -50},  # offset 控制偏移多少
            legend_opts={"show": False},
        )
        bar.set_series_opts()
        bar.reversal_axis()
        bar.page_title = "模块图"
        bar.render(self.e2_html_path)

    def _screenshot_(self):
        file_name = _Utils().cur_time + '.png'
        file_path = os.path.join(self.screenshot_dir, file_name)
        shot = False
        if self.driver is not ...:
            try:
                self.driver().save_screenshot(file_path)
                shot = True
            except Exception:
                ...
        if not shot:
            ImageGrab.grab(bbox=(0, 80, 1920, 1070)).save(file_path)
        file_path = './screenshots/' + file_name
        return file_path

    def _draw_by_matplotlib2_(self, data):
        plt = self.view
        x = list(data.keys())
        y1, y2 = [], []
        for i in data.values():
            v1, v2, v3 = i
            y1.append(v1 + v3)
            y2.append(v2)

        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.figure(figsize=(5, 3 + len(x) / 2))
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.yticks([])

        plt.bar(x, y1, width=len(x) / 6, color=self.__pfs_color__[0])
        plt.bar(x, y2, width=len(x) / 6, color=self.__pfs_color__[1])
        plt.xticks(x, fontsize=15)

        for a, b, c in zip(x, y1, y2):
            plt.text(a, (b + c) / 2 - 0.5, b, ha="center", fontsize=20)
            plt.text(a, c / 2 - 0.2, c, ha="center", fontsize=15)

        plt.savefig(self.summary_module_pic_path, dpi=250)
