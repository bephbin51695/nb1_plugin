import time

import requests
import xlrd
import nonebot
from nonebot import CommandSession, on_command
from typing import Tuple

__plugin_name__ = 'jita'
__plugin_usage__ = r"""EVE国服市场姬
价格已包含皮尔米特星系
查询物品价格：
jita [物品名称]
查询即时矿物收购价：
mineral/矿价"""

bot = nonebot.get_bot()
dic = {}


@bot.server_app.before_serving
def init_dict():
    data = xlrd.open_workbook('./wot/plugins/typeID.xls')
    table = data.sheets()[0]
    c1 = table.col_values(0, 1)
    c2 = table.col_values(1, 1)
    global dic
    dic = dict(zip(c2, c1))


@on_command('mineral', aliases='矿价', only_to_me=False)
async def mineral(session: CommandSession):
    tup_n = ('三钛合金', '同位聚合体', '类银超金属', '类晶体胶矿', '莫尔石',
             '超噬矿', '超新星诺克石', '晶状石英核岩', '色动力学三羧基')
    tup_id = ('34', '37', '36', '35', '11399', '40', '38', '39', '48927')
    result = await market_json(tup_n, tup_id)
    await session.send(result)


@on_command('月矿', aliases='卫星矿', only_to_me=False)
async def mineral(session: CommandSession):
    tup_n = ('烃类', '标准大气', '蒸发岩沉积物', '硅酸盐', '钨', '钛', '钪',
             '钴', '铬', '钒', '镉', '铂', '汞', '铯', '铪', '锝', '镝',
             '钕', '钷', '铥')
    tup_id = ('16633', '16634', '16635', '16636', '16637', '16638',
              '16639', '16640', '16641', '16642', '16643', '16644',
              '16646', '16647', '16648', '16649', '16650', '16651',
              '16652', '16653')
    result = await market_json(tup_n, tup_id)
    await session.send(result)


@on_command('p1', only_to_me=False)
async def p1(session: CommandSession):
    tup_n = ('等离子体团', '电解物', '氧化剂', '细菌', '蛋白质', '生物燃料', '工业纤维',
             '反应金属', '稀有金属', '有毒金属', '手性结构', '水', '氧', '生物质', '硅')
    tup_id = ('2389', '2390', '2392', '2393', '2395', '2396', '2397',
              '2398', '2399', '2400', '2401', '3645', '3683', '3779', '9828')
    result = await market_json(tup_n, tup_id)
    await session.send(result)


@on_command('p2', only_to_me=False)
async def p2(session: CommandSession):
    tup_n = ('核能燃料', '超张力塑料', '氧化物', '培养基', '聚芳酰胺', '微纤维护盾',
             '水冷CPU', '生物电池', '纳米体', '机械元件', '合成油', '肥料',
             '合成纺织品', '硅酸盐玻璃', '家畜', '病原体', '建筑模块', '火箭燃料',
             '冷却剂', '消费级电器', '超导体', '传信器', '微型电子元件', '基因肉制品')
    tup_id = ('44', '2312', '2317', '2319', '2321', '2327', '2328', '2329',
              '2463', '3689', '3691', '3693', '3695', '3697', '3725', '3775',
              '3828', '9830', '9832', '9836', '9838', '9840', '9842', '15317')
    result = await market_json(tup_n, tup_id)
    await session.send(result)


@on_command('p3', only_to_me=False)
async def p3(session: CommandSession):
    tup_n = ('凝缩液', '监控无人机', '合成神经键', '凝胶基质生物胶', '超级计算机',
             '灵巧单元建筑模块', '核反应堆', '控制面板', '生物技术研究报告', '工业炸药',
             '密封薄膜', '危险物探测系统', '冷冻保存防腐剂', '制导系统', '大气内穿梭机',
             '机器人技术', '透颅微控器', '乌克米超导体', '数据芯片', '高科技传信器', '疫苗')
    tup_id = ('2344', '2345', '2346', '2348', '2349', '2351', '2352', '2354',
              '2358', '2360', '2361', '2366', '2367', '9834', '9846', '9848',
              '12836', '17136', '17392', '17898', '28974')
    result = await market_json(tup_n, tup_id)
    await session.send(result)


@on_command('p4', only_to_me=False)
async def p4(session: CommandSession):
    tup_n = ('广播节点', '反破损快速反应无人机', '纳米-工厂', '有机砂浆喷注器', '递推计算模块', '自协调能源核心', '无菌管道', '湿件主机')
    tup_id = ('2867', '2868', '2869', '2870', '2871', '2872', '2875', '2876')
    result = await market_json(tup_n, tup_id)
    await session.send(result)


