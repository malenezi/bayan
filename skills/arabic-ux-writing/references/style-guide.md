# Arabic style guide for interfaces

## Contents
- Register
- Address and gender
- Sentence shape
- Definite or indefinite
- Punctuation and spacing
- Numerals
- Diacritics
- English terms inside Arabic
- Length and layout
- Tone by situation

## Register

Write Modern Standard Arabic that is contemporary and plain: the Arabic of a good news site or a well-made banking app, not of a legal contract and not of a chat between friends.

| Too formal | Right | Too casual |
|---|---|---|
| نأمل منكم التكرّم بإدخال البيانات المطلوبة | أدخل بياناتك | دخّل بياناتك |
| لقد تمّت عملية الحفظ بنجاح | حُفظت التغييرات | تمام، انحفظ |

- Dialect belongs only in brands that have chosen it, and then consistently. Never mix dialect words into MSA sentences.
- Government and financial products lean formal; consumer and youth products lean warm. Formal still means short.
- Prefer common words over rare ones: «استخدام» over «استعمال» in tech contexts, «اختيار» over «انتقاء».

## Address and gender

Arabic verbs and pronouns carry gender, and interfaces rarely know the reader's.

- **Actions and labels**: use the verbal noun. It is neutral and is the convention users know: «حفظ»، «إرسال»، «إنشاء حساب».
- **Instructions**: masculine singular imperative is the long-standing generic form in Arabic interfaces: «أدخل رمز التحقق». Use it by default.
- **Where the product wants explicitly inclusive text**, rephrase rather than doubling forms. Avoid «أدخل/ي» and «عزيزي/عزيزتي». Options: a nominal phrase («إدخال رمز التحقق»), the passive («يُدخَل الرمز هنا»), or the first-person plural for what the product does («أرسلنا لك رمزًا»).
- **Talking about a third person** whose gender is unknown (a user name in a notification): restructure so no verb agrees with the name. «تعليق جديد من {name}», not «علّق {name}».
- Address the reader as «أنت» implicitly through verbs and suffixes. The plural «أنتم» suits formal announcements to a group, not interface instructions.
- The product speaks as «نحن» sparingly: for apologies and for what it did on the user's behalf.

## Sentence shape

- Lead with the verb: «تعذّر تحميل الملف», not «الملف لم يتمكن من التحميل».
- One idea per sentence. Join with «و» or «ثم», not with chains of commas.
- Use the active voice when the actor matters, and the true passive (not «تمّ» plus a noun) when it does not: «حُذف الملف» rather than «تمّ حذف الملف». «تمّ» is acceptable occasionally; it should not start every confirmation.
- Drop filler: «من فضلك»، «الرجاء»، «يُرجى» are not needed on every instruction. Keep one where a request really is a favour.
- Possession uses the suffix: «حسابك», not «الحساب الخاص بك».

## Definite or indefinite

- Destinations and sections take the article: «الإعدادات»، «الإشعارات»، «الملف الشخصي».
- Actions do not: «حفظ»، «بحث»، «تصفية».
- An action on a specific object: «حذف الملف»، «تعديل الطلب».
- Field labels are definite when they name a known attribute: «الاسم الكامل»، «رقم الجوال».
- Statuses are indefinite adjectives or nouns: «مكتمل»، «قيد المراجعة»، «مسودة».

## Punctuation and spacing

- Comma `،`, semicolon `؛`, question mark `؟`. Full stop, colon and exclamation mark are shared with Latin.
- No space before a punctuation mark, one space after it.
- The conjunction «و» attaches to the next word with no space: «الاسم والبريد», not «الاسم و البريد». The same goes for «بـ»، «لـ»، «كـ»، «فـ».
- An attached particle cannot join a Latin word or a number. The convention is the particle, one tatweel and a space: «بـ 3 خطوات»، «لـ GitHub». Better still, rephrase with a standalone preposition («في»، «مع»، «إلى»): «في 3 خطوات».
- Labels, buttons and headings take no final full stop. Full sentences in body text and errors do.
- Quotation marks: «…». Use them for interface element names inside sentences: اضغط «حفظ».
- Ellipsis `…` for ongoing states: «جارٍ الحفظ…».
- Avoid exclamation marks. One in a celebration is enough; none in errors.
- Slashes and parentheses are fine; do not hand-reverse brackets to "fix" display, the renderer mirrors them.

