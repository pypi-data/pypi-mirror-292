import os
import time
from collections import deque

from airtestProject.airtest.core import api as air
from airtestProject.airtest.core.android.recorder import Recorder
from airtestProject.airtest.report.report import LogToHtml
from airtestProject.airtest.core.android.adb import ADB
from airtestProject.airtest.core import api as air
from airtestProject.manager.DeviceManager import DeviceManager, uwa_auto_setup
from airtestProject.commons.utils.logger import log
from airtestProject.factory.operateFactory import operate
import random
from airtestProject.commons.stateMachine.task import check_func, TaskCaseTemplate, put_task, stop_machine_f, \
    only_run_this, start_tag, TaskRunner

# screen = G.DEVICE.snapshot()
# w, h= device().get_current_resolution() #获取手机分辨率
input_pos = [0.5, 0.66]
select_server_pos = [0.5, 0.72]
start_game_pos = [0.5, 0.78]
role_man_pos = [0.69, 0.3]
role_men_pos = [0.3, 0.3]
enter_game_pos = [0.8, 0.8]



class LoginPage(TaskCaseTemplate):
    def __init__(self, script_root, Project=None):
        super().__init__()
        if Project is not None:
            operate('air').set_dict(script_root, Project)

    @put_task
    def check_enter_login_view(self):
        if operate().wait_element_appear("StartGameBtn"):
            log.step("进入登录界面成功")
            return True
        else:
            log.step("进入登录界面失败")
            return False

    @start_tag()
    def input_account(self):
        user = ''.join(str(random.randint(1, 9)) for _ in range(6))
        operate().set_text(input_pos, user)
        log.step(f'输入账号-{user}')

    @put_task()
    def click_server(self):
        operate().click(select_server_pos)

    @put_task(run_again_num=3)
    def select_server(self):
        operate().swipe((0.12, 0.5))  # 在0.1s内上划0.5个屏幕
        operate().sleep(1.0)
        operate().click("外网服务器")
        operate().sleep(1.0)
        operate().click("技术中心测试服")

    @put_task
    def click_start_game(self):
        operate().click(start_game_pos)

    @put_task
    def click_role(self):
        operate().wait_for_any(["RoleMan", "RoleMen"])
        operate().click(role_man_pos)

    @stop_machine_f
    def click_enter_game(self):
        # operate().wait_next_element(enter_game_pos, "ContinueBtn")
        while True:
            if not operate().exists("ContinueBtn"):
                break
            else:
                operate().click("ContinueBtn")
        operate().sleep(10.0)


