import os
import subprocess
import sys
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

user_processes = {}


class TokenModal(discord.ui.Modal, title="매크로 등록 및 시작"):
    user_token = discord.ui.TextInput(
        label="디스코드 계정 토큰",
        placeholder="본인 계정의 비밀 토큰을 입력하세요.",
        style=discord.TextStyle.short,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        token_val = self.user_token.value.strip()

        if user_id in user_processes:
            user_processes[user_id].terminate()
            del user_processes[user_id]

        proc = subprocess.Popen([sys.executable, "worker.py", token_val])
        user_processes[user_id] = proc

        await interaction.response.send_message(
            f"✅ **매크로가 성공적으로 등록 및 실행되었습니다!**\n"
            f"이제 채팅창에서 `$메크로시작 30m 3m (내용)` 또는 `$메크로중지`를 사용하실 수 있습니다.",
            ephemeral=True,
        )


class MacroControlView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔑 토큰 등록 및 매크로 시작",
        style=discord.ButtonStyle.success,
        custom_id="btn_start_macro",
    )
    async def start_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(TokenModal())

    @discord.ui.button(
        label="🛑 매크로 연결 해제",
        style=discord.ButtonStyle.danger,
        custom_id="btn_stop_macro",
    )
    async def stop_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        user_id = interaction.user.id

        if user_id in user_processes:
            user_processes[user_id].terminate()
            del user_processes[user_id]
            await interaction.response.send_message(
                "🛑 **매크로 연결이 정상적으로 해제되었습니다.**",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "⚠️ 현재 실행 중인 매크로가 없습니다.", ephemeral=True
            )


@bot.event
async def on_ready():
    print(f"관리자 메인 봇 로그인 성공: {bot.user}")
    bot.add_view(MacroControlView())


@bot.command(name="패널생성")
@commands.has_permissions(administrator=True)
async def create_panel(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    embed = discord.Embed(
        title="⚡ 자동 매크로 관리 시스템",
        description=(
            "아래 버튼을 눌러 본인의 계정 토큰을 등록하면 자동 매크로 기능이 활성화됩니다.\n\n"
            "**[기능 안내]**\n"
            "• **🔑 토큰 등록 및 매크로 시작**: 계정 토큰을 입력하여 매크로 시스템 작동\n"
            "• **🛑 매크로 연결 해제**: 현재 연결된 매크로 시스템 중지 및 해제\n\n"
            "**[사용 명령어 예시]**\n"
            "`$메크로시작 30m 3m 메시지내용` (30분 동안 3분 간격 메시지 전송)\n"
            "`$메크로중지` (작업 중인 모든 메시지 중단)"
        ),
        color=discord.Color.blue(),
    )
    embed.set_footer(
        text="⚠️ 입력하신 토큰은 타인에게 공개되지 않으며 ephemeral 입력창으로 처리됩니다."
    )

    await ctx.send(embed=embed, view=MacroControlView())


BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(BOT_TOKEN)
