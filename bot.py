import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# ================== SOZLAMALAR ==================
BOT_TOKEN = "8693133281:AAEd-R7CYzf2eBy4iF_XJ2E8RceYR9sH0EU"
ADMIN_ID = 7904589263  # <-- O'Z TELEGRAM IDINGIZ

KARTA_RAQAM = "5614688701023433"
KARTA_NOMI = "RUXSHONA RO'ZIBOYEVA"

# Kanal chat IDlari (maxfiy kanallar uchun -100 bilan boshlanadi)
AI_MASTER_CHAT_ID = -1003739282791
DASTURLASH_CHAT_ID = -1003867021251
KOMPYUTER_CHAT_ID = -1003738869557
KEAJ_1_2_CHAT_ID = -1003542192299  # Kelajak yoshlari 1-2 sinflar
KEAJ_3_4_CHAT_ID =  -1003752565500  # Kelajak yoshlari 3-4 sinflar

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================== FOYDALANUVCHI VA OBUNA ==================
users = {}  # Foydalanuvchi ma'lumotlari
channels = {
    "ai_master": {"name": "🤖 AI Master", "chat_id": AI_MASTER_CHAT_ID},
    "dasturlash": {"name": "💻 Dasturlashni 0 dan o'rganamiz", "chat_id": DASTURLASH_CHAT_ID},
    "kompyuter": {"name": "🖥 Kompyuter asoslari", "chat_id": KOMPYUTER_CHAT_ID},
    "kelajak_1_2": {"name": "👶 Kelajak yoshlari 1-2 sinflar", "chat_id": KEAJ_1_2_CHAT_ID},
    "kelajak_3_4": {"name": "🧒 Kelajak yoshlari 3-4 sinflar", "chat_id": KEAJ_3_4_CHAT_ID}
}

# Obuna narxlari
subscriptions = {
    "1_oy": ("1 oy", 150000, 30),
    "3_oy": ("3 oy", 400000, 90),
    "6_oy": ("6 oy", 800000, 180),
    "1_yil": ("1 yil", 1000000, 365),
    "1_oy_kelajak": ("1 oy", 200000, 30),
    "4_oy_kelajak": ("4 oy", 750000, 120)
}

# ================== VIKTORINA SAVOLLARI ==================
quiz_data = {
    "ai_master": {
        0: [
            {"question": "AI nima?", "options": ["Sun'iy intellekt", "Internet", "Kompyuter", "Robot"], "correct": 0},
            {"question": "ChatGPT qaysi kompaniya tomonidan yaratildi?", "options": ["OpenAI", "Google", "Microsoft", "Apple"], "correct": 0},
        ]
    },
    "dasturlash": {
        0: [
            {"question": "HTML nima?", "options": ["Dasturlash tili", "MarkUp tili", "Grafik dastur", "Video format"], "correct": 1},
            {"question": "Python qaysi tipga kiradi?", "options": ["Yuqori darajali", "Past darajali", "Assembler", "SQL"], "correct": 0},
        ]
    },
    "kompyuter": {
        0: [
            {"question": "RAM nima?", "options": ["Xotira", "Qattiq disk", "Monitor", "Protsessor"], "correct": 0},
            {"question": "CPU qaysi qismini bildiradi?", "options": ["Markaziy protsessor", "Xotira", "Grafik karta", "Tarmoq"], "correct": 0},
        ]
    },
    "kelajak_1_2": {
        0: [
            {"question": "Matematika: 2+3=?", "options": ["4", "5", "6", "3"], "correct": 1},
            {"question": "Ona tili: 'Salom' so'zi qaysi tilga tegishli?", "options": ["Ingliz", "O'zbek", "Rus", "Fransuz"], "correct": 1},
            {"question": "O‘qish: So'z qayerda ishlatiladi?", "options": ["Darsda", "O'yinda", "Uyda", "Kitobda"], "correct": 3},
            {"question": "Rustili: 'print' bu nima?", "options": ["Matematika", "Kod", "O'qish", "Ovqat"], "correct": 1},
        ]
    },
    "kelajak_3_4": {
        0: [
            {"question": "Matematika: 12-5=?", "options": ["7", "8", "6", "5"], "correct": 0},
            {"question": "Ona tili: 'Kitob' so'zi qaysi tilga tegishli?", "options": ["Ingliz", "O'zbek", "Rus", "Fransuz"], "correct": 1},
            {"question": "O‘qish: Asar qayerda ishlatiladi?", "options": ["Darsda", "Kitobda", "O'yinda", "Uyda"], "correct": 1},
            {"question": "Rustili: 'let x = 5;' bu qaysi amaliyot?", "options": ["O'zgaruvchi yaratish", "Chop etish", "Shart", "Funktsiya"], "correct": 0},
        ]
    }
}

