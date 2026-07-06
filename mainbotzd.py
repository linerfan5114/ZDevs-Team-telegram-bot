import json
import os
import random
import html
from datetime import datetime

import telebot
from telebot import types

BOT_TOKEN = "8382359167:AAG-i1VU_eTXXyQLo4WLBD5okKhlmg9cPa4"
ADMIN_IDS = []
DATA_FILE = "team_bot_data.json"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

pending = {}


def esc(value):
    return html.escape(str(value))


def _empty_data():
    return {
        "members": {},
        "ideas": [],
        "projects": [],
        "challenges": [],
        "scores": {},
        "next_idea_id": 1,
        "next_project_id": 1,
        "next_challenge_id": 1,
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        return _empty_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in _empty_data().items():
            data.setdefault(k, v)
        return data
    except (json.JSONDecodeError, OSError):
        return _empty_data()


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(DATA, f, ensure_ascii=False, indent=2)


DATA = load_data()


def upsert_member(user_id, username, name, expertise, birthdate, major, term, skills, location):
    key = str(user_id)
    joined_at = DATA["members"].get(key, {}).get("joined_at") or datetime.now().strftime("%Y-%m-%d %H:%M")
    DATA["members"][key] = {
        "user_id": user_id,
        "username": username,
        "name": name,
        "expertise": expertise,
        "birthdate": birthdate,
        "major": major,
        "term": term,
        "skills": skills,
        "location": location,
        "joined_at": joined_at,
    }
    save_data()


def get_member(user_id):
    return DATA["members"].get(str(user_id))


def get_all_members():
    return sorted(DATA["members"].values(), key=lambda m: m["joined_at"])


def add_idea(user_id, username, topic, description):
    idea = {
        "id": DATA["next_idea_id"],
        "user_id": user_id,
        "username": username,
        "topic": topic,
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    DATA["ideas"].append(idea)
    DATA["next_idea_id"] += 1
    save_data()


def get_all_ideas():
    return sorted(DATA["ideas"], key=lambda i: i["id"], reverse=True)


STATUS_DEV = "در حال توسعه"
STATUS_DONE = "اتمام یافته"


def add_project(name, description, doers, employer, status, creator_id):
    project = {
        "id": DATA["next_project_id"],
        "name": name,
        "description": description,
        "doers": doers,
        "employer": employer,
        "status": status,
        "creator_id": creator_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    DATA["projects"].append(project)
    DATA["next_project_id"] += 1
    save_data()


def get_all_projects(status_filter=None):
    projects = DATA["projects"]
    if status_filter:
        projects = [p for p in projects if p["status"] == status_filter]
    return sorted(projects, key=lambda p: p["id"], reverse=True)


def get_project(project_id):
    for p in DATA["projects"]:
        if p["id"] == project_id:
            return p
    return None


def update_project_status(project_id, status):
    p = get_project(project_id)
    if p:
        p["status"] = status
        save_data()


def add_challenge(question, a, b, c, d, correct):
    challenge = {
        "id": DATA["next_challenge_id"],
        "question": question,
        "option_a": a,
        "option_b": b,
        "option_c": c,
        "option_d": d,
        "correct_option": correct.upper(),
    }
    DATA["challenges"].append(challenge)
    DATA["next_challenge_id"] += 1
    save_data()


def get_random_challenge():
    if not DATA["challenges"]:
        return None
    return random.choice(DATA["challenges"])


def get_challenge(challenge_id):
    for c in DATA["challenges"]:
        if c["id"] == challenge_id:
            return c
    return None


SEED_QUESTIONS = [
    {"question": "پیچیدگی زمانی جستجوی دودویی (Binary Search) در بدترین حالت چیه؟",
     "a": "O(1)", "b": "O(log n)", "c": "O(n)", "d": "O(n^2)", "correct": "B"},
    {"question": "کدوم ساختار داده از قانون LIFO (آخرین ورودی، اولین خروجی) پیروی می‌کنه؟",
     "a": "Queue", "b": "Stack", "c": "Linked List", "d": "Heap", "correct": "B"},
    {"question": "در پایتون، خروجی type([]) چیه؟",
     "a": "list", "b": "array", "c": "tuple", "d": "set", "correct": "A"},
    {"question": "کدوم مورد یک زبان برنامه‌نویسی نیست؟",
     "a": "Rust", "b": "Kotlin", "c": "HTML", "d": "Go", "correct": "C"},
    {"question": "در Git، دستور git commit چه کاری انجام میده؟",
     "a": "تغییرات رو به سرور ریموت push می‌کنه",
     "b": "یک نسخه‌ی جدید از تغییرات staged رو در تاریخچه ذخیره می‌کنه",
     "c": "یک شاخه‌ی جدید می‌سازه", "d": "فایل‌ها رو حذف می‌کنه", "correct": "B"},
    {"question": "HTTP status code شماره 404 به چه معناست؟",
     "a": "درخواست موفق بوده", "b": "خطای سرور", "c": "منبع پیدا نشد", "d": "دسترسی غیرمجاز", "correct": "C"},
    {"question": "کدوم مورد یک پایگاه داده‌ی NoSQL هست؟",
     "a": "MySQL", "b": "PostgreSQL", "c": "MongoDB", "d": "SQLite", "correct": "C"},
    {"question": "در برنامه‌نویسی شیءگرا، مفهوم Inheritance به چه معناست؟",
     "a": "پنهان‌سازی جزئیات پیاده‌سازی",
     "b": "به ارث بردن ویژگی‌ها و رفتار از یک کلاس دیگه",
     "c": "تبدیل نوع داده", "d": "اجرای همزمان چند تسک", "correct": "B"},
    {"question": "کدوم مورد یک الگوریتم مرتب‌سازی نیست؟",
     "a": "Bubble Sort", "b": "Quick Sort", "c": "Merge Sort", "d": "Binary Search", "correct": "D"},
    {"question": "در جاوااسکریپت، const چه فرقی با let داره؟",
     "a": "هیچ فرقی ندارن", "b": "مقدار متغیر const بعد از تعریف قابل تغییر نیست",
     "c": "const فقط برای رشته‌ها استفاده میشه", "d": "let فقط داخل توابع کار می‌کنه", "correct": "B"},
    {"question": "REST API معمولا از کدوم فرمت داده برای تبادل اطلاعات استفاده می‌کنه؟",
     "a": "JSON", "b": "EXE", "c": "MP3", "d": "ISO", "correct": "A"},
    {"question": "پیچیدگی زمانی الگوریتم Bubble Sort در بدترین حالت چقدره؟",
     "a": "O(n log n)", "b": "O(n)", "c": "O(n^2)", "d": "O(1)", "correct": "C"},
]


def seed_challenges_if_empty():
    if not DATA["challenges"]:
        for q in SEED_QUESTIONS:
            add_challenge(q["question"], q["a"], q["b"], q["c"], q["d"], q["correct"])


def update_score(user_id, username, delta):
    key = str(user_id)
    if key not in DATA["scores"]:
        DATA["scores"][key] = {"user_id": user_id, "username": username, "score": 0, "answered": 0}
    DATA["scores"][key]["username"] = username
    DATA["scores"][key]["score"] += delta
    DATA["scores"][key]["answered"] += 1
    save_data()


def get_leaderboard(limit=10):
    scores = list(DATA["scores"].values())
    scores.sort(key=lambda s: s["score"], reverse=True)
    return scores[:limit]


BTN_PROFILE = "👤 عضویت / پروفایل من"
BTN_MEMBERS = "👥 لیست اعضای تیم"
BTN_IDEAS = "💡 ایده‌ها"
BTN_PROJECTS = "📁 پروژه‌ها"
BTN_CHALLENGE = "🎯 چالش برنامه‌نویسی"
BTN_LEADERBOARD = "🏆 جدول امتیازات"
BTN_HELP = "ℹ️ راهنما"


def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(types.KeyboardButton(BTN_PROFILE), types.KeyboardButton(BTN_MEMBERS))
    kb.add(types.KeyboardButton(BTN_IDEAS), types.KeyboardButton(BTN_PROJECTS))
    kb.add(types.KeyboardButton(BTN_CHALLENGE), types.KeyboardButton(BTN_LEADERBOARD))
    kb.add(types.KeyboardButton(BTN_HELP))
    return kb


def is_admin(user_id):
    return user_id in ADMIN_IDS


def uname(from_user):
    return f"@{from_user.username}" if from_user.username else from_user.first_name


def send_long(chat_id, text, chunk_size=3500):
    for start in range(0, len(text), chunk_size):
        bot.send_message(chat_id, text[start:start + chunk_size])


def set_pending(chat_id, user_id, step, data=None):
    pending[(chat_id, user_id)] = {"step": step, "data": data or {}}


def get_pending(chat_id, user_id):
    return pending.get((chat_id, user_id))


def clear_pending(chat_id, user_id):
    pending.pop((chat_id, user_id), None)


@bot.message_handler(commands=["start"])
def cmd_start(message):
    clear_pending(message.chat.id, message.from_user.id)
    text = (
        f"سلام {esc(message.from_user.first_name)} 👋\n\n"
        "به ربات مدیریت تیم برنامه‌نویسی خوش اومدی!\n"
        "این ربات برای تیم زیر ساخته شده:\n"
        "🔗 https://t.me/zdevs_tm\n\n"
        "از منوی پایین می‌تونی:\n"
        "• توی تیم عضو بشی و پروفایلت رو بسازی\n"
        "• اعضای تیم رو ببینی\n"
        "• ایده‌ی جدید ثبت کنی یا ایده‌های دیگران رو ببینی\n"
        "• پروژه ثبت کنی و وضعیتش رو مدیریت کنی\n"
        "• توی چالش‌های سرگرمی برنامه‌نویسی شرکت کنی و امتیاز بگیری\n\n"
        "برای شروع یکی از دکمه‌های پایین رو بزن 👇"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())


def show_help(chat_id):
    text = (
        "📖 <b>راهنمای ربات</b>\n\n"
        f"{esc(BTN_PROFILE)}\nثبت‌نام توی تیم یا مشاهده و ویرایش پروفایلت\n\n"
        f"{esc(BTN_MEMBERS)}\nمشاهده لیست همه‌ی اعضای ثبت‌شده تیم\n\n"
        f"{esc(BTN_IDEAS)}\nثبت ایده‌ی جدید یا دیدن ایده‌های ثبت‌شده\n\n"
        f"{esc(BTN_PROJECTS)}\nثبت پروژه‌ی جدید، دیدن لیست پروژه‌ها و تغییر وضعیتشون\n\n"
        f"{esc(BTN_CHALLENGE)}\nیه سوال تصادفی برنامه‌نویسی جواب بده و امتیاز بگیر\n\n"
        f"{esc(BTN_LEADERBOARD)}\nجدول برترین امتیازها توی چالش‌ها\n\n"
        "هر موقع وسط یه فرم گیر کردی، دستور /cancel رو بفرست تا لغو بشه."
    )
    bot.send_message(chat_id, text)


@bot.message_handler(commands=["help"])
def cmd_help(message):
    show_help(message.chat.id)


@bot.message_handler(commands=["cancel"])
def cmd_cancel(message):
    clear_pending(message.chat.id, message.from_user.id)
    bot.send_message(message.chat.id, "❌ عملیات لغو شد.", reply_markup=main_menu())


def show_profile(chat_id, m):
    text = (
        "🪪 <b>پروفایل عضو تیم</b>\n\n"
        f"👤 نام: {esc(m['name'])}\n"
        f"🔗 یوزرنیم: {esc(m['username'] or '—')}\n"
        f"🛠 فیلد تخصص: {esc(m['expertise'])}\n"
        f"🎂 تاریخ تولد: {esc(m['birthdate'])}\n"
        f"🎓 رشته: {esc(m['major'])}\n"
        f"📚 ترم: {esc(m['term'])}\n"
        f"⚡️ اسکیل‌ها: {esc(m['skills'])}\n"
        f"📍 محل سکونت: {esc(m['location'])}\n"
    )
    bot.send_message(chat_id, text)


def start_registration(chat_id, user_id):
    set_pending(chat_id, user_id, "reg_name")
    bot.send_message(
        chat_id,
        "بریم چند تا سوال کوتاه بپرسم تا پروفایلت ساخته بشه.\n\n"
        "1️⃣ اسمت (نام و نام خانوادگی) چیه؟\n"
        "(هر موقع خواستی لغو کنی، /cancel رو بزن)"
    )


def profile_entry(message):
    member = get_member(message.from_user.id)
    if member:
        show_profile(message.chat.id, member)
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="edit_profile"))
        bot.send_message(message.chat.id, "می‌خوای اطلاعاتت رو ویرایش کنی؟", reply_markup=kb)
    else:
        start_registration(message.chat.id, message.from_user.id)


@bot.callback_query_handler(func=lambda c: c.data == "edit_profile")
def edit_profile_cb(call):
    bot.answer_callback_query(call.id)
    start_registration(call.message.chat.id, call.from_user.id)


def step_reg_name(message, data):
    data["name"] = message.text.strip()
    bot.send_message(message.chat.id, "2️⃣ فیلد تخصصت چیه؟ (مثلا: بک‌اند، فرانت‌اند، موبایل، هوش مصنوعی و ...)")
    return "reg_expertise"


def step_reg_expertise(message, data):
    data["expertise"] = message.text.strip()
    bot.send_message(message.chat.id, "3️⃣ تاریخ تولدت چیه؟ (مثلا: 1380/05/12)")
    return "reg_birthdate"


def step_reg_birthdate(message, data):
    data["birthdate"] = message.text.strip()
    bot.send_message(message.chat.id, "4️⃣ رشته‌ی تحصیلیت چیه؟")
    return "reg_major"


def step_reg_major(message, data):
    data["major"] = message.text.strip()
    bot.send_message(message.chat.id, "5️⃣ ترم چندی؟")
    return "reg_term"


def step_reg_term(message, data):
    data["term"] = message.text.strip()
    bot.send_message(message.chat.id, "6️⃣ اسکیل‌هات رو با کاما (,) از هم جدا کن\nمثلا: Python, Django, React")
    return "reg_skills"


def step_reg_skills(message, data):
    data["skills"] = message.text.strip()
    bot.send_message(message.chat.id, "7️⃣ محل سکونتت کجاست؟ (شهر)")
    return "reg_location"


def step_reg_location(message, data):
    data["location"] = message.text.strip()
    username = uname(message.from_user)
    upsert_member(
        user_id=message.from_user.id,
        username=username,
        name=data["name"],
        expertise=data["expertise"],
        birthdate=data["birthdate"],
        major=data["major"],
        term=data["term"],
        skills=data["skills"],
        location=data["location"],
    )
    bot.send_message(message.chat.id, "✅ پروفایلت با موفقیت ثبت شد! خوش اومدی به تیم 🎉", reply_markup=main_menu())
    show_profile(message.chat.id, get_member(message.from_user.id))
    return None


def list_members(message):
    members = get_all_members()
    if not members:
        bot.send_message(message.chat.id, "هنوز هیچ عضوی توی تیم ثبت‌نام نکرده.")
        return
    text = f"👥 <b>اعضای تیم ({len(members)} نفر)</b>\n\n"
    for m in members:
        text += (
            f"— <b>{esc(m['name'])}</b> ({esc(m['username'] or '—')})\n"
            f"   🛠 {esc(m['expertise'])} | 🎓 {esc(m['major'])} ترم {esc(m['term'])}\n"
            f"   ⚡️ {esc(m['skills'])}\n"
            f"   📍 {esc(m['location'])}\n\n"
        )
    send_long(message.chat.id, text)


def ideas_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("➕ ثبت ایده جدید", callback_data="idea_new"))
    kb.add(types.InlineKeyboardButton("📋 مشاهده ایده‌ها", callback_data="idea_list"))
    return kb


