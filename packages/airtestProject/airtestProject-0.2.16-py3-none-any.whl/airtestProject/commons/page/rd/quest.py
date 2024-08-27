import math
import os
import time
from airtestProject.factory.operateFactory import operate
import threading
from airtestProject.commons.stateMachine.task import check_func, TaskCaseTemplate, put_task, stop_machine_f, \
    only_run_this, start_tag, TaskRunner
from airtestProject.airtest.core.helper import G
from airtestProject.commons.utils.logger import log
import numpy as np
from airtestProject.commons.utils.tools import run_with_timer

# snp_list = [(slice(884, 939), slice(412, 705))]

null_pos = [0.7, 0.45]  # 空位置
close_pos = [0.8, 0.16]  # 关闭位置
move_init_pos = [0.15, 0.75]  # 摇杆默认位置
move_forward_pos = [0.15, 0.65]  # 摇杆向前移动位置
move_backward_pos = [0.15, 0.85]  # 摇杆向后移动位置
move_left_pos = [0.05, 0.75]  # 摇杆向左移动位置
move_right_pos = [0.25, 0.75]  # 摇杆向右移动位置
attack_pos = [0.84, 0.82]  # 攻击键
skill_1_pos = [0.77, 0.9]   # 小技能
skill_2_pos = [0.77, 0.75]  # 大招
change_soul = [0.9, 0.55]   # 切换技


# 自动战斗

def auto_fight(quest_id, num):
    @check_func(f'正在进行剧情-{quest_id}-自动战斗')
    def _auto_fight():
        for i in range(num):
            operate().click(attack_pos)
            operate().click(attack_pos)
            operate().click(attack_pos)
            operate().click(attack_pos)
            operate().click(attack_pos)
            operate().click(skill_1_pos)
            operate().click(skill_2_pos)
            operate().click(change_soul)

    _auto_fight()

@check_func
def move_forward():
    operate().swipe((move_init_pos[0], move_init_pos[1]), (move_forward_pos[0], move_forward_pos[1]))


def do_quest(quest_id, interval, max_executions):
    @check_func(f'正在播放剧情-{quest_id}')
    def _do_quest():
        run_with_timer(quest_start, 2, 5, quest_end)

    def quest_start():
        if operate().exists("跳过"):
            operate().click("跳过")
        elif operate().exists("自动"):
            operate().click("自动")
        else:
            operate().click(move_init_pos)

    def quest_end():
        return operate().exists("MainSetting")

    _do_quest()


def run_quest(quest_id):
    @check_func(f'正在进行剧情-{quest_id}寻路')
    def _run_quest():
        operate().set_text("快捷", "&AutoRunQuest")
        operate().sleep(2.0)
        operate().click("发送")

    _run_quest()


class QuestPage(TaskCaseTemplate):
    def __init__(self, script_root, Project=None):
        super().__init__()
        if Project is not None:
            operate('air').set_dict(script_root, Project)

    @put_task()
    def quest_1(self):  # 主线第1个剧情TimeLine
        quest_id_1 = 10110101
        do_quest(quest_id_1,2,5)

    @put_task
    def quest_2(self):  # 主线第2个剧情寻路
        quest_id_2 = 10110103
        run_quest(quest_id_2)

    @put_task
    def quest_3(self):   # 主线第3个剧情TimeLine
        quest_id_3 = 10110105
        do_quest(quest_id_3, 2, 5)

    @put_task
    def quest_4(self):   # 主线第4个剧情战斗
        quest_id_4 = 10110106
        auto_fight(quest_id_4, 5)

    @put_task
    def quest_5(self):    # 主线第5个剧情战斗
        quest_id_5 = 101101061
        auto_fight(quest_id_5, 5)

    @put_task
    def quest_6(self):    # 主线第6个剧情战斗
        quest_id_6 = 101101062
        auto_fight(quest_id_6, 10)






    # def sure(self):
    #     operate().click("NotLock")
    #     if operate().exists("Lock"):
    #         auto_fight(10)
    #     elif operate().exists("NotLock"):
    #         move_forward()



