import sys
import re
import asyncio
import discord

USER_TOKEN = sys.argv[1]

# Client 객체 생성 (이벤트 직접 수신 방식)
client = discord.Client(self_bot=True)
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

@client.event
async def on_ready():
    print(f"✅ 셀프봇 연결 완료: {client.user}")

@client.event
async def on_message(message):
    # 본인이 작성한 메시지만 감지
    if message.author.id != client.user.id:
        return

    content = message.content.strip()

    # 매크로 시작 명령어 처리
    if content.startswith("$메크로시작"):
        try:
            await message.delete()
        except Exception:
            pass

        parts = content.split(" ", 3)
        if len(parts) < 4:
            notice = await message.channel.send("❌ 사용법: `$메크로시작 30m 3m 입력할내용`")
            await asyncio.sleep(2)
            await notice.delete()
            return

        total_str, interval_str, send_text = parts[1], parts[2], parts[3]
        total_sec = parse_time(total_str)
        interval_sec = parse_time(interval_str)

        if not total_sec or not interval_sec or interval_sec <= 0:
            notice = await message.channel.send("❌ 시간 형식이 올바르지 않습니다.")
            await asyncio.sleep(2)
            await notice.delete()
            return

        task = asyncio.create_task(run_macro(message.channel, total_sec, interval_sec, send_text, total_str, interval_str))
        active_tasks.append(task)

    # 매크로 중지 명령어 처리
    elif content.startswith("$메크로중지"):
        try:
            await message.delete()
        except Exception:
            pass

        count = 0
        for task in list(active_tasks):
            if not task.done():
                task.cancel()
                count += 1
        active_tasks.clear()

        notice = await message.channel.send(f"🛑 매크로({count}개) 중지 완료!")
        await asyncio.sleep(2)
        await notice.delete()

async def run_macro(channel, total_sec, interval_sec, send_text, total_str, interval_str):
    notice = await channel.send(f"✅ 매크로 시작! (`{total_str}` 동안 `{interval_str}` 간격)")
    await asyncio.sleep(2)
    try:
        await notice.delete()
    except Exception:
        pass

    elapsed = 0
    try:
        while elapsed < total_sec:
            await channel.send(send_text)
            await asyncio.sleep(interval_sec)
            elapsed += interval_sec

        done_notice = await channel.send(f"🏁 매크로 종료 (`{total_str}` 경과)")
        await asyncio.sleep(2)
        await done_notice.delete()
    except asyncio.CancelledError:
        pass

try:
    client.run(USER_TOKEN)
except Exception as e:
    print(f"토큰 로그인 에러: {e}")