def ideas_entry(message):
    bot.send_message(message.chat.id, "💡 بخش مدیریت ایده‌ها:", reply_markup=ideas_menu())


@bot.callback_query_handler(func=lambda c: c.data == "idea_new")
def idea_new_cb(call):
    bot.answer_callback_query(call.id)
    set_pending(call.message.chat.id, call.from_user.id, "idea_topic")
    bot.send_message(call.message.chat.id, "موضوع ایده رو بنویس:")


def step_idea_topic(message, data):
    data["topic"] = message.text.strip()
    bot.send_message(message.chat.id, "حالا توضیح کامل‌تری درباره ایده بده:")
    return "idea_description"


def step_idea_description(message, data):
    description = message.text.strip()
    username = uname(message.from_user)
    add_idea(message.from_user.id, username, data["topic"], description)
    bot.send_message(message.chat.id, "✅ ایده‌ات با موفقیت ثبت شد!", reply_markup=main_menu())
    return None


@bot.callback_query_handler(func=lambda c: c.data == "idea_list")
def idea_list_cb(call):
    bot.answer_callback_query(call.id)
    ideas = get_all_ideas()
    if not ideas:
        bot.send_message(call.message.chat.id, "هنوز هیچ ایده‌ای ثبت نشده.")
        return
    text = f"💡 <b>ایده‌های ثبت‌شده ({len(ideas)} مورد)</b>\n\n"
    for i in ideas:
        text += (
            f"#{i['id']} — <b>{esc(i['topic'])}</b>\n"
            f"   {esc(i['description'])}\n"
            f"   ثبت‌کننده: {esc(i['username'])} | {esc(i['created_at'])}\n\n"
        )
    send_long(call.message.chat.id, text)


