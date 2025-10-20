# 🕌 Namoz Vaqtlari Telegram Boti

Butun O‘zbekiston viloyatlari uchun **Islom.uz API** orqali namoz vaqtlarini ko‘rsatib beruvchi Telegram bot. Foydalanuvchi o‘z viloyatini tanlash orqali har kuni yangilanib boradigan namoz vaqtlarini olish imkoniyatiga ega.

---

## 📦 Xususiyatlar

* ✅ O‘zbekistonning **barcha viloyatlari** bo‘yicha namoz vaqtlarini olish
* ✅ Islom.uz rasmiy API’dan foydalanadi
* ✅ Bugungi kun va haftalik jadval ko‘rinishi
* ✅ Majburiy kanal obunasi (join check)
* ✅ Administrator uchun boshqaruv paneli
* ✅ Minimal resurslarda tez ishlash

---

## 🔧 Sozlash (Config)

Bot ishga tushishi uchun quyidagi ma’lumotlarni `config.py` (yoki `.env`) fayliga kiritish kerak:

| Parametr           | Tavsif                              | Namuna             |
| ------------------ | ----------------------------------- | ------------------ |
| `BOT_TOKEN`        | BotFather orqali olingan bot tokeni | `123456:ABCDEF...` |
| `ADMIN_ID`         | Admin ID (faqat bitta)              | `123456789`        |
| `CHANNEL_USERNAME` | Majburiy obuna kanali               | `@namoz_uz`        |

`config.py` misol:

```python
BOT_TOKEN = "BOT_TOKENINGIZNI_KIRITIN"
ADMIN_ID = 123456789
CHANNEL_USERNAME = "@kanal_nomi"
```

---

## 🛠️ O‘rnatish va ishga tushirish

```bash
# 1. Repo'ni yuklash
git clone <repo-link>
cd namoz-bot

# 2. Kerakli kutubxonalarni o‘rnatish
pip install -r requirements.txt

# 3. Botni ishga tushirish
python bot.py
```

---

## 🌍 Viloyatlar qo‘llab-quvvatlanadi

* Toshkent
* Andijon
* Farg‘ona
* Namangan
* Buxoro
* Samarqand
* Navoiy
* Xorazm
* Qashqadaryo
* Surxondaryo
* Sirdaryo
* Jizzax
* Qoraqalpog‘iston Respublikasi

---

## 📡 API manbasi

Bu bot **Islom.uz API** dan foydalanadi.
Nomoz vaqtlarini olish uchun so‘rov manzili viloyat nomiga mos ravishda yuboriladi.

---

## 📬 Buyruqlar (User Commands)

| Buyruq   | Tavsif                              |
| -------- | ----------------------------------- |
| `/start` | Boshlash va viloyat tanlash         |
| `/today` | Bugungi namoz vaqtlarini ko‘rsatish |
| `/week`  | Haftalik jadval                     |
| `/help`  | Yordam menyusi                      |

---

## 🛡 Admin Buyruqlari

| Buyruq       | Tavsif                                  |
| ------------ | --------------------------------------- |
| `/broadcast` | Hamma foydalanuvchilarga xabar yuborish |
| `/stats`     | Foydalanuvchilar sonini ko‘rish         |
| `/ban`       | Foydalanuvchini bloklash                |

> Eslatma: Admin buyruqlari faqat `ADMIN_ID` orqali ishlatiladi.

---

## 🧩 Kelajakdagi rejalashtirilgan funksiyalar (Roadmap)

* 📌 Avtomatik tong/saharlik eslatmalari
* 📌 Har kunlik push notification
* 📌 Hijriy taqvim integratsiyasi
* 📌 Bir nechta til qo‘llash (Uzbek / Rus / English)
* 📌 Adminga webhook orqali boshqaruv

---

## 🤝 Hissa qo‘shish (Contribution)

1. Fork qiling
2. O‘zgartirishlarni kiriting
3. Pull Request yarating
4. Tasdiqlangandan so‘ng qo‘shiladi

---

## 📜 Litsenziya

Ushbu loyiha MIT licenziyasi ostida tarqatiladi. Istalgan holda o‘zgartirish va foydalanish mumkin.

---

## 👤 Muallif

Loyiha muallifi: Azamatjon

Agar savollar bo‘lsa quyidagi Telegram orqali bog‘laning: `ADMIN_ID`
