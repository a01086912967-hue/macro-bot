import os
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class TokenModal(discord.ui.Modal, title="🔑 매크로 토큰 등록"):
    user_token = discord.ui.TextInput(
        label="디스코드 토큰 (Authorization)",
        placeholder="따옴표나 공백 없이 토큰만 입력하세요.",
        style=discord.TextStyle.paragraph,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "✅ **토큰 등록 요청이 접수되었습니다.**",
            ephemeral=True
        )

class MacroControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔑 토큰 등록 및 매크로 시작", style=discord.ButtonStyle.primary, custom_id="start_macro_button")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TokenModal())

    @discord.ui.button(label="🛑 매크로 연결 해제", style=discord.ButtonStyle.danger, custom_id="stop_macro_button")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🛑 **매크로 연결이 해제되었습니다.**", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ 메인 관리자 봇 실행 완료: {bot.user}")

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
            "1. **`🔑 토큰 등록 및 매크로 시작`** 버튼 클릭 후 토큰 입력\n"
            "2. 아무 채널이나 DM에서 명령어 입력:\n"
            "   `$메크로시작 30m 3m 내용`\n"
            "3. 매크로 중지: `$메크로중지` 입력"
        ),
        color=discord.Color.blue()
    )

    view = MacroControlView()
    await ctx.send(embed=embed, view=view)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