def projects_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("➕ ثبت پروژه جدید", callback_data="proj_new"))
    kb.add(types.InlineKeyboardButton("📋 همه‌ی پروژه‌ها", callback_data="proj_list_all"))
    kb.add(
        types.InlineKeyboardButton("🚧 در حال توسعه", callback_data="proj_list_dev"),
        types.InlineKeyboardButton("✅ اتمام یافته", callback_data="proj_list_done"),
    )
    return kb


def projects_entry(message):
    bot.send_message(message.chat.id, "📁 بخش مدیریت پروژه‌ها:", reply_markup=projects_menu())


@bot.callback_query_handler(func=lambda c: c.data == "proj_new")
def proj_new_cb(call):
    bot.answer_callback_query(call.id)
    set_pending(call.message.chat.id, call.from_user.id, "proj_name")
    bot.send_message(call.message.chat.id, "نام پروژه رو بنویس:")


def step_proj_name(message, data):
    data["name"] = message.text.strip()
    bot.send_message(message.chat.id, "توضیح پروژه رو بنویس:")
    return "proj_description"


def step_proj_description(message, data):
    data["description"] = message.text.strip()
    bot.send_message(message.chat.id, "انجام‌دهنده(ها) رو بنویس (اسم یا یوزرنیم، با کاما جدا کن):")
    return "proj_doers"


