import discord
from discord.ext import commands
import aiohttp
import asyncio
from google import genai

# Gemini Yapay Zeka Ayarı
ai_client = genai.Client(api_key="GEMINI_API_KEY")

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
        await channel.send(f"Ooo {member.mention} gelmiş! 🎉 Hoş geldin kanka, adını yaşını yaz da kaydını yapalım.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    icerek = message.content.lower().strip()

    # 1. Ünlemsiz Doğal Selamlaşma
    if icerek in ["sa", "s.a", "s.a.", "selam", "selamun aleykum", "selamün aleyküm"] or icerek.startswith("sa "):
        await message.channel.send(f"Aleykümselam {message.author.mention}, naber la?")

    # 2. Tamamen İnsan Gibi Saran Kanka Sohbeti
    elif bot.user.mentioned_in(message):
        prompt = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
        
        if prompt:
            async with message.channel.typing():
                system_prompt = (
                    "Sen Discord sunucusunda takılan, herkesin kankası olan, samimi, "
                    "doğal ve sıcakkanlı bir insansın. Asla 'yapay zeka' veya resmi bir asistan gibi konuşma. "
                    "Klavyeden yazan normal bir genç gibi samimi, kısa-orta uzunlukta, akıcı ve sohbeti saran bir dille cevap ver. "
                    "Gereksiz uzatma, resmiyet yapma."
                )
                
                # Yoğunluk (503) Hatalarına Karşı Otomatik Deneme Sistemi
                response = None
                for _ in range(3):
                    try:
                        response = ai_client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=f"{system_prompt}\n\nKullanıcı: {prompt}"
                        )
                        if response and response.text:
                            break
                    except Exception:
                        await asyncio.sleep(1) # Hata alırsa 1 saniye bekleyip tekrar dener
                
                if response and response.text:
                    await message.reply(response.text)
                else:
                    await message.reply("Kanka sunucu şu an biraz yoğun, tekrar yazsana bi.")

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

bot.run("DISCORD_TOKEN")