# ================== START ==================
@dp.message(Command("start"))
async def start(message: types.Message):
    text = """
Assalomu alaykum 👋
TechMasterBot ga xush kelibsiz!

Bu bot orqali siz o‘zingizni qiziqtirgan sohada bilim olishingiz va bilimlaringizni mustahkamlashingiz mumkin.
"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=channels[key]["name"], callback_data=f"channel_{key}")]
            for key in channels
        ]
    )
    await message.answer(text, reply_markup=keyboard)

# ================== KANAL TANLASH ==================
@dp.callback_query(lambda c: c.data.startswith("channel_"))
async def choose_channel(callback: types.CallbackQuery):
    key = callback.data.replace("channel_", "")
    users[callback.from_user.id] = {"channel": key}

    # Tugmalar
    if key in ["kelajak_1_2", "kelajak_3_4"]:
        sub_keys = ["1_oy_kelajak", "4_oy_kelajak"]
    else:
        sub_keys = ["1_oy", "3_oy", "6_oy", "1_yil"]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{subscriptions[s][0]} - {subscriptions[s][1]} so'm", callback_data=f"sub_{s}")]
            for s in sub_keys
        ]
    )

    # Info matn
    info_text = f"""
Siz {channels[key]['name']} kanalini tanladingiz ✅

📚 Kanal haqida ma’lumot:
- Har 10 kunda **test / viktorina** bo‘ladi.
- Testdan muvaffaqiyatli o'tgan o‘quvchilar kanalga qoladi va **bonuslar, sovg‘alar** qo‘lga kiritishadi.
- Agar testdan o'tolmasangiz, kanalni davom ettirish uchun **jarima** mavjud: 
  - Kursdan chiqmaslik uchun **20 000 so‘m** to‘lashingiz kerak.

📝 Foydalanuvchilar uchun qoidalar:
- Testlar har 10 kunda bo‘ladi.
- Testni muvaffaqiyatli topshirish bonuslar va sovg‘alarni olishingizga imkon beradi.
- Jarima to‘lansa, kanalga qolishingiz mumkin va bilimlarni davom ettirasiz.
- Bu tizim barcha kanallar uchun umumiy: AI Master, Dasturlash, Kompyuter asoslari, Kelajak yoshlari 1-2, Kelajak yoshlari 3-4.