def step_proj_doers(message, data):
    data["doers"] = message.text.strip()
    bot.send_message(message.chat.id, "کارفرما کیه؟ (اگه پروژه شخصی/تیمیه بنویس: ندارد)")
    return "proj_employer"


def step_proj_employer(message, data):
    data["employer"] = message.text.strip()
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🚧 در حال توسعه", callback_data="proj_save_dev"),
        types.InlineKeyboardButton("✅ اتمام یافته", callback_data="proj_save_done"),
    )
    bot.send_message(message.chat.id, "وضعیت فعلی پروژه چیه؟", reply_markup=kb)
    return "proj_status"


def step_proj_status(message, data):
    bot.send_message(message.chat.id, "لطفا از دکمه‌های بالا وضعیت رو انتخاب کن.")
    return "proj_status"


@bot.callback_query_handler(func=lambda c: c.data in ("proj_save_dev", "proj_save_done"))
def proj_save_cb(call):
    bot.answer_callback_query(call.id)
    key = (call.message.chat.id, call.from_user.id)
    info = pending.get(key)
    if not info or info.get("step") != "proj_status":
        bot.send_message(call.message.chat.id, "چیزی برای ذخیره پیدا نشد، دوباره امتحان کن.")
        return
    data = info["data"]
    status = STATUS_DEV if call.data == "proj_save_dev" else STATUS_DONE
    add_project(data["name"], data["description"], data["doers"], data["employer"], status, call.from_user.id)
    clear_pending(call.message.chat.id, call.from_user.id)
    bot.send_message(call.message.chat.id, "✅ پروژه با موفقیت ثبت شد!", reply_markup=main_menu())


