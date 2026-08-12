import os, sys, asyncio, re, discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
user_clients = {}

def parse_time(time_str: str) -> int:
    match = re.match(r"^(\d+)([sSmMhH])$", time_str)
    if not match: return None
    amount, unit = int(match.group(1)), match.group(2).lower()
    if unit == "s": return amount
    elif unit == "m": return amount * 60
    elif unit == "h": return amount * 3600

class MacroRunner:
    def __init__(self, token):
        self.token = token
        intents_self = discord.Intents.default()
        intents_self.message_content = True
        self.client = discord.Client(intents=intents_self, self_bot=True)
        self.active_tasks = []
        self.setup_events()

    def setup_events(self):
        @self.client.event
        async def on_message(message):
            if message.author.id != self.client.user.id: return
            content = message.content.strip()

            if content.startswith("$메크로시작"):
                try: await message.delete()
                except: pass
                parts = content.split(" ", 3)
                if len(parts) < 4:
                    notice = await message.channel.send("❌ 사용법: `$메크로시작 30m 3m 입력할내용`")
                    await asyncio.sleep(2)
                    try: await notice.delete()
                    except: pass
                    return

                total_str, interval_str, send_text = parts[1], parts[2], parts[3]
                total_sec, interval_sec = parse_time(total_str), parse_time(interval_str)

                if not total_sec or not interval_sec or interval_sec <= 0:
                    notice = await message.channel.send("❌ 시간 형식이 올바르지 않습니다.")
                    await asyncio.sleep(2)
                    try: await notice.delete()
                    except: pass
                    return

                task = asyncio.create_task(self.run_loop(message.channel, total_sec, interval_sec, send_text, total_str, interval_str))
                self.active_tasks.append(task)

            elif content.startswith("$메크로중지"):
                try: await message.delete()
                except: pass
                count = 0
                for task in list(self.active_tasks):
                    if not task.done():
                        task.cancel()
                        count += 1
                self.active_tasks.clear()
                notice = await message.channel.send(f"🛑 현재 진행 중인 매크로({count}개)를 중지했습니다.")
                await asyncio.sleep(2)
                try: await notice.delete()
                except: pass

    async def run_loop(self, channel, total_sec, interval_sec, send_text, total_str, interval_str):
        notice = await channel.send(f"✅ 매크로 시작! (`{total_str}` 동안 `{interval_str}` 간격)")
        await asyncio.sleep(2)
        try: await notice.delete()
        except: pass

        elapsed = 0
        try:
            while elapsed < total_sec:
                await channel.send(send_text)
                await asyncio.sleep(interval_sec)
                elapsed += interval_sec
            done_notice = await channel.send(f"🏁 매크로 종료 (`{total_str}` 경과)")
            await asyncio.sleep(2)
            try: await done_notice.delete()
            except: pass
        except asyncio.CancelledError:
            pass

    async def start(self):
        try: await self.client.start(self.token)
        except Exception as e: print(f"셀프봇 로그인 실패: {e}")

    async def stop(self):
        await self.client.close()

class TokenModal(discord.ui.Modal, title="🔑 매크로 토큰 등록"):
    user_token = discord.ui.TextInput(label="디스코드 토큰", placeholder="토큰만 입력하세요.", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        token_value = self.user_token.value.strip()

        if user_id in user_clients:
            await user_clients[user_id].stop()
            del user_clients[user_id]

        runner = MacroRunner(token_value)
        user_clients[user_id] = runner
        asyncio.create_task(runner.start())

        await interaction.followup.send("✅ **매크로 연결 완료!**\n명령어: `$메크로시작 10m 1m 테스트문구`", ephemeral=True)

class MacroControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔑 토큰 등록 및 매크로 시작", style=discord.ButtonStyle.primary, custom_id="start_macro_button")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TokenModal())

    @discord.ui.button(label="🛑 매크로 연결 해제", style=discord.ButtonStyle.danger, custom_id="stop_macro_button")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        if user_id in user_clients:
            await user_clients[user_id].stop()
            del user_clients[user_id]
            await interaction.followup.send("🛑 **매크로 연결이 완전히 해제되었습니다.**", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ **현재 실행 중인 매크로가 없습니다.**", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ 메인 관리자 봇 실행 완료: {bot.user}")

@bot.command(name="패널생성")
@commands.has_permissions(administrator=True)
async def create_panel(ctx):
    try: await ctx.message.delete()
    except: pass

    embed = discord.Embed(
        title="🤖 디스코드 매크로 컨트롤 패널",
        description="아래 버튼을 눌러 본인의 계정 토큰을 등록하고 매크로를 시작하세요.",
        color=discord.Color.blue()
    )
    view = MacroControlView()
    await ctx.send(embed=embed, view=view)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
