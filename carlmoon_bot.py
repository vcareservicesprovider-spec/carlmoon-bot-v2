from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import uuid
from datetime import datetime
import os
import asyncio

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 863542771
ADMIN_USERNAME = "@Vcare524"

# Escrow Wallets
USDT_TRC20 = "TAdJBVX4LgiczxhAx7EeMjmJhqQp3KS7mf"
BTC_ADDRESS = "bc1q933q770ghps420a56pw5pg7xq9vgsv6s0sxhsq"
ETH_BEP20 = "0xe29affb667ad5f2f338f112231ce49e1953b2647"
LTC_ADDRESS = "LXhNNYjLJQkKxANmD1nSqQk4zvZ5aNEaVX"

deals = {}


def is_admin(user_id):
    return user_id == ADMIN_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 *Welcome to Carl Moon Escrow Services*\n\n"
        "Secure Manual Escrow with *5% commission*.\n\n"
        "📌 *How it works:*\n"
        "1. /newdeal – Create a deal\n"
        "2. /amount 100 – Set amount\n"
        "3. Bot shows escrow wallets\n"
        "4. /creategroup – Create private group with Admin\n"
        "5. Buyer sends crypto → Admin releases\n\n"
        "Type /help for all commands or /guide for step-by-step.",
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Carl Moon Escrow – Commands*\n\n"
        "/newdeal – Create new deal\n"
        "/amount – Set amount\n"
        "/description – Add details\n"
        "/seller – Set seller wallet\n"
        "/buyer – Set buyer wallet\n"
        "/confirm – Confirm the deal\n"
        "/creategroup – Create private group with Admin\n"
        "/status – View deal details\n"
        "/mydeals – Your deals\n"
        "/pay_seller – Release to seller\n"
        "/pay_seller 50 – Partial release\n"
        "/refund_buyer – Refund to buyer\n"
        "/dispute – Open dispute\n"
        "/cancel – Cancel deal\n"
        "/terms – Show terms\n"
        "/buyerterms – Set buyer terms\n"
        "/sellerterms – Set seller terms\n"
        "/dealinfo – Full deal summary\n"
        "/whoami – Your role in the deal\n"
        "/balance – Show deal amount & fee\n"
        "/guide – Step-by-step guide\n"
        "/support – Support\n"
        "/whatisescrow – How it works\n"
        "/rules – Rules\n"
        "/reset – Reset roles\n\n"
        "*Admin Only:*\n"
        "/alldeals – View all deals\n"
        "/admin_release – Force release\n"
        "/admin_refund – Force refund"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Step-by-Step Guide*\n\n"
        "*Buyer:*\n"
        "1. /newdeal\n"
        "2. /amount 100\n"
        "3. /buyer YOUR_WALLET\n"
        "4. /buyerterms Your terms\n"
        "5. /confirm\n"
        "6. Send crypto to the address shown\n"
        "7. Wait for release\n\n"
        "*Seller:*\n"
        "1. Join the deal\n"
        "2. /seller YOUR_WALLET\n"
        "3. /sellerterms Your terms\n"
        "4. /confirm\n"
        "5. Deliver the product/service\n"
        "6. Receive payment after release\n\n"
        "*Admin:*\n"
        "Checks payment and uses /admin_release or /admin_refund"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def newdeal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = str(uuid.uuid4())[:8]
    user_id = update.effective_user.id

    deals[deal_id] = {
        "creator": user_id,
        "buyer": None,
        "seller": None,
        "buyer_address": None,
        "seller_address": None,
        "amount": 0,
        "description": "No description yet",
        "buyer_terms": "Not set",
        "seller_terms": "Not set",
        "status": "created",
        "buyer_confirmed": False,
        "seller_confirmed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "fee_percent": 5
    }

    context.user_data["current_deal"] = deal_id

    await update.message.reply_text(
        f"✅ *New escrow deal created!*\n\n"
        f"Deal ID: `{deal_id}`\n"
        f"Status: Created 🔒\n"
        f"Commission: 5%\n\n"
        f"*Next Steps:*\n"
        f"1. /amount 100\n"
        f"2. /description details\n"
        f"3. /buyer or /seller\n"
        f"4. /buyerterms or /sellerterms\n"
        f"5. /creategroup\n"
        f"6. Both parties /confirm",
        parse_mode="Markdown"
    )


