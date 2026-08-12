import os
import asyncio
import re
import aiohttp
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 유저별 토큰 및 매크로 태스크 관리
user_tokens = {}
user_tasks = {}

def parse_time(time_str: str) -> int:
    match = re.match(r"^(\d+)([sSmMhH])$", time_str)
    if not match:
        return None
    amount, unit = int(match.group(1)), match.group(2).lower()
    if unit == "s": return amount
    elif unit == "m": return amount * 60
    elif unit == "h": return amount * 3600

# REST API 직접 전송 함수 (라이브러리 충돌 완전 차단)
async def send_discord_message(token, channel_id, content):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    payload = {"content": content}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            return resp.status

async def macro_loop(user_id, token, channel_id, total_sec, interval_sec, content):
    elapsed = 0
    await send_discord_message(token, channel_id, f"✅ 매크로 동작 시작! ({total_sec}초 동안 {interval_sec}초 간격)")
    try:
        while elapsed < total_sec:
            await send_discord_message(token, channel_id, content)
            await asyncio.sleep(interval_sec)
            elapsed += interval_sec
        await send_discord_message(token, channel_id, "🏁 매크로가 완료되었습니다.")
    except asyncio.CancelledError:
        await send_discord_message(token, channel_id, "🛑 매크로가 강제 중지되었습니다.")
    finally:
        if user_id in user_tasks:
            del user_tasks[user_id]

class TokenModal(discord.ui.Modal, title="🔑 매크로 토큰 등록"):
    user_token = discord.ui.TextInput(
        label="디스코드 토큰 (Authorization)",
        placeholder="따옴표 없이 토큰을 입력하세요.",
        style=discord.TextStyle.paragraph,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        token_val = self.user_token.value.strip().replace('"', '').replace("'", "")

        user_tokens[user_id] = token_val

        await interaction.followup.send(
            "✅ **토큰 등록 완료!**\n\n"
            "이제 실행을 원하는 **채널 ID**를 확인하신 후, 채널에 아래 명령어를 입력하세요:\n"
            "`!시작 [전체시간] [간격] [내용]`\n"
            "*(예시: `!시작 10m 1m 안녕하세요`)*",
            ephemeral=True
        )

class MacroControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔑 토큰 등록 및 매크로 시작", style=discord.ButtonStyle.primary, custom_id="start_macro_btn")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TokenModal())

    @discord.ui.button(label="🛑 매크로 연결 해제", style=discord.ButtonStyle.danger, custom_id="stop_macro_btn")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        
        if user_id in user_tasks:
            user_tasks[user_id].cancel()
            del user_tasks[user_id]
        if user_id in user_tokens:
            del user_tokens[user_id]

        await interaction.followup.send("🛑 **매크로 및 토큰 연결이 완전히 해제되었습니다.**", ephemeral=True)

@bot.event
async def on_ready():
    print(f"========================================")
    print(f"✅ 메인 봇 로그인 성공: {bot.user}")
    print(f"========================================")

@bot.command(name="패널생성")
@commands.has_permissions(administrator=True)
async def create_panel(ctx):
    try: await ctx.message.delete()
    except Exception: pass

    embed = discord.Embed(
        title="🤖 디스코드 매크로 컨트롤 패널",
        description=(
            "아래 버튼을 눌러 계정 토큰을 등록하세요.\n\n"
            "**[ 사용법 ]**\n"
            "1. **`🔑 토큰 등록 및 매크로 시작`** 클릭 후 토큰 입력\n"
            "2. 매크로를 돌릴 채널에서 명령어 입력:\n"
            "   `!시작 [전체시간] [간격] [내용]`\n"
            "   *(예: `!시작 30m 3m 테스트`)*\n"
            "3. 중지하려면 패널의 **`🛑 매크로 연결 해제`** 클릭"
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=MacroControlView())

@bot.command(name="시작")
async def start_macro_cmd(ctx, total_str: str, interval_str: str, *, content: str):
    user_id = ctx.author.id
    if user_id not in user_tokens:
        await ctx.send("❌ 먼저 패널에서 **토큰을 등록**해 주세요!", delete_after=3)
        return

    total_sec = parse_time(total_str)
    interval_sec = parse_time(interval_str)

    if not total_sec or not interval_sec or interval_sec <= 0:
        await ctx.send("❌ 시간 형식이 올바르지 않습니다. (예: 10m 1m)", delete_after=3)
        return

    if user_id in user_tasks:
        user_tasks[user_id].cancel()

    token = user_tokens[user_id]
    task = asyncio.create_task(macro_loop(user_id, token, ctx.channel.id, total_sec, interval_sec, content))
    user_tasks[user_id] = task
    try: await ctx.message.delete()
    except Exception: pass

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
