# 🏆 Tournament Master Bot

بوت Discord مجاني 100% لإدارة البطولات في سيرفرات الألعاب.

## 📋 المميزات

- ✅ إنشاء بطولات (`/create_tournament`)
- ✅ تسجيل اللاعبين (`/register`)
- ✅ توليد Bracket تلقائي (`/start_tournament`)
- ✅ إبلاغ النتائج (`/report_result`)
- ✅ لوحة تحكم (`/dashboard`)
- ✅ نظام Disputes (`/dispute`)
- ✅ قاعدة بيانات SQLite محلية

## 🚀 التشغيل على Railway (مجاني)

### الخطوة 1: إنشاء حساب Railway
1. اذهب إلى https://railway.app
2. سجل الدخول بحساب GitHub

### الخطوة 2: رفع الكود
1. أنشئ repo جديد على GitHub
2. ارفع هذه الملفات:
   - `tournament_master_bot.py`
   - `requirements.txt`
3. اربط Railway بالـ repo

### الخطوة 3: إضافة متغير البيئة
1. في Railway → Variables
2. أضف: `DISCORD_TOKEN = (الـ Token الخاص بك)`
3. عدّل الكود: غيّر `TOKEN = "YOUR_BOT_TOKEN_HERE"` إلى:
   ```python
   import os
   TOKEN = os.environ.get("DISCORD_TOKEN")
   ```

### الخطوة 4: Deploy
اضغط Deploy — والبوت يعمل 24/7 مجاناً!

## 🛠️ الأوامر المتاحة

| الأمر | الوصف |
|-------|-------|
| `/create_tournament` | إنشاء بطولة جديدة (للأدمن فقط) |
| `/register` | التسجيل في بطولة |
| `/start_tournament` | بدء البطولة وتوليد Bracket |
| `/report_result` | إبلاغ نتيجة مباراة |
| `/dashboard` | عرض إحصائيات البطولة |
| `/dispute` | فتح تذكرة dispute |
| `/help` | عرض جميع الأوامر |

## ⚠️ ملاحظات

- تأكد من أن البوت لديه صلاحيات: Send Messages, Read Message History, Manage Channels, Manage Roles
- قاعدة البيانات SQLite تُخزن محلياً — استخدم Railway Volume للحفظ الدائم
