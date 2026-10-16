"""Category tree (mirrors the Excel template tables 1:1), localized names and keyword classifier.

The order of GROUPS and of the subs inside each group is EXACTLY the order of the tables / rows in
assets/personal-budget-template.xlsx - reports.py relies on that to fill the template.
"""
import re
from typing import Optional

# (key, en, uz, ru)
GROUPS = [
    ("home", "HOME EXPENSES", "UY XARAJATLARI", "РАСХОДЫ НА ЖИЛЬЁ", [
        ("rent", "Mortgage/Rent", "Ipoteka/Ijara", "Ипотека/Аренда"),
        ("insurance", "Home/Rental Insurance", "Uy sugʻurtasi", "Страхование жилья"),
        ("electricity", "Electricity", "Elektr energiya", "Электричество"),
        ("gas", "Gas/Oil", "Gaz/Yoqilgʻi", "Газ/Топливо"),
        ("water", "Water/Sewer/Trash", "Suv/Kanalizatsiya/Chiqindi", "Вода/Канализация/Мусор"),
        ("phone", "Phone", "Telefon", "Телефон"),
        ("cable", "Cable/Satellite", "Kabel/Sunʼiy yoʻldosh TV", "Кабельное/Спутник ТВ"),
        ("internet", "Internet", "Internet", "Интернет"),
        ("furnishings", "Furnishings/Appliances", "Mebel/Maishiy texnika", "Мебель/Бытовая техника"),
        ("lawn", "Lawn/Garden", "Hovli/Bogʻ", "Газон/Сад"),
        ("maintenance", "Maintenance/Supplies", "Taʼmirlash/Jihozlar", "Обслуживание/Материалы"),
        ("improvements", "Improvements", "Yaxshilashlar", "Улучшения"),
        ("other", "Other", "Boshqa", "Прочее"),
    ]),
    ("transport", "TRANSPORTATION", "TRANSPORT", "ТРАНСПОРТ", [
        ("payments", "Vehicle Payments", "Avtomobil toʻlovlari", "Платежи за авто"),
        ("insurance", "Auto Insurance", "Avto sugʻurta", "Автостраховка"),
        ("fuel", "Fuel", "Yoqilgʻi", "Топливо"),
        ("fare", "Bus/Taxi/Train Fare", "Avtobus/Taksi/Poyezd", "Автобус/Такси/Поезд"),
        ("repairs", "Repairs", "Taʼmir", "Ремонт"),
        ("registration", "Registration/License", "Roʻyxat/Guvohnoma/Jarima", "Регистрация/Права/Штрафы"),
        ("other", "Other", "Boshqa", "Прочее"),
    ]),
    ("health", "HEALTH", "SOGʻLIQ", "ЗДОРОВЬЕ", [
        ("insurance", "Health Insurance", "Tibbiy sugʻurta", "Медстраховка"),
        ("doctor", "Doctor/Dentist", "Shifokor/Tish shifokori", "Врач/Стоматолог"),
        ("medicine", "Medicine/Drugs", "Dori-darmon", "Лекарства"),
        ("club", "Health Club Dues", "Fitnes/Sport zal", "Фитнес-клуб"),
        ("life", "Life Insurance", "Hayot sugʻurtasi", "Страхование жизни"),
        ("vet", "Veterinarian/Pet Care", "Veterinar/Uy hayvonlari", "Ветеринар/Питомцы"),
        ("other", "Other", "Boshqa", "Прочее"),
    ]),
    ("charity", "CHARITY/GIFTS", "XAYRIYA/SOVGʻALAR", "БЛАГОТВОРИТЕЛЬНОСТЬ/ПОДАРКИ", [
        ("gifts", "Gifts Given", "Sovgʻalar", "Подарки"),
        ("charity", "Charitable Donations", "Xayriya", "Благотворительность"),
        ("religious", "Religious Donations", "Sadaqa/Diniy xayriya", "Религиозные пожертвования"),
        ("other", "Other", "Boshqa", "Прочее"),
    ]),
    ("daily", "DAILY LIVING", "KUNDALIK EHTIYOJLAR", "ПОВСЕДНЕВНЫЕ РАСХОДЫ", [
        ("groceries", "Groceries", "Oziq-ovqat", "Продукты"),
        ("supplies", "Personal Supplies", "Shaxsiy buyumlar", "Личные принадлежности"),
        ("clothing", "Clothing", "Kiyim-kechak", "Одежда"),
        ("cleaning", "Cleaning", "Tozalash/Uy-roʻzgʻor", "Уборка"),
        ("education", "Education/Lessons", "Taʼlim/Darslar", "Образование/Уроки"),
        ("dining", "Dining/Eating Out", "Restoran/Kafe", "Кафе/Рестораны"),
        ("salon", "Salon/Barber", "Salon/Sartarosh", "Салон/Парикмахерская"),
        ("petfood", "Pet Food", "Hayvon ozuqasi", "Корм для питомцев"),
        ("other", "Other", "Boshqa", "Прочее"),
    ]),
    ("fun", "ENTERTAINMENT", "KOʻNGIL OCHAR", "РАЗВЛЕЧЕНИЯ", [
        ("activities", "Activities", "Tadbirlar", "Мероприятия"),
        ("books", "Books", "Kitoblar", "Книги"),
        ("games", "Games", "Oʻyinlar", "Игры"),
        ("stuff", "Fun Stuff", "Koʻngilochar narsalar", "Развлечения"),
        ("hobbies", "Hobbies", "Xobbi", "Хобби"),
        ("media", "Media", "Kino/Musiqa", "Кино/Музыка"),
        ("outdoor", "Outdoor Recreation", "Tabiatda dam olish", "Отдых на природе"),
        ("sports", "Sports", "Sport", "Спорт"),
        ("gadgets", "Toys/Gadgets", "Oʻyinchoq/Gadjetlar", "Игрушки/Гаджеты"),
        ("travel", "Vacation/Travel", "Sayohat/Taʼtil", "Отпуск/Путешествия"),
        ("other", "Other", "Boshqa", "Прочее"),
    ]),
    ("savings", "SAVINGS", "JAMGʻARMA", "НАКОПЛЕНИЯ", [
        ("emergency", "Emergency Fund", "Favqulodda zaxira", "Резервный фонд"),
        ("car", "Car Replacement", "Mashina almashtirish", "Замена авто"),
        ("retirement", "Retirement Fund", "Pensiya jamgʻarmasi", "Пенсионные накопления"),
        ("investments", "Investments", "Investitsiyalar", "Инвестиции"),
        ("education", "Education Fund", "Taʼlim jamgʻarmasi", "Фонд образования"),
        ("other", "Other", "Boshqa", "Прочее"),
    ]),
    ("oblig", "OBLIGATIONS", "MAJBURIYATLAR", "ОБЯЗАТЕЛЬСТВА", [
        ("student", "Student Loans", "Taʼlim krediti", "Студенческий кредит"),
        ("card", "Credit Card Debt", "Kredit karta qarzi", "Долг по кредитной карте"),
        ("loans", "Other Loans", "Boshqa kreditlar", "Другие кредиты"),
        ("alimony", "Alimony/Child Support", "Aliment", "Алименты"),
        ("federal", "Federal Taxes", "Davlat soliqlari", "Государственные налоги"),
        ("local", "State/Local Taxes", "Mahalliy soliqlar", "Местные налоги"),
        ("other", "Other", "Boshqa", "Прочее"),
    ]),
    ("subs", "SUBSCRIPTIONS", "OBUNALAR", "ПОДПИСКИ", [
        ("newspaper", "Newspaper", "Gazeta", "Газета"),
        ("magazines", "Magazines", "Jurnallar", "Журналы"),
        ("dues", "Dues/Memberships", "Obuna/Aʼzolik", "Подписки/Членство"),
        ("other", "Other", "Boshqa", "Прочее"),
    ]),
    ("misc", "MISCELLANEOUS", "BOSHQA XARAJATLAR", "ПРОЧЕЕ", [
        ("bank", "Bank Fees", "Bank komissiyasi", "Банковские комиссии"),
        ("postage", "Postage", "Pochta/Yetkazib berish", "Почта/Доставка"),
        ("other", "Other", "Boshqa", "Прочее"),
        ("other2", "Other", "Boshqa", "Прочее"),
    ]),
]

