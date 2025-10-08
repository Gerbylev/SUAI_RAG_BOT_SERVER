from langchain_core.tools import tool

from services.guap_schedule_service import guap_schedule_service
from utils.logger import get_logger

logger = get_logger("AgentTools")


@tool
async def get_teacher_schedule(teacher_name: str) -> str:
    """
    Получает расписание преподавателя из ГУАП.

    Используй эту функцию когда пользователь спрашивает про расписание преподавателя.
    Имя преподавателя может быть указано не полностью - функция найдет наиболее подходящего.

    Args:
        teacher_name: Имя преподавателя (может быть неполным, например "Иванов" или "Иванов А")

    Returns:
        str: Отформатированное расписание преподавателя или сообщение об ошибке
    """
    logger.info(f"Запрос расписания для преподавателя: {teacher_name}")

    try:
        teacher = await guap_schedule_service.search_teacher(teacher_name)

        if not teacher:
            return f"Преподаватель '{teacher_name}' не найден в системе ГУАП. Проверьте правильность написания имени."

        schedule_data = await guap_schedule_service.get_teacher_schedule(teacher["id"], teacher["name"])

        if "error" in schedule_data:
            return f"Ошибка при получении расписания для {teacher['name']}: {schedule_data['error']}"

        formatted_schedule = await guap_schedule_service.format_schedule_for_llm(schedule_data)
        return formatted_schedule

    except Exception as e:
        logger.error(f"Ошибка в get_teacher_schedule: {e}")
        return f"Произошла ошибка при получении расписания: {str(e)}"


@tool
async def get_group_schedule(group_number: str) -> str:
    """
    Получает расписание группы из ГУАП.

    Используй эту функцию когда пользователь спрашивает про расписание группы.
    Номер группы может быть указан не полностью - функция найдет наиболее подходящую.

    Args:
        group_number: Номер группы (например "1234" или "М1234")

    Returns:
        str: Отформатированное расписание группы или сообщение об ошибке
    """
    logger.info(f"Запрос расписания для группы: {group_number}")

    try:
        group = await guap_schedule_service.search_group(group_number)

        if not group:
            return f"Группа '{group_number}' не найдена в системе ГУАП. Проверьте правильность номера группы."

        schedule_data = await guap_schedule_service.get_group_schedule(group["id"], group["name"])

        if "error" in schedule_data:
            return f"Ошибка при получении расписания для группы {group['name']}: {schedule_data['error']}"

        formatted_schedule = await guap_schedule_service.format_schedule_for_llm(schedule_data)
        return formatted_schedule

    except Exception as e:
        logger.error(f"Ошибка в get_group_schedule: {e}")
        return f"Произошла ошибка при получении расписания: {str(e)}"


@tool
async def get_department_schedule(department_name: str) -> str:
    """
    Получает расписание кафедры из ГУАП.

    Используй эту функцию когда пользователь спрашивает про расписание кафедры.
    Название кафедры может быть указано не полностью - функция найдет наиболее подходящую.

    Args:
        department_name: Название кафедры (может быть неполным)

    Returns:
        str: Отформатированное расписание кафедры или сообщение об ошибке
    """
    logger.info(f"Запрос расписания для кафедры: {department_name}")

    try:
        department = await guap_schedule_service.search_department(department_name)

        if not department:
            return f"Кафедра '{department_name}' не найдена в системе ГУАП. Проверьте правильность названия."

        schedule_data = await guap_schedule_service.get_department_schedule(department["id"], department["name"])

        if "error" in schedule_data:
            return f"Ошибка при получении расписания для кафедры {department['name']}: {schedule_data['error']}"

        formatted_schedule = await guap_schedule_service.format_schedule_for_llm(schedule_data)
        return formatted_schedule

    except Exception as e:
        logger.error(f"Ошибка в get_department_schedule: {e}")
        return f"Произошла ошибка при получении расписания: {str(e)}"


@tool
async def get_room_schedule(room_number: str) -> str:
    """
    Получает расписание аудитории из ГУАП.

    Используй эту функцию когда пользователь спрашивает про расписание аудитории или какие занятия проходят в аудитории.
    Номер аудитории может быть указан не полностью - функция найдет наиболее подходящую.

    Args:
        room_number: Номер аудитории (например "101" или "52-03")

    Returns:
        str: Отформатированное расписание аудитории или сообщение об ошибке
    """
    logger.info(f"Запрос расписания для аудитории: {room_number}")

    try:
        room = await guap_schedule_service.search_room(room_number)

        if not room:
            return f"Аудитория '{room_number}' не найдена в системе ГУАП. Проверьте правильность номера."

        schedule_data = await guap_schedule_service.get_room_schedule(room["id"], room["name"])

        if "error" in schedule_data:
            return f"Ошибка при получении расписания для аудитории {room['name']}: {schedule_data['error']}"

        formatted_schedule = await guap_schedule_service.format_schedule_for_llm(schedule_data)
        return formatted_schedule

    except Exception as e:
        logger.error(f"Ошибка в get_room_schedule: {e}")
        return f"Произошла ошибка при получении расписания: {str(e)}"
