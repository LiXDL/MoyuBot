from enum import Enum


class DBStatusCode(Enum):
    INSERT_SUCCESS = 201
    DELETE_SUCCESS = 202
    UPDATE_SUCCESS = 203
    SEARCH_SUCCESS = 204

    INSERT_FAIL = 301
    DELETE_FAIL = 302
    UPDATE_FAIL = 303
    SEARCH_FAIL = 304

    UNKNOWN_ERROR = 404


class InteractionMessage:
    RECORD_CHANGE_SUCCESS = '已更新记录。'
    RECORD_FIND_SUCCESS = '找到记录：{}。'
    RECORD_LIST_EMPTY = '记录为空。'
    RECORD_LIST_SUCCESS = '记录如下：'

    RECORD_CHANGE_FAIL = '记录更新失败。'
    RECORD_FIND_FAIL = '未找到记录：{}。'
    RECORD_CHANGE_ABORT = '放弃更新记录。'

    PRIVATE_MESSAGE_SENT_CHECK = '已通过私聊发送。'

    ERROR_MESSAGE = '发生错误，请联系管理员。'
    INVALID_ARG = '非法参数！请重新输入！'
    INVALID_ARG_NUMBER = '参数数量错误！请重新输入！'
    REQUEST_ARG = '未检测到参数，请输入参数。'
    REQUEST_CONFIRM = '请确认操作[y/n]。'
    CONFIRMATION_MESSAGE = ['y', 'n', 'yes', 'no']

    MEMBER_MANAGER_HELP_MESSAGE = '''
    成员管理：
    0. 使用英文逗号","作为参数分隔符
    1. /添加成员 QQ号,昵称,游戏账号,密码（仅限超管使用）
    2. /移除成员 QQ号（仅限超管使用）
    3. /更新成员 QQ号,昵称,游戏账号,密码（仅限超管使用）
    4. /搜索成员 [QQ号/昵称]
    5. /成员列表
    '''