def format_project(p):
    return (
        f"#{p['id']} — <b>{esc(p['name'])}</b>\n"
        f"   📝 {esc(p['description'])}\n"
        f"   👨‍💻 انجام‌دهندگان: {esc(p['doers'])}\n"
        f"   🏢 کارفرما: {esc(p['employer'])}\n"
        f"   📌 وضعیت: {esc(p['status'])}\n"
    )


@bot.callback_query_handler(func=lambda c: c.data in ("proj_list_all", "proj_list_dev", "proj_list_done"))
def proj_list_cb(call):
    bot.answer_callback_query(call.id)
    status_filter = None
    if call.data == "proj_list_dev":
        status_filter = STATUS_DEV
    elif call.data == "proj_list_done":
        status_filter = STATUS_DONE

    projects = get_all_projects(status_filter)
    if not projects:
        bot.send_message(call.message.chat.id, "پروژه‌ای با این فیلتر پیدا نشد.")
        return

    text = f"📁 <b>لیست پروژه‌ها ({len(projects)} مورد)</b>\n\n"
    text += "\n".join(format_project(p) for p in projects)
    send_long(call.message.chat.id, text)

    bot.send_message(
        call.message.chat.id,
        "برای تغییر وضعیت یه پروژه، دستور زیر رو با شماره‌ی پروژه بفرست:\n"
        "<code>/setstatus شماره</code>\n"
        "مثال: <code>/setstatus 3</code>"
    )