LANG_IDX = {"en": 1, "uz": 2, "ru": 3}
FALLBACK_CAT = "misc.other"
GROUP_KEYS = [g[0] for g in GROUPS]


def group_name(lang: str, gkey: str) -> str:
    for g in GROUPS:
        if g[0] == gkey:
            return g[LANG_IDX[lang]]
    return gkey


def sub_name(lang: str, cat: str) -> str:
    g, s = cat.split(".", 1)
    for grp in GROUPS:
        if grp[0] == g:
            for sub in grp[4]:
                if sub[0] == s:
                    return sub[LANG_IDX[lang]]
    return cat


def split_cat(cat: Optional[str]) -> tuple:
    """'daily.clothing' -> ('daily', 'clothing'); None/unknown -> fallback."""
    cat = cat or FALLBACK_CAT
    if "." not in cat:
        cat = FALLBACK_CAT
    return tuple(cat.split(".", 1))


def valid_cat(cat: str) -> bool:
    g, _, s = (cat or "").partition(".")
    return any(grp[0] == g and any(sub[0] == s for sub in grp[4]) for grp in GROUPS)


def cat_label(lang: str, cat: Optional[str]) -> str:
    g, _ = split_cat(cat)
    return f"{group_name(lang, g).capitalize()} › {sub_name(lang, cat or FALLBACK_CAT)}"


