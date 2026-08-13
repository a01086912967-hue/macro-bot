import os
import discord
from discord.ext import commands
from discord import ui

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 1. 토큰 및 정보 입력 양식 (팝업 창)
class TokenRegisterModal(ui.Modal, title="🔑 매크로 토큰 및 정보 등록"):
    user_token = ui.TextInput(
        label="디스코드 유저 토큰 (Self Bot Token)",
        placeholder="본인 계정 토큰을 입력하세요",
        style=discord.TextStyle.short,
        required=True
    )
    guild_id = ui.TextInput(
        label="서버 ID",
        placeholder="작동할 서버 ID를 입력하세요",
        style=discord.TextStyle.short,
        required=True
    )
    channel_id = ui.TextInput(
        label="채널 ID",
        placeholder="작동할 채널 ID를 입력하세요",
        style=discord.TextStyle.short,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        # 입력받은 정보 양식 제출 성공 안내 (실제 로직 없이 수신 완료 메시지만 출력)
        await interaction.response.send_message(
            f"✅ **등록 요청 완료**\n- 서버 ID: `{self.guild_id.value}`\n- 채널 ID: `{self.channel_id.value}`\n토큰 정보가 정상적으로 수신되었습니다.", 
            ephemeral=True
        )

# 2. 패널 버튼 컨트롤
class MacroControlView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🔑 토큰 등록 및 매크로 시작", style=discord.ButtonStyle.primary, custom_id="start_macro_button")
    async def start_button(self, interaction: discord.Interaction, button: ui.Button):
        # 버튼 누르면 입력 양식(Modal) 팝업 띄우기
        await interaction.response.send_modal(TokenRegisterModal())

    @ui.button(label="🛑 매크로 연결 해제", style=discord.ButtonStyle.danger, custom_id="stop_macro_button")
    async def stop_button(self, interaction: discord.Interaction, button: ui.Button):
        # 해제 누르면 단순 안내 메시지만 전송
        await interaction.response.send_message("🛑 매크로 연결이 해제되었습니다.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ 관리자 봇 온라인: {bot.user}")

@bot.command(name="패널생성")
@commands.has_permissions(administrator=True)
async def create_panel(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    embed = discord.Embed(
        title="🤖 디스코드 매크로 컨트롤 패널",
        description="아래 버튼을 눌러 토큰을 등록하거나 매크로 연결을 관리하세요.",
        color=discord.Color.blue()
    )

    view = MacroControlView()
    await ctx.send(embed=embed, view=view)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
