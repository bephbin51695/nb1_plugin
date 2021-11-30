import os

import datetime
import aiofiles
import requests
import ujson
from lxml import etree
from nonebot import CommandSession, on_command
from nonebot.log import logger

__plugin_name__ = 'wn8'
__plugin_usage__ = r"""坦克世界亚服wn8查询/绑定
wn8 [昵称]
bind [昵称]"""


@on_command('bind', only_to_me=False)
async def bind(session: CommandSession):
    userQQ = str(session.ctx['user_id'])
    args = session.current_arg_text.strip().split()
    if len(args) > 1:
        region = args[0]
        name = " ".join(args[1:])
    elif len(args) == 1:
        name = args[0]
        region = "sea"
    else:
        name = ''
        region = "sea"
    if region not in {"sea", "ru", "cn"}:
        session.finish("服务器选择错误，可接受的参数为：sea、ru、cn")
    if not name:
        session.finish('bind [server] 昵称\nserver可选参数为cn、sea、ru\ne.g. bind ru Iiquidator')
    h = htmlbody(name, region)
    ifvalid = await h.judge_valid()
    if ifvalid:
        session.finish(ifvalid)
    bind_result = await bind_user(userQQ, name, region)
    await session.send(bind_result)


@on_command('wn8', only_to_me=False)
async def wn8(session: CommandSession):
    # session.finish('由于网络封锁，本功能暂时失效')
    userQQ = str(session.ctx['user_id'])
    args = session.current_arg_text.strip().split()
    if len(args) > 1:
        region = args[0]
        name = " ".join(args[1:])
    elif len(args) == 1:
        name = args[0]
        if name in {"sea", "ru", "cn"}:
            region = name
            name = ''
        else:
            region = "sea"
    else:
        name = ''
        region = "sea"
    if region not in {"sea", "ru", "cn"}:
        session.finish("服务器选择错误，可接受的参数为：sea、ru、cn")
    if not name:
        name = await get_name_from_json(userQQ, region)
        if not name:
            session.finish('wn8 [server] [昵称]\n默认服务器为亚服\ne.g. wn8 ru Iiquidator')
        h = htmlbody(name, region)
        await h.judge_valid()
    else:
        h = htmlbody(name, region)
        ifvalid = await h.judge_valid()
        if ifvalid:
            session.finish(ifvalid)
    if region == "cn":
        wn8_report = await h.get_zhanji()
    else:
        wn8_report = await h.get_wn8()
    await session.send(wn8_report)


async def bind_user(userQQ: str, name: str, region: str):
    p = f'./wot/plugins/data/{userQQ}.json'
    content = await readJson(p)
    if not content:
        userStructure = {
            'time': "1970-01-01",
            'length': 0,
            "wot_id": {
                "sea": "",
                "ru": "",
                "cn": ""
            }
        }
        userStructure['wot_id'][region] = name
        await writeJson(p, userStructure)
    else:
        content['wot_id'][region] = name
        await writeJson(p, content)
    return f'玩家:{name}\n绑定{region}成功,直接输入wn8 [对应服务器] 即可查询'


class htmlbody:
    name = ''
    url = ''
    html = ''
    region = ''

    def __init__(self, n, region):
        self.name = n
        self.region = region
        self.url = f'https://wotlabs.net/{region}/player/{n}'
        if region == "cn":
            self.url = f'https://wotbox.ouj.com/wotbox/index.php?r=default/index&pn={n}'

    async def judge_valid(self):
        try:
            # proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
            # response = requests.get(self.url, proxies=proxies)
            response = requests.get(self.url, timeout=15)
        except:
            return '信号不良,请重试'
        wb_data = response.text
        self.html = etree.HTML(wb_data)
        try:
            if self.region == "cn":
                self.html.xpath("/html/body/div[1]/div[3]/div/div[2]/div[1]/div[2]/div[1]/span[1]/text()")[0]
            else:
                self.html.xpath(
                    '//*[@id="tankerStats"]/table/tbody/tr[14]/td[2]/text()')[0]
        except IndexError:
            return '玩家不存在'

    async def get_wn8(self):
        try:
            total_wn8 = self.html.xpath(
                '//*[@id="tankerStats"]/table/tbody/tr[14]/td[2]/text()')[0]
            total_wr = self.html.xpath(
                '//*[@id="tankerStats"]/table/tbody/tr[3]/td[3]/a/text()')[0]
        except IndexError:
            return '玩家不存在'
        except AttributeError:
            logger.error("print html:")
            logger.error(self.html)
            return '信号不良,请重试\n//TODO'
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
            d_time_format = datetime.datetime.strptime(d_time_str, '%B%d,%Y,%I:%M%p')
            d_time_formated = f'From {datetime.datetime.strftime(d_time_format, "%Y-%m-%d %H:%M")}:'
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

    async def get_zhanji(self):
        try:
            atk = self.html.xpath("/html/body/div[1]/div[3]/div/div[2]/div[1]/div[2]/div[1]/span[1]/text()")[0]
            kb_wr = self.html.xpath(
                "/html/body/div[1]/div[3]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/p[2]/text()")[0]
            kb_tier = self.html.xpath(
                "/html/body/div[1]/div[3]/div/div[2]/div[2]/div[1]/div[2]/div[3]/div[2]/p[2]/text()")[0]
            kb_dmg = self.html.xpath("/html/body/div[1]/div[3]/div/div[2]/div[2]/div[1]/ul/li[1]/p[2]/text()")[0]
        except IndexError:
            atk = "7100"
            kb_wr = kb_tier = kb_dmg = "N/A"
        except AttributeError:
            logger.error("print html:")
            logger.error(self.html)
            return "请重试"
        result = f'''玩家昵称:{self.name}
战斗力:{atk}
千场胜率:{kb_wr}
千场均伤:{kb_dmg}
出战等级:{kb_tier}
数据来源偶游盒子
输入bind可绑定昵称'''
        return result


async def get_name_from_json(userQQ: str, region: str):
    p = f'./wot/plugins/data/{userQQ}.json'
    content = await readJson(p)
    if content == False or not content['wot_id'][region]:
        return False
    name = content['wot_id'][region]
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