@bot.message_handler(commands=["setstatus"])
def cmd_setstatus(message):
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(message.chat.id, "فرمت درست: /setstatus شماره_پروژه")
        return
    project_id = int(parts[1])
    project = get_project(project_id)
    if not project:
        bot.send_message(message.chat.id, "پروژه‌ای با این شماره پیدا نشد.")
        return
    if project["creator_id"] != message.from_user.id and not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "فقط ثبت‌کننده‌ی پروژه یا ادمین می‌تونه وضعیتش رو تغییر بده.")
        return
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🚧 در حال توسعه", callback_data=f"proj_setstatus_{project_id}_dev"),
        types.InlineKeyboardButton("✅ اتمام یافته", callback_data=f"proj_setstatus_{project_id}_done"),
    )
    bot.send_message(message.chat.id, f"وضعیت جدید برای پروژه‌ی «{esc(project['name'])}» رو انتخاب کن:", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("proj_setstatus_"))
def proj_setstatus_cb(call):
    bot.answer_callback_query(call.id)
    _, _, project_id, new_status = call.data.split("_")
    status = STATUS_DEV if new_status == "dev" else STATUS_DONE
    update_project_status(int(project_id), status)
    bot.send_message(call.message.chat.id, f"✅ وضعیت پروژه به «{esc(status)}» تغییر کرد.")


def send_challenge(chat_id):
    q = get_random_challenge()
    if not q:
        bot.send_message(chat_id, "هنوز هیچ سوالی توی بانک چالش‌ها ثبت نشده.")
        return
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(f"A) {q['option_a']}", callback_data=f"chal_{q['id']}_A"))
    kb.add(types.InlineKeyboardButton(f"B) {q['option_b']}", callback_data=f"chal_{q['id']}_B"))
    kb.add(types.InlineKeyboardButton(f"C) {q['option_c']}", callback_data=f"chal_{q['id']}_C"))
    kb.add(types.InlineKeyboardButton(f"D) {q['option_d']}", callback_data=f"chal_{q['id']}_D"))
    bot.send_message(chat_id, f"🎯 <b>سوال:</b>\n\n{esc(q['question'])}", reply_markup=kb)


def challenge_entry(message):
    send_challenge(message.chat.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("chal_") and c.data != "chal_next")
def challenge_answer_cb(call):
    _, challenge_id, answer = call.data.split("_")
    q = get_challenge(int(challenge_id))
    if not q:
        bot.answer_callback_query(call.id, "این سوال دیگه در دسترس نیست.")
        return

    correct = q["correct_option"]
    username = uname(call.from_user)

    if answer == correct:
        update_score(call.from_user.id, username, 10)
        bot.answer_callback_query(call.id, "✅ آفرین! جواب درست بود. +10 امتیاز")
        result_text = "✅ جواب درست بود! +10 امتیاز 🎉"
    else:
        update_score(call.from_user.id, username, 0)
        correct_text = q[f"option_{correct.lower()}"]
        bot.answer_callback_query(call.id, "❌ جواب اشتباه بود.")
        result_text = f"❌ جواب اشتباه بود.\nجواب درست: {correct}) {esc(correct_text)}"

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("➡️ سوال بعدی", callback_data="chal_next"))
    bot.edit_message_text(
        f"🎯 {esc(q['question'])}\n\n{result_text}",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=kb,
    )


