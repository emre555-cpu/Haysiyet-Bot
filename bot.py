
import os
import logging
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bot")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log.info("Bot aktif: %s", bot.user)
    log.info("Sunucu sayısı: %s", len(bot.guilds))


# Yeni üye karşılama
@bot.event
async def on_member_join(member):
    kanal = discord.utils.get(
        member.guild.text_channels, name="hosgeldin"
    )
    if kanal:
        await kanal.send(
            f"Ooo {member.mention} gelmiş! 🥳 "
            "Hoş geldin kanka! Adını ve yaşını yaz, kaydını yapalım."
        )


# Selamlaşma
@bot.listen("on_message")
async def selam_cevapla(message):
    if message.author.bot or not message.guild:
        return

    metin = message.content.lower().strip()

    selamlar = {
        "sa", "s.a", "s.a.", "selam",
        "selamün aleyküm", "selamun aleykum"
    }

    if metin in selamlar:
        await message.channel.send(
            f"Aleykümselam {message.author.mention}, naber kanka? 😎"
        )


# Yardım
@bot.command(name="yardim", aliases=["yardım", "help"])
async def yardim(ctx):
    await ctx.send(
        "**Kanka Bot Komutları**\n"
        "`!ping` — Bot çalışıyor mu?\n"
        "`!kayit @üye İsim 20` — Üyeyi kaydet\n"
        "`!ekle :emoji:` — Özel emoji ekle\n"
        "`!yardim` — Komutları göster"
    )


# Bağlantı testi
@bot.command()
async def ping(ctx):
    await ctx.send(f"Bot aktif! 🟢 Gecikme: {round(bot.latency * 1000)} ms")


# Üye kayıt
@bot.command(name="kayit", aliases=["kayıt"])
@commands.guild_only()
@commands.has_permissions(manage_roles=True)
async def kayit(ctx, member: discord.Member, *, bilgi: str):
    parcalar = bilgi.rsplit(" ", 1)

    if len(parcalar) != 2 or not parcalar[1].isdigit():
        await ctx.send("Kullanım: `!kayit @üye Ahmet 20`")
        return

    isim, yas_metni = parcalar
    yas = int(yas_metni)

    if not 1 <= yas <= 99 or not isim.strip():
        await ctx.send("Geçerli bir isim ve yaş gir kanka.")
        return

    rol = discord.utils.get(ctx.guild.roles, name="Üye")
    bot_uye = ctx.guild.me

    if rol is None:
        await ctx.send("Sunucuda **Üye** rolü bulunamadı.")
        return

    if bot_uye is None or rol >= bot_uye.top_role:
        await ctx.send("Botun rolünü **Üye** rolünün üstüne taşı.")
        return

    if member.top_role >= bot_uye.top_role:
        await ctx.send("Bu üyenin rolü botun rolünden yüksek veya eşit.")
        return

    try:
        await member.edit(nick=f"{isim.strip()} | {yas}")
        await member.add_roles(rol, reason=f"Kayıt: {ctx.author}")
        await ctx.send(
            f"Tamamdır {member.mention}! **{isim.strip()} | {yas}** "
            "olarak kaydoldun. 🔥"
        )
    except discord.Forbidden:
        await ctx.send("Botun rol veya takma ad değiştirme yetkisini kontrol et.")
    except discord.HTTPException:
        await ctx.send("Kayıt sırasında Discord hatası oluştu.")


# Özel emoji ekleme
@bot.command(name="ekle")
@commands.guild_only()
@commands.has_permissions(manage_emojis_and_stickers=True)
async def ekle(ctx, emoji: discord.PartialEmoji, isim: str = None):
    if not emoji.is_custom_emoji():
        await ctx.send("Kanka, özel bir Discord emojisi göndermelisin.")
        return

    try:
        yeni = await ctx.guild.create_custom_emoji(
            name=isim or emoji.name or "yeni_emoji",
            image=await emoji.read()
        )
        await ctx.send(f"Emoji eklendi: {yeni}")
    except discord.Forbidden:
        await ctx.send("Botun emoji ekleme yetkisi yok.")
    except discord.HTTPException:
        await ctx.send("Emoji eklenemedi; sunucu sınırını kontrol et.")


# Komut hataları
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bu komut için yetkin yok kanka.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Komut eksik. `!yardim` yazarak örneklere bak.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Üyeyi etiketlediğinden ve komutu doğru yazdığından emin ol.")
    else:
        log.error("Komut hatası: %s", error)
        await ctx.send("Bir hata oluştu. Render loglarını kontrol et.")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Render Environment bölümünde DISCORD_TOKEN eksik!")
    bot.run(TOKEN)
