import unicodedata
from pathlib import Path
from typing import Literal
import ujson as json
from nonebot import get_driver, on_command
from nonebot.matcher import Matcher
from nonebot.message import event_preprocessor
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
    unescape,
)

from .utils import recall_msg_dealer, MessageChecker

usage: str ="""

指令表:
  监听私聊 qq qq1 qq2 ...
  监听群聊 qq qq1 qq2 ...
  监听私聊 all
  监听群聊 all
  取消监听私聊 qq qq1 qq2 ...
  取消监听群聊 qq qq1 qq2 ...
  取消监听私聊 all
  取消监听群聊 all

  查看监听列表

  传话私聊 qq XXXXXX
  传话群聊 qq XXXXXX

""".strip()


__plugin_meta__ = PluginMetadata(
    name="应声谲",
    description="转发指定会话消息给SUPERUSER",
    usage=usage,
    type="application",
    homepage="https://github.com/tkgs0/nonebot-plugin-eavesdropper",
    supported_adapters={"~onebot.v11"}
)


superusers = get_driver().config.superusers

file_path = Path() / 'data' / 'eavesdropper' / 'eavesdropper.json'
file_path.parent.mkdir(parents=True, exist_ok=True)


namelist: dict = (
    json.loads(file_path.read_text('utf-8'))
    if file_path.is_file()
    else {}
)


def save_namelist() -> None:
    file_path.write_text(
        json.dumps(
            namelist,
            ensure_ascii=False,
            escape_forward_slashes=False,
            indent=2
        ),
        encoding='utf-8'
    )


template: dict = {
    'group': {
        'all': False, 
        'list': []
    },
    'priv': {
        'all': False, 
        'list': []
    }
}


def check_self_id(self_id) -> str:
    self_id = f'{self_id}'
    if namelist.get(self_id) == None:
        namelist.update({
            self_id: {}
        })
        save_namelist()

    return self_id


def check_master(self_id, master_id) -> str:
    self_id = check_self_id(self_id)
    master_id = f'{master_id}'
    temp: dict = {}
    temp.update(template)

    try:
        if not namelist[self_id].get(master_id):
            namelist[self_id].update({
                master_id: temp
            })
            save_namelist()
        for i in template:
            if namelist[self_id][master_id].get(i) == None:
                namelist[self_id][master_id].update({i: temp[i]})
                save_namelist()
    except Exception:
        namelist[self_id].update({
            master_id: temp
        })
        save_namelist()

    return master_id


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def handle_msg(repo: Message):
    try:
        return recall_msg_dealer(repo)
    except Exception:
        if not MessageChecker(repr(repo)).check_cq_code:
            return repo
    return


async def send_msg(bot: Bot, event: MessageEvent, master_id: str, msg = None):
    if master_id in superusers:
        await bot.send_private_msg(
            user_id=int(master_id),
            message=(
                f"[msg_id: {event.message_id}]\n[群聊{event.group_id}][@{event.user_id}]\n[{event.sender.card or event.sender.nickname}]:\n{msg}"
                if isinstance(event, GroupMessageEvent)
                else f"[msg_id: {event.message_id}]\n[私聊][@{event.user_id}]\n[{event.sender.nickname}]:\n{msg}"
            )
        )


@event_preprocessor
async def listen_priv_processor(bot: Bot, event: PrivateMessageEvent):
    self_id = check_self_id(event.self_id)
    uid = str(event.user_id)
    for i in namelist[self_id]:
        if namelist[self_id][i].get('priv') and (namelist[self_id][i]['priv']['all'] or uid in namelist[self_id][i]['priv']['list']):
            await send_msg(bot, event, i, handle_msg(event.get_message()))
    return


@event_preprocessor
async def listen_group_processor(bot: Bot, event: GroupMessageEvent):
    self_id = check_self_id(event.self_id)
    gid = str(event.group_id)
    for i in namelist[self_id]:
        if namelist[self_id][i].get('group') and (namelist[self_id][i]['group']['all'] or gid in namelist[self_id][i]['group']['list']):
            await send_msg(bot, event, i, handle_msg(event.get_message()))
    return


