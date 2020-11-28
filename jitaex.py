import time
import xml.etree.ElementTree as ET

import requests
import xlrd
from nonebot import CommandSession, on_command

__plugin_name__ = 'jita'
__plugin_usage__ = r"""EVE国服市场姬
价格已包含皮尔米特星系
查询物品价格：
jita [物品名称]
查询即时矿物收购价：
mineral/矿价"""

@on_command('mineral',aliases='矿价',only_to_me=False)

async def mineral(session: CommandSession):
	result = await market_json()
	await session.send(result)

async def market_json():
    result='吉他/皮米矿物最高收购价(ISK)：\n'
    tup_n = ('三钛合金','同位聚合体','类银超金属','类晶体胶矿','莫尔石','超噬矿','超新星诺克石','晶状石英核岩','色动力学三羧基')
    tup_id = ('34','37','36','35','11399','40','38','39','48927')
    for i in range(9):
        t_ID=tup_id[i]
        url_jita = f'https://www.ceve-market.org/api/market/region/10000002/system/30000142/type/{t_ID}.json'
        url_pimi = f'https://www.ceve-market.org/api/market/region/10000002/system/30000144/type/{t_ID}.json'
        data_json_jita = requests.get(url_jita).json()
        data_json_pimi = requests.get(url_pimi).json()
        time.sleep(0.05)
        buy_max = data_json_jita['buy']['max']
        if data_json_pimi['buy']['max'] > buy_max: buy_max = data_json_pimi['buy']['max']
        n=tup_n[i]
        s=f'{n:\u3000<8}{buy_max}\n'
        result+=s
    return result

@on_command('jita',only_to_me=False)

async def jita(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    name = stripped_arg
    if not stripped_arg: session.finish('.jita [物品]')
    p_report = get_price_of_name(name)
    await session.send(p_report)


def get_price_of_name(name: str) -> str:
	data = xlrd.open_workbook('./wot/plugins/typeID.xls')
	table = data.sheets()[0]
	nrows = table.nrows
	ID_list = []
	Name_list = []
	for i in range(nrows):
		try:
			l = table.row_values(i)
			if l[1].find(name) != -1:
				Name_list.append(l[1])
				ID_list.append(int(l[0]))
		except:
			raise
	if not ID_list: return '未搜索到物品\n蓝图、涂装、服饰暂不支持'
	t_ID = ID_list[0]
	t_Name = Name_list[0]
	result = get_data(t_ID,t_Name)
	t_Num = len(ID_list)

	#防爆措施
	if t_Num > 3: t_Num = 3
	try:
		if ID_list[1]:
			for i in range(1,t_Num):
				t_ID = ID_list[i]
				t_Name = Name_list[i]
				result += ('\n' + get_data(t_ID,t_Name))
				time.sleep(0.05)
	except:
		pass
	result_sum = f'''{result}
数据源:当前吉他/皮米价格'''
	return result_sum

def get_data(t_ID: str,t_name: str) -> str:	
	url_jita = f'https://www.ceve-market.org/api/market/region/10000002/system/30000142/type/{t_ID}.json'
	url_pimi = f'https://www.ceve-market.org/api/market/region/10000002/system/30000144/type/{t_ID}.json'
	data_json_jita = requests.get(url_jita).json()
	data_json_pimi = requests.get(url_pimi).json()
	buy_max = data_json_jita['buy']['max']
	sell_min = data_json_jita['sell']['min']

	if data_json_pimi['buy']['max'] > buy_max: buy_max = data_json_pimi['buy']['max']
	if data_json_pimi['sell']['min'] < sell_min and data_json_pimi['sell']['min']!= 0 or sell_min == 0: sell_min = data_json_pimi['sell']['min']
	
	buy_unit = sell_unit = ''
	if buy_max >= 10000 and buy_max < 100000000:
		buy_max /= 10000
		buy_unit = '万'  
	elif buy_max >= 100000000:
		buy_max /= 100000000
		buy_unit = '亿'
	if sell_min >= 10000 and sell_min < 100000000:
		sell_min /= 10000
		sell_unit = '万'  
	elif sell_min >= 100000000:
		sell_min /= 100000000
		sell_unit = '亿'
	result = f'''{t_name}
求购出价: {buy_max}{buy_unit} ISK
卖方出价: {sell_min}{sell_unit} ISK'''
	return result

