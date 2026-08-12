import asyncio
import re
import sys
import discord
from discord.ext import commands

# 메인 봇으로부터 전달받은 유저 토큰
USER_TOKEN = sys.argv[1]

# discord.py-self 전용 기본 설정 (Intents 충돌 방지)
bot = commands.Bot(command_prefix="$", self_bot=True)
active_tasks = []


def parse_time(time_str: str) -> int:
    match = re.match(r"^(\d+)([sSmMhH])$", time_str)
    if not match:
        return None
    amount, unit = int(match.group(1)), match.group(2).lower()
    if unit == "s":
        return amount
    elif unit == "m":
        return amount * 60
    elif unit == "h":
        return amount * 3600


@bot.event
async def on_ready():
    print(f"==========================================")
    print(f"셀프봇 접속 성공! 계정: {bot.user}")
    print(f"==========================================")


@bot.command(name="메크로시작")
async def start_macro(
    ctx, total_time_str: str, interval_time_str: str, *, content: str
):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    total_seconds = parse_time(total_time_str)
    interval_seconds = parse_time(interval_time_str)

    if total_seconds is None or interval_seconds is None:
        notice = await ctx.send(
            "❌ 시간 형식이 올바르지 않습니다. (예: `$메크로시작 30m 3m 내용`)"
        )
        await asyncio.sleep(1)
        await notice.delete()
        return

    if interval_seconds <= 0 or total_seconds < interval_seconds:
        notice = await ctx.send(
            "❌ 반복 간격은 0보다 커야 하며, 전체 시간보다 길 수 없습니다."
        )
        await asyncio.sleep(1)
        await notice.delete()
        return

    task = asyncio.create_task(
        run_macro_loop(
            ctx,
            total_seconds,
            interval_seconds,
            content,
            total_time_str,
            interval_time_str,
        )
    )
    active_tasks.append(task)


async def run_macro_loop(
    ctx, total_seconds, interval_seconds, content, total_str, interval_str
):
    notice = await ctx.send(
        f"✅ 매크로 시작! (`{total_str}` 동안 `{interval_str}` 간격)"
    )
    await asyncio.sleep(1)
    try:
        await notice.delete()
    except Exception:
        pass

    elapsed_time = 0
    try:
        while elapsed_time < total_seconds:
            await ctx.send(content)
            await asyncio.sleep(interval_seconds)
            elapsed_time += interval_seconds

        done_notice = await ctx.send(
            f"🏁 매크로 완료되었습니다. (`{total_str}` 경과)"
        )
        await asyncio.sleep(1)
        await done_notice.delete()

    except asyncio.CancelledError:
        pass


@bot.command(name="메크로중지")
async def stop_macro(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    count = 0
    for task in list(active_tasks):
        if not task.done():
            task.cancel()
            count += 1

    active_tasks.clear()

    notice = await ctx.send(
        f"🛑 현재 진행 중인 모든 매크로({count}개)를 중지했습니다."
    )
    await asyncio.sleep(1)
    try:
        await notice.delete()
    except Exception:
        pass


try:
    bot.run(USER_TOKEN)
except Exception as e:
    print(f"셀프봇 로그인/실행 에러 발생: {e}")
