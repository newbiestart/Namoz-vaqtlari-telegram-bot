#!/usr/bin/env python3
"""
Namaz Vaqtlari Telegram Bot
Bitta faylga birlashtirilgan versiya.
Webhook ishlatmaydi, polling ishlatadi.
Majburiy kanal obunasini talab qiladi.
"""

import logging
import requests
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters,
    ContextTypes,
    ConversationHandler
)
from telegram.constants import ParseMode

# --- Konfiguratsiya ---
# O'zgartiring: BotFather dan olgan tokeningizni shu yerga kiriting
BOT_TOKEN = ""
# O'zgartiring: Majburiy obuna qilinishi kerak bo'lgan kanal username'si
CHANNEL_ID = ""
# O'zgartiring: Adminingizning Telegram ID'sini kiriting
ADMIN_ID = 

# API konfiguratsiyasi
PRAYER_API_BASE_URL = "https://islomapi.uz/api"

# Xabarlarni sozlash (Uzbek tilida)
MESSAGES = {
    'welcome': """🕌 Assalomu alaykum!
Namoz vaqtlarini bilish uchun botga xush kelibsiz!
Botdan foydalanish uchun quyidagi kanalga obuna bo'ling:
{channel}
Keyin ✅ 'Obuna bo'ldim' tugmasini bosing.
""",
    'subscription_confirmed': "✅ Obuna tekshirildi! Endi quyidagi tugmani bosing:",
    'subscription_not_confirmed': """❌ Siz hali ham kanalga obuna bo'lmagansiz!
Iltimos, avval quyidagi kanalga obuna bo'ling:
{channel}
Keyin qaytadan 'Obuna bo'ldim' tugmasini bosing.
""",
    'main_menu': """🕌 Assalomu alaykum!
Namoz vaqtlarini bilish uchun botga xush kelibsiz!
Quyidagi tugmani bosing:""",
    'select_region': "🗺 Viloyatingizni tanlang:",
    'select_city': "🏘 Shahar/tumanni tanlang:",
    'prayer_times_title': "🕌 Bugungi namoz vaqtlari",
    'error_api': "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
    'error_no_data': "❌ Tanlangan hudud uchun ma'lumot topilmadi.",
    'back_to_regions': "⬅️ Viloyatlarga qaytish",
    'back_to_cities': "⬅️ Shaharlarga qaytish"
}

# Namoz vaqtlari nomlari (API kalitlari bilan moslashtirilgan)
PRAYER_NAMES = {
    'times': [
        ('Bomdod', 'tong_saharlik'),
        ('Quyosh', 'quyosh'),
        ('Peshin', 'peshin'),
        ('Asr', 'asr'),
        ('Shom', 'shom_iftor'),
        ('Xufton', 'hufton')
    ]
}

# Barcha mintaqalar (shaharlar/viloyatlar)
# Ma'lumotlarni tashqi fayldan emas, kod ichidan olamiz
REGIONS_BY_PROVINCE = {
    "Toshkent viloyati": [
        "Toshkent", "Bekobod", "Angren", "Guliston", "Arnasoy"
    ],
    "Samarqand viloyati": [
        "Samarqand", "Urgut", "Kattaqo'rg'on", "Jambay", "Zomin"
    ],
    "Farg'ona viloyati": [
        "Farg'ona", "Qo'qon", "Marg'ilon", "Rishton", "Quva", "Uchqo'rg'on"
    ],
    "Andijon viloyati": [
        "Andijon", "Xo'jaobod", "Oltiariq", "Buloqboshi", "Paxtaobod"
    ],
    "Namangan viloyati": [
        "Namangan", "Kosonsoy", "Pop", "Chust", "Mingbuloq"
    ],
    "Qashqadaryo viloyati": [
        "Qarshi", "Shahrisabz", "G'uzor", "Koson", "Tallimarjon"
    ],
    "Surxondaryo viloyati": [
        "Termiz", "Denov", "Sherobod", "Boysun", "Dehqonobod"
    ],
    "Buxoro viloyati": [
        "Buxoro", "G'allaorol", "Olot", "Jondor", "Qorako'l"
    ],
    "Navoiy viloyati": [
        "Navoiy", "Zarafshon", "Uchquduq", "Nurota", "Konimex"
    ],
    "Jizzax viloyati": [
        "Jizzax", "Zomin", "G'allaorol", "Do'stlik", "Yangiobod" # Yangibozor -> Yangiobod
    ],
    "Xorazm viloyati": [
        "Urganch", "Xiva", "Hazrasp", "Shovot", "Qo'ng'irot"
    ],
    "Qoraqalpog'iston": [
        "Nukus", "Chimboy", "Mo'ynoq", "Chortoq", "Taxtakopir", "Turtkol"
    ]
}