def handle_message(
    self_id,
    master_id,
    args,
    mode: bool,
) -> str | None:
    self_id = check_self_id(self_id)
    master_id = check_master(self_id, master_id)

    content: str = args.extract_plain_text().strip()

    if content.startswith("群聊"):
        type_ = "group"
    elif content.startswith("私聊"):
        type_ = "priv"
    else:
        return

    uids: list = content[2:].split()

    if not uids:
        return usage

    if uids[0].lower() == 'all':
        namelist[self_id][master_id][type_]['all'] = mode
        save_namelist()
        return f"已{'开启' if mode else '取消'}全局监听{content[:2]}"

    for uid in uids:
        if not is_number(uid):
            return '参数错误, id必须是数字..'

    return handle_namelist(self_id, master_id, uids, mode, type_)


def handle_namelist(
    self_id,
    master_id,
    uids: list,
    mode: bool,
    type_: Literal['group', 'priv'],
) -> str:
    self_id = check_self_id(self_id)
    master_id = check_master(self_id, master_id)

    types = {
        'group': '群聊',
        'priv': '私聊',
    }

    if mode:
        namelist[self_id][master_id][type_]['list'].extend(uids)
        namelist[self_id][master_id][type_]['list'] = list(set(namelist[self_id][master_id][type_]['list']))
        _mode = '开启'
    else:
        namelist[self_id][master_id][type_]['list'] = [uid for uid in namelist[self_id][master_id][type_]['list'] if uid not in uids]
        _mode = '取消'
    save_namelist()

    _type = types[type_]
    return f"已{_mode}监听 {len(uids)} 个{_type}: {', '.join(uids)}"


listen_add = on_command("监听", permission=SUPERUSER, priority=2, block=False)

@listen_add.handle()
async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    msg = handle_message(event.self_id, event.user_id, args, True)
    if msg:
        matcher.stop_propagation()
        await listen_add.finish(msg)


listen_del = on_command("取消监听", permission=SUPERUSER, priority=2, block=False)

@listen_del.handle()
async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    msg = handle_message(event.self_id, event.user_id, args, False)
    if msg:
        matcher.stop_propagation()
        await listen_del.finish(msg)


check_namelist = on_command("查看监听列表", permission=SUPERUSER, priority=2, block=True)

@check_namelist.handle()
async def _(event: MessageEvent):
    self_id = check_self_id(event.self_id)
    master_id = check_master(event.self_id, event.user_id)
    
    namelist[self_id][master_id]

    await check_namelist.finish(f"""
群聊:
  全局监听: {'开' if namelist[self_id][master_id]['group']['all'] else '关'}
  监听列表: {namelist[self_id][master_id]['group']['list']}
私聊:
  全局监听: {'开' if namelist[self_id][master_id]['priv']['all'] else '关'}
  监听列表: {namelist[self_id][master_id]['priv']['list']}
""".strip())




tell = on_command("传话", permission=SUPERUSER, priority=2, block=False)


@tell.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    content = unescape(str(arg).strip())
    if content.startswith("群聊"):
        matcher.state["FLAG"] = True
    elif content.startswith("私聊"):
        matcher.state["FLAG"] = False
    else:
        await tell.finish()

    matcher.stop_propagation()

    args = content[2:].split(maxsplit=1)
    if not args:
        await tell.finish(usage)
    if not is_number(args[0]):
        await tell.finish('参数错误, id必须是数字..')
    matcher.state["UID"] = args[0]
    if args[1:]:
        matcher.state["ARG"] = args[1:]


@tell.got("ARG", prompt="内容呢?")
async def _(matcher: Matcher, bot: Bot):
    await tell.finish(
        repr(
            (
                await bot.send_group_msg(
                    group_id=int(matcher.state["UID"]),
                    message=Message(matcher.state["ARG"])
                )
            ) if matcher.state["FLAG"]
            else (
                await bot.send_private_msg(
                    user_id=int(matcher.state["UID"]),
                    message=Message(matcher.state["ARG"])
                )
            )
        )
    )
