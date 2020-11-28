from nonebot import on_command, CommandSession
import urllib.request

__plugin_name__ = 'stat'
__plugin_usage__ = 'EVE晨曦监视器\nstat'

@on_command('stat', only_to_me=False)

async def stat(session: CommandSession):
	img_url = 'https://images.ceve-market.org/status/status.png'
	urllib.request.urlretrieve(img_url,filename="status.png")
	local_url = "file:///root/bot/status.png"
	await session.send(f'[CQ:image,file={local_url}]')
