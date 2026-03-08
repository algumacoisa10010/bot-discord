import os
import discord
from discord.ext import commands
from discord import ui, TextChannel, Color
import asyncio
import difflib
from collections import defaultdict
from datetime import datetime, timedelta

# ================= CONFIG ================= #

bot.run(os.getenv("TOKEN"))

GIF_BANNER = "https://media.discordapp.net/attachments/1479835854435520607/1480074101304463473/standard_7.gif?ex=69af02ac&is=69adb12c&hm=b45cd49a90821231861193e6bc4f161900834aadd5a651cc7c549750e136a83e&="

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=",",
    intents=intents,
    help_command=None
)

logs_config = {}

# ================= PERMISSÃO MOD ================= #

def is_moderator():
    async def predicate(ctx):
        perms = ctx.author.guild_permissions
        if perms.administrator or perms.manage_messages or perms.manage_guild:
            return True
        await ctx.send("❌ Apenas moderadores podem usar o bot.")
        return False
    return commands.check(predicate)

# ================= ANTI SPAM ================= #

spam_tracker = defaultdict(list)

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    now = datetime.now()
    spam_tracker[message.author.id].append(now)

    spam_tracker[message.author.id] = [
        t for t in spam_tracker[message.author.id]
        if now - t < timedelta(seconds=5)
    ]

    if len(spam_tracker[message.author.id]) > 5:
        try:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention} ⚠️ Pare de spammar.",
                delete_after=3
            )
        except:
            pass

    await bot.process_commands(message)

# ================= READY ================= #

@bot.event
async def on_ready():
    print(f"Bot online {bot.user}")

# ================= HELP ================= #

@bot.command()
@is_moderator()
async def help(ctx):

    embed = discord.Embed(
        title="⚙️ Painel Oficial de Moderação",
        description="Sistema avançado com proteção e controle.",
        color=0x000000
    )

    embed.set_author(
        name=bot.user.name,
        icon_url=bot.user.display_avatar.url
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_image(url=GIF_BANNER)

    embed.add_field(
        name="🔨 Moderação",
        value=(
            "`,ban @user motivo`\n"
            "`,kick @user motivo`\n"
            "`,mute @user 10m`\n"
            "`,unmute @user`\n"
            "`,clear 10`\n"
            "`,lock`\n"
            "`,unlock`"
        ),
        inline=False
    )

    embed.add_field(
        name="🛠️ Utilidades",
        value="`,msg texto` → Bot envia mensagem personalizada.",
        inline=False
    )

    embed.add_field(
        name="🧩 Sistema",
        value="Anti-Spam automático ativo.",
        inline=False
    )

    embed.set_footer(
        text="Vitrine Games BR • 2026 | Made by patrocinadobet",
        icon_url=bot.user.display_avatar.url
    )

    await ctx.send(embed=embed)

# ================= MODERAÇÃO ================= #

@bot.command()
@is_moderator()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} foi banido.")

@bot.command()
@is_moderator()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} foi expulso.")

@bot.command()
@is_moderator()
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 {amount} mensagens apagadas.")
    await asyncio.sleep(3)
    await msg.delete()

# ================= MUTE ================= #

@bot.command()
@is_moderator()
async def mute(ctx, member: discord.Member, tempo: str):

    try:
        unidade = tempo[-1]
        valor = int(tempo[:-1])
        conversao = {"s":1, "m":60, "h":3600}
        segundos = valor * conversao[unidade]
    except:
        return await ctx.send("⚠️ Use formato correto: 10s, 5m ou 1h")

    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not role:
        role = await ctx.guild.create_role(name="Muted")

        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False, speak=False)

    await member.add_roles(role)
    await ctx.send(f"🔇 {member.mention} mutado por {tempo}")

    await asyncio.sleep(segundos)

    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"🔊 {member.mention} foi desmutado.")

# ================= VOICE ================= #

@bot.command()
@is_moderator()
async def call(ctx):

    if not ctx.author.voice:
        return await ctx.send("❌ Você precisa estar em um canal de voz.")

    canal = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.disconnect()

    await canal.connect()
    await ctx.send(f"✅ Entrei no canal **{canal.name}**")

@bot.command()
@is_moderator()
async def desconect(ctx):

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Sai do canal de voz.")
    else:
        await ctx.send("❌ Não estou em nenhum canal.")

# ================= SETUP EMBED ================= #

class EmbedModal(discord.ui.Modal, title="Criar Embed"):

    titulo = discord.ui.TextInput(label="Título")
    descricao = discord.ui.TextInput(label="Descrição", style=discord.TextStyle.paragraph)
    banner = discord.ui.TextInput(label="URL do Banner")

    def __init__(self, cor):
        super().__init__()
        self.cor = cor

    async def on_submit(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title=self.titulo.value,
            description=self.descricao.value,
            color=self.cor
        )

        embed.set_image(url=self.banner.value)

        await interaction.response.send_message("✅ Embed criada!", ephemeral=True)
        await interaction.channel.send(embed=embed)

class CorSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(label="Preto", emoji="⚫", value="preto"),
            discord.SelectOption(label="Azul", emoji="🔵", value="azul"),
            discord.SelectOption(label="Verde", emoji="🟢", value="verde"),
            discord.SelectOption(label="Vermelho", emoji="🔴", value="vermelho"),
            discord.SelectOption(label="Roxo", emoji="🟣", value="roxo")
        ]

        super().__init__(placeholder="Escolha a cor da embed", options=options)

    async def callback(self, interaction: discord.Interaction):

        cores = {
            "preto": 0x000000,
            "azul": discord.Color.blue(),
            "verde": discord.Color.green(),
            "vermelho": discord.Color.red(),
            "roxo": discord.Color.purple()
        }

        await interaction.response.send_modal(
            EmbedModal(cores[self.values[0]])
        )

