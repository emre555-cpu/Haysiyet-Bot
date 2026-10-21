
import os
import logging
import discord
from discord.ext import commands
from google import genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kankabot")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
ai_client = None


@bot.event
async def on_ready():
    global ai_client

    if GEMINI_API_KEY and ai_client is None:
        ai_client = genai.Client(api_key=GEMINI_API_KEY)

    print(f">>> {bot.user} kanka modunda aktif! <<<")


@bot.event
async def on_member_join(member):
    channel = discord.utils.get(
        member.guild.text_channels, name="hosgeldin"
    )

    if channel:
        await channel.send(
            f"Ooo {member.mention} gelmiş! 🥳 "
            "Hoş geldin kanka, adını yaşını yaz da kaydını yapalım."
        )


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    icerik = message.content.lower().strip()

    selamlar = [
        "sa", "s.a", "s.a.", "selam",
        "selamun aleykum", "selamün aleyküm"
    ]

    if icerik in selamlar or icerik.startswith("sa "):
        await message.channel.send(
            f"Aleykümselam {message.author.mention}, naber la?"
        )

    elif bot.user and bot.user.mentioned_in(message):
        prompt = message.content
        prompt = prompt.replace(f"<@{bot.user.id}>", "")
        prompt = prompt.replace(f"<@!{bot.user.id}>", "")
        prompt = prompt.strip()

        if prompt:
            if not ai_client:
                await message.reply(
                    "Kanka Gemini API Key ayarlanmamış, sahibime söyle!"
                )
            else:
                system_prompt = (
                    "Sen Discord'da samimi, mizahi, genç bir kankasın. "
                    "Kanka, la, olum gibi kelimeleri dozunda kullan. "
                    "Doğal, kısa ve konuya uygun cevap ver. "
                    "Gereksiz resmiyetten ve uzun açıklamalardan kaçın."
                )

                try:
                    async with message.channel.typing():
                        response = await (
                            ai_client.aio.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=(
                                    f"{system_prompt}\n"
                                    f"Kullanıcı dedi ki: {prompt}"
                                )
                            )
                        )

                    cevap = response.text
                    if cevap:
                        await message.reply(cevap[:2000])
                    else:
                        await message.reply(
                            "Kanka bu sefer cevap çıkaramadım, bi daha dene."
                        )

                except Exception:
                    logger.exception("Gemini yanıt hatası")
                    await message.reply(
                        "Kanka cevap verirken bir sorun çıktı, birazdan dene."
                    )

    await bot.process_commands(message)


@bot.command()
@commands.has_permissions(manage_roles=True)
async def kayit(ctx, member: discord.Member, isim: str, yas: int):
    if not 1 <= yas <= 99:
        await ctx.send("Kanka, geçerli bir yaş gir.")
        return

    rol = discord.utils.get(ctx.guild.roles, name="Üye")

    if not rol:
        await ctx.send("Kanka, sunucuda 'Üye' rolü bulunamadı.")
        return

    if rol >= ctx.guild.me.top_role:
        await ctx.send(
            "Kanka, botun rolünü sunucu ayarlarından 'Üye' rolünün "
            "üstüne taşıman lazım."
        )
        return

    if member.top_role >= ctx.guild.me.top_role:
        await ctx.send("Bu üyenin rolü botun rolüne eşit veya daha yüksek.")
        return

    try:
        yeni_isim = f"{isim} | {yas}"
        await member.add_roles(rol, reason=f"Kayıt: {ctx.author}")
        await member.edit(nick=yeni_isim)
        await ctx.send(
            f"Tamamdır {member.mention}! İsmin **{yeni_isim}** oldu "
            "ve Üye rolünü aldın. 🔥"
        )
    except discord.Forbidden:
        await ctx.send(
            "Botun yetkisi yetersiz. Rol sırasını ve izinlerini kontrol et."
        )
    except discord.HTTPException:
        await ctx.send("Kanka, işlem tamamlanamadı. Tekrar dene.")


@bot.command()
@commands.has_permissions(manage_emojis_and_stickers=True)
async def ekle(ctx, emoji: discord.PartialEmoji, name: str = None):
    if not ctx.guild:
        return

    if not emoji.is_custom_emoji():
        await ctx.send("Kanka, özel bir Discord emojisi göndermen lazım.")
        return

    emoji_adi = name or emoji.name or "yeni_emoji"

    try:
        image_bytes = await emoji.read()
        yeni_emoji = await ctx.guild.create_custom_emoji(
            name=emoji_adi,
            image=image_bytes
        )
        await ctx.send(f"Ekledim emojiyi, hayırlı olsun: {yeni_emoji}")

    except discord.Forbidden:
        await ctx.send(
            "Botun emoji ekleme yetkisi yok kanka."
        )
    except discord.HTTPException:
        await ctx.send(
            "Emoji eklenemedi. Emoji sınırını ve adını kontrol et."
        )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Kanka, bu komut için yetkin yok.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "Komut eksik kanka. Örnek: `!kayit @üye Ahmet 20`"
        )
    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "Kullanım hatalı. Örnek: `!kayit @üye Ahmet 20`"
        )
    else:
        logger.error("Komut hatası: %s", error)
        await ctx.send("Komut çalışırken bir hata oluştu.")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError(
            "DISCORD_TOKEN çevre değişkeni bulunamadı!"
        )

    bot.run(DISCORD_TOKEN)
