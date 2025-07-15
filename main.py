import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

data_file = "gold_data.json"
if not os.path.exists(data_file):
    with open(data_file, "w") as f:
        json.dump({}, f)

rank_thresholds = {
    "Bronz": 100,
    "Ezüst": 500,
    "Arany": 1000
}

items = {
    "vbucks500": 5000,
    "vbucks800": 8000
}

def load_data():
    with open(data_file, "r") as f:
        return json.load(f)

def save_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f)

def get_cooldown_msg(minutes):
    messages = [
        f"⏳ Nyugi, még fő a loot! Várj **{minutes} percet**.",
        f"💤 Peely pihen. Chill még **{minutes} perc**!",
        f"🛠️ Loot újratöltés. Vissza **{minutes} perc** múlva!",
        f"📦 A llama úton van. Várj **{minutes} percet**!",
        f"🚫 Spamelés = cooldown. **{minutes} perc** várás!",
        f"🥶 Lefagyott a bot. **{minutes} perc** kell neki.",
        f"🎮 Most épp szünetel a drop. **{minutes} perc** még.",
        f"🐟 Most épp üres a tó. Próbáld később (**{minutes} perc**)!",
        f"💔 Ez most nem jött össze. **{minutes} perc** pihi.",
        f"🎯 Kis cooldown, nagy loot jön. Várj **{minutes} percet**.",
    ]
    return random.choice(messages)

@bot.event
async def on_ready():
    print(f"[BOT ONLINE] Bejelentkezve mint {bot.user}")
@bot.command()
async def bal(ctx):
    user_id = str(ctx.author.id)
    data = load_data()
    gold = data.get(user_id, {}).get("gold", 0)
    await ctx.send(f"💰 {ctx.author.mention}, jelenlegi egyenleged: {gold} GOLD")

@bot.command()
async def claim(ctx):
    user_id = str(ctx.author.id)
    now = datetime.utcnow()
    data = load_data()
    user = data.get(user_id, {"gold": 0})
    last = user.get("last_claim", "1970-01-01T00:00:00")
    if now - datetime.fromisoformat(last) < timedelta(minutes=30):
        remain = int((timedelta(minutes=30) - (now - datetime.fromisoformat(last))).total_seconds() / 60)
        return await ctx.send(get_cooldown_msg(remain))
    user["last_claim"] = now.isoformat()
    amount = random.randint(10, 100)
    user["gold"] += amount
    data[user_id] = user
    save_data(data)
    await ctx.send(f"🎁 {ctx.author.mention}, szereztél {amount} GOLD-ot! 🍌")
@bot.command()
async def info(ctx):
    msg = (
        "📜 **GOLDBOT PARANCSOK** 📜\n\n"
        "**💰 Alap:**\n"
        "`!bal` – Megnézed mennyi GOLD-od van\n"
        "`!claim` – 30 percenként 10-100 GOLD\n"
        "`!daily` – Napi jutalom: 100 GOLD\n"
        "`!rank` – Jelenlegi rangod\n\n"
        "**🎲 Mini-játékok:**\n"
        "`!hunt` – Vadászat (10 perc cooldown)\n"
        "`!peca` – Horgászat (10 perc cooldown)\n"
        "`!flip [összeg] [heads/tails]` – Pénzfeldobás\n"
        "`!rob @tag` – Rablás (1 óra cooldown)\n\n"
        "**📦 Bolt & kereskedelem:**\n"
        "`!shop` – Bolt státusz (loot loading...)\n"
        "`!buy [item]` – Vásárlás pl.: vbucks500\n"
        "`!pay @tag [összeg]` – GOLD küldése másnak\n\n"
        "**🏆 Ranglisták:**\n"
        "`!top` – Top 25 játékos\n"
        "`!topgold` – Top 10 játékos\n\n"
        "🧠 Tipp: Használd ki a cooldownokat, gyűjtsd a GOLD-ot és urald a ranglistát!"
    )
    await ctx.send(msg)


@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    now = datetime.utcnow()
    data = load_data()
    user = data.get(user_id, {"gold": 0})
    last = user.get("last_daily", "1970-01-01T00:00:00")
    if now.date() == datetime.fromisoformat(last).date():
        return await ctx.send("📆 Már felvetted a napi lootodat! Gyere vissza holnap!")
    user["last_daily"] = now.isoformat()
    user["gold"] += 100
    data[user_id] = user
    save_data(data)
    await ctx.send(f"🗓️ Napi jutalom: 100 GOLD {ctx.author.mention}!")

