import os
import subprocess
import discord
from discord import app_commands
from discord.ext import commands

# 봇 실행 환경 설정
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 현재 실행 중인 셀프봇 프로세스를 저장하는 변수 (유저 ID: process)
running_workers = {}


# 토큰 입력 모달 창
class TokenModal(discord.ui.Modal, title="🔑 매크로 토큰 등록"):
    user_token = discord.ui.TextInput(
        label="디스코드 토큰 (Authorization)",
        placeholder="따옴표나 공백 없이 토큰만 정확히 입력하세요.",
        style=discord.TextStyle.paragraph,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # 3초 초과 오류(Unknown interaction) 방지를 위한 즉시 응답 처리
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        token_value = self.user_token.value.strip()

        # 기존 실행 중인 매크로가 있다면 종료
        if user_id in running_workers:
            proc = running_workers[user_id]
            if proc.poll() is None:
                proc.terminate()
            del running_workers[user_id]

        # worker.py 프로세스 비동기 실행
        try:
            process = subprocess.Popen(
                ["python3", "worker.py", token_value],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            running_workers[user_id] = process

            await interaction.followup.send(
                "✅ **매크로가 성공적으로 등록 및 실행되었습니다!**\n"
                "채팅창에 `$메크로시작 10m 1m 입력할내용` 형식으로 입력해 보세요.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ 매크로 실행 중 오류가 발생했습니다: {e}", ephemeral=True
            )


# 패널 버튼 뷰
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
        # 3초 초과 오류 방지를 위해 응답 지연 처리
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
    print(f"========================================")
    print(f"✅ 메인 관리자 봇 로그인 성공: {bot.user}")
    print(f"========================================")


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
            "   `$메크로시작 [전체시간] [반복간격] [내용]`\n"
            "   *(예시: `$메크로시작 30m 3m 안녕하세요`)*\n"
            "3. 매크로 중지: `$메크로중지` 입력 또는 패널에서 **`🛑 매크로 연결 해제`** 버튼 클릭"
        ),
        color=discord.Color.blue(),
    )
    view = MacroControlView()
    await ctx.send(embed=embed, view=view)


if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN 환경변수가 설정되지 않았습니다.")
    else:
        bot.run(TOKEN)
