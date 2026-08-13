import os
import asyncio
import discord
from discord.ext import commands

# 환경변수에서 봇 토큰 로드
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 버튼 클릭 시 나타나는 모달 창
class SimpleModal(discord.ui.Modal, title="🔑 정보 입력"):
    input_text = discord.ui.TextInput(
        label="입력 창",
        placeholder="내용을 입력하세요.",
        style=discord.TextStyle.paragraph,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"✅ **입력이 완료되었습니다!**\n입력한 내용: `{self.input_text.value}`",
            ephemeral=True
        )

# 패널에 부착될 버튼 UI
class ControlPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔑 등록하기", style=discord.ButtonStyle.primary, custom_id="btn_register")
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SimpleModal())

    @discord.ui.button(label="ℹ️ 안내 정보", style=discord.ButtonStyle.secondary, custom_id="btn_info")
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("ℹ️ 이 패널은 관리자 전용 안내 버튼입니다.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ 관리자 봇 정상 실행 완료: {bot.user}")

@bot.command(name="패널생성")
@commands.has_permissions(administrator=True)
async def create_panel(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    embed = discord.Embed(
        title="🤖 디스코드 안내 컨트롤 패널",
        description=(
            "아래 버튼을 눌러 원하는 기능을 이용하세요.\n\n"
            "• **`🔑 등록하기`**: 모달 입력창을 호출합니다.\n"
            "• **`ℹ️ 안내 정보`**: 간단한 안내 메시지를 확인합니다."
        ),
        color=discord.Color.blue()
    )

    view = ControlPanelView()
    await ctx.send(embed=embed, view=view)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