@on_command('col', only_to_me=False)
async def col(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    name = stripped_arg
    if not stripped_arg:
        session.finish('.col [物品]')
    if name == '格鲁汀':
        name = '核心加强植入体'
    name_list = get_full_name(name)
    id_list = get_id_list(name_list)
    if len(id_list) != 6 and name != '核心加强植入体':
        await session.finish('参数非法')
    if not id_list:
        await session.finish('未搜索到物品\n缺少物品请私聊我')
    p_report = get_col(stripped_arg, id_list)
    await session.send(p_report)


@on_command('jita', only_to_me=False)
async def jita(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    name = stripped_arg
    if not stripped_arg:
        session.finish('.jita [物品]')
    name_list = get_full_name(name)
    id_list = get_id_list(name_list)
    if not id_list:
        await session.finish('未搜索到物品\n缺少物品请私聊我')
    p_report = get_price(id_list, name_list)
    await session.send(p_report)


async def market_json(tup_n: tuple, tup_id: tuple):
    result = '吉他/皮米最高收购价(ISK)：\n'
    for i in range(len(tup_n)):
        t_id = tup_id[i]
        url_jita = f'https://www.ceve-market.org/api/market/region/10000002/system/30000142/type/{t_id}.json'
        url_pimi = f'https://www.ceve-market.org/api/market/region/10000002/system/30000144/type/{t_id}.json'
        try:
            data_json_jita = requests.get(url_jita, timeout=5).json()
            data_json_pimi = requests.get(url_pimi, timeout=5).json()
        except requests.exceptions.ConnectTimeout:
            return "ceve-market连接超时\n请检查ceve-market国服市场中心是否能够正常访问\nhttps://www.ceve-market.org"
        time.sleep(0.05)
        buy_max = data_json_jita['buy']['max']
        if data_json_pimi['buy']['max'] > buy_max:
            buy_max = data_json_pimi['buy']['max']
        n = tup_n[i]
        s = f'{n:\u3000<10}{get_unit(buy_max)[0]}{get_unit(buy_max)[1]}\n'
        result += s
    return result


def get_full_name(name: str) -> list:
    col = dic.keys()
    name_list = [s for s in col if name in s]
    name_list.sort(key=lambda s: len(s))
    return name_list


def get_id_list(name_list: list) -> list:
    id_list = []
    for item in name_list:
        id_list.append(dic.get(item))
    return id_list


def get_col(arg: str, id_list: list) -> str:
    col_sell = 0
    col_buy = 0
    if arg == '格鲁汀':
        id_list = id_list[:4]
    for i in range(len(id_list)):
        res = get_digit(int(id_list[i]))
        if res == (-2, 0):
            return "ceve-market连接超时\n请检查ceve-market国服市场中心是否能够正常访问\nhttps://www.ceve-market.org"
        if res != (-1, 0):
            col_sell += res[0]
            col_buy += res[1]
            time.sleep(0.05)
    return f'''{arg}套装：
买: {get_unit(col_buy)[0]}{get_unit(col_buy)[1]} ISK
卖: {get_unit(col_sell)[0]}{get_unit(col_sell)[1]} ISK
数据源:当前吉他/皮米价格'''


def get_digit(t_id: int) -> Tuple[float, float]:
    url_jita = f'https://www.ceve-market.org/api/market/region/10000002/system/30000142/type/{t_id}.json'
    url_pimi = f'https://www.ceve-market.org/api/market/region/10000002/system/30000144/type/{t_id}.json'
    try:
        data_json_jita = requests.get(url_jita, timeout=5).json()
        data_json_pimi = requests.get(url_pimi, timeout=5).json()
    except requests.exceptions.ConnectTimeout:
        return -2, 0
    buy_max = data_json_jita['buy']['max']
    sell_min = data_json_jita['sell']['min']

    if data_json_pimi['buy']['max'] > buy_max:
        buy_max = data_json_pimi['buy']['max']
    if data_json_pimi['sell']['min'] < sell_min and data_json_pimi['sell']['min'] != 0 or sell_min == 0:
        sell_min = data_json_pimi['sell']['min']
    if buy_max == 0 and sell_min == 0:
        return -1, 0
    return sell_min, buy_max


def get_price(id_list: list, name_list: list) -> str:
    result = ''
    search_tag = 0
    for i in range(len(id_list)):
        search_tag += 1
        if search_tag > 4 or i > 5:
            break
        temp_data = get_data(int(id_list[i]), name_list[i])
        if temp_data == "-2":
            return "ceve-market连接超时\n请检查ceve-market国服市场中心是否能够正常访问\nhttps://www.ceve-market.org"
        if temp_data != "-1":
            result += temp_data
            time.sleep(0.05)
        else:
            search_tag -= 1
    if result == '':
        return '未搜索到有效物品\n缺少物品请私聊我\n注:无货物品已过滤'
    result_sum = f'{result}数据源:当前吉他/皮米价格'
    return result_sum


def get_data(t_id: int, t_name: str) -> str:
    url_jita = f'https://www.ceve-market.org/api/market/region/10000002/system/30000142/type/{t_id}.json'
    url_pimi = f'https://www.ceve-market.org/api/market/region/10000002/system/30000144/type/{t_id}.json'
    try:
        data_json_jita = requests.get(url_jita, timeout=5).json()
        data_json_pimi = requests.get(url_pimi, timeout=5).json()
    except requests.exceptions.ConnectTimeout:
        return "-2"
    buy_max = data_json_jita['buy']['max']
    sell_min = data_json_jita['sell']['min']

    if data_json_pimi['buy']['max'] > buy_max:
        buy_max = data_json_pimi['buy']['max']
    if data_json_pimi['sell']['min'] < sell_min and data_json_pimi['sell']['min'] != 0 or sell_min == 0:
        sell_min = data_json_pimi['sell']['min']
    if buy_max == 0 and sell_min == 0:
        return "-1"
    result = f'''{t_name}
买: {get_unit(buy_max)[0]}{get_unit(buy_max)[1]} ISK
卖: {get_unit(sell_min)[0]}{get_unit(sell_min)[1]} ISK\n'''
    if t_id == 44992:
        result += f'''伊甸币x500(月卡)
买: {get_unit(buy_max * 500)[0]}{get_unit(buy_max * 500)[1]} ISK
卖: {get_unit(sell_min * 500)[0]}{get_unit(sell_min * 500)[1]} ISK\n'''
    return result


def get_unit(price: float) -> Tuple[float, str]:
    unit = ''
    if 10000 <= price < 100000000:
        price /= 10000
        unit = '万'
    elif price >= 100000000:
        price /= 100000000
        unit = '亿'
    return price, unit