class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(CorSelect())

@bot.command()
@is_moderator()
async def setupembed(ctx):

    embed = discord.Embed(
        title="🛠 Criador de Embed",
        description="Selecione a cor da embed.",
        color=0x000000
    )

    await ctx.send(embed=embed, view=SetupView())

# ================= LOGS ================= #

class LogsModal(ui.Modal, title="Configurar Log"):

    titulo = ui.TextInput(label="Título")
    descricao = ui.TextInput(label="Descrição (use {user})", style=discord.TextStyle.paragraph)
    gif = ui.TextInput(label="URL do GIF")
    tipo = ui.TextInput(label="Tipo (entrada/saída)")

    def __init__(self, canal, cor):
        super().__init__()
        self.canal = canal
        self.cor = cor

    async def on_submit(self, interaction: discord.Interaction):

        logs_config[interaction.guild.id] = {
            "channel": self.canal.id,
            "color": self.cor,
            "modal_data": {
                "titulo": self.titulo.value,
                "descricao": self.descricao.value,
                "gif": self.gif.value,
                "tipo": self.tipo.value.lower()
            }
        }

        await interaction.response.send_message(
            f"✅ Logs configurados em {self.canal.mention}",
            ephemeral=True
        )

class LogsColorSelect(ui.Select):

    def __init__(self, canal):

        options = [
            discord.SelectOption(label="Preto", emoji="⚫", value="preto"),
            discord.SelectOption(label="Azul", emoji="🔵", value="azul"),
            discord.SelectOption(label="Verde", emoji="🟢", value="verde"),
            discord.SelectOption(label="Vermelho", emoji="🔴", value="vermelho"),
            discord.SelectOption(label="Roxo", emoji="🟣", value="roxo")
        ]

        super().__init__(placeholder="Escolha a cor da embed", options=options)
        self.canal = canal

    async def callback(self, interaction: discord.Interaction):

        cores = {
            "preto": 0x000000,
            "azul": Color.blue(),
            "verde": Color.green(),
            "vermelho": Color.red(),
            "roxo": Color.purple()
        }

        await interaction.response.send_modal(
            LogsModal(self.canal, cores[self.values[0]])
        )

class SetupLogsView(ui.View):

    def __init__(self, canal):
        super().__init__(timeout=60)
        self.add_item(LogsColorSelect(canal))

@bot.command()
@is_moderator()
async def setuplogs(ctx):

    await ctx.send("📌 Envie a menção do canal onde os logs vão aparecer.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    msg = await bot.wait_for("message", check=check)

    canal_id = int(msg.content.strip("<#>"))
    canal = ctx.guild.get_channel(canal_id)

    await ctx.send(
        "Escolha a cor da embed:",
        view=SetupLogsView(canal)
    )

# ================= EVENTOS LOG ================= #

@bot.event
async def on_member_join(member):

    if member.guild.id not in logs_config:
        return

    cfg = logs_config[member.guild.id]
    canal = member.guild.get_channel(cfg["channel"])

    data = cfg["modal_data"]

    desc = data["descricao"].replace("{user}", member.mention)

    embed = discord.Embed(
        title=data["titulo"],
        description=desc,
        color=cfg["color"],
        timestamp=datetime.utcnow()
    )

    embed.set_author(name=str(member), icon_url=member.display_avatar.url)
    embed.set_image(url=data["gif"])

    if data["tipo"] == "entrada":
        await canal.send(embed=embed)

@bot.event
async def on_member_remove(member):

    if member.guild.id not in logs_config:
        return

    cfg = logs_config[member.guild.id]
    canal = member.guild.get_channel(cfg["channel"])

    data = cfg["modal_data"]

    desc = data["descricao"].replace("{user}", member.mention)

    embed = discord.Embed(
        title=data["titulo"],
        description=desc,
        color=cfg["color"],
        timestamp=datetime.utcnow()
    )

    embed.set_author(name=str(member), icon_url=member.display_avatar.url)
    embed.set_image(url=data["gif"])

    if data["tipo"] == "saída":
        await canal.send(embed=embed)


# ================= TESTLOG ================= #

@bot.command()
@is_moderator()
async def testlog(ctx, tipo: str = "entrada"):

    guild_id = ctx.guild.id

    if guild_id not in logs_config:
        return await ctx.send("❌ Logs ainda não configurados. Use `,setuplogs` primeiro.")

    cfg = logs_config[guild_id]
    canal = ctx.guild.get_channel(cfg["channel"])

    if not canal:
        return await ctx.send("❌ Canal de logs não encontrado.")

    data = cfg["modal_data"]

    descricao = data["descricao"].replace("{user}", ctx.author.mention)

    embed = discord.Embed(
        title=data["titulo"],
        description=descricao,
        color=cfg["color"],
        timestamp=datetime.utcnow()
    )

    embed.set_author(
        name=str(ctx.author),
        icon_url=ctx.author.display_avatar.url
    )

    embed.set_image(url=data["gif"])

    await canal.send(embed=embed)

    await ctx.send(f"✅ Mensagem de teste enviada em {canal.mention}")