@bot.command()
async def hunt(ctx):
    user_id = str(ctx.author.id)
    now = datetime.utcnow()
    data = load_data()
    user = data.get(user_id, {"gold": 0})
    last = user.get("last_hunt", "1970-01-01T00:00:00")
    if now - datetime.fromisoformat(last) < timedelta(minutes=10):
        remain = int((timedelta(minutes=10) - (now - datetime.fromisoformat(last))).total_seconds() / 60)
        return await ctx.send(get_cooldown_msg(remain))
    user["last_hunt"] = now.isoformat()
    amount = random.randint(20, 60)
    user["gold"] += amount
    data[user_id] = user
    save_data(data)
    await ctx.send(f"🔫 Vadászat sikeres! Loot: {amount} GOLD {ctx.author.mention}!")

@bot.command()
async def flip(ctx, amount: int, choice: str):
    user_id = str(ctx.author.id)
    data = load_data()
    user = data.get(user_id, {"gold": 0})
    if user["gold"] < amount:
        return await ctx.send("❌ Nincs elég GOLD-od!")
    if choice.lower() not in ["heads", "tails"]:
        return await ctx.send("🪙 Tippeld meg: heads vagy tails?")
    coin = random.choice(["heads", "tails"])
    if coin == choice.lower():
        user["gold"] += amount
        result = f"✅ Nyertél {amount} GOLD-ot!"
    else:
        user["gold"] -= amount
        result = f"❌ Vesztettél {amount} GOLD-ot!"
    data[user_id] = user
    save_data(data)
    await ctx.send(f"🪙 Feldobott: {coin} – {result}")

@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    sender = str(ctx.author.id)
    receiver = str(member.id)
    data = load_data()
    user = data.get(sender, {"gold": 0})
    if user["gold"] < amount:
        return await ctx.send("😬 Nincs elég GOLD-od a küldéshez!")
    user["gold"] -= amount
    target = data.get(receiver, {"gold": 0})
    target["gold"] += amount
    data[sender] = user
    data[receiver] = target
    save_data(data)
    await ctx.send(f"📤 {ctx.author.mention} küldött {amount} GOLD-ot {member.mention}-nek!")

@bot.command()
async def shop(ctx):
    shop_msgs = [
        "🛍️ A bolt még épül, mint egy új POI. Hamarosan jönnek a vbucksos cuccok!",
        "💸 A shopba épp most pakoljuk be a lootot!",
        "🎁 Türelem, jönnek a beváltható cuccok!",
        "🚧 Under construction – loot on the way!",
        "👀 A bolt hamarosan kinyit, figyeld!",
        "🥷 Peely most csempészi be a lootokat.",
        "🎮 A bolt loading... hamarosan tele lesz vbucks-szal és rangokkal!",
        "🔧 Épp reszeljük a bolt backendjét.",
        "🛠️ Dolgozunk rajta – loot jön mindjárt.",
        "📦 Nemsokára: vbucksos ajándékok és menő rangok!",
    ]
    await ctx.send(random.choice(shop_msgs))

@bot.command()
async def buy(ctx, item: str):
    user_id = str(ctx.author.id)
    data = load_data()
    user = data.get(user_id, {"gold": 0})
    if item not in items:
        return await ctx.send("❌ Nincs ilyen item a boltban!")
    if user["gold"] < items[item]:
        return await ctx.send("💸 Nincs elég GOLD-od!")
    user["gold"] -= items[item]
    data[user_id] = user
    save_data(data)
    await ctx.send(f"🎉 Megvetted: {item} – jó lootolást!")

@bot.command()
async def rank(ctx):
    user_id = str(ctx.author.id)
    data = load_data()
    gold = data.get(user_id, {}).get("gold", 0)
    current_rank = "Nincs rang"
    for rank, threshold in sorted(rank_thresholds.items(), key=lambda x: x[1]):
        if gold >= threshold:
            current_rank = rank
    await ctx.send(f"🏅 {ctx.author.mention}, jelenlegi rangod: **{current_rank}** ({gold} GOLD)")
@bot.command()
async def topgold(ctx):
    data = load_data()
    sorted_users = sorted(data.items(), key=lambda x: x[1].get("gold", 0), reverse=True)[:10]
    msg = "🏆 **Top 10 GOLD játékos:**\n"
    for i, (uid, user) in enumerate(sorted_users, 1):
        try:
            member = await bot.fetch_user(int(uid))
            msg += f"{i}. {member.name} – {user.get('gold', 0)} GOLD\n"
        except:
            continue
    await ctx.send(msg)

