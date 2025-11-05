import logging
from aiogram import Bot, Dispatcher, types, executor
import aiosqlite

API_TOKEN = "8452694935:AAEkdibaq00y1Tc9070WB4DK4rHvFm8M1Fc"
ADMIN_ID = 1182191962

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def init_db():
    async with aiosqlite.connect("tillaabi.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS settings (gold_price REAL)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)""")
        cur = await db.execute("SELECT COUNT(*) FROM settings")
        count = (await cur.fetchone())[0]
        if count == 0:
            await db.execute("INSERT INTO settings (gold_price) VALUES (985000)")
        await db.commit()

async def get_gold_price():
    async with aiosqlite.connect("tillaabi.db") as db:
        cur = await db.execute("SELECT gold_price FROM settings LIMIT 1")
        price = await cur.fetchone()
        return price[0] if price else 0

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    async with aiosqlite.connect("tillaabi.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
        await db.commit()
    await message.answer(
        "👋 Assalomu alaykum! Bu *Tilla Abi* bot.\n\n"
        "💰 Rasm yuboring — biz sizga taxminiy qiymatini aytamiz.\n"
        "📏 Siz shuningdek vazn va proba ma’lumotlarini ham kiritishingiz mumkin.",
        parse_mode="Markdown"
    )

@dp.message_handler(content_types=['photo'])
async def photo_handler(message: types.Message):
    await message.reply("📸 Rasm qabul qilindi!\n\nEndi oltinning *vaznini (grammda)* kiriting:", parse_mode="Markdown")
    await message.photo[-1].download(f"user_{message.from_user.id}.jpg")

@dp.message_handler(lambda msg: msg.text.isdigit())
async def weight_input(message: types.Message):
    gold_price = await get_gold_price()
    weight = float(message.text)
    approx_value = gold_price * weight
    await message.answer(
        f"💎 Sizning oltiningiz taxminiy qiymati:\n\n"
        f"⚖️ Vazn: {weight} g\n"
        f"💰 Narx: {approx_value:,.0f} so‘m\n\n"
        f"Agar bu sizga maqul bo‘lsa, admin bilan bog‘lanish uchun telefon raqamingizni yuboring."
    )

@dp.message_handler(commands=['setprice'])
async def set_price_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Sizda bu buyruqdan foydalanish huquqi yo‘q.")
        return
    args = message.get_args()
    if not args:
        await message.answer("📏 Narxni o‘rnatish uchun: /setprice [yangi_narx]")
        return
    try:
        new_price = float(args)
        async with aiosqlite.connect("tillaabi.db") as db:
            await db.execute("UPDATE settings SET gold_price = ?", (new_price,))
            await db.commit()
        await message.answer(f"✅ Narx yangilandi: {new_price} so‘m/g")
    except ValueError:
        await message.answer("❌ Noto‘g‘ri format! Misol: /setprice 985000")

@dp.message_handler(commands=['getprice'])
async def get_price_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    price = await get_gold_price()
    await message.answer(f"💰 Hozirgi narx: {price} so‘m/g")

async def on_startup(_):
    await init_db()
    print("✅ Tilla Abi bot ishga tushdi!")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)


