# Owner: <achen>
# !/usr/bin/python3
# 2020/3/6 2:19 PM
# chat_process_base

from config import SENTRY
from appium_robot.robot.tools.function_tools import *
from collections import Iterable

"""
需求：控制对话流程，能够自由的配置对话逻辑和流程。

架构思想：
对话流程可以认为由一系列的动作（推二维码、发文字、检测对方回复、拉群等）构成，同时一个对话流程的动作不是固定的，可以根据条件触发相应的动作.
关键在于两点：
1. 动作库actions：它是一个字典，字典的key即为动作的id. 
2. 如何根据条件触发动作？本架构采用动作决策者的类DecisionMaker来实现这个：
    1) 创建DecisionMaker对象，创建时传入参数conditions_dict(动作条件字典，决策的内在逻辑，即根据不同条件触发相应的动作，其key即为动作id）
    2) DecisionMaker对象的主方法会返回动作的id, 传入ActionExecutor对象
    3) ActionExecutor对象通过id从动作库中取到这个动作对象。再调用这个动作的主方法触发动作
动作再往上抽象：每一个动作是一种行为，决策也是一种行为。每个行为有其主方法（即下文Base抽象类的run方法）
每个行为都会有返回值param，作为下一个行为的参数，如此，一个完整的对话流程就是一系列有序的行为的流程，
配置对话流程即配置行为列表(process_steps)的过程, 配置过程具体参考最后的测试函数test
"""


def send_message_action(content):
    if content:
        print('send message: %s     ok!' % content)
        return True
    else:
        return False


def receive_message_action():
    message = input('请输入信息:')
    return message


def re_search_condition(text, pattern) -> bool:
    if re.search(pattern, text):
        return True
    else:
        return False


def re_exclude_condition(text, pattern) -> bool:
    if re.search(pattern, text):
        return False
    else:
        return True


"""
注：上面4个函数为测试用，作为执行某个动作对象的主方法condition_callable所调用的函数，特别注意的是目前采用如下写法：
    self.condition_callable(*args, *self.args, **kwargs), 一定要注意参数顺序，否则容易出错。
"""


class Base(object):
    def run(self, *args, **kwargs):
        raise NotImplementedError


class ActionBase(Base):
    def __init__(self, action_callable, *args, **kwargs):
        self.action_callable = action_callable
        self.args = args
        self.kwargs = kwargs

    def perform(self):
        return self.action_callable(*self.args, **self.kwargs)

    def run(self, *args, **kwargs):
        return self.perform()


class ConditionBase(object):
    def __init__(self, condition_callable, *args, **kwargs):
        self.condition_callable = condition_callable
        self.args = args
        self.kwargs = kwargs

    def is_condition_met(self, *args, **kwargs) -> bool:
        kwargs.update(self.kwargs)
        return self.condition_callable(*args, *self.args, **kwargs)


class DecisionMaker(Base):
    def __init__(self, conditions_dict: dict):
        self.conditions_dict = conditions_dict

    def action_maker(self, *ags, **kw):
        for action_id in self.conditions_dict:
            for condition in self.conditions_dict[action_id]:
                try:
                    # import ipdb
                    # ipdb.set_trace()
                    if condition.is_condition_met(*ags, **kw):
                        return action_id
                except Exception as e:
                    print('is_condition_met方法发生错误：%s' % e.__repr__())

    def run(self, *args, **kwargs):
        return self.action_maker(*args, **kwargs)


class ActionExecutor(Base):
    def __init__(self, actions_dict: dict):
        self.actions_dict = actions_dict

    def execute(self, action_id):
        if action_id and action_id in self.actions_dict:
            return self.actions_dict[action_id].perform()

    def run(self, *args, **kwargs):
        return self.execute(*args, **kwargs)


class AutoResponse(Base):
    def __init__(self, decision_maker, action_executor):
        self.decision_maker = decision_maker
        self.action_executor = action_executor

    def run(self, *args, **kwargs):
        # import ipdb
        # ipdb.set_trace()
        action_id = self.decision_maker.run(*args, **kwargs)
        return self.action_executor.run(action_id)


class ChatProcessEngine(object):
    def __init__(self, process_steps, initial_param: dict=None):
        self.process_steps = process_steps
        self.initial_param = initial_param or dict()

    def start(self):
        param = self.initial_param
        if self.size > 0:
            for node_step in self.process_steps:
                if 'get' in dir(param):
                    param = node_step.run(**param)
                elif not isinstance(param, str) and isinstance(param, Iterable):
                    param = node_step.run(*param)
                elif param is not None:
                    param = node_step.run(param)
                else:
                    param = node_step.run()
            return param
        else:
            print('步骤未配置')

    @property
    def size(self):
        return len(self.process_steps)


def test():
    actions = {
        '1': ActionBase(action_callable=send_message_action, content='hello world'),
        '2': ActionBase(action_callable=receive_message_action)
    }

    conditions = {
        '1': [ConditionBase(condition_callable=re_search_condition, pattern='不用|不要|不必|不了吧|不需要')],
        '2': [ConditionBase(condition_callable=re_exclude_condition, pattern='不用|不要|不必|不了吧|不需要'), ]
    }
    conditions_2 = {
        '1': [ConditionBase(condition_callable=bool)]
    }
    decision_maker = DecisionMaker(conditions)
    decision_maker_2 = DecisionMaker(conditions_2)
    action_executor = ActionExecutor(actions)
    auto_response = AutoResponse(decision_maker, action_executor)
    auto_response_2 = AutoResponse(decision_maker_2, action_executor)
    process_steps = [actions['1'], actions['2'], auto_response, actions['2'], auto_response_2]
    chat_engine_0 = ChatProcessEngine(process_steps=process_steps)
    # 下面字典的key表示机器人的id, 可以为每个聊天机器人配置不同的流程
    chat_robot_engine_dict = {
        '0': chat_engine_0
    }
    chat_robot_engine_dict['0'].start()


if __name__ == '__main__':
    """
    python3 -m appium_robot.robot.wechat.intelligent_chat.chat_process_base
    """
    show_module(form='*')
    test()
