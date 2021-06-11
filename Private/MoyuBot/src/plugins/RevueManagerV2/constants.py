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

    RECORD_ALREADY_EXIST = 401
    RECORD_NOT_EXIST = 402

    UNKNOWN_ERROR = 500


class InteractionMessage:
    RECORD_CHANGE_SUCCESS = '已更新记录。'
    RECORD_FIND_SUCCESS = '找到记录：{}。'
    RECORD_LIST_EMPTY = '记录为空。'
    RECORD_LIST_SUCCESS = '记录如下：'
    RECORD_ALREADT_EXIST = '已存在对应记录，请勿重复添加。'

    RECORD_CHANGE_FAIL = '记录更新失败。'
    RECORD_FIND_FAIL = '未找到记录：{}。'
    RECORD_CHANGE_ABORT = '放弃更新记录。'

    PRIVATE_MESSAGE_SENT_CHECK = '已通过私聊发送。'

    ERROR_MESSAGE = '发生错误，请联系管理员。'
    INVALID_ARG = '非法参数！请重新输入！'
    INVALID_ARG_NUMBER = '参数数量错误！请重新输入！'
    REQUEST_ARG = '未检测到参数，请输入参数。'
    REQUEST_CONFIRM = '请确认操作[y/n]。'
    CONFIRMATION_MESSAGE = ['y', 'n', 'yes', 'no', 'Y', 'N', 'YES', 'NO']

    REPEATE_ADD_TEAM_CARD = '请输入卡牌名,卡牌us以添加单张卡牌\n' + \
                            '或[confirm]完成录入，[abort]放弃录入'
    REPEATE_ADD_MESSAGE = ['confirm', 'abort']
    NOT_ENOUGH_TEAM = '队伍中必须至少有一张卡牌，请重新添加。'

    OVERALL_HELPER = '''
    工会战管理插件：
    0. 使用"/"作为命令起始，英文逗号","作为参数分隔符
    1. /成员管理 用于查看成员管理部分命令
    2. /boss管理 用于查看Boss管理部分命令
    3. /记录管理 用于查看出刀记录管理部分命令
    4. /队伍管理 用于记录可用的刀型
    '''.strip()

    MEMBER_MANAGER_HELP_MESSAGE = '''
    成员管理：
    0. 使用英文逗号","作为参数分隔符，请遵循参数输入顺序
    1. /添加成员 QQ号,昵称,游戏账号,密码（仅限超管私聊使用）
    2. /移除成员 QQ号（仅限超管使用）
    3. /更新成员 QQ号,昵称,游戏账号,密码（仅限超管私聊使用）
    4. /搜索成员 QQ号|昵称
    5. /成员列表
    '''.strip()

    BOSS_MANAGER_HELP_MESSAGE = '''
    boss管理：
    0. 使用英文逗号","作为参数分隔符，请遵循参数输入顺序
    1. /添加boss|ab BossID,Boss名,血量（仅限管理使用）
    2. /添加boss组|abr Boss1名,Boss2名,Boss3名,Boss4名,
        Boss1血量,Boss2血量,Boss3血量,Boss4血量,
        起始难度(包括),终止难度(不包括)（仅限管理使用）
    3. /移除boss|rb BossID（仅限管理使用）
    4. /更新boss|ub BossID,Boss名,血量（仅限管理使用）
    5. /搜索boss|sb BossID|Boss名
    6. /boss列表|lb
    '''.strip()

    RECORD_MANAGER_HELP_MESSAGE = '''
    记录管理：
    0. 使用英文逗号","作为参数分隔符，请遵循参数输入顺序及格式
    1. /添加记录|ar 刀序(第几刀),BossID,队伍序号,伤害值,
        {回合数(留空默认为6)},
        {日期(YYYY-MM-DD留空默认为当天)},
        {QQ号(留空默认为发送者QQ号)}
        {或使用@功能自动获取QQ号，且@为最优先模式}
    2. /删除记录|rr QQ号,BossID,伤害值（仅限管理使用）
    3. /搜索记录|sr 用于查看搜索命令
    '''.strip()

    RECORD_SEARCH_HELP_MESSAGE = '''
    请使用指定对象的搜索命令：必须{可选}
    /search_record.member|搜索记录.成员|sr.m QQ号|昵称,{日期(YYYY-MM-DD)|-all}
    /search_record.boss|搜索记录.boss|sr.b BossID|Boss名,{日期(YYYY-MM-DD)|-all}
    '''.strip()

    TEAM_MANAGER_HELPER_MESSAGE = '''
    队伍管理：
    0. 使用英文逗号“,”作为参数分隔符，请遵循参数输入顺序及格式
    1. /添加队伍|at 个人队伍序号,{QQ号(留空默认为发送者QQ号)|或使用@功能自动获取QQ号，且@为最优先模式}
        将触发单卡添加模式，请遵循提示
    2. /删除队伍|rt QQ号,个人队伍序号（仅限管理使用）
    3. /查询队伍|st QQ号|昵称(或使用@功能自动获取QQ号，且@为最优先模式),{个人队伍序号}
    4. 队伍管理模块与卡牌数据库尚在开发，无法提供有效的联动查询，请自行确保队伍中卡牌可识别
    '''.strip()