## Numerals

- One digit system per product: Western `0-9` or Arabic-Indic `٠-٩`. Follow the product; default to Western for digital products in the Gulf and North Africa.
- With Western digits keep `.` for decimals, `,` for thousands and `%` for percent. With Arabic-Indic digits use `٫` `٬` `٪`.
- Number and counted noun: agreement rules are intricate (3 to 10 take a plural genitive, 11 to 99 a singular accusative). When a count is variable, either supply all plural forms through the i18n system or use the label form: «عدد المهام: {count}».
- Spell out one and two with the noun: «ملف واحد»، «ملفان», never «1 ملف».
- Ordinals: «الخطوة الأولى» or «الخطوة 1»; not «الخطوة 1st» equivalents.
- Dates: day, month name, year: «15 نوفمبر 2026». Times: «9:30 ص»، «4:00 م».
- Currency after the amount: «120 ريالًا» in running text, «120 ر.س» in tables and prices.

## Diacritics

Unvowelled text is the norm. Add a mark only when it prevents a misreading or is part of standard spelling:

- Tanween fatha on adverbs and objects, written on the letter before the alef: «شكرًا»، «مرحبًا»، «جدًّا»، «نهائيًا». Be consistent: either always or never within a product; always is preferred.
- Shadda where it distinguishes words: «مُدرِّب» and «مُدرَّب», «علّم» and «علم».
- A vowel on passives that would otherwise read as active: «حُذف»، «أُرسل»، «يُرجى».
- «جارٍ», not «جاري», for "in progress".
- No full vocalisation except in content for children or learners.

## English terms inside Arabic

1. If an established Arabic term exists, use it: «تنزيل»، «كلمة المرور»، «المتصفح».
2. If the Arabic is correct but not yet familiar to the audience, give the Latin term once in parentheses at first mention: «واجهة برمجة التطبيقات (API)».
3. Product, brand and technology names stay in Latin script: Excel, GitHub, Python. Do not add the article to a Latin word; rephrase: «منصة GitHub», not «الـ GitHub».
4. Transliterate only what users already say in Arabic letters: «إنترنت»، «فيديو»، «كاميرا»، «بلوتوث».
5. Acronyms stay in Latin capitals. If spelled out, spell out the Arabic: «مؤشر الأداء الرئيسي».
6. In markup, wrap Latin runs that carry symbols or digits in `<bdi dir="ltr">`.

## Length and layout

- Arabic strings are often shorter than English in characters and similar in width; some are much longer (single English words that need an Arabic phrase). Never truncate to fit: ask for the space or choose a shorter correct phrase.
- Arabic has almost no abbreviations. Do not invent them; «ر.س»، «ص»، «م»، «هـ»، «كم»، «د» for minutes in compact timers are the usual exceptions.
- Capitalisation carries no meaning in Arabic, so title case and ALL CAPS emphasis must be re-expressed with wording or left to the design.

## Tone by situation

| Situation | Tone | Example |
|---|---|---|
| Routine success | Brief, factual | حُفظت التغييرات |
| Milestone | Warm, one line | أحسنت! أكملت إعداد حسابك |
| Recoverable error | Calm, specific, with the next step | تعذّر رفع الملف. تأكّد من أن حجمه أقل من 10 ميغابايت ثم أعد المحاولة. |
| System failure | Take responsibility, no jargon | حدث خلل من جهتنا. نعمل على إصلاحه، حاول بعد قليل. |
| Destructive confirmation | Plain, states the consequence | سيُحذف المشروع وجميع ملفاته نهائيًا. |
| Security and money | Formal, exact | أرسلنا رمز التحقق إلى الرقم المنتهي بـ 42 |
| Empty state | Encouraging, points to the first action | لا توجد مهام بعد. أضف مهمتك الأولى. |
