import os
import discord
from discord.ext import commands
from discord import ui

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 1. 토큰만 입력받는 팝업 창 (Modal)
class TokenRegisterModal(ui.Modal, title="🔑 토큰 등록"):
    user_token = ui.TextInput(
        label="디스코드 계정 토큰",
        placeholder="본인의 계정 토큰을 입력하세요.",
        style=discord.TextStyle.short,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "✅ 토큰이 성공적으로 등록되었습니다! 매크로를 시작할 준비가 완료되었습니다.", 
            ephemeral=True
        )

# 2. 패널 버튼 컨트롤
class MacroControlView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🔑 토큰 등록 및 매크로 시작", style=discord.ButtonStyle.primary, custom_id="start_macro_button")
    async def start_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(TokenRegisterModal())

    @ui.button(label="🛑 매크로 연결 해제", style=discord.ButtonStyle.danger, custom_id="stop_macro_button")
    async def stop_button(self, interaction: discord.Interaction, button: ui.Button):
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
        description=(
            "아래 버튼을 눌러 본인의 계정 토큰을 등록하고 매크로를 시작하세요.\n\n"
            "**[ 사용법 ]**\n"
            "1. `🔑 토큰 등록 및 매크로 시작` 버튼 클릭 후 토큰 입력\n"
            "2. 아무 채널이나 DM에서 명령어 입력: `$메크로시작 30m 3m 내용`\n"
            "3. 매크로 중지: `$메크로중지` 입력"
        ),
        color=0x3498db  # 원래 임베드 옆선 파란색상
    )

    view = MacroControlView()
    await ctx.send(embed=embed, view=view)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
