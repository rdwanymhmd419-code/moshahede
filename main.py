import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ========== اطلاعات پنل شما ==========
PANEL_URL = "http://87.248.152.205:8081/hke43Y4nhZ23K1vc4S"
PANEL_USERNAME = "amir"
PANEL_PASSWORD = "amirreza871221"
# ====================================

def login_to_panel():
    session = requests.Session()
    try:
        response = session.post(
            f"{PANEL_URL}/login",
            json={"username": PANEL_USERNAME, "password": PANEL_PASSWORD},
            timeout=10
        )
        if response.status_code == 200:
            return session
    except Exception as e:
        print(f"Login error: {e}")
    return None

def get_all_clients_traffic(session):
    try:
        response = session.get(f"{PANEL_URL}/panel/api/inbounds/list", timeout=10)
        if response.status_code == 200:
            data = response.json()
            clients = []
            if data.get("success") and data.get("obj"):
                for inbound in data["obj"]:
                    for client in inbound.get("clients", []):
                        email = client.get("email")
                        if email:
                            total_bytes = client.get("total", 0)
                            up = client.get("up", 0)
                            down = client.get("down", 0)
                            used = up + down
                            remaining = total_bytes - used
                            clients.append({
                                "email": email,
                                "used": used / (1024**3),
                                "total": total_bytes / (1024**3),
                                "remaining": remaining / (1024**3)
                            })
            return clients
    except Exception as e:
        print(f"Error getting clients: {e}")
    return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📊 دریافت حجم کاربران", callback_data="get_volume")]]
    await update.message.reply_text(
        "سلام! 👋\n\nبه ربات مدیریت پنل خوش اومدی.\nبرای مشاهده لیست حجم کاربران، دکمه زیر رو بزن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def get_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    session = login_to_panel()
    if not session:
        await query.edit_message_text("❌ خطا در اتصال به پنل.\nلطفاً بعداً تلاش کن.")
        return
    
    clients = get_all_clients_traffic(session)
    if not clients:
        await query.edit_message_text("❌ هیچ کاربری پیدا نشد.")
        return
    
    message = "📊 **لیست حجم کاربران**\n\n"
    for client in clients:
        message += f"🔹 **{client['email']}**\n"
        message += f"   مصرف شده: {client['used']:.2f} گیگ\n"
        message += f"   حجم کل: {client['total']:.2f} گیگ\n"
        message += f"   باقی مونده: {client['remaining']:.2f} گیگ\n\n"
    
    await query.edit_message_text(message, parse_mode="Markdown")

def main():
    # توکن ربات رو از متغیر محیطی میگیره (برای Railway)
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        print("❌ خطا: توکن ربات پیدا نشد. متغیر BOT_TOKEN رو تنظیم کن.")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(get_volume, pattern="get_volume"))
    
    print("✅ ربات روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
