from nonebot import on_command, CommandSession
from random import randint
import os
import datetime
import aiofiles
import ujson
from dateutil.parser import parse

__plugin_name__ = '今日长度'
__plugin_usage__ = r'''查询今日DD长度（仅供娱乐 切勿当真）
查询本人：
今日长度
查询指定用户:
今日长度 [@qq]'''

FAILURE = 'failure'
SUCCESS = 'success'


@on_command('今日长度', only_to_me=False)
async def todaylen(session: CommandSession):
    userQQ = str(session.ctx['user_id'])
    try:
        userQQ = str(session.ctx['message'][1]['data']['qq'])
    except IndexError:
        pass
    at = f'[CQ:at,qq={userQQ}]'
    todaylength = await getlength(userQQ)
    if userQQ == 'all':
        sendMsg = f'全体成员今日的平均丁丁长度是{abs(todaylength)}cm'
    elif todaylength < 0:
        sendMsg = f'{at}今日的牛牛长度是....今天你是女孩子'
    else:
        sendMsg = f'{at}今日的牛牛长度是{todaylength}cm'
    await session.send(sendMsg)


async def getlength(userQQ):
    neg_seed = randint(1, 10)
    length = randint(0, 30)
    if neg_seed == 1: length = -length
    p = f'./wot/plugins/data/{userQQ}.json'
    content = await readJson(p)
    if content == FAILURE:
        userStructure = {
            'time': await getCurrentTime(),
            'length': length,
            "wot_id": {
                "sea": "",
                "ru": "",
                "cn": ""
            }
        }
        await writeJson(p, userStructure)
        return length
    interval = await getTimeDiff(content['time'])
    if interval >= 1:
        content['time'] = await getCurrentTime()
        content['length'] = length
        await writeJson(p, content)
        return length
    length = content['length']
    return length


async def readJson(p):
    if not os.path.exists(p):
        return FAILURE
    async with aiofiles.open(p, 'r', encoding='utf-8') as f:
        content = await f.read()
    content = ujson.loads(content)
    return content


async def writeJson(p, info):
    async with aiofiles.open(p, 'w', encoding='utf-8') as f:
        await f.write(ujson.dumps(info))
    return SUCCESS


async def getCurrentTime():
    nowDate = str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d'))
    return nowDate


async def getTimeDiff(origin):
    a = parse(origin)
    b = parse(await getCurrentTime())
    return int((b - a).days)