@bot.command()
async def top(ctx):
    data = load_data()
    sorted_users = sorted(data.items(), key=lambda x: x[1].get("gold", 0), reverse=True)[:25]
    msg = "🏆 **Top 25 GOLD játékos:**\n"
    for i, (uid, user) in enumerate(sorted_users, 1):
        try:
            member = await bot.fetch_user(int(uid))
            msg += f"{i}. {member.name} – {user.get('gold', 0)} GOLD\n"
        except:
            continue
    await ctx.send(msg)

@bot.command()
async def peca(ctx):
    user_id = str(ctx.author.id)
    now = datetime.utcnow()
    data = load_data()
    user = data.get(user_id, {"gold": 0})
    last = user.get("last_peca", "1970-01-01T00:00:00")
    if now - datetime.fromisoformat(last) < timedelta(minutes=10):
        remain = int((timedelta(minutes=10) - (now - datetime.fromisoformat(last))).total_seconds() / 60)
        return await ctx.send(get_cooldown_msg(remain))
    user["last_peca"] = now.isoformat()

    halak = ["Aranyhal", "Lazac", "Tonhal", "Jetpack rája", "Legendás Peelyhal"]
    szemetek = ["Műanyag zacskó", "Büdös rongy", "Hamis Battle Pass", "Repedt vbucks token"]

    if random.randint(1, 2) == 1:
        hal = random.choice(halak)
        nyer = random.randint(10, 250)
        user["gold"] += nyer
        msg = f"🎣 Kifogtál egy **{hal}**-t! Nyeremény: {nyer} GOLD!"
    else:
        szemet = random.choice(szemetek)
        veszteseg = random.randint(10, 200)
        user["gold"] = max(0, user["gold"] - veszteseg)
        msg = f"🗑️ Sajnos csak egy **{szemet}** akadt a horogra… és elvesztettél {veszteseg} GOLD-ot."

    data[user_id] = user
    save_data(data)
    await ctx.send(msg)

@bot.command()
async def rob(ctx, member: discord.Member):
    user_id = str(ctx.author.id)
    target_id = str(member.id)
    now = datetime.utcnow()
    data = load_data()
    user = data.get(user_id, {"gold": 0})
    target = data.get(target_id, {"gold": 0})

    last = user.get("last_rob", "1970-01-01T00:00:00")
    if now - datetime.fromisoformat(last) < timedelta(hours=1):
        remain = int((timedelta(hours=1) - (now - datetime.fromisoformat(last))).total_seconds() / 60)
        return await ctx.send(get_cooldown_msg(remain))

    user_gold = user.get("gold", 0)
    target_gold = target.get("gold", 0)
    max_rob = int(user_gold * 0.25)
    user["last_rob"] = now.isoformat()

    rob_success = [
        f"🥷 Sikeres rablás! {{user}} nem is tudta mi történt... {{amount}} GOLD már nálad van!",
        f"💰 Kirámoltad {{user}}-t mint egy afkos chestet! Zsákmány: {{amount}} GOLD.",
        f"🔫 Peely mögéd állt, te meg kifosztottad {{user}}-t! {{amount}} GOLD a jutalom!",
        f"👟 Olyan gyors voltál, hogy még a storm se kapott el! {{user}}-től szereztél {{amount}} GOLD-ot.",
        f"🎯 Tökéletes támadás! {{user}} meg se mozdult, te meg elhoztad: {{amount}} GOLD."
    ]
    rob_fail = [
        f"💀 Lebuktál, és buktál {{amount}} GOLD-ot.",
        f"🚨 {member.name} visszacsapott! Elvesztettél {{amount}} GOLD-ot.",
        f"🛑 A biztonsági rendszer kiszúrt – mínusz {{amount}} GOLD.",
        f"⚠️ Hiba a rendszerben: loot elveszett: {{amount}} GOLD.",
        f"🔥 A rablás visszanyalt – {member.name} nevet, te mínuszban: {{amount}} GOLD."
    ]

    if random.randint(1, 100) <= 25 and target_gold > 0:
        stolen = int(target_gold * 0.25)
        target["gold"] -= stolen
        user["gold"] += stolen
        msg = random.choice(rob_success).replace("{user}", member.name).replace("{amount}", str(stolen))
    else:
        loss = max(1, int(user_gold * 0.25))
        user["gold"] = max(0, user["gold"] - loss)
        msg = random.choice(rob_fail).replace("{user}", member.name).replace("{amount}", str(loss))

    data[user_id] = user
    data[target_id] = target
    save_data(data)
    await ctx.send(msg)
from keep_alive import keep_alive

keep_alive()
bot.run(TOKEN)
