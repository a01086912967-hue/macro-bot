\import os
import subprocess
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
running_workers = {}


class TokenModal(discord.ui.Modal, title="🔑 매크로 토큰 등록"):
    user_token = discord.ui.TextInput(
        label="디스코드 토큰 (Authorization)",
        placeholder="따옴표나 공백 없이 토큰만 입력하세요.",
        style=discord.TextStyle.paragraph,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        token_value = self.user_token.value.strip()

        # 기존 프로세스 종료
        if user_id in running_workers:
            proc = running_workers[user_id]
            if proc.poll() is None:
                proc.terminate()
            del running_workers[user_id]

        try:
            # 버퍼링 없이 백그라운드로 셀프봇 프로세스 독립 실행
            process = subprocess.Popen(
                ["python3", "-u", "worker.py", token_value]
            )
            running_workers[user_id] = process

            await interaction.followup.send(
                "✅ **매크로가 실행되었습니다!**\n"
                "채팅창에 `$메크로시작 10m 1m 내용` 형식으로 입력해 보세요.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ 매크로 실행 오류: {e}", ephemeral=True
            )


class MacroControlView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔑 토큰 등록 및 매크로 시작",
        style=discord.ButtonStyle.primary,
        custom_id="start_macro_button",
    )
    async def start_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(TokenModal())

    @discord.ui.button(
        label="🛑 매크로 연결 해제",
        style=discord.ButtonStyle.danger,
        custom_id="stop_macro_button",
    )
    async def stop_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        if user_id in running_workers:
            proc = running_workers[user_id]
            if proc.poll() is None:
                proc.terminate()
            del running_workers[user_id]

            await interaction.followup.send(
                "🛑 **매크로 연결이 완전히 해제되었습니다.**", ephemeral=True
            )
        else:
            await interaction.followup.send(
                "⚠️ **현재 실행 중인 매크로가 없습니다.**", ephemeral=True
            )


@bot.event
async def on_ready():
    print(f"✅ 메인 관리자 봇 로그인 성공: {bot.user}")


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
            "2. 원하는 채팅방(DM, 타 서버 등)에서 명령어 입력:\n"
            "   `$메크로시작 [전체시간] [반복간격] [내용]`\n"
            "3. 매크로 중지: `$메크로중지` 입력"
        ),
        color=discord.Color.blue(),
    )

    view = MacroControlView()
    await ctx.send(embed=embed, view=view)


if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