# --------------------------------------------------------------------------- normalisation
_APOS = "'ʻʼ’‘`´"
_STOP = set("""
oldim oldik olindi oldi sotib sotibolish sotib oldim xarid uchun berdim berdik toladim toladik tolov
tolab xarajat xarajati pul puli puliga som sum ta dona kg gr g l litr sht va bilan bugun kecha ertalab
kechqurun ga ni dan da ning да купил купила купили за на заплатил заплатила оплатил оплатила сум сумм руб
bought paid for a the some and to on
""".split())


def norm(text: str) -> str:
    t = text.lower().replace("ё", "е")
    for ch in _APOS:
        t = t.replace(ch, "")
    t = re.sub(r"[^\w\s-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def rule_key(item: str) -> str:
    """Stable key for a user's learned rule: content words only (no numbers/units/verbs)."""
    toks = [w for w in norm(item).split() if not re.fullmatch(r"[\d.,-]+", w) and w not in _STOP]
    return " ".join(toks[:4])


# --------------------------------------------------------------------------- keyword rules
def W(*stems: str) -> str:
    """Word-prefix match: \\b(stem1|stem2|...). Add \\b at the end of a stem for an exact word."""
    return r"\b(?:" + "|".join(stems) + ")"


RULES: list = []


def _r(cat: str, pattern: str) -> None:
    RULES.append((re.compile(pattern), cat))


# ---- most specific first --------------------------------------------------------------
# vehicle
_r("transport.repairs",
   r"(?:mashina|avto|avtomobil|машин|авто|nexia|gentra|cobalt|kobalt|matiz|chevrolet).*(?:remont|tamir|ремонт|repair)"
   r"|(?:remont|tamir|ремонт|repair).*(?:mashina|avto|машин|авто)|"
   + W("balon", "shina", "vulkaniz", "akkumulyator", "zapchast", "запчаст", "шины", "шиномонтаж",
       "moy ?almash", "moy ?alishtir", "moyka", "мойк", "car ?wash", "mashina yuv"))
_r("transport.insurance", W("avto ?sugurta", "osago", "каско", "осаго", "kasko", "auto insurance", "car insurance"))
_r("transport.fuel", W("benzin", "metan", "propan", "solyarka", "dizel", "yoqilgi", "yoqilg", "azs\\b", "бензин",
                         "заправк", "заправил", "fuel", "petrol", "gas station", "ai-?9\\d", "ai ?9\\d"))
_r("transport.fare", W("taksi", "taxi", "yandex", "mytaxi", "bolt\\b", "uber", "avtobus", "metro", "poyezd", "poezd",
                         "elektrichka", "yol ?kira", "marshrutka", "такси", "автобус", "метро", "поезд", "проезд",
                         "bus\\b", "train", "fare\\b", "transport"))
_r("transport.registration", W("prava\\b", "guvohnoma", "haydovchilik", "texosmotr", "tex ?osmotr", "техосмотр",
                               "jarima", "штраф", "права\\b", "license", "registration", "royxat"))
_r("transport.payments", W("lizing", "avtokredit", "лизинг", "автокредит"))

# insurance (generic variants)
_r("health.life", W("hayot ?sugurta", "страхование жизни", "life insurance"))
_r("health.insurance", W("tibbiy ?sugurta", "медстрах", "health insurance"))
_r("home.insurance", W("uy ?sugurta", "kvartira ?sugurta", "страхование (?:жилья|квартиры|дома)", "home insurance"))

# home & utilities
_r("home.rent", W("ijara", "kvartira", "kvartplata", "arenda", "аренд", "квартир", "ipoteka", "ипотек", "xonadon",
                  "rent\\b", "mortgage"))
_r("home.electricity", W("elektr", "svet\\b", "свет\\b", "электр", "tok ?puli", "electric", "light bill"))
_r("home.water", W("suv ?puli", "suv ?tolov", "kommunal", "коммунал", "chiqindi", "musor", "мусор", "kanalizats",
                   "канализ", "водоснабж", "water bill", "sewer", "trash"))
_r("home.gas", W("gaz\\b", "gaz ?puli", "газ\\b", "gas bill"))
_r("home.phone", W("telefon ?(?:balans|puli|tolov|raqam)", "balans", "paynet", "ucell", "beeline", "uzmobile", "mobiuz",
                   "humans", "mobil ?aloqa", "пополнение", "пополнил", "баланс", "связь", "phone bill", "top ?up",
                   "tarif\\b", "тариф"))
_r("home.cable", W("kabel", "sputnik", "iptv", "tv ?puli", "кабельн", "спутник", "tvbox"))
_r("home.internet", W("internet", "wifi", "wi-?fi", "интернет", "vayfay", "provayder", "wi fi"))
_r("home.furnishings", W("mebel", "divan", "shkaf", "stol\\b", "stul\\b", "krovat", "muzlatgich", "kir ?yuvish ?mashina",
                         "konditsioner", "televizor", "pylesos", "changyutgich", "texnika", "jihoz", "мебел", "диван",
                         "шкаф", "холодильник", "стиральн", "кондиционер", "пылесос", "техник", "furniture", "appliance"))
_r("home.lawn", W("bogh", "hovli", "gazon", "газон", "огород", "сад\\b", "daraxt", "kochat", "urugl", "семена",
                  "ugit", "удобрен", "lawn", "garden"))
_r("home.improvements", W("uy ?qurish", "kapital ?remont", "evroremont", "евроремонт", "renovat", "yaxshilash"))
_r("home.maintenance", W("remont", "tamir", "santexnik", "slesar", "ремонт", "сантех", "boyoq", "kraska", "qurilish",
                         "lampa", "shurup", "gvozd", "maintenance", "plumber", "elektrik", "электрик"))

# health
_r("health.club", W("fitnes", "fitness", "sport ?zal", "sportzal", "trenajyor", "basseyn", "бассейн", "фитнес",
                    "тренажер", "спортзал", "gym\\b", "yoga"))
_r("health.vet", W("veterinar", "ветеринар", "vet\\b", "pet ?care", "mushuk(?:ni)? ?(?:davo|ukol|vet)", "it ?davo"))
_r("health.medicine", W("dori", "apteka", "tabletka", "vitamin", "sirop", "lekarstv", "аптек", "лекарств", "таблетк",
                        "витамин", "медикамент", "medicine", "pharmacy", "drugstore"))
_r("health.doctor", W("shifokor", "vrach", "doktor", "tish\\b", "stomatolog", "klinika", "kasalxona", "poliklinika",
                      "tahlil", "analiz", "ukol", "uzi\\b", "mrt\\b", "rentgen", "massaj", "врач", "доктор", "зуб",
                      "стоматолог", "клиник", "больниц", "анализ", "узи\\b", "doctor", "dentist", "hospital", "clinic"))

# charity & gifts
_r("charity.religious", W("sadaqa", "zakot", "fitr", "masjid", "qurbon", "hayit", "diniy", "милостын", "закят",
                          "садака", "пожертвован", "church", "mosque", "tithe"))
_r("charity.charity", W("xayriya", "ehson", "yetim", "nogiron", "благотвор", "donat", "charity"))
_r("charity.gifts", W("sovga", "hadya", "podarok", "подар", "gift", "tugilgan ?kun", "toyga", "toy ?puli",
                      "свадьб", "день рожден", "birthday"))

# savings & obligations
_r("savings.emergency", W("favqulodda", "zaxira", "резерв", "emergency"))
_r("savings.retirement", W("pensiya", "пенси", "retire"))
_r("savings.education", W("talim ?jamg", "фонд образ", "education fund"))
_r("savings.investments", W("investitsiya", "aksiya", "obligatsiya", "bitcoin", "btc\\b", "kripto", "crypto", "инвест",
                            "акци[июя]", "depozit", "deposit", "омонат", "omonat"))
_r("savings.car", W("mashina ?uchun ?jamg", "avto ?jamg", "car fund"))
_r("savings.other", W("jamgar", "копил", "накоплен", "saving", "tejadim"))
_r("oblig.student", W("talaba ?kredit", "student loan", "студенческ"))
_r("oblig.card", W("kredit ?karta", "кредитн\\w* ?карт", "credit card", "karta ?qarz"))
_r("oblig.alimony", W("aliment", "алимент", "nafaqa", "child support"))
_r("oblig.local", W("mahalliy ?soliq", "yer ?solig", "mulk ?solig", "земельн\\w* налог", "налог на имущ", "property tax",
                    "local tax"))
_r("oblig.federal", W("soliq", "налог", "tax\\b", "taxes"))
_r("oblig.loans", W("kredit", "qarz", "nasiya", "rassrochka", "рассрочк", "кредит", "долг", "zaym", "займ", "loan",
                    "ssuda", "mikroqarz"))

# subscriptions & misc
_r("subs.newspaper", W("gazeta", "газет", "newspaper"))
_r("subs.magazines", W("jurnal", "журнал", "magazine"))
_r("subs.dues", W("azolik", "obuna", "podpis", "подпис", "netflix", "spotify", "youtube", "premium", "apple ?music",
                  "icloud", "chatgpt", "claude", "subscription", "yandex ?plus", "членск", "membership", "vpn\\b",
                  "kinopoisk", "disney", "hbo", "google ?one", "dropbox", "canva", "notion"))
_r("misc.bank", W("komissiya", "komissiy", "bank ?xizmat", "комисси", "bank fee", "fee\\b", "sms ?xizmat"))
_r("misc.postage", W("pochta", "почт", "postage", "yetkazib ?ber", "dostavka", "доставк", "kuryer", "курьер", "cdek",
                     "yandex ?dostavka"))

# daily living
_r("daily.petfood", W("it ?ozuq", "mushuk ?ozuq", "korm\\b", "корм", "pet ?food", "hayvon ?ozuq", "kuchuk ?ozuq"))
_r("daily.education", W("kontrakt", "maktab", "universitet", "kurs\\b", "kurslar", "repetitor", "dars\\b", "darslar",
                        "ielts", "bogcha", "talim", "oquv", "школ", "университет", "курсы", "репетитор", "урок",
                        "обучен", "tuition", "lesson", "course", "school", "kindergarten", "детсад"))
_r("daily.salon", W("sartarosh", "salon", "manikyur", "pedikyur", "soch ?olish", "barber", "парикмахер", "маникюр",
                    "стрижк", "салон", "haircut", "gozallik", "nail\\b", "spa\\b"))
_r("daily.clothing", W("paypoq", "kiyim", "koylak", "shim\\b", "shimlar", "kurtka", "poyabzal", "krossovka", "etik\\b",
                       "tufli", "futbolka", "shapka", "qolqop", "palto", "kostyum", "libos", "sumka", "noski",
                       "носк", "одежд", "куртк", "джинс", "обув", "кроссов", "рубашк", "футболк", "платье", "ботинк",
                       "shoes", "socks", "shirt", "jeans", "clothes", "dress\\b", "jacket", "sneaker"))
_r("daily.cleaning", W("tozalash", "poroshok", "chistka", "ximchistka", "uborka", "supurgi", "latta", "gubka",
                       "чистящ", "порошок", "уборк", "химчистк", "губк", "clean", "detergent", "kir ?yuv"))
_r("daily.supplies", W("shampun", "kosmetika", "tish ?pasta", "pasta\\b", "prokladka", "salfetka", "salfet", "dezodorant",
                       "parfyum", "krem\\b", "shaxsiy", "sovun", "sochiq", "шампунь", "косметик", "зубная паста",
                       "гигиен", "дезодорант", "парфюм", "крем\\b", "бритва", "мыло", "razor", "toothpaste",
                       "shampoo", "soap", "supplies"))
_r("daily.dining", W("kafe", "restoran", "choyxona", "oshxona", "fast ?food", "shaurma", "lavash", "burger", "pitsa",
                     "pizza", "kofe", "coffee", "evos", "maxway", "bellissimo", "oqtepa", "lounge", "tushlik",
                     "kechki ?ovqat", "nonushta", "ovqatlan", "stolovaya", "столов", "кафе", "ресторан", "обед",
                     "ужин", "завтрак", "шаурма", "пицц", "кофе", "бургер", "lunch", "dinner", "breakfast",
                     "restaurant", "cafe", "starbucks", "kfc", "mcdonald", "dodo", "doner", "donar", "hot-?dog",
                     "xotdog", "ichimlik", "cola\\b", "kola\\b", "pepsi", "fanta", "sharbat", "choy ?ichdim",
                     "samsa", "somsa", "osh\\b", "plov", "палов"))
_r("daily.groceries", W("oziq", "ovqat", "non\\b", "nonlar", "gosht", "sut\\b", "sutli", "tuxum", "olma", "nok\\b",
                        "noklar", "banan", "uzum", "anor", "limon", "apelsin", "mandarin", "pomidor", "bodring",
                        "sabzi", "kartoshka", "piyoz", "sarimsoq", "guruch", "makaron", "yog\\b", "moy\\b", "un\\b",
                        "shakar", "tuz\\b", "choy\\b", "qaymoq", "qatiq", "pishloq", "sosiska", "kolbasa", "tovuq",
                        "baliq", "meva", "sabzavot", "poliz", "tarvuz", "qovun", "bozor", "bazar", "market",
                        "supermarket", "magazin", "korzinka", "makro\\b", "havas", "baraka", "konfet", "shokolad",
                        "pechenye", "yogurt", "ayron", "sok\\b", "suv\\b", "продукт", "хлеб", "молок", "мяс", "яйц",
                        "овощ", "фрукт", "яблок", "картош", "рис\\b", "сахар", "масл", "чай\\b", "сыр\\b", "колбас",
                        "курица", "рыба", "магазин", "рынок", "базар", "супермаркет", "grocer", "bread", "milk",
                        "meat", "eggs", "vegetable", "fruit", "apple", "rice\\b", "sugar", "tea\\b", "cheese"))

# entertainment (after the sub-/health-specific ones)
_r("fun.travel", W("sayohat", "aviabilet", "bilet", "mehmonxona", "hotel", "отель", "билет", "путешеств", "отпуск",
                   "turizm", "ekskursiya", "viza\\b", "visa\\b", "hostel", "booking", "airbnb", "samolyot", "reys",
                   "avia", "vacation", "trip\\b", "flight", "dam ?olish"))
_r("fun.gadgets", W("oyinchoq", "игрушк", "toy\\b", "toys", "lego", "konstruktor", "gadjet", "gadget", "telefon",
                    "phone\\b", "iphone", "samsung", "noutbuk", "laptop", "naushnik", "наушник", "ноутбук", "телефон",
                    "планшет", "planshet", "smartfon", "smartwatch"))
_r("fun.games", W("oyin", "game", "playstation", "ps5", "steam", "xbox", "pubg", "roblox", "nintendo", "игр",
                  "pc ?klub", "kompyuter ?klub"))
_r("fun.books", W("kitob", "kniga", "книг", "book", "darslik", "qissa", "roman\\b"))
_r("fun.activities", W("konsert", "teatr", "sirk", "muzey", "attraksion", "akvapark", "aquapark", "bouling", "bowling",
                       "bilyard", "karaoke", "festival", "tadbir", "мероприят", "концерт", "театр", "музей",
                       "аттракцион", "аквапарк", "боулинг", "бильярд", "караоке", "party", "ziyofat", "event\\b"))
_r("fun.media", W("kino", "film", "кино", "фильм", "musiqa", "music", "музык", "podcast", "media"))
_r("fun.outdoor", W("piknik", "kemping", "palatka", "baliq ?ovlash", "treking", "поход", "природ", "park\\b", "sayr",
                    "camping", "hiking", "fishing", "ot ?minish", "dacha", "дача"))
_r("fun.sports", W("sport", "futbol", "tennis", "basketbol", "velosiped", "velik", "yugurish", "boks", "kurash",
                   "plavan", "футбол", "теннис", "спорт", "велосипед", "koptok", "stadion"))
_r("fun.hobbies", W("hobbi", "xobbi", "xobby", "gitara", "rangtasvir", "tikish", "toqish", "коллекц", "хобби",
                    "рукодел", "guitar", "fotoapparat", "kamera", "foto\\b", "hobby"))
_r("fun.stuff", W("zavq", "ermak", "fun\\b", "развлеч", "kayf"))


def classify(item: str, user_rules: Optional[dict] = None) -> Optional[str]:
    """Return 'group.sub' or None when nothing matches (the bot then asks the user)."""
    text = norm(item)
    if not text:
        return None
    if user_rules:                                   # what this user taught the bot beats built-in rules
        toks = set(rule_key(item).split())
        key = rule_key(item)
        if key in user_rules:
            return user_rules[key]
        best = None
        for k, cat in user_rules.items():
            kt = set(k.split())
            if kt and kt <= toks and (best is None or len(kt) > best[0]):
                best = (len(kt), cat)
        if best:
            return best[1]
    for rx, cat in RULES:
        if rx.search(text):
            return cat
    return None
