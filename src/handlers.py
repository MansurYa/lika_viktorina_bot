from collections import defaultdict
from telegram import Update
from telegram.ext import CallbackContext
from state import UserState
import random
import re
import logging

logger = logging.getLogger(__name__)
user_states = defaultdict(UserState)


def clear_text(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r'[^a-zа-я0-9\s]', '', text)


def get_reaction_to_user_answer(quiz_data, user_answer: str, question_type: str, valid_answers: list):
    clean_answer = clear_text(user_answer)
    username = "user"  # Просто заглушка, т.к. username недоступен в этой функции

    if question_type == "any":
        compliment = random.choice(quiz_data["compliments_for_any"])
        return quiz_data["response_templates"]["any"].replace("$compliment", compliment)

    elif question_type == "lika":
        if "я" in clean_answer.split():
            compliment = random.choice(quiz_data["compliments_for_correct"])
            hearts = ["❤️", "💖", "💕", "💓", "💗", "💘", "💝", "💞", "💟"]
            heart = random.choice(hearts)
            return quiz_data["response_templates"]["correct"].replace("$compliment", f"{compliment}{heart}")

        lika_variants = ["лика", "ликуся", "ликуша", "ликусенька", "ликулечка",
                        "лик", "лька", "лека", "лиика", "ликаа", "лика)",
                        "этоя", "моеимя", "ая", "моя"]
        alisa_eva_variants = ["алиса-ева", "алисаева", "алиса", "ева", "алису",
                             "алисе", "алисин", "алисинка", "алис", "евушка"]

        hearts = ["❤️", "💖", "💕", "💓", "💗", "💘", "💝", "💞", "💟"]
        heart = random.choice(hearts)

        if any(variant in clean_answer for variant in lika_variants):
            return quiz_data["response_templates"]["incorrect"].replace(
                "$correct_answer", f"Алиса-Ева {heart}"
            )
        elif any(variant in clean_answer for variant in alisa_eva_variants):
            return quiz_data["response_templates"]["incorrect"].replace(
                "$correct_answer", f"Лика {heart}"
            )
        else:
            return quiz_data["response_templates"]["incorrect"].replace(
                "$correct_answer", f"Лика {heart}"
            )

    elif question_type in ["standard", "mansur"]:
        clean_valid_answers = [clear_text(ans) for ans in valid_answers]

        if any(valid in clean_answer for valid in clean_valid_answers):
            compliment = random.choice(quiz_data["compliments_for_correct"])
            return quiz_data["response_templates"]["correct"].replace("$compliment", compliment)
        else:
            correct_answer = valid_answers[0] if valid_answers else "???"
            return quiz_data["response_templates"]["incorrect"].replace("$correct_answer", correct_answer)

    return "⛔ Неизвестный тип вопроса. Пропускаем."


async def handle_messages(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update.effective_user
    username = user.username or user.full_name or str(user.id)
    state = user_states[chat_id]
    quiz_data = context.bot_data["quiz_data"]

    logger.info(f"Ответ от @{username}: {update.message.text}")

    if state.quiz_completed:
        await update.message.reply_text(
            "🎉 Викторина уже завершена!\nИспользуйте /start чтобы начать заново"
        )
        return

    current_question = quiz_data["questions"][state.current_question_index]

    response = get_reaction_to_user_answer(
        quiz_data=quiz_data,
        user_answer=update.message.text,
        question_type=current_question["type"],
        valid_answers=current_question["valid_answers"]
    )

    await update.message.reply_text(response)

    state.next_question_index()

    if state.current_question_index < len(quiz_data["questions"]):
        next_question = quiz_data["questions"][state.current_question_index]
        await update.message.reply_text(f"{state.current_question_index + 1}. {next_question['question']}")

        logger.info(f"Пользователю @{username} отправлен вопрос: {next_question['question']}")
    else:
        await update.message.reply_text(quiz_data["final_message"])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open('../assets/lika.png', 'rb')
        )
        state.complete_quiz()
        logger.info(f"Викторина завершена для @{username}")


async def handle_start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update.effective_user
    username = user.username or user.full_name or str(user.id)
    state = user_states[chat_id]
    quiz_data = context.bot_data["quiz_data"]

    state.reset_state()
    await update.message.reply_text("🪄 Начинаем викторину!")
    await update.message.reply_text(quiz_data["start_message"])

    first_question = quiz_data["questions"][0]
    await update.message.reply_text(f"1. {first_question['question']}")
    logger.info(f"Начато прохождение викторины для @{username}")
    logger.info(f"Первый вопрос для @{username}: {first_question['question']}")
