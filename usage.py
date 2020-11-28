import nonebot
from nonebot import on_command, CommandSession

@on_command('usage', aliases=['help', '帮助'])
async def _(session: CommandSession):
	plugins = list(filter(lambda p: p.name, nonebot.get_loaded_plugins()))

	arg = session.current_arg_text.strip().lower()
	if not arg:
		await session.send(
			'一个兴趣使然的Bot By Kray@771689599\n我现在支持的功能有:\n' + '\n'.join(p.name for p in plugins) + '\n使用：@我 帮助 [功能名称]\n以获取更多信息,私聊无需@\n范例:@我 帮助 jita')
		return

	for p in plugins:
		if p.name.lower() == arg:
			await session.send(p.usage)
