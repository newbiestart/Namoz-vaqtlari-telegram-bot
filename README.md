# 🕌 Namoz Vaqtlari Telegram Boti

Butun O‘zbekiston viloyatlari uchun **Islom.uz API** orqali namoz vaqtlarini ko‘rsatib beruvchi Telegram bot. Foydalanuvchi o‘z viloyatini tanlash orqali har kuni yangilanib boradigan namoz vaqtlarini olish imkoniyatiga ega.

---

## 📦 Xususiyatlar

- ✅ O‘zbekistonning **barcha viloyatlari** bo‘yicha namoz vaqtlarini olish
- ✅ Islom.uz rasmiy API’dan foydalanadi
- ✅ Bugungi kun va haftalik jadval ko‘rinishi
- ✅ Majburiy kanal obunasi (join check)
- ✅ Administrator uchun boshqaruv paneli (sozlamaga qarab)

---

## 🔧 Sozlash (Config)

Bot ishga tushishi uchun quyidagi ma’lumotlarni `config.py` (yoki `.env`) fayliga kiritish kerak:

| Parametr | Tavsif | Namuna |
|--------|---------|--------|
| `BOT_TOKEN` | BotFather orqali olingan bot tokeni | `123456:ABCDEF...` |
| `ADMIN_ID` | Admin ID (faqat bitta) | `123456789` |
| `CHANNEL_USERNAME` | Majburiy obuna kanali | `@namoz_uz` |

`config.py` misol:
```python
BOT_TOKEN = "BOT_TOKENINGIZNI_KIRITIN"
ADMIN_ID = 123456789
CHANNEL_USERNAME = "@kanal_nomi"