async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /amount 100")
        return
    try:
        value = float(context.args[0])
    except:
        await update.message.reply_text("Please enter a valid number.\nExample: /amount 150")
        return

    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal. Use /newdeal first.")
        return

    deals[deal_id]["amount"] = value
    fee = value * 0.05
    net = value - fee

    text = (
        f"✅ *Amount set successfully!*\n\n"
        f"Deal Amount: *{value}*\n"
        f"Carl Moon Fee (5%): *{fee:.2f}*\n"
        f"Seller will receive: *{net:.2f}*\n\n"
        f"────────────────────\n"
        f"*Send the payment to one of these Escrow Wallets:*\n\n"
        f"*USDT (TRC20):*\n`{USDT_TRC20}`\n\n"
        f"*BTC:*\n`{BTC_ADDRESS}`\n\n"
        f"*ETH / BEP20:*\n`{ETH_BEP20}`\n\n"
        f"*LTC:*\n`{LTC_ADDRESS}`\n\n"
        f"────────────────────\n"
        f"After sending, notify the admin.\n"
        f"Also use /creategroup to make a private group."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal. Use /newdeal first.")
        return

    deal = deals[deal_id]
    amount = deal.get("amount", 0)
    fee = amount * 0.05
    net = amount - fee

    text = (
        f"*Current Deal Balance*\n\n"
        f"Deal ID: `{deal_id}`\n"
        f"Amount: *{amount}*\n"
        f"5% Fee: *{fee:.2f}*\n"
        f"Seller receives: *{net:.2f}*\n"
        f"Status: *{deal['status']}*\n\n"
        f"Note: This is the deal amount only.\n"
        f"Real crypto balance must be checked on blockchain."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def buyerterms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /buyerterms Pay after delivery")
        return
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deals[deal_id]["buyer_terms"] = " ".join(context.args)
    await update.message.reply_text(f"✅ Buyer terms set:\n{deals[deal_id]['buyer_terms']}")


async def sellerterms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /sellerterms Delivery in 24 hours")
        return
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deals[deal_id]["seller_terms"] = " ".join(context.args)
    await update.message.reply_text(f"✅ Seller terms set:\n{deals[deal_id]['seller_terms']}")


async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deal = deals[deal_id]
    text = (
        f"*Deal Terms*\n\n"
        f"*Buyer terms:*\n{deal.get('buyer_terms', 'Not set')}\n\n"
        f"*Seller terms:*\n{deal.get('seller_terms', 'Not set')}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def dealinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deal = deals[deal_id]
    fee = deal["amount"] * 0.05
    net = deal["amount"] - fee
    text = (
        f"*Deal Info*\n\n"
        f"ID: `{deal_id}`\n"
        f"Status: *{deal['status']}*\n"
        f"Amount: {deal['amount']}\n"
        f"5% Fee: {fee:.2f}\n"
        f"Seller receives: {net:.2f}\n"
        f"Description: {deal['description']}\n"
        f"Buyer terms: {deal.get('buyer_terms', 'Not set')}\n"
        f"Seller terms: {deal.get('seller_terms', 'Not set')}\n"
        f"Buyer confirmed: {'Yes' if deal['buyer_confirmed'] else 'No'}\n"
        f"Seller confirmed: {'Yes' if deal['seller_confirmed'] else 'No'}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deal = deals[deal_id]
    user_id = update.effective_user.id
    roles = []
    if user_id == deal["creator"]:
        roles.append("Creator")
    if user_id == deal.get("buyer"):
        roles.append("Buyer")
    if user_id == deal.get("seller"):
        roles.append("Seller")
    if is_admin(user_id):
        roles.append("Admin")
    role_text = ", ".join(roles) if roles else "Not part of this deal"
    await update.message.reply_text(f"Your role: *{role_text}*", parse_mode="Markdown")


async def creategroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if not deal_id:
        deal_id = str(uuid.uuid4())[:5].upper()

    group_name = f"Carl Moon Escrow #{deal_id.upper()}"

    text = (
        f"💬 *Escrow Group Created*\n\n"
        f"*Group Name:* {group_name}\n\n"
        f"*Creator:* {ADMIN_USERNAME}\n\n"
        f"Join this escrow group and share the link with the buyer/seller.\n\n"
        f"⚠️ *Note:* This group is for 2 members only — third parties are not allowed to join."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤝 Join Group (Click Me)", url="https://t.me/Vcare524")]
    ])

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /description iPhone 15 Pro Max")
        return
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deals[deal_id]["description"] = " ".join(context.args)
    await update.message.reply_text(f"✅ Description updated:\n{deals[deal_id]['description']}")


async def seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /seller WALLET_ADDRESS")
        return
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deals[deal_id]["seller"] = update.effective_user.id
    deals[deal_id]["seller_address"] = context.args[0]
    await update.message.reply_text(f"✅ Seller address set:\n`{context.args[0]}`", parse_mode="Markdown")


async def buyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /buyer WALLET_ADDRESS")
        return
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deals[deal_id]["buyer"] = update.effective_user.id
    deals[deal_id]["buyer_address"] = context.args[0]
    await update.message.reply_text(f"✅ Buyer address set:\n`{context.args[0]}`", parse_mode="Markdown")


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deal = deals[deal_id]
    user_id = update.effective_user.id
    if user_id == deal.get("buyer"):
        deal["buyer_confirmed"] = True
        await update.message.reply_text("✅ Buyer confirmed the deal.")
    elif user_id == deal.get("seller"):
        deal["seller_confirmed"] = True
        await update.message.reply_text("✅ Seller confirmed the deal.")
    else:
        await update.message.reply_text("You are not the buyer or seller of this deal.")
        return
    if deal["buyer_confirmed"] and deal["seller_confirmed"]:
        deal["status"] = "locked"
        await update.message.reply_text("🔒 Both parties confirmed. Deal is now locked.")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deal = deals[deal_id]
    fee = deal["amount"] * 0.05
    net = deal["amount"] - fee
    text = (
        f"*Deal Status*\n\n"
        f"ID: `{deal_id}`\n"
        f"Status: *{deal['status']}*\n"
        f"Description: {deal['description']}\n"
        f"Amount: {deal['amount']}\n"
        f"5% Fee: {fee:.2f}\n"
        f"Seller receives: {net:.2f}\n"
        f"Buyer confirmed: {'Yes' if deal['buyer_confirmed'] else 'No'}\n"
        f"Seller confirmed: {'Yes' if deal['seller_confirmed'] else 'No'}\n"
        f"Created: {deal['created_at']}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def mydeals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = "*Your Deals:*\n\n"
    found = False
    for deal_id, deal in deals.items():
        if deal["creator"] == user_id or deal["buyer"] == user_id or deal["seller"] == user_id:
            text += f"• `{deal_id}` – {deal['status']} – {deal['description'][:30]}\n"
            found = True
    if not found:
        text = "You have no deals yet."
    await update.message.reply_text(text, parse_mode="Markdown")


async def alldeals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only command.")
        return
    if not deals:
        await update.message.reply_text("No deals found.")
        return
    text = "*All Deals (Admin View):*\n\n"
    for deal_id, deal in deals.items():
        text += f"• `{deal_id}` | {deal['status']} | {deal['amount']} | {deal['description'][:25]}\n"
    await update.message.reply_text(text, parse_mode="Markdown")


async def pay_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deals[deal_id]["status"] = "released_to_seller"
    await update.message.reply_text("✅ Payment marked as released to seller.")


async def refund_buyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deals[deal_id]["status"] = "refunded_to_buyer"
    await update.message.reply_text("✅ Payment marked as refunded to buyer.")


async def dispute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deals[deal_id]["status"] = "disputed"
    await update.message.reply_text("⚠️ Dispute opened. Admin will review.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if deal_id and deal_id in deals:
        deals[deal_id]["status"] = "cancelled"
        await update.message.reply_text("Deal cancelled.")
    else:
        await update.message.reply_text("No active deal.")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deals[deal_id]["buyer"] = None
    deals[deal_id]["seller"] = None
    deals[deal_id]["buyer_address"] = None
    deals[deal_id]["seller_address"] = None
    deals[deal_id]["buyer_confirmed"] = False
    deals[deal_id]["seller_confirmed"] = False
    await update.message.reply_text("✅ Buyer & Seller roles reset.")


async def whatisescrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*What is Carl Moon Manual Escrow?*\n\n"
        "Buyer sends crypto to the official escrow wallets shown by the bot.\n"
        "Admin verifies the transaction on the blockchain.\n"
        "After confirmation, admin releases the funds to the seller (minus 5% fee).\n\n"
        "Use /creategroup to create a private group with the Admin.",
        parse_mode="Markdown"
    )


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Rules*\n\n"
        "1. Only send funds to the wallets shown by the bot\n"
        "2. Always take a screenshot of your transaction\n"
        "3. Create a group with Admin using /creategroup\n"
        "4. Admin decision is final in disputes\n"
        "5. 5% fee is deducted from every deal"
    )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"For support contact the owner: {ADMIN_USERNAME}")


async def admin_release(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Only the owner can use this command.")
        return
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deals[deal_id]["status"] = "admin_released"
    await update.message.reply_text("✅ Admin marked the deal as released to seller.")


async def admin_refund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Only the owner can use this command.")
        return
    deal_id = context.user_data.get("current_deal")
    if not deal_id or deal_id not in deals:
        await update.message.reply_text("No active deal.")
        return
    deals[deal_id]["status"] = "admin_refunded"
    await update.message.reply_text("✅ Admin marked the deal as refunded to buyer.")


def main():
    if not TOKEN:
        raise ValueError("TOKEN environment variable is missing")

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("guide", guide))
    app.add_handler(CommandHandler("newdeal", newdeal))
    app.add_handler(CommandHandler("amount", amount))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("buyerterms", buyerterms))
    app.add_handler(CommandHandler("sellerterms", sellerterms))
    app.add_handler(CommandHandler("terms", terms))
    app.add_handler(CommandHandler("dealinfo", dealinfo))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("creategroup", creategroup))
    app.add_handler(CommandHandler("description", description))
    app.add_handler(CommandHandler("seller", seller))
    app.add_handler(CommandHandler("buyer", buyer))
    app.add_handler(CommandHandler("confirm", confirm))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("mydeals", mydeals))
    app.add_handler(CommandHandler("alldeals", alldeals))
    app.add_handler(CommandHandler("pay_seller", pay_seller))
    app.add_handler(CommandHandler("refund_buyer", refund_buyer))
    app.add_handler(CommandHandler("dispute", dispute))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("whatisescrow", whatisescrow))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("admin_release", admin_release))
    app.add_handler(CommandHandler("admin_refund", admin_refund))

    print("Carl Moon Escrow Bot is now active...")
    app.run_polling()


if __name__ == "__main__":
    main()