# Holatlar
CHECK_SUBSCRIPTION, MAIN_MENU = range(2)

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Yordamchi funksiyalar ---

def get_all_regions():
    """Barcha mintaqalarni tekis ro'yxat sifatida olish"""
    all_regions = []
    for province_regions in REGIONS_BY_PROVINCE.values():
        all_regions.extend(province_regions)
    return all_regions

def get_province_by_region(region_name):
    """Mintaqa nomi bo'yicha viloyatni topish"""
    for province, regions in REGIONS_BY_PROVINCE.items():
        if region_name in regions:
            return province
    return None

def get_regions_by_province(province_name):
    """Viloyat nomi bo'yicha mintaqalar ro'yxatini olish"""
    return REGIONS_BY_PROVINCE.get(province_name, [])

def get_main_keyboard():
    """Asosiy klaviatura tugmachalarini olish"""
    keyboard = [["🕌 Namoz vaqtlari"]]
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        one_time_keyboard=False
    )

# --- PrayerTimesAPI sinfi (ichki) ---
class PrayerTimesAPI:
    """Namoz vaqtlari API bilan integratsiya qilish uchun sinf"""

    def __init__(self, base_url):
        self.base_url = base_url

    def get_daily_prayer_times(self, region):
        """
        Tanlangan mintaqaga oid bugungi namoz vaqtlarini olish.
        Args:
            region (str): Mintaqa nomi.
        Returns:
            dict: Namoz vaqtlari ma'lumotlari yoki xato yuz berganda None.
        """
        try:
            url = f"{self.base_url}/present/day"
            params = {'region': region}
            logger.info(f"Mintaqa uchun namoz vaqtlari olinmoqda: {region}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if not data:
                logger.warning(f"Mintaqa uchun ma'lumot topilmadi: {region}")
                return None
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"API so'rovi xatosi, mintaqasi {region}: {e}")
            return None
        except ValueError as e:
            logger.error(f"JSON ajratish xatosi, mintaqasi {region}: {e}")
            return None
        except Exception as e:
            logger.error(f"Kutilmagan xato, mintaqasi {region}: {e}")
            return None

    def format_prayer_times(self, prayer_data, region):
        """
        Namoz vaqtlari ma'lumotlarini o'qishga qulay formatga keltirish.
        Args:
            prayer_data (dict): Xom namoz vaqtlari ma'lumotlari.
            region (str): Mintaqa nomi.
        Returns:
            str: Formatlangan namoz vaqtlari xabari.
        """
        try:
            if not prayer_data:
                return "❌ Ma'lumot topilmadi"

            # Joriy sana
            today = datetime.now().strftime("%d.%m.%Y")
            message = f"🕌 *{region}* - {today}\n"

            # Har bir namoz vaqtini formatlash
            times_data = prayer_data.get('times', {})
            for uzbek_name, api_key in PRAYER_NAMES['times']:
                if api_key in times_data:
                    time_str = times_data[api_key]
                    message += f"🕐 *{uzbek_name}:* `{time_str}`\n"

            # Hijriy sanani qo'shish
            hijri_data = prayer_data.get('hijri_date', {})
            if isinstance(hijri_data, dict):
                hijri_text = f"{hijri_data.get('day', '')} {hijri_data.get('month', '')}"
                message += f"\n📅 Hijriy sana: {hijri_text.strip()}"
            else:
                message += f"\n📅 Hijriy sana: Noma'lum"
            return message
        except Exception as e:
            logger.error(f"Namoz vaqtlarini formatlashda xato: {e}")
            return "❌ Ma'lumotni formatlashda xatolik"

    def get_formatted_prayer_times(self, region):
        """
        Mintaqa uchun namoz vaqtlarini olish va formatlash.
        Args:
            region (str): Mintaqa nomi.
        Returns:
            str: Formatlangan namoz vaqtlari xabari.
        """
        prayer_data = self.get_daily_prayer_times(region)
        return self.format_prayer_times(prayer_data, region)

