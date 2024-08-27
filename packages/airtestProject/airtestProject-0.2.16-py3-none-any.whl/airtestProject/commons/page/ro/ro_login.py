
import string
from airtestProject.airtest.core.api import *
from airtestProject.commons.utils.logger import log
from airtestProject.factory.operateFactory import operate
import numpy as np
import  sys
ST.OPDELAY= 3.0


def r_user_name():
    # 生成一个包含所有文字的字符集
    chinese_chars = ''.join(chr(i) for i in range(0x4E00, 0x9FFF)) + \
                    ''.join(chr(i) for i in range(0x3400, 0x4DBF))

    # 添加英文字母到字符集
    all_chars = chinese_chars + string.ascii_letters
    # 使用random.choice随机选择字符，生成指定长度的字符串
    random_string = ''.join(np.random.choice(list(all_chars), 6))
    return random_string

def relative_position(x,y):
    screen_width=G.DEVICE.display_info['width']
    screen_height=G.DEVICE.display_info['height']
    return x*screen_width, y*screen_height

class RoLoginPage:
    def __init__(self,adb, script_root, project="Ro", log_path=None):
        self.adb = adb

        if project is not None:
            operate(language=[ "ch_tra", "en"]).set_dict(script_root, project)
        if log_path is not None:
            self.log_path = log_path
        else:
            self.log_path = None



    @log.wrap("检查是否进入登陆界面")
    def check_enter_login(self,pos):
        if operate().exists("closebtn"):
            operate().click("closebtn")
            if operate().wait_element_appear(pos):
                log.step('进入登录界面')
                return True
            else:
                log.test("未进入登录界面")
                return False

    @log.tag("开始登录操作")
    def ro_login_air(self,server_name=["测试服","95001"]):

        if operate().exists("尊敬的玩家"):# 如果有弹出公告的话，就关闭公告
            operate().click("closebtn")
        if self.check_enter_login("账号"):
            operate().click("changeserver")
            operate().wait("选择区服")
            operate().click(server_name[0])
            operate().click(server_name[1])
            # operate().click(self.relative_position(0.3,0.3 ))
            log.step("点击"+server_name[1])
        else:
            sys.exit(0)
        # if self.check_enter_login("点击画面"):
        operate().wait("账号")
        operate().click("点击画面")# 选择区服后重新回到登录界面，点击制定区域进入创角界面
        if operate().exists("选择角色"):
            log.tag("进入角色界面")
            snapshot()
        else:
            log.info("进入角色界面失败")
            sys.exit(0)

    @log.tag("开始创建角色")
    def create_role(self):
        if operate().exists("添加角色"):
            log.step("添加角色")
            operate().click("添加角色")
            if operate().wait("创建角色"):
                log.tag("进入创角界面")
                snapshot()
                operate().click("男")
                operate().set_text("请输入昵称",r_user_name())
                operate().click("开始冒险")

    def choose_role(self):
        if operate().exists("继续冒险"):
            operate().click("继续冒险")
            log.step("选择已有角色")
        else:
            self.create_role()
    # def del_roe(self):
    # def role(self):
    #     if operate().exists("")


if __name__ == '__main__':
    from airtestProject.manager.DeviceManager import DeviceManager
    DeviceManager().auto_setup()
    RoLoginPage().ro_login_air()