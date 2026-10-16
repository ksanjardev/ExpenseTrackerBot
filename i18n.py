"""All user-facing texts (bot UI + report labels) in Uzbek (Latin), Russian and English."""

LANGS = {"uz": "🇺🇿 Oʻzbekcha", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
DEFAULT_LANG = "uz"

S = {
    "uz": {
        "choose_lang": "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "lang_set": "✅ Til: Oʻzbekcha",
        "welcome": ("Salom, {name}! 👋\n\nMen xarajatlaringizni yozib boraman. Shunchaki yozing, masalan:\n"
                    "<code>10 ta paypoq oldim 13k</code>\n<code>taksi 25 000</code>\n<code>3 kg olma 45 ming</code>\n\n"
                    "Bir nechta xarajatni har birini yangi qatordan yozishingiz mumkin. Toifani oʻzim aniqlayman; "
                    "bilmasam — soʻrayman va keyingi safar eslab qolaman.\n\n"
                    "Buyruqlar:\n/stats — statistika (rasm, Excel, PDF, matn)\n/today — bugungi xarajatlar\n"
                    "/undo — oxirgi yozuvni oʻchirish\n/remind 19:30 — eslatma vaqti (/remind off — oʻchirish)\n"
                    "/lang — tilni oʻzgartirish\n\n"
                    "Har kuni soat {remind} da eslataman, yakshanba kuni esa haftalik Excel hisobot yuboraman."),
        "reminder": "🕕 Bugun nimalarga pul sarfladingiz?\nMasalan: <code>10 ta paypoq oldim 13k</code>",
        "no_price": "🤔 Narxni topa olmadim: <i>{line}</i>\nMasalan: <code>{line} 13k</code>",
        "unnamed": "Nomsiz",
        "today_total": "Bugun jami",
        "today_empty": "Bugun hali xarajat yoʻq.",
        "undo_done": "🗑 Oʻchirildi: {item} — {amount}",
        "undo_none": "Oʻchiradigan yozuv yoʻq.",
        "remind_usage": "Masalan: /remind 19:30   yoki   /remind off",
        "remind_off": "🔕 Eslatma oʻchirildi.",
        "remind_on": "🔔 Eslatma har kuni {time} da (Toshkent vaqti).",
        "ask_period": "Qaysi davr uchun statistika kerak?",
        "ask_format": "{period} — qaysi koʻrinishda yuboray?",
        "ask_lang": "{period} · {format} — fayl qaysi tilda boʻlsin?",
        "generating": "⏳ Tayyorlanmoqda...",
        "no_data": "Bu davrda xarajat topilmadi.",
        "weekly_caption": "📊 Haftalik hisobot\n💰 Jami: {total}",
        "ask_cat": "🏷 «{item}» qaysi toifaga kiradi?",
        "pick_group": "Toifani tanlang:",
        "pick_sub": "{group} — qaysi biri?",
        "cat_saved": "✅ {item} → {cat}\n(Keyingi safar avtomatik shunday yozaman)",
        "back": "⬅️ Orqaga",
        "need_category": "👆 Toifasi nomaʼlum — tanlang:",
        "periods": {"today": "Bugun", "week": "Oxirgi 7 kun", "month": "Shu oy", "year": "Shu yil"},
        "formats": {"img": "📊 Rasm", "xlsx": "📗 Excel", "pdf": "📕 PDF", "txt": "💬 Matn"},
        "cmds": {"stats": "Statistika", "today": "Bugungi xarajatlar", "undo": "Oxirgisini oʻchirish",
                 "remind": "Eslatma vaqti", "lang": "Tilni oʻzgartirish", "start": "Boshlash"},
        # ---- report words
        "currency": "soʻm", "title": "Xarajatlar", "total": "Jami", "count": "Xarajatlar soni",
        "by_cat": "Toifalar boʻyicha", "top_items": "Eng koʻp xarajatlar", "by_day": "Kunlar boʻyicha", "by_month": "Oylar boʻyicha",
        "all_items": "Barcha xarajatlar", "no_data_short": "Maʼlumot yoʻq.", "date": "Sana", "time": "Vaqt",
        "item": "Nima uchun", "category": "Toifa", "subcategory": "Kichik toifa", "amount": "Summa",
        "avg_day": "Kunlik oʻrtacha", "biggest": "Eng katta xarajat", "dashboard": "Boshqaruv paneli",
        "details": "Xarajatlar", "budget_title": "Shaxsiy byudjet jadvali", "daily_chart": "Kunlik xarajat",
        "cat_chart": "Toifalar boʻyicha xarajat", "period": "Davr", "months": ["YAN", "FEV", "MAR", "APR", "MAY", "IYUN",
                                                                               "IYUL", "AVG", "SEN", "OKT", "NOY", "DEK"],
        "tbl_total": "Jami", "tbl_avg": "Oʻrt.", "file_prefix": "xarajatlar", "weekly_prefix": "haftalik",
    },
    "ru": {
        "choose_lang": "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "lang_set": "✅ Язык: Русский",
        "welcome": ("Привет, {name}! 👋\n\nЯ веду учёт ваших расходов. Просто пишите, например:\n"
                    "<code>10 пар носков 13k</code>\n<code>такси 25 000</code>\n<code>3 кг яблок 45 тыс</code>\n\n"
                    "Можно писать несколько расходов — каждый с новой строки. Категорию я определяю сам; если не "
                    "знаю — спрошу и запомню.\n\n"
                    "Команды:\n/stats — статистика (картинка, Excel, PDF, текст)\n/today — расходы за сегодня\n"
                    "/undo — удалить последнюю запись\n/remind 19:30 — время напоминания (/remind off — выключить)\n"
                    "/lang — сменить язык\n\n"
                    "Каждый день в {remind} я напоминаю, а по воскресеньям присылаю недельный отчёт в Excel."),
        "reminder": "🕕 На что вы сегодня потратили деньги?\nНапример: <code>10 пар носков 13k</code>",
        "no_price": "🤔 Не нашёл сумму: <i>{line}</i>\nНапример: <code>{line} 13k</code>",
        "unnamed": "Без названия",
        "today_total": "Сегодня всего",
        "today_empty": "Сегодня расходов пока нет.",
        "undo_done": "🗑 Удалено: {item} — {amount}",
        "undo_none": "Нет записей для удаления.",
        "remind_usage": "Например: /remind 19:30   или   /remind off",
        "remind_off": "🔕 Напоминание выключено.",
        "remind_on": "🔔 Напоминание каждый день в {time} (по Ташкенту).",
        "ask_period": "За какой период нужна статистика?",
        "ask_format": "{period} — в каком виде отправить?",
        "ask_lang": "{period} · {format} — на каком языке сделать файл?",
        "generating": "⏳ Готовлю...",
        "no_data": "За этот период расходов нет.",
        "weekly_caption": "📊 Недельный отчёт\n💰 Всего: {total}",
        "ask_cat": "🏷 К какой категории относится «{item}»?",
        "pick_group": "Выберите категорию:",
        "pick_sub": "{group} — какая именно?",
        "cat_saved": "✅ {item} → {cat}\n(В следующий раз запишу так автоматически)",
        "back": "⬅️ Назад",
        "need_category": "👆 Категория неизвестна — выберите:",
        "periods": {"today": "Сегодня", "week": "Последние 7 дней", "month": "Этот месяц", "year": "Этот год"},
        "formats": {"img": "📊 Картинка", "xlsx": "📗 Excel", "pdf": "📕 PDF", "txt": "💬 Текст"},
        "cmds": {"stats": "Статистика", "today": "Расходы за сегодня", "undo": "Удалить последнюю",
                 "remind": "Время напоминания", "lang": "Сменить язык", "start": "Начать"},
        "currency": "сум", "title": "Расходы", "total": "Итого", "count": "Количество расходов",
        "by_cat": "По категориям", "top_items": "Самые крупные расходы", "by_day": "По дням", "by_month": "По месяцам",
        "all_items": "Все расходы", "no_data_short": "Нет данных.", "date": "Дата", "time": "Время",
        "item": "На что", "category": "Категория", "subcategory": "Подкатегория", "amount": "Сумма",
        "avg_day": "В среднем за день", "biggest": "Самый крупный расход", "dashboard": "Дашборд",
        "details": "Расходы", "budget_title": "Личный бюджет", "daily_chart": "Расходы по дням",
        "cat_chart": "Расходы по категориям", "period": "Период", "months": ["ЯНВ", "ФЕВ", "МАР", "АПР", "МАЙ", "ИЮН",
                                                                            "ИЮЛ", "АВГ", "СЕН", "ОКТ", "НОЯ", "ДЕК"],
        "tbl_total": "Итого", "tbl_avg": "Сред.", "file_prefix": "rashody", "weekly_prefix": "nedelya",
    },
    "en": {
        "choose_lang": "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "lang_set": "✅ Language: English",
        "welcome": ("Hi, {name}! 👋\n\nI keep track of your spending. Just write, for example:\n"
                    "<code>10 pairs of socks 13k</code>\n<code>taxi 25 000</code>\n<code>3 kg apples 45 thousand</code>\n\n"
                    "You can send several expenses, one per line. I detect the category myself; if I don't know it "
                    "I'll ask once and remember.\n\n"
                    "Commands:\n/stats — statistics (image, Excel, PDF, text)\n/today — today's expenses\n"
                    "/undo — delete the last entry\n/remind 19:30 — reminder time (/remind off — disable)\n"
                    "/lang — change language\n\n"
                    "I remind you every day at {remind} and send a weekly Excel report on Sundays."),
        "reminder": "🕕 What did you spend money on today?\nFor example: <code>10 pairs of socks 13k</code>",
        "no_price": "🤔 Couldn't find the price: <i>{line}</i>\nFor example: <code>{line} 13k</code>",
        "unnamed": "Unnamed",
        "today_total": "Today total",
        "today_empty": "No expenses yet today.",
        "undo_done": "🗑 Deleted: {item} — {amount}",
        "undo_none": "Nothing to delete.",
        "remind_usage": "For example: /remind 19:30   or   /remind off",
        "remind_off": "🔕 Reminder turned off.",
        "remind_on": "🔔 Reminder every day at {time} (Tashkent time).",
        "ask_period": "Which period do you need statistics for?",
        "ask_format": "{period} — which format should I send?",
        "ask_lang": "{period} · {format} — which language for the file?",
        "generating": "⏳ Preparing...",
        "no_data": "No expenses found for this period.",
        "weekly_caption": "📊 Weekly report\n💰 Total: {total}",
        "ask_cat": "🏷 Which category does “{item}” belong to?",
        "pick_group": "Pick a category:",
        "pick_sub": "{group} — which one?",
        "cat_saved": "✅ {item} → {cat}\n(I'll file it like this automatically next time)",
        "back": "⬅️ Back",
        "need_category": "👆 Category unknown — please pick:",
        "periods": {"today": "Today", "week": "Last 7 days", "month": "This month", "year": "This year"},
        "formats": {"img": "📊 Image", "xlsx": "📗 Excel", "pdf": "📕 PDF", "txt": "💬 Text"},
        "cmds": {"stats": "Statistics", "today": "Today's expenses", "undo": "Delete last entry",
                 "remind": "Reminder time", "lang": "Change language", "start": "Start"},
        "currency": "UZS", "title": "Expenses", "total": "Total", "count": "Number of expenses",
        "by_cat": "By category", "top_items": "Biggest expenses", "by_day": "By day", "by_month": "By month",
        "all_items": "All expenses", "no_data_short": "No data.", "date": "Date", "time": "Time",
        "item": "What for", "category": "Category", "subcategory": "Subcategory", "amount": "Amount",
        "avg_day": "Average per day", "biggest": "Biggest expense", "dashboard": "Dashboard",
        "details": "Expenses", "budget_title": "Personal Budget Spreadsheet", "daily_chart": "Daily spending",
        "cat_chart": "Spending by category", "period": "Period", "months": ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                                                                           "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"],
        "tbl_total": "Total", "tbl_avg": "Avg", "file_prefix": "expenses", "weekly_prefix": "weekly",
    },
}