@bot.callback_query_handler(func=lambda c: c.data == "chal_next")
def challenge_next_cb(call):
    bot.answer_callback_query(call.id)
    send_challenge(call.message.chat.id)


def leaderboard_entry(message):
    top = get_leaderboard(10)
    if not top:
        bot.send_message(message.chat.id, "هنوز هیچ‌کس توی چالش‌ها شرکت نکرده. اولین نفر باش! 🚀")
        return
    text = "🏆 <b>جدول برترین امتیازها</b>\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for idx, row in enumerate(top):
        prefix = medals[idx] if idx < 3 else f"{idx + 1}."
        text += f"{prefix} {esc(row['username'])} — {row['score']} امتیاز ({row['answered']} سوال)\n"
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["addchallenge"])
def cmd_addchallenge(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "این دستور فقط برای ادمین‌های ربات در دسترسه.")
        return
    set_pending(message.chat.id, message.from_user.id, "chal_question")
    bot.send_message(message.chat.id, "متن سوال رو بنویس:")


def step_chal_question(message, data):
    data["question"] = message.text.strip()
    bot.send_message(message.chat.id, "گزینه A رو بنویس:")
    return "chal_a"


def step_chal_a(message, data):
    data["a"] = message.text.strip()
    bot.send_message(message.chat.id, "گزینه B رو بنویس:")
    return "chal_b"


def step_chal_b(message, data):
    data["b"] = message.text.strip()
    bot.send_message(message.chat.id, "گزینه C رو بنویس:")
    return "chal_c"


def step_chal_c(message, data):
    data["c"] = message.text.strip()
    bot.send_message(message.chat.id, "گزینه D رو بنویس:")
    return "chal_d"


def step_chal_d(message, data):
    data["d"] = message.text.strip()
    bot.send_message(message.chat.id, "کدوم گزینه درسته؟ (یکی از حروف A, B, C, D رو بفرست)")
    return "chal_correct"


def step_chal_correct(message, data):
    correct = message.text.strip().upper()
    if correct not in ("A", "B", "C", "D"):
        bot.send_message(message.chat.id, "فقط یکی از حروف A, B, C, D رو بفرست. دوباره امتحان کن.")
        return "chal_correct"
    add_challenge(data["question"], data["a"], data["b"], data["c"], data["d"], correct)
    bot.send_message(message.chat.id, "✅ سوال جدید به بانک چالش‌ها اضافه شد!", reply_markup=main_menu())
    return None


STEP_HANDLERS = {
    "reg_name": step_reg_name,
    "reg_expertise": step_reg_expertise,
    "reg_birthdate": step_reg_birthdate,
    "reg_major": step_reg_major,
    "reg_term": step_reg_term,
    "reg_skills": step_reg_skills,
    "reg_location": step_reg_location,
    "idea_topic": step_idea_topic,
    "idea_description": step_idea_description,
    "proj_name": step_proj_name,
    "proj_description": step_proj_description,
    "proj_doers": step_proj_doers,
    "proj_employer": step_proj_employer,
    "proj_status": step_proj_status,
    "chal_question": step_chal_question,
    "chal_a": step_chal_a,
    "chal_b": step_chal_b,
    "chal_c": step_chal_c,
    "chal_d": step_chal_d,
    "chal_correct": step_chal_correct,
}

BUTTON_HANDLERS = {
    BTN_PROFILE: profile_entry,
    BTN_MEMBERS: list_members,
    BTN_IDEAS: ideas_entry,
    BTN_PROJECTS: projects_entry,
    BTN_CHALLENGE: challenge_entry,
    BTN_LEADERBOARD: leaderboard_entry,
    BTN_HELP: lambda message: show_help(message.chat.id),
}


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.startswith("/"):
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.text in BUTTON_HANDLERS:
        clear_pending(chat_id, user_id)
        BUTTON_HANDLERS[message.text](message)
        return

    info = get_pending(chat_id, user_id)
    if info:
        handler_fn = STEP_HANDLERS.get(info["step"])
        if handler_fn:
            next_step = handler_fn(message, info["data"])
            if next_step:
                pending[(chat_id, user_id)] = {"step": next_step, "data": info["data"]}
            else:
                clear_pending(chat_id, user_id)


if __name__ == "__main__":
    seed_challenges_if_empty()
    print("ربات در حال اجراست")
    bot.infinity_polling(skip_pending=True)