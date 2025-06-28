import json
import logging

logger = logging.getLogger(__name__)


def load_quiz_data(file_path: str) -> dict:
    try:
        logger.info(f"Загрузка данных викторины из {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if not data.get("questions") or not isinstance(data["questions"], list):
            logger.error("Некорректные вопросы викторины")
            return {}

        logger.info(f"Загружено вопросов: {len(data['questions'])}")
        return data

    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Ошибка чтения JSON: {file_path}")
        return {}
    except Exception as e:
        logger.error(f"Ошибка загрузки: {str(e)}")
        return {}
