"""
服务器讯息打印

"""
from datetime import datetime, timezone, timedelta
from pyrogram import filters
from bot import bot, emby_line, emby_whitelist_line, config
from bot.func_helper.user_prefs import get_user_line
from bot.func_helper.emby import emby
from bot.func_helper.filters import user_in_group_on_filter
from bot.sql_helper.sql_emby import sql_get_emby
from bot.func_helper.fix_bottons import cr_page_server
from bot.func_helper.msg_utils import callAnswer, editMessage
 


@bot.on_callback_query(filters.regex('server') & user_in_group_on_filter)
async def server(_, call):
    data = sql_get_emby(tg=call.from_user.id)
    if not data:
        return await editMessage(call, '⚠️ 数据库没有你，请重新 /start录入')
    await callAnswer(call, '🌐查询中...')
    try:
        j = int(call.data.split(':')[1])
    except IndexError:
        # 第一次查看
        send = await editMessage(call, "**▎🌐查询中...\n\nο(=•ω＜=)ρ⌒☆ 发送bibo电波~bibo~ \n⚡ 点击按钮查看相应服务器状态**")
        if send is False:
            return

        keyboard, sever = await cr_page_server()
        server_info = sever[0]['server'] if sever == '' else ''
    else:
        keyboard, sever = await cr_page_server()
        server_info = ''.join([item['server'] for item in sever if item['id'] == j])

    pwd = '空' if not data.pwd else data.pwd
    # 应用用户自选线路（若存在），否则使用默认线路
    selected_line = get_user_line(call.from_user.id)
    base_line = selected_line or emby_line
    if data.lv == 'b':
        line = f'{base_line}'
    elif data.lv == 'a':
        line = f'{base_line}'
        # 白名单用户可额外显示白名单专属线路
        if emby_whitelist_line and emby_whitelist_line != base_line:
            line += f'\n{emby_whitelist_line}'
    else:
        line = ' - **无权查看**'
    # 构建可选线路列表（如有配置）
    selectable_lines_text = ''
    try:
        lines = getattr(config, 'emby_lines', []) or []
        if lines and data.lv in ['a', 'b']:
            selectable_lines_text = "\n可选线路：\n" + "\n".join([f"[{i+1}] {u}" for i, u in enumerate(lines)]) + "\n"
    except Exception:
        pass
    try:
        online = emby.get_current_playing_count()
    except:
        online = 'Emby服务器断连 ·0'
    text = f'**▎↓目前线路 & 用户密码：**`{pwd}`\n' \
           f'{line}\n' \
           f'{selectable_lines_text}\n' \
           f'{server_info}' \
           f'· 🎬 在线 | **{online}** 人\n\n' \
           f'**· 🌏 [{(datetime.now(timezone(timedelta(hours=8)))).strftime("%Y-%m-%d %H:%M:%S")}]**'

    await editMessage(call, text, buttons=keyboard)

