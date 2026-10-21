import os
import asyncio
import aiohttp
import discord
from discord.ext import commands
from google import genai

# Çevre Değişkenlerinden (Environment Variables) Token ve Key çekme
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Yapay Zeka Ayarı (Güncel ve Kararlı Model)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

class MyBot(commands.Bot):
    async def setup_hook(self):
        self.http.connector = aiohttp.TCPConnector(ssl=False)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = MyBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'>>> {bot.user.name} kanka modunda aktif ve hazır! <<<')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="hosgeldin")
    if channel:
        await channel.send(f"Ooo {member.mention} gelmiş! 🥳 Hoş geldin kanka, adını yaşını yaz da kaydını yapalım.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    icerek = message.content.lower().strip()

    # 1. Ünlemsiz Doğal Selamlaşma
    if icerek in ["sa", "s.a", "s.a.", "selam", "selamun aleykum", "selamün aleyküm"] or icerek.startswith("sa "):
        await message.channel.send(f"Aleykümselam {message.author.mention}, naber la?")

    # 2. Tamamen İnsan Gibi Saran Kanka Sohbeti (Gemini Destekli)
    elif bot.user.mentioned_in(message):
        prompt = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        
        if prompt:
            async with message.channel.typing():
                system_prompt = (
                    "Sen Discord sunucusunda samimi, kafa, argoyu dozunda kullanan, sokak ağzıyla konuşan "
                    "genç bir mahalle kankası gibisin. 'Kanka', 'la', 'olum', 'lan', 'ya' gibi samimi kelimeler kullan. "
                    "Asla bir yapay zeka veya asistan gibi resmi konuşma! Kısa, öz ve mizahi cevaplar ver."
                )
                
                try:
                    response = ai_client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=f"{system_prompt}\nKullanıcı dedi ki: {prompt}"
                    )
                    await message.reply(response.text)
                except Exception as e:
                    await message.reply(f"Kanka bi hata çıktı ama hallederiz: {e}")

    await bot.process_commands(message)

# Kayıt Sistemi Komutu
@bot.command()
@commands.has_permissions(manage_roles=True)
async def kayit(ctx, member: discord.Member, isim: str, yas: int):
    rol_ismi = "Üye"
    rol = discord.utils.get(ctx.guild.roles, name=rol_ismi)

    if not rol:
        await ctx.send(f"Kanka sunucuda '{rol_ismi}' rolü yok, önce onu açman lazım.")
        return

    try:
        yeni_isim = f"{isim} | {yas}"
        await member.edit(nick=yeni_isim)
        await member.add_roles(rol)
        await ctx.send(f"Tamamdır, {member.mention} artık **{yeni_isim}** oldu ve rolünü kaptı! 🔥")
    except Exception as e:
        await ctx.send(f"Yetkim yetmedi kanka: {e}")

# Emoji Yükleme Komutu
@bot.command()
async def ekle(ctx, emoji: discord.PartialEmoji, name: str = None):
    if not name:
        name = emoji.name

    try:
        image_bytes = await emoji.read()
        new_emoji = await ctx.guild.create_custom_emoji(name=name, image=image_bytes)
        await ctx.send(f"Ekledim emojiyi, hayırlı olsun: {new_emoji}")
    except Exception as e:
        await ctx.send(f"Ekleyemedim kanka hata çıktı: {e}")

bot.run(DISCORD_TOKEN)
