import logging
import sys

from airtestProject.airtest.core.api import *
from airtestProject.factory.operateFactory import *
from airtestProject.commons.utils.logger import log




def open_ui_list(ui_list):
    for ui in ui_list:
        if operate().exists(ui):
            operate().click(ui)
def close_ui_list():
    pass
def open_with_click_each_ui():
    dict_ui={"材料":["養成材料"],"裝備":["王裝","珍品裝備"]}
    for key in dict_ui.keys():
        print("now key is "+key+"--------------")
        if operate(language=["ch_tra", "en"]).exists(key):
            log.info(f"key {key} is exists!!!!!!!!!!!!!!")
            operate().click(key)
            for ui in dict_ui[key]:
                print("now ui is "+ui+"--------------")
                if operate().exists(ui):
                    log.info(f"{ui} is exists!!!!!!!!!!!!!!!!!!!!!")
                    operate().click(ui)
                else:
                    log.info(f"{ui} is not  exists!!!!!!!!!!!!!!")
        else:
            log.info(f"key {key} is not  exists!!!!!!!!!!!!!!")




class actPage:

    def __init__(self, adb, script_root, Project="Ro", log_path=None):
        self.adb = adb
        if Project is not None:
            operate(language=["ch_tra", "en"]).set_dict(script_root, Project)
        if log_path is not None:
            self.log_path = log_path
        else:
            self.log_path = None

    def open_ui(self, ui, ui_view, fun_name="air"):

        @log.wrap(f'正在打开{ui}界面')
        def _open_ui():
            operate().click(ui)

            if operate().wait(ui_view):
                sleep(1)
                log.info(f"成功点击打开{ui}")
                return True
            else:
                log.info(f"打开{ui}失败")
                return False
        _open_ui()

    def close_ui(self, ui_view, close_pos, fun_name='air'):
        """

        :param ui_view: 当前界面
        :param close_pos: 关闭按钮
        :param fun_name: 选用poco或air
        :return:
        """

        @log.wrap(f'执行关闭ui界面{ui_view}')
        def _close_ui():
            if operate().wait_element_appear(close_pos):
                operate().click(close_pos)
                if operate().wait(ui_view):
                    log.info("关闭ui界面")
                else:
                    log.error(f"关闭{ui_view}失败")

        _close_ui()

    def open_with_click_each_ui(self,dict_ui):
        for key in dict_ui.keys():
            print("now key is " + key + "--------------")
            if operate(language=["ch_tra", "en"]).exists(key):
                log.info(f"key {key} is exists!!!!!!!!!!!!!!")
                operate().click(key)
                for ui in dict_ui[key]:
                    print("now ui is " + ui + "--------------")
                    if operate().exists(ui):
                        log.info(f"{ui} is exists!!!!!!!!!!!!!!!!!!!!!")
                        operate().click(ui)
                    else:
                        log.info(f"{ui} is not  exists!!!!!!!!!!!!!!")
            else:
                log.info(f"key {key} is not  exists!!!!!!!!!!!!!!")
    def open_ui_list(self,ui_list):

        for ui in ui_list:
            if operate().exists(ui):
                log.info(f"{ui} is exists!!!!!!!!!!!!!!!!!!!!!")
                operate().click(ui)
            else:
                log.info(f"{ui} is not  exists!!!!!!!!!!!!!!")

    def sales_view(self):

        self.open_ui("賣場","交易?")
        self.open_with_click_each_ui({"材料": ["養成材料"], "裝備": ["王裝", "珍品裝備","普通裝備"],"卡片":[],"其他":[]})
        self.close_ui("卖场", "back")

    def equips_view(self):
        if self.open_ui("裝備提升","插卡") is False:
            print("打开失败")
            sys.exit()
        self.open_ui_list(["强化","精煉","插卡","洗練","附魔","鍛造"])
        self.close_ui("装备入口","equip-back")

    def liupai_views(self):
        pass

    def skill_views(self):
        if self.open_ui("技能","設定") is False:
            print("打开失败")
            sys.exit()
        self.open_ui_list(["設定","隊列","技能"])
        self.close_ui("技能","skill-back")

    def huodong_views(self):
        self.open_ui("活動","活動")
        self.open_ui_list(["必做","选做","休闲","全部"])
        self.close_ui("活動","huodong-back")

    def bag_views(self):
        self.open_ui("背包","背包")
        self.open_ui_list(["裝備","卡片","附魔石","消耗品","倉庫"])
        self.close_ui("背包","bag-back")

if __name__ == '__main__':

    from airtestProject.airtest.core import api as air
    from airtestProject.manager.DeviceManager import DeviceManager
    DeviceManager().auto_setup(__file__)
    open_with_click_each_ui()
    adb = air.device().adb

