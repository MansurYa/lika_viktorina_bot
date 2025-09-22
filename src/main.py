from telegram.ext import Application, CommandHandler, MessageHandler, filters
from loader import load_quiz_data
from handlers import handle_messages, handle_start
import logging

TG_TOKEN = ""

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_log.txt"),
        logging.StreamHandler()
    ]
)

logging.getLogger("httpx").setLevel(logging.CRITICAL)    # Отключаем логирование для httpx


def main():
    quiz_data = load_quiz_data(file_path="../lika-questions.json")
    if not quiz_data.get("questions"):
        logging.error("Не удалось загрузить данные викторины")
        return

    application = Application.builder().token(TG_TOKEN).build()
    application.bot_data['quiz_data'] = quiz_data

    application.add_handler(CommandHandler('start', handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    logging.info("Бот запущен")
    application.run_polling()


if __name__ == "__main__":
    main()
