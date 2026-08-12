# 🏆 Tournament Master Bot - Final Version

بوت Discord مجاني 100% لإدارة البطولات في سيرفرات الألعاب.
يعمل على Render.com بشكل تلقائي 24/7.

---

## 📦 الملفات المطلوبة

| الملف | الوظيفة |
|-------|---------|
| `tournament_master_bot.py` | الكود الرئيسي |
| `requirements.txt` | المكتبات المطلوبة |
| `runtime.txt` | تحديد إصدار Python |
| `Procfile` | أمر التشغيل التلقائي |

---

## 🚀 خطوات التشغيل على Render (مرة واحدة فقط)

### الخطوة 1: رفع الملفات على GitHub
1. أنشئ repo جديد على GitHub
2. ارفع الأربعة ملفات أعلاه
3. اضغط Commit changes

### الخطوة 2: إنشاء خدمة على Render
1. اذهب إلى [dashboard.render.com](https://dashboard.render.com)
2. اضغط **New** → **Web Service**
3. اختر الـ repo من GitHub
4. املأ البيانات:
   - **Name**: tournament-master-bot
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 tournament_master_bot.py`
   - **Plan**: Free
5. اضغط **Create Web Service**

### الخطوة 3: إضافة الـ Token
1. في Render → تبويب **Environment**
2. اضغط **Add Environment Variable**
3. **Key**: `DISCORD_TOKEN`
4. **Value**: (الصق الـ Token من Discord Developer Portal)
5. اضغط **Save Changes**

### الخطوة 4: إعادة البناء
1. تبويب **Deploy**
2. اضغط **Manual Deploy** → **Deploy latest commit**
3. انتظر 2-3 دقائق

### ✅ بعد النجاح:
سترى في الـ Logs:
```
✅ Web server running on port 8080
✅ Tournament Master is online as Tournament Master#XXXX
✅ Synced 7 commands
```

---

## 🤖 أوامر البوت

| الأمر | الوصف | من يستخدمه |
|-------|-------|-----------|
| `/create_tournament` | إنشاء بطولة جديدة | الأدمن |
| `/register` | التسجيل في بطولة | أي عضو |
| `/start_tournament` | بدء البطولة وتوليد Bracket | الأدمن |
| `/report_result` | إبلاغ نتيجة مباراة | اللاعبون |
| `/dashboard` | عرض إحصائيات البطولة | أي عضو |
| `/dispute` | فتح تذكرة شكوى | اللاعبون |
| `/help` | عرض جميع الأوامر | أي عضو |

---

## 💰 كيف تربح من البوت

### نموذج Freemium:
| الخطة | السعر | المميزات |
|-------|-------|---------|
| مجاني | $0 | بطولات حتى 8 لاعبين |
| Pro | $5/شهر | بطولات حتى 64 لاعب |
| Premium | $15/شهر | غير محدود + دخول مدفوع |

### طرق الربح:
1. **اشتراكات شهرية** — Discord Server Subscriptions
2. **دخول البطولات** — $5 للاعب
3. **إعلانات** — سيرفرات كبيرة تدفع $200-500
4. **رعاية** — شركات ألعاب ترعى بطولاتك

---

## ⚠️ ملاحظات مهمة

- البوت يعمل **24/7** تلقائياً
- لا تحتاج لأي تدخل بعد الإعداد
- الخطة المجانية قد تُسبت البوت بعد 15 دقيقة من عدم النشاط (يعود تلقائياً)
- لا تشارك الـ Token مع أحد

---

## 🔧 الدعم

إذا واجهت أي مشكلة، تأكد من:
1. ✅ الـ Token صحيح ومضاف في Environment Variables
2. ✅ البوت مضاف لسيرفر Discord مع الصلاحيات الصحيحة
3. ✅ Start Command هو: `python3 tournament_master_bot.py`
