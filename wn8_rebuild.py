import os

import datetime
import aiofiles
import requests_async as requests
import ujson
from lxml import etree
from nonebot import CommandSession, on_command

__plugin_name__ = 'wn8'
__plugin_usage__ = r"""坦克世界亚服wn8查询/绑定
wn8 [昵称]
bind [昵称]"""


@on_command('bind', only_to_me=False)
async def bind(session: CommandSession):
    userQQ = str(session.ctx['user_id'])
    name = session.current_arg_text.strip()
    if not name:
        session.finish('bind [昵称]\ne.g. bind Iiquidator')
    h = htmlbody(name)
    ifvalid = await h.judge_valid()
    if ifvalid != None:
        session.finish(ifvalid)
    bind_result = await bind_user(userQQ, name)
    await session.send(bind_result)


@on_command('wn8', only_to_me=False)
async def wn8(session: CommandSession):
    userQQ = str(session.ctx['user_id'])
    name = session.current_arg_text.strip()
    if not name:
        name = await get_name_from_json(userQQ)
        if name == False:
            session.finish('wn8 [昵称]\ne.g. wn8 Iiquidator')
        h = htmlbody(name)
        await h.judge_valid()
    else:
        h = htmlbody(name)
        ifvalid = await h.judge_valid()
        if ifvalid != None:
            session.finish(ifvalid)
    wn8_report = await h.get_wn8()
    await session.send(wn8_report)


async def bind_user(userQQ: str, name: str):
    p = f'./wot/plugins/data/{userQQ}.json'
    content = await readJson(p)
    if content == False:
        userStructure = {
            'time': "1970-01-01",
            'length': 0,
            'wot_id': name
        }
        await writeJson(p, userStructure)
    else:
        content['wot_id'] = name
        await writeJson(p, content)
    return f'玩家:{name}\n绑定成功,直接输入wn8即可查询'


class htmlbody:
    name = ''
    url = ''
    html = ''

    def __init__(self, n):
        self.name = n
        self.url = f'https://wotlabs.net/sea/player/{n}'

    async def judge_valid(self):
        try:
            response = await requests.get(self.url)
        except:
            return '信号不良,请重试'
        wb_data = response.text
        self.html = etree.HTML(wb_data)
        try:
            self.html.xpath(
                '//*[@id="mainContainerFrontPage"]/div[3]/div[2]/@class')[0]
            return '玩家不存在'
        except IndexError:
            pass

    async def get_wn8(self):
        total_wn8 = self.html.xpath(
            '//*[@id="tankerStats"]/table/tbody/tr[14]/td[2]/text()')[0]
        total_wr = self.html.xpath(
            '//*[@id="tankerStats"]/table/tbody/tr[3]/td[3]/a/text()')[0]
        try:
            kb_wn8 = self.html.xpath(
                '//*[@id="tankerStats"]/table/tbody/tr[14]/td[7]/text()')[0]
            kb_wr = self.html.xpath(
                '//*[@id="tankerStats"]/table/tbody/tr[3]/td[13]/span/text()')[0]
        except IndexError:
            kb_wn8 = kb_wr = 'N/A'
        try:
            d_time_list = self.html.xpath(
                '//*[@id="tankerStats"]/div[7]/div[2]/text()')[0].split()[-11:-6]
            d_time_str = ''.join(d_time_list)
            d_time_format = datetime.datetime.strptime(d_time_str,'%B%d,%Y,%I:%M%p')
            d_time_formated = f'From {datetime.datetime.strftime(d_time_format,"%Y-%m-%d %H:%M")}:'
        except:
            d_time_formated = '24h内:'
        try:
            d_wn8 = self.html.xpath(
                '//*[@id="tankerStats"]/table/tbody/tr[14]/td[3]/text()')[0]
            d_win = self.html.xpath(
                '//*[@id="tankerStats"]/table/tbody/tr[3]/td[4]/text()')[0]
            d_lose = self.html.xpath(
                '//*[@id="tankerStats"]/table/tbody/tr[4]/td[4]/text()')[0]
            d_wr = self.html.xpath(
                '//*[@id="tankerStats"]/table/tbody/tr[3]/td[5]/span/text()')[0]
            d_tier = self.html.xpath(
                '//*[@id="tankerStats"]/table/tbody/tr[2]/td[3]/text()')[0]
            d_damage = self.html.xpath(
                '//*[@id="tankerStats"]/table/tbody/tr[10]/td[5]/span/text()')[0]
            d_sum = f'''{d_time_formated}
    WN8:{d_wn8}
    Wins/Losses:{d_win}/{d_lose}[{d_wr}]
    平均等级:{d_tier}
    场均伤害:{d_damage}'''
        except IndexError:
            d_sum = f'24h内暂无数据'
        result = f'''玩家昵称:{self.name}
总体WN8:{total_wn8}
总体胜率:{total_wr}
千场WN8:{kb_wn8}
千场胜率:{kb_wr}
{d_sum}
数据源自wotlabs
输入bind可绑定昵称'''
        return result


async def get_name_from_json(userQQ: str):
    p = f'./wot/plugins/data/{userQQ}.json'
    content = await readJson(p)
    if content == False or not content['wot_id']:
        return False
    name = content['wot_id']
    return name


async def readJson(p):
    if not os.path.exists(p):
        return False
    async with aiofiles.open(p, 'r', encoding='utf-8') as f:
        content = await f.read()
    content = ujson.loads(content)
    return content


async def writeJson(p, info):
    async with aiofiles.open(p, 'w', encoding='utf-8') as f:
        await f.write(ujson.dumps(info))
    return True