# Global PrayerTimesAPI nusxasi
prayer_api = PrayerTimesAPI(PRAYER_API_BASE_URL)

# --- Bot Handlerlari ---

async def check_subscription(user_id, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchining kanalga obuna bo'lganligini tekshirish"""
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Obuna tekshirishda xato: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Boshlash komandasi (/start)"""
    user_id = update.effective_user.id
    is_subscribed = await check_subscription(user_id, context)

    if not is_subscribed:
        keyboard = [[InlineKeyboardButton("✅ Obuna bo'ldim", callback_data="check_sub")]]
        await update.message.reply_text(
            MESSAGES['welcome'].format(channel=CHANNEL_ID),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHECK_SUBSCRIPTION
    else:
        # Obuna bo'lgan bo'lsa, asosiy menyuni ko'rsatamiz
        keyboard = [["🕌 Namoz vaqtlari"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text(MESSAGES['main_menu'], reply_markup=reply_markup)
        return MAIN_MENU

async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"Obuna bo'ldim" tugmasi bosilganda obunani qayta tekshirish"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    is_subscribed = await check_subscription(user_id, context)

    if is_subscribed:
        await query.edit_message_text(MESSAGES['subscription_confirmed'])
        # Asosiy menyuni ko'rsatish
        keyboard = [["🕌 Namoz vaqtlari"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        # Yangi xabar yuborish
        await query.message.reply_text(MESSAGES['main_menu'], reply_markup=reply_markup)
        return MAIN_MENU
    else:
        keyboard = [[InlineKeyboardButton("✅ Obuna bo'ldim", callback_data="check_sub")]]
        # Yangi xabar yuborish
        await query.message.reply_text(
            MESSAGES['subscription_not_confirmed'].format(channel=CHANNEL_ID),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHECK_SUBSCRIPTION

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Matnli xabarlarni qayta ishlash"""
    try:
        text = update.message.text
        if text == "🕌 Namoz vaqtlari":
            await show_regions(update, context)
        else:
            # Noma'lum xabar
            await update.message.reply_text(
                "Iltimos, tugmalardan foydalaning.",
                reply_markup=get_main_keyboard()
            )
    except Exception as e:
        logger.error(f"Xabar handlerida xato: {e}")
        await update.message.reply_text(MESSAGES['error_api'])

async def show_regions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Viloyatlarni tanlash uchun klaviaturani ko'rsatish"""
    try:
        keyboard = []
        provinces = list(REGIONS_BY_PROVINCE.keys())
        # 2 ustunli tartib
        for i in range(0, len(provinces), 2):
            row = []
            row.append(InlineKeyboardButton(
                provinces[i], 
                callback_data=f"province:{provinces[i]}"
            ))
            if i + 1 < len(provinces):
                row.append(InlineKeyboardButton(
                    provinces[i + 1], 
                    callback_data=f"province:{provinces[i + 1]}"
                ))
            keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            MESSAGES['select_region'],
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Viloyatlarni ko'rsatishda xato: {e}")
        await update.message.reply_text(MESSAGES['error_api'])

async def show_cities(update: Update, context: ContextTypes.DEFAULT_TYPE, province: str):
    """Viloyat uchun shaharlarni tanlash klaviaturasini ko'rsatish"""
    try:
        cities = get_regions_by_province(province)
        if not cities:
            await update.callback_query.answer("Bu viloyat uchun shaharlar topilmadi")
            return

        keyboard = []
        # 2 ustunli tartib
        for i in range(0, len(cities), 2):
            row = []
            row.append(InlineKeyboardButton(
                cities[i], 
                callback_data=f"city:{cities[i]}"
            ))
            if i + 1 < len(cities):
                row.append(InlineKeyboardButton(
                    cities[i + 1], 
                    callback_data=f"city:{cities[i + 1]}"
                ))
            keyboard.append(row)
        # Orqaga qaytish tugmasi
        keyboard.append([InlineKeyboardButton(
            MESSAGES['back_to_regions'], 
            callback_data="back_to_regions"
        )])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            f"{MESSAGES['select_city']}\n📍 {province}",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Shaharlarni ko'rsatishda xato: {e}")
        await update.callback_query.answer("Xatolik yuz berdi")

async def show_prayer_times(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """Tanlangan shahar uchun namoz vaqtlarini ko'rsatish"""
    try:
        # Yuklanmoqda xabarini ko'rsatish
        await update.callback_query.answer("Ma'lumot yuklanmoqda...")
        # Namoz vaqtlarini olish
        prayer_times_text = prayer_api.get_formatted_prayer_times(city)
        # Orqaga qaytish tugmasi
        keyboard = [[InlineKeyboardButton(
            MESSAGES['back_to_regions'], 
            callback_data="back_to_regions"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            prayer_times_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Namoz vaqtlarini ko'rsatishda xato: {e}")
        await update.callback_query.answer("Namoz vaqtlarini olishda xatolik")
        await update.callback_query.edit_message_text(
            MESSAGES['error_api'],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                MESSAGES['back_to_regions'], 
                callback_data="back_to_regions"
            )]])
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline klaviatura tugmalarini bosishni qayta ishlash"""
    try:
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == "check_sub":
            # Obunani qayta tekshirish
            await check_subscription_callback(update, context)
        elif data.startswith("province:"):
            province = data.replace("province:", "")
            await show_cities(update, context, province)
        elif data.startswith("city:"):
            city = data.replace("city:", "")
            await show_prayer_times(update, context, city)
        elif data == "back_to_regions":
            # Viloyatlarga qaytish
            provinces = list(REGIONS_BY_PROVINCE.keys())
            keyboard = []
            # 2 ustunli tartib
            for i in range(0, len(provinces), 2):
                row = []
                row.append(InlineKeyboardButton(
                    provinces[i], 
                    callback_data=f"province:{provinces[i]}"
                ))
                if i + 1 < len(provinces):
                    row.append(InlineKeyboardButton(
                        provinces[i + 1], 
                        callback_data=f"province:{provinces[i + 1]}"
                    ))
                keyboard.append(row)
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                MESSAGES['select_region'],
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Tugma callbackida xato: {e}")
        await query.answer("Xatolik yuz berdi")

# --- Asosiy funksiya ---

def main():
    """Botni ishga tushirish uchun asosiy funksiya"""
    try:
        # Ilova yaratish
        application = Application.builder().token(BOT_TOKEN).build()

        # Conversation Handler (Majburiy obuna uchun)
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                CHECK_SUBSCRIPTION: [CallbackQueryHandler(check_subscription_callback, pattern="^check_sub$")],
                MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)]
            },
            fallbacks=[],
            per_message=False,
            per_chat=True,
            per_user=True
        )

        # Handlerlarni qo'shish
        application.add_handler(conv_handler)
        application.add_handler(CallbackQueryHandler(button_callback)) # Boshqa inline tugmalar
        # Asosiy menyudagi tugmani qayta ishlash uchun
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

        # Polling orqali ishga tushirish (webhook emas)
        logger.info("Polling boshlanmoqda...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xato: {e}")
        raise

if __name__ == '__main__':
    main()