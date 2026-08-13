import os
import discord
from discord.ext import commands

# 호스팅 환경변수에서 DISCORD_TOKEN을 가져옵니다.
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class MacroControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔑 토큰 등록 및 매크로 시작", style=discord.ButtonStyle.primary, custom_id="start_macro_button")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "✅ **매크로 시작 안내**\n`$메크로시작 시간 간격 내용` 형식으로 입력하세요.\n예시: `$메크로시작 30m 3m 안녕하세요`", 
            ephemeral=True
        )

    @discord.ui.button(label="🛑 매크로 연결 해제", style=discord.ButtonStyle.danger, custom_id="stop_macro_button")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🛑 **매크로 중지 안내**\n`$메크로중지`를 입력하세요.", 
            ephemeral=True
        )

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
            "아래 버튼을 누르거나 안내된 명령어를 입력하여 매크로를 제어하세요.\n\n"
            "**[ 사용 방법 ]**\n"
            "1. **매크로 시작**: `$메크로시작 30m 3m 내용`\n"
            "2. **매크로 중지**: `$메크로중지`"
        ),
        color=discord.Color.blue()
    )

    view = MacroControlView()
    await ctx.send(embed=embed, view=view)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
