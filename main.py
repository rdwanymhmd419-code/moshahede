# main.py

import os
import json
import logging

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update
)

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext
)

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("8229879923:AAE0I1Tv08kwSX2jHO7A6GNCDIr5jL8Ildo")
ADMIN_ID = int(os.getenv("5993860770"))

DB_FILE = "db.json"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# DATABASE
# =========================

def load_db():

    if not os.path.exists(DB_FILE):

        data = {

            "categories": [],

            "plans": [],

            "tickets": [],

            "settings": {

                "buy_color": "🟢",

                "support_color": "🔴",

                "test_color": "🔵"

            }

        }

        save_db(data)

        return data

    with open(DB_FILE, "r", encoding="utf-8") as f:

        return json.load(f)

def save_db(data):

    with open(DB_FILE, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

db = load_db()

# =========================
# HELPERS
# =========================

def is_admin(user_id):

    return int(user_id) == ADMIN_ID

def main_menu():

    buy_icon = db["settings"]["buy_color"]

    support_icon = db["settings"]["support_color"]

    test_icon = db["settings"]["test_color"]

    keyboard = [

        [

            InlineKeyboardButton(
                f"{buy_icon} خرید سرویس",
                callback_data="buy_service"
            )

        ],

        [

            InlineKeyboardButton(
                f"{support_icon} پشتیبانی",
                callback_data="support"
            )

        ],

        [

            InlineKeyboardButton(
                f"{test_icon} تست",
                callback_data="test"
            )

        ]

    ]

    return InlineKeyboardMarkup(keyboard)

def admin_menu():

    keyboard = [

        [

            InlineKeyboardButton(
                "📁 افزودن دسته بندی",
                callback_data="add_category"
            )

        ],

        [

            InlineKeyboardButton(
                "✏️ ویرایش دسته بندی",
                callback_data="edit_category"
            )

        ],

        [

            InlineKeyboardButton(
                "🗑 حذف دسته بندی",
                callback_data="delete_category"
            )

        ],

        [

            InlineKeyboardButton(
                "📦 افزودن پلن",
                callback_data="add_plan"
            )

        ],

        [

            InlineKeyboardButton(
                "✏️ ویرایش پلن",
                callback_data="edit_plan"
            )

        ],

        [

            InlineKeyboardButton(
                "🗑 حذف پلن",
                callback_data="delete_plan"
            )

        ],

        [

            InlineKeyboardButton(
                "🎨 تغییر رنگ دکمه ها",
                callback_data="colors"
            )

        ]

    ]

    return InlineKeyboardMarkup(keyboard)

# =========================
# STATES
# =========================

user_state = {}

# =========================
# START
# =========================

def start(update: Update, context: CallbackContext):

    user_id = update.effective_user.id

    if is_admin(user_id):

        update.message.reply_text(

            "👑 پنل مدیریت",

            reply_markup=admin_menu()

        )

    else:

        update.message.reply_text(

            "🏠 به فروشگاه خوش آمدید",

            reply_markup=main_menu()

        )

# =========================
# CALLBACKS
# =========================

def callbacks(update: Update, context: CallbackContext):

    query = update.callback_query

    query.answer()

    user_id = query.from_user.id

    data = query.data

    # =========================
    # BUY SERVICE
    # =========================

    if data == "buy_service":

        if len(db["categories"]) == 0:

            query.message.reply_text(
                "❌ دسته بندی وجود ندارد"
            )

            return

        keyboard = []

        for category in db["categories"]:

            keyboard.append([

                InlineKeyboardButton(

                    category["name"],

                    callback_data=
                    f"category_{category['id']}"

                )

            ])

        query.message.reply_text(

            "📁 دسته بندی را انتخاب کنید",

            reply_markup=
            InlineKeyboardMarkup(keyboard)

        )

    # =========================
    # SUPPORT
    # =========================

    elif data == "support":

        query.message.reply_text(

            "🆘 پشتیبانی:\n@support"

        )

    # =========================
    # TEST
    # =========================

    elif data == "test":

        query.message.reply_text(

            "✅ درخواست تست ثبت شد"

        )

    # =========================
    # SHOW PLANS
    # =========================

    elif data.startswith("category_"):

        category_id = int(
            data.split("_")[1]
        )

        keyboard = []

        found = False

        for plan in db["plans"]:

            if plan["category_id"] == category_id:

                found = True

                keyboard.append([

                    InlineKeyboardButton(

                        f"{plan['name']} | {plan['price']} تومان",

                        callback_data=
                        f"buy_{plan['id']}"

                    )

                ])

        if not found:

            query.message.reply_text(
                "❌ پلنی وجود ندارد"
            )

            return

        query.message.reply_text(

            "📦 پلن را انتخاب کنید",

            reply_markup=
            InlineKeyboardMarkup(keyboard)

        )

    # =========================
    # BUY PLAN
    # =========================

    elif data.startswith("buy_"):

        plan_id = int(
            data.split("_")[1]
        )

        selected_plan = None

        for plan in db["plans"]:

            if plan["id"] == plan_id:

                selected_plan = plan

                break

        if selected_plan is None:

            query.message.reply_text(
                "❌ پلن پیدا نشد"
            )

            return

        query.message.reply_text(

            f"✅ سفارش ثبت شد\n\n"

            f"📦 {selected_plan['name']}\n"

            f"💰 {selected_plan['price']} تومان\n\n"

            f"برای دریافت سرویس به پشتیبانی پیام دهید"

        )

    # =========================
    # ADD CATEGORY
    # =========================

    elif data == "add_category":

        user_state[user_id] = "add_category"

        query.message.reply_text(
            "📁 نام دسته بندی را ارسال کنید"
        )

    # =========================
    # DELETE CATEGORY
    # =========================

    elif data == "delete_category":

        if len(db["categories"]) == 0:

            query.message.reply_text(
                "❌ دسته بندی وجود ندارد"
            )

            return

        keyboard = []

        for category in db["categories"]:

            keyboard.append([

                InlineKeyboardButton(

                    category["name"],

                    callback_data=
                    f"remove_category_{category['id']}"

                )

            ])

        query.message.reply_text(

            "🗑 انتخاب دسته بندی",

            reply_markup=
            InlineKeyboardMarkup(keyboard)

        )

    # =========================
    # REMOVE CATEGORY
    # =========================

    elif data.startswith("remove_category_"):

        category_id = int(
            data.split("_")[2]
        )

        db["categories"] = [

            x for x in db["categories"]

            if x["id"] != category_id

        ]

        save_db(db)

        query.message.reply_text(
            "✅ دسته بندی حذف شد"
        )

    # =========================
    # ADD PLAN
    # =========================

    elif data == "add_plan":

        if len(db["categories"]) == 0:

            query.message.reply_text(
                "❌ ابتدا دسته بندی بسازید"
            )

            return

        keyboard = []

        for category in db["categories"]:

            keyboard.append([

                InlineKeyboardButton(

                    category["name"],

                    callback_data=
                    f"select_category_{category['id']}"

                )

            ])

        query.message.reply_text(

            "📁 دسته بندی پلن را انتخاب کنید",

            reply_markup=
            InlineKeyboardMarkup(keyboard)

        )

    # =========================
    # SELECT CATEGORY FOR PLAN
    # =========================

    elif data.startswith("select_category_"):

        category_id = int(
            data.split("_")[2]
        )

        user_state[user_id] = {

            "step": "plan_name",

            "category_id": category_id

        }

        query.message.reply_text(
            "📦 نام پلن را ارسال کنید"
        )

    # =========================
    # DELETE PLAN
    # =========================

    elif data == "delete_plan":

        if len(db["plans"]) == 0:

            query.message.reply_text(
                "❌ پلنی وجود ندارد"
            )

            return

        keyboard = []

        for plan in db["plans"]:

            keyboard.append([

                InlineKeyboardButton(

                    plan["name"],

                    callback_data=
                    f"remove_plan_{plan['id']}"

                )

            ])

        query.message.reply_text(

            "🗑 انتخاب پلن",

            reply_markup=
            InlineKeyboardMarkup(keyboard)

        )

    # =========================
    # REMOVE PLAN
    # =========================

    elif data.startswith("remove_plan_"):

        plan_id = int(
            data.split("_")[2]
        )

        db["plans"] = [

            x for x in db["plans"]

            if x["id"] != plan_id

        ]

        save_db(db)

        query.message.reply_text(
            "✅ پلن حذف شد"
        )

    # =========================
    # COLORS
    # =========================

    elif data == "colors":

        keyboard = [

            [

                InlineKeyboardButton(
                    "🟢 خرید",
                    callback_data="color_buy"
                )

            ],

            [

                InlineKeyboardButton(
                    "🔴 پشتیبانی",
                    callback_data="color_support"
                )

            ],

            [

                InlineKeyboardButton(
                    "🔵 تست",
                    callback_data="color_test"
                )

            ]

        ]

        query.message.reply_text(

            "🎨 انتخاب دکمه",

            reply_markup=
            InlineKeyboardMarkup(keyboard)

        )

    elif data == "color_buy":

        user_state[user_id] = "color_buy"

        query.message.reply_text(
            "🎨 ایموجی جدید خرید را ارسال کنید"
        )

    elif data == "color_support":

        user_state[user_id] = "color_support"

        query.message.reply_text(
            "🎨 ایموجی جدید پشتیبانی را ارسال کنید"
        )

    elif data == "color_test":

        user_state[user_id] = "color_test"

        query.message.reply_text(
            "🎨 ایموجی جدید تست را ارسال کنید"
        )

# =========================
# TEXT HANDLER
# =========================

def texts(update: Update, context: CallbackContext):

    user_id = update.effective_user.id

    text = update.message.text

    if user_id not in user_state:

        return

    state = user_state[user_id]

    # =========================
    # ADD CATEGORY
    # =========================

    if state == "add_category":

        new_id = len(db["categories"]) + 1

        db["categories"].append({

            "id": new_id,

            "name": text

        })

        save_db(db)

        del user_state[user_id]

        update.message.reply_text(
            "✅ دسته بندی اضافه شد"
        )

    # =========================
    # PLAN NAME
    # =========================

    elif isinstance(state, dict):

        if state["step"] == "plan_name":

            state["name"] = text

            state["step"] = "plan_price"

            user_state[user_id] = state

            update.message.reply_text(
                "💰 قیمت پلن را ارسال کنید"
            )

            return

        elif state["step"] == "plan_price":

            new_id = len(db["plans"]) + 1

            db["plans"].append({

                "id": new_id,

                "name": state["name"],

                "price": text,

                "category_id":
                state["category_id"]

            })

            save_db(db)

            del user_state[user_id]

            update.message.reply_text(
                "✅ پلن اضافه شد"
            )

    # =========================
    # COLORS
    # =========================

    elif state == "color_buy":

        db["settings"]["buy_color"] = text

        save_db(db)

        del user_state[user_id]

        update.message.reply_text(
            "✅ تغییر کرد"
        )

    elif state == "color_support":

        db["settings"]["support_color"] = text

        save_db(db)

        del user_state[user_id]

        update.message.reply_text(
            "✅ تغییر کرد"
        )

    elif state == "color_test":

        db["settings"]["test_color"] = text

        save_db(db)

        del user_state[user_id]

        update.message.reply_text(
            "✅ تغییر کرد"
        )

# =========================
# MAIN
# =========================

def main():

    updater = Updater(
        TOKEN,
        use_context=True
    )

    dp = updater.dispatcher

    dp.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    dp.add_handler(
        CallbackQueryHandler(
            callbacks
        )
    )

    dp.add_handler(
        MessageHandler(
            Filters.text &
            ~Filters.command,
            texts
        )
    )

    updater.start_polling()

    print("BOT STARTED")

    updater.idle()

if __name__ == "__main__":

    main()
