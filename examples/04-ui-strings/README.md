# Example 04: reviewing an Arabic strings file

**Skill:** `arabic-ux-writing` · **Files:** [en.json](en.json), [ar.before.json](ar.before.json), [ar.json](ar.json)

## Prompt

> Here are our English strings and the Arabic we got from a translation plugin. Review the Arabic and fix it. Gulf audience, professional but friendly.

## Mechanical check first

```bash
python ../../shared/scripts/i18n_parity.py --json ar.before.json en.json
python ../../shared/scripts/bidi_lint.py ar.before.json
```

```
P01  common.settings   key missing from Arabic
P03  common.learnMore  Arabic and English are identical (untranslated?): 'Learn more'
P06  files.tooLarge    placeholders differ: ar=['{maximum}'] en=['{max}']
1 file(s) checked: 0 error(s), 3 warning(s), 0 info      (Latin , and ? after Arabic text)
```

## Review

Repeated problems: «الخاص بك» for possession, «قم بـ» before every action, missing hamzas, «تحميل» used for both upload and download.

| Key | Before | After | Why |
|---|---|---|---|
| `auth.signIn` | سجل الدخول | تسجيل الدخول | Buttons use the verbal noun |
| `auth.forgot` | هل نسيت كلمه السر الخاصة بك? | نسيت كلمة المرور؟ | Taa marbuta, term, calque, Arabic question mark |
| `auth.welcomeBack` | مرحبا بعودتك, {name} | أهلًا بعودتك يا {name} | Punctuation; natural greeting |
| `auth.sessionExpired` | لقد انتهت صلاحية الجلسة الخاصة بك. من فضلك قم بتسجيل الدخول مرة اخرى. | انتهت الجلسة. سجّل الدخول من جديد. | Filler removed; hamza |
| `files.upload` / `files.download` | تحميل ملف / تحميل | رفع ملف / تنزيل | One term per concept |
| `files.empty` | ليس لديك اي ملفات حتى الان. قم برفع ملفك الاول للبدء. | لا توجد ملفات بعد. ارفع ملفك الأول لتبدأ. | Hamzas; «قم بـ» |
| `files.tooLarge` | الملف كبير جدا! الحجم الاقصى هو {maximum} ميجا. | حجم الملف أكبر من {max} ميغابايت. اختر ملفًا أصغر. | Placeholder was renamed; no exclamation in errors; next step added |
| `files.deleteTitle` | هل أنت متأكد أنك تريد حذف هذا الملف? | حذف الملف؟ | Ask about the action |
| `files.deleteBody` | هذا الإجراء لا يمكن التراجع عنه. | سيُحذف الملف نهائيًا، ولا يمكن استرجاعه. | State the consequence |
| `files.saved` | تم حفظ التغييرات بنجاح | حُفظت التغييرات | «تم … بنجاح» filler |
| `files.count` | {count} ملف | عدد الملفات: {count} | Noun cannot agree with every number |
| `activity.commented` | {name} علّق على الملف الخاص بك | تعليق جديد من {name} على ملفك | Verb gender depended on the name |
| `activity.minutesAgo` | منذ {n} دقائق | قبل {n} دقائق | Shorter, usual in interfaces |
| `common.save` | احفظ | حفظ | Parallel with «إلغاء» |
| `common.tryAgain` | حاول مرة اخرى | إعادة المحاولة | Verbal noun; hamza |
| `common.learnMore` | Learn more | اعرف المزيد | Untranslated |
| `common.dashboard` | لوحة التحكم | لوحة المعلومات | It shows indicators; not an admin panel |
| `common.settings` | (missing) | الإعدادات | Missing key |

Unchanged: `common.cancel`.

**Needs a decision:** `activity.minutesAgo` still shows «دقائق» for every number. Correct Arabic needs the six plural forms; the skill recommends ICU plurals or `Intl.RelativeTimeFormat("ar")`.

## After

```bash
python ../../shared/scripts/i18n_parity.py --json ar.json en.json   # 20 pair(s)/element(s) checked: 0 problem(s)
python ../../shared/scripts/bidi_lint.py ar.json                    # 0 error(s), 0 warning(s), 0 info
```
