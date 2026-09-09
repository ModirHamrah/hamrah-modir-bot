# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters,
)

TOKEN = os.environ.get("BOT_TOKEN")

reports = []
consumptions = []
leave_requests = []
overtimes = []
photos = []

(REPORT_PROJECT, REPORT_STAGE, REPORT_TEXT,
 MASRAF_PROJECT, MASRAF_ITEM, MASRAF_QTY,
 LEAVE_FROM, LEAVE_TO, LEAVE_REASON,
 OVERTIME_HOURS, OVERTIME_DESC,
 PHOTO_CAPTION) = range(12)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def fa_date():
    return datetime.now().strftime("%Y/%m/%d %H:%M")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"سلام {user.first_name} 👋\n\n"
        "به ربات **همراه مدیر** خوش آمدید.\n\n"
        "دستورات اصلی:\n"
        "📝 /gozaresh — ثبت گزارش روزانه\n"
        "📦 /masraf — ثبت مصرف انبار\n"
        "📷 /aks — ارسال عکس کار\n"
        "🏖 /morakhasi — درخواست مرخصی\n"
        "📅 /mande_morakhasi — مانده مرخصی\n"
        "⏰ /ezafe_kar — ثبت اضافه‌کار\n\n"
        "دستورات مدیریتی:\n"
        "📊 /vaziyat — وضعیت مجموعه\n"
        "👥 /moshtarian — مشتریان مانده‌دار\n"
        "🏭 /anbar — موجودی انبار\n"
        "💳 /checkha — چک‌های نزدیک\n"
        "🗂 /hame — خلاصه همه مجموعه‌ها\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END

async def gozaresh_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 نام پروژه یا مشتری را بنویسید:\n(برای لغو /cancel)")
    return REPORT_PROJECT

async def gozaresh_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["report_project"] = update.message.text
    await update.message.reply_text("مرحله کار را بنویسید:\n(برش / نوارکاری / مونتاژ / نصب / روکش)")
    return REPORT_STAGE

async def gozaresh_stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["report_stage"] = update.message.text
    await update.message.reply_text("توضیحات کار انجام‌شده را بنویسید:")
    return REPORT_TEXT

async def gozaresh_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    report = {
        "user_id": user.id,
        "user_name": user.full_name,
        "project": context.user_data.get("report_project"),
        "stage": context.user_data.get("report_stage"),
        "text": update.message.text,
        "date": fa_date(),
    }
    reports.append(report)
    await update.message.reply_text(
        f"✅ گزارش ثبت شد.\n\nپروژه: {report['project']}\nمرحله: {report['stage']}\nزمان: {report['date']}"
    )
    return ConversationHandler.END

async def masraf_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📦 نام پروژه / مشتری را بنویسید:")
    return MASRAF_PROJECT

async def masraf_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["masraf_project"] = update.message.text
    await update.message.reply_text("نام کالا را بنویسید:\n(مثال: یکرو سفید / نوار یک میل)")
    return MASRAF_ITEM

async def masraf_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["masraf_item"] = update.message.text
    await update.message.reply_text("تعداد یا متراژ را بنویسید:")
    return MASRAF_QTY

async def masraf_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    item = {
        "user_id": user.id,
        "user_name": user.full_name,
        "project": context.user_data.get("masraf_project"),
        "item": context.user_data.get("masraf_item"),
        "qty": update.message.text,
        "date": fa_date(),
    }
    consumptions.append(item)
    await update.message.reply_text(
        f"✅ مصرف ثبت شد.\n\nپروژه: {item['project']}\nکالا: {item['item']}\nمقدار: {item['qty']}"
    )
    return ConversationHandler.END

async def morakhasi_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏖 تاریخ شروع مرخصی را بنویسید:\n(مثال: 1405/06/15)")
    return LEAVE_FROM

async def leave_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["leave_from"] = update.message.text
    await update.message.reply_text("تاریخ پایان را بنویسید:")
    return LEAVE_TO

async def leave_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["leave_to"] = update.message.text
    await update.message.reply_text("دلیل مرخصی را بنویسید:")
    return LEAVE_REASON

async def leave_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    req = {
        "user_id": user.id,
        "user_name": user.full_name,
        "from": context.user_data.get("leave_from"),
        "to": context.user_data.get("leave_to"),
        "reason": update.message.text,
        "date": fa_date(),
        "status": "در انتظار تأیید",
    }
    leave_requests.append(req)
    await update.message.reply_text(
        f"✅ درخواست مرخصی ثبت شد.\n\nاز: {req['from']}\nتا: {req['to']}\nوضعیت: {req['status']}"
    )
    return ConversationHandler.END

async def mande_morakhasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 مانده مرخصی شما:\n\nدر نسخه فعلی عدد واقعی بعد از اتصال به پنل نمایش داده می‌شود.")

async def ezafe_kar_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏰ تعداد ساعت اضافه‌کار را بنویسید:")
    return OVERTIME_HOURS

async def overtime_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["overtime_hours"] = update.message.text
    await update.message.reply_text("توضیحات (پروژه و دلیل) را بنویسید:")
    return OVERTIME_DESC

async def overtime_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ot = {
        "user_id": user.id,
        "user_name": user.full_name,
        "hours": context.user_data.get("overtime_hours"),
        "desc": update.message.text,
        "date": fa_date(),
    }
    overtimes.append(ot)
    await update.message.reply_text(f"✅ اضافه‌کار ثبت شد.\n\nساعت: {ot['hours']}\nتوضیح: {ot['desc']}")
    return ConversationHandler.END

async def aks_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 عکس کار را بفرستید.\nمی‌توانید همراه عکس توضیح هم بنویسید.")
    return PHOTO_CAPTION

async def photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