Shuni yodda tuting va bilimlaringizni sinab boring! 🎓
"""

    # Shu yerda await ishlaydi, chunki async funksiya ichida
    await callback.message.answer(info_text, reply_markup=keyboard)
# ================== OBUNA TANLASH ==================
@dp.callback_query(lambda c: c.data.startswith("sub_"))
async def choose_sub(callback: types.CallbackQuery):
    sub_key = callback.data.replace("sub_", "")
    users[callback.from_user.id]["subscription"] = sub_key

    text = "⚠️ Muhim!Siz obuna bo'lgan sanadan boshlab har 10 kunda viktorina bo‘ladi va siz shu viktorinadan o'tsangiz sizga bonuslar beriladi, agar o'ta olmasangiz siz bilan tuzgan shartnomamiz o'z nihoyasiga yetadi. Afsus, kanalda qolish uchun jarima narxini to'lashga majbur bo'lasiz (15 ming). Rozimisiz?"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✅ Roziman", callback_data="agree")]]
    )
    await callback.message.answer(text, reply_markup=keyboard)

# ================== ROZILIK ==================
@dp.callback_query(lambda c: c.data == "agree")
async def agree(callback: types.CallbackQuery):
    text = f"💳 Karta raqam: {KARTA_RAQAM}\n👤 Karta nomi: {KARTA_NOMI}\nTo‘lov qilgach chek yuboring."
    await callback.message.answer(text)

# ================== CHEK QABUL QILISH ==================
@dp.message(lambda message: message.photo)
async def receive_check(message: types.Message):
    user_id = message.from_user.id
    user_data = users.get(user_id, {})
    sub_key = user_data.get("subscription")
    sub_text = subscriptions[sub_key][0] if sub_key else "Obuna turi tanlanmagan"

    forwarded = await message.forward(ADMIN_ID)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=f"✅ Tasdiqlash ({user_id})", callback_data=f"approve_check_{user_id}"),
            InlineKeyboardButton(text=f"❌ Rad etish ({user_id})", callback_data=f"reject_check_{user_id}")
        ]]
    )

    await bot.send_message(ADMIN_ID,
        f"Foydalanuvchi chek yubordi.\n📌 Obuna turi: {sub_text}\nFoydalanuvchi ID: {user_id}",
        reply_markup=keyboard
    )
    await message.answer("Chekingiz qabul qilindi ✅ Chek tastiqlanishi 1-2 soat vaqt olishi mumkin.")

# ================== ADMIN CHEK TASDIQLASH ==================
@dp.callback_query(lambda c: c.data.startswith("approve_check_"))
async def admin_approve_check(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz ❌", show_alert=True)
        return
    user_id = int(callback.data.split("_")[-1])
    if user_id not in users:
        await callback.answer("Foydalanuvchi topilmadi ❌", show_alert=True)
        return
    channel_key = users[user_id]["channel"]
    sub_key = users[user_id]["subscription"]
    days = subscriptions[sub_key][2]
    expire_date = datetime.now() + timedelta(days=days)
    users[user_id]["expire"] = expire_date
    users[user_id]["progress"] = 0
    invite = await bot.create_chat_invite_link(chat_id=channels[channel_key]["chat_id"], member_limit=1)
    await bot.send_message(user_id, f"✅ To‘lov tasdiqlandi!\nKanalga kirish: {invite.invite_link}\nObuna muddati: {subscriptions[sub_key][0]}")
    await callback.message.edit_text(f"Chek tasdiqlandi ✅ (Foydalanuvchi: {user_id})")
    await callback.answer("Foydalanuvchi kanalga qo‘shildi ✅", show_alert=True)

# ================== ADMIN RAD ETISH ==================
@dp.callback_query(lambda c: c.data.startswith("reject_check_"))
async def admin_reject_check(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz ❌", show_alert=True)
        return
    user_id = int(callback.data.split("_")[-1])
    await callback.message.answer("Foydalanuvchi uchun rad etish sababi yozing:")

    @dp.message(lambda m: True)
    async def send_rejection_reason(message: types.Message):
        await bot.send_message(user_id, f"⚠️ Sizning chekingiz rad etildi.\nSabab: {message.text}")
        await message.answer("Rad etish xabari foydalanuvchiga yuborildi ✅")
        dp.message.outer_handlers.remove(send_rejection_reason)

# ================== 30 KUNLIK ESLATMA ==================
async def subscription_reminder():
    while True:
        await asyncio.sleep(3600)
        now = datetime.now()
        for user_id, data in users.items():
            if "expire" in data:
                days_left = (data["expire"] - now).days
                if days_left == 0 and not data.get("reminder_sent", False):
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[[
                            InlineKeyboardButton(text="📨 Foydalanuvchiga xabar yuborish",
                                                 callback_data=f"notify_user_{user_id}")
                        ]]
                    )
                    await bot.send_message(ADMIN_ID,
                        f"Foydalanuvchi {user_id} obunasi 30 kunlik muddatini tugatmoqda. 24 soat ichida xabar yuborishingiz mumkin.",
                        reply_markup=keyboard
                    )
                    data["reminder_sent"] = True

@dp.callback_query(lambda c: c.data.startswith("notify_user_"))
async def notify_user(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz ❌", show_alert=True)
        return
    user_id = int(callback.data.split("_")[-1])
    await callback.message.answer("Foydalanuvchiga xabar yuborish matnini yozing (24 soat ichida):")
    start_time = datetime.now()

    @dp.message(lambda m: True)
    async def send_reminder_message(message: types.Message):
        nonlocal start_time
        if datetime.now() > start_time + timedelta(hours=24):
            await message.answer("⏳ 24 soat ichida xabar yuborish muddati tugadi.")
        else:
            await bot.send_message(user_id, f"📢 Admindan xabar: {message.text}")
            await message.answer("Xabar foydalanuvchiga yuborildi ✅")
        dp.message.outer_handlers.remove(send_reminder_message)

# ================== RUN ==================
async def main():
    asyncio.create_task(subscription_reminder())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