def t(lang: str, key: str, **kw):
    val = S.get(lang, S[DEFAULT_LANG]).get(key)
    if val is None:
        val = S["en"][key]
    return val.format(**kw) if kw and isinstance(val, str) else val


# Translations of the Help sheet of the template (cell -> text). English = original, left untouched.
HELP = {
    "uz": {
        "A1": "YORDAM", "A4": "Kirish",
        "B4": "Bu shaxsiy byudjet jadvali butun yil uchun byudjet tuzishga yordam beradi. Bu kelajakdagi moliyaviy "
              "ahvolingizni oldindan koʻrish uchun foydali, ayniqsa koʻchish yoki ish almashtirish kabi katta "
              "oʻzgarishlar paytida.",
        "A6": "1-qadam:", "B6": "Byudjet toifalarini belgilang",
        "B8": "Har bir asosiy toifa alohida Excel jadvalidir. Kichik toifalarni oʻzgartirishingiz mumkin. Asosiy "
              "toifa (butun jadval) qoʻshsangiz yoki olib tashlasangiz, umumiy jadvaldagi formulalarni ham "
              "oʻzgartirishingiz kerak.",
        "B10": "Kichik toifa qoʻshish uchun jadval ichida oʻng tugmani bosing: Insert > Table Rows Above. Olib "
               "tashlash uchun: Delete > Table Rows.",
        "A12": "2-qadam:", "B12": "Boshlangʻich balansni kiriting",
        "B14": "Naqd pul va karta hisobingizdagi balanslarni qoʻshib, boshlangʻich balansni hisoblang.",
        "B16": "Yanvardan boshqa oyni ham boshlash mumkin: ustun nomini oʻzgartiring va qolganlarini oʻngga "
               "nusxalang.",
        "A18": "3-qadam:", "B18": "Byudjetingizni belgilang",
        "B20": "Oʻtgan chek, bank koʻchirmasi, hisob-kitob va maoshingiz maʼlumotlariga tayanib, har bir toifa "
               "uchun byudjet summalarini kiriting.",
        "A22": "Doimiy xarajatlar", "B23": "Ijara yoki ipoteka kabi doimiy xarajatlarga har oy bir xil summani kiriting.",
        "A25": "Oʻzgaruvchan xarajatlar",
        "B26": "Kommunal toʻlovlar, oziq-ovqat, sovgʻalar kabi oʻzgaruvchan xarajatlarga taxminiy summani "
               "yozing yoki oʻrtacha oylik summani kiriting.",
        "A28": "Izoh qoʻshing",
        "B29": "Xarajatni tushuntirish uchun katakka izoh qoʻshing, masalan «Sovgʻalar» ga tugʻilgan kunlar ismlarini.",
        "A32": "4-qadam:", "B32": "Yil oxiridagi balansni tahlil qiling",
        "B34": "Balans oʻsib borayotgan boʻlsa, jamgʻarmaga koʻproq mablagʻ ajratish mumkin.",
        "B36": "Balans qulay darajadan pastga tushsa, baʼzi xarajatlarni qisqartirish kerak boʻlishi mumkin.",
        "A38": "Keyingi qadam",
        "B39": "Bu jadval oylik byudjetni tuzishning oddiy usuli. Murakkabroq vosita kerak boʻlganda quyidagi "
               "Money Management Template ni sinab koʻring.",
        "A42": "Oʻxshash shablonlar va manbalar",
    },
    "ru": {
        "A1": "СПРАВКА", "A4": "Введение",
        "B4": "Эта таблица личного бюджета помогает составить бюджет на целый год. Это позволяет прогнозировать "
              "будущие финансы, особенно при больших переменах: переезде или смене работы.",
        "A6": "Шаг 1:", "B6": "Определите категории бюджета",
        "B8": "Каждая основная категория — отдельная таблица Excel. Подкатегории можно менять. Если вы добавляете "
              "или удаляете основную категорию (целую таблицу), нужно изменить формулы в итоговой таблице.",
        "B10": "Чтобы добавить подкатегорию, щёлкните правой кнопкой внутри таблицы: Вставить > Строки таблицы "
               "выше. Чтобы удалить: Удалить > Строки таблицы.",
        "A12": "Шаг 2:", "B12": "Введите начальный баланс",
        "B14": "Сложите остатки на своих счетах (наличные, карта) — это ваш начальный баланс.",
        "B16": "Можно начать не с января: измените название столбца и скопируйте его вправо.",
        "A18": "Шаг 3:", "B18": "Определите свой бюджет",
        "B20": "Опираясь на чеки, банковские выписки, счета и данные о зарплате, заполните суммы бюджета по "
               "каждой категории.",
        "A22": "Постоянные расходы", "B23": "Для постоянных расходов (аренда, ипотека) вводите одну и ту же сумму каждый месяц.",
        "A25": "Переменные расходы",
        "B26": "Для переменных расходов (коммунальные услуги, продукты, подарки) укажите ожидаемые суммы по "
               "месяцам или среднемесячную сумму.",
        "A28": "Добавляйте примечания",
        "B29": "Добавьте примечание к ячейке, чтобы пояснить расход, например имена именинников в «Подарках».",
        "A32": "Шаг 4:", "B32": "Проанализируйте конечный баланс",
        "B34": "Если прогнозируемый баланс растёт, можно откладывать больше на накопления.",
        "B36": "Если баланс падает ниже комфортного уровня, возможно, нужно сократить часть расходов.",
        "A38": "Следующий шаг",
        "B39": "Эта таблица — простой способ составить месячный бюджет. Для более продвинутого инструмента "
               "попробуйте шаблон Money Management Template ниже.",
        "A42": "Похожие шаблоны и ресурсы",
    },
}
