import sys
import re
import asyncio
import discord

USER_TOKEN = sys.argv[1].strip()

# 셀프봇 client 설정
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
    print(f"========================================")
    print(f"✅ 셀프봇 정상 로그인 완료: {client.user} (ID: {client.user.id})")
    print(f"========================================")

@client.event
async def on_message(message):
    # 본인이 보낸 메시지가 아니면 무시
    if message.author.id != client.user.id:
        return

    content = message.content.strip()

    # $메크로시작 명령어 처리
    if content.startswith("$메크로시작"):
        try:
            await message.delete()
        except Exception as e:
            print(f"메시지 삭제 실패: {e}")

        parts = content.split(" ", 3)
        if len(parts) < 4:
            notice = await message.channel.send("❌ 사용법: `$메크로시작 30m 3m 입력할내용`")
            await asyncio.sleep(2)
            try:
                await notice.delete()
            except Exception:
                pass
            return

        total_str, interval_str, send_text = parts[1], parts[2], parts[3]
        total_sec = parse_time(total_str)
        interval_sec = parse_time(interval_str)

        if not total_sec or not interval_sec or interval_sec <= 0:
            notice = await message.channel.send("❌ 시간 형식이 올바르지 않습니다. (예: 10m, 1h, 30s)")
            await asyncio.sleep(2)
            try:
                await notice.delete()
            except Exception:
                pass
            return

        task = asyncio.create_task(run_macro(message.channel, total_sec, interval_sec, send_text, total_str, interval_str))
        active_tasks.append(task)

    # $메크로중지 명령어 처리
    elif content.startswith("$메크로중지"):
        try:
            await message.delete()
        except Exception as e:
            print(f"메시지 삭제 실패: {e}")

        count = 0
        for task in list(active_tasks):
            if not task.done():
                task.cancel()
                count += 1
        active_tasks.clear()

        notice = await message.channel.send(f"🛑 현재 진행 중인 매크로({count}개)를 중지했습니다.")
        await asyncio.sleep(2)
        try:
            await notice.delete()
        except Exception:
            pass

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
        try:
            await done_notice.delete()
        except Exception:
            pass
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        client.run(USER_TOKEN)
    except Exception as e:
        print(f"❌ 셀프봇 실행 중 오류 발생: {e}")
