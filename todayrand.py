from nonebot import on_command, CommandSession
from random import randint
import os
import datetime
import aiofiles
import ujson
from dateutil.parser import parse
from nonebot.log import logger

__plugin_name__ = '今日长度'
__plugin_usage__ = r'''查询今日DD长度（仅供娱乐 切勿当真）
查询本人：
今日长度
查询指定用户:
今日长度 [@qq]
例:今日长度 @nanoha'''

FAILURE = 'failure'
SUCCESS = 'success'


@on_command('今日长度', only_to_me=False)
async def todaylen(session: CommandSession):
    userQQ = str(session.ctx['user_id'])
    extra_words = ['，小姐姐的派派可以让我摸摸吗\n(๑‾ ꇴ ‾๑)', '，什么嘛，原来是可爱的小豆丁呀\n(*°ｰ°)v', '，可以让我一口吃掉吗\n罒ω罒',
              '，也许我们今晚能做很多很多事情呢\n(〃∇〃)', '，单是看到哥哥的长度就....\n(〃w〃)', '，嘶哈嘶哈\n(((o(*°▽°*)o)))...']
    try:
            group_id = str(session.ctx['group_id'])
            userQQ = str(session.ctx['message'][1]['data']['qq'])
    except IndexError:
            pass
    except KeyError:
            group_id = 'null'
    at = f'[CQ:at,qq={userQQ}]'
    todaylength = await getlength(userQQ)
    if userQQ == 'all':
            sendMsg = f'全体成员今日的平均丁丁长度是{abs(todaylength)}cm'
    elif todaylength <= 0:
            sendMsg = f'{at}今日的牛~牛长度是....今天你是女孩子({todaylength}cm)'
    else:
            sendMsg = f'{at}今日的牛~牛长度是{todaylength}cm'
    if group_id in {'224199904'}:
            return
    await session.finish(sendMsg)
    #await session.finish(str(todaylength))
    if todaylength <= 0:
            sendMsg += extra_words[0]
    elif 1 <= todaylength <= 3:
            sendMsg += extra_words[1]
    elif 4 <= todaylength <= 10:
            sendMsg += extra_words[2]
    elif 11 <= todaylength <= 17:
            sendMsg += extra_words[3]
    elif 18 <= todaylength <= 24:
            sendMsg += extra_words[4]
    else:
            sendMsg += extra_words[5]
    #await session.finish(sendMsg)

async def getlength(userQQ):
    neg_seed = randint(1,10)
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
                            "cn": "",
                            "eu": "",
            "na": ""
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
            content= await f.read()
    content = ujson.loads(content)
    return content

async def writeJson(p, info):
    async with aiofiles.open(p, 'w', encoding='utf-8') as f:
            await f.write(ujson.dumps(info))
    return SUCCESS

async def getCurrentTime():
    nowDate = str(datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d'))
    return nowDate

async def getTimeDiff(origin):
    a = parse(origin)
    b = parse(await getCurrentTime())
    return int((b - a).days)

