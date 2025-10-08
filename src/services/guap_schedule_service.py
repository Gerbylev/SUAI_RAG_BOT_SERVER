from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

from utils.logger import get_logger

logger = get_logger("GuapScheduleService")


class GuapScheduleService:
    """Сервис для работы с расписанием ГУАП"""

    BASE_URL = "https://guap.ru/rasp"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def close(self):
        """Закрывает HTTP клиент"""
        await self.client.aclose()

    async def _get_select_options(self, select_id: str, select_name: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Получает опции из селекта на странице

        Args:
            select_id: ID селекта
            select_name: Name атрибут селекта (опционально)

        Returns:
            Список опций
        """
        try:
            response = await self.client.get(self.BASE_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Ищем селект
            select = soup.find("select", {"id": select_id}) or (soup.find("select", {"name": select_name}) if select_name else None)

            if not select:
                logger.warning(f"Селект {select_id} не найден")
                return []

            options = select.find_all("option")
            result = []

            for option in options:
                value = option.get("value")
                if isinstance(value, list):
                    value = value[0] if value else ""
                value = str(value).strip() if value else ""

                text = option.get_text().strip()

                if value and text and value != "0":
                    result.append({"id": value, "name": text})

            return result

        except Exception as e:
            logger.error(f"Ошибка при получении опций селекта {select_id}: {e}")
            return []

    async def _fuzzy_search(self, query: str, items: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """
        Нечеткий поиск в списке элементов

        Args:
            query: Поисковый запрос
            items: Список элементов для поиска

        Returns:
            Наиболее подходящий элемент или None
        """
        if not items:
            return None

        best_match = None
        best_ratio = 0.0
        search_query = query.lower()

        for item in items:
            item_name_lower = item["name"].lower()

            # Проверяем точное вхождение
            if search_query in item_name_lower:
                ratio = len(search_query) / len(item_name_lower)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = item
            else:
                # Используем алгоритм схожести строк
                ratio = SequenceMatcher(None, search_query, item_name_lower).ratio()
                if ratio > best_ratio and ratio > 0.6:  # Порог схожести 60%
                    best_ratio = ratio
                    best_match = item

        if best_match:
            logger.info(f"Найдено совпадение: {best_match['name']} (схожесть: {best_ratio:.2f})")

        return best_match

    async def search_teacher(self, teacher_name: str) -> Optional[Dict[str, str]]:
        """
        Ищет преподавателя по имени с нечетким совпадением

        Args:
            teacher_name: Имя преподавателя (может быть неполным)

        Returns:
            Словарь с данными преподавателя или None
        """
        logger.info(f"Поиск преподавателя: {teacher_name}")
        teachers = await self._get_select_options("selPrep", "pr")
        return await self._fuzzy_search(teacher_name, teachers)

    async def search_group(self, group_number: str) -> Optional[Dict[str, str]]:
        """
        Ищет группу по номеру

        Args:
            group_number: Номер группы

        Returns:
            Словарь с данными группы или None
        """
        logger.info(f"Поиск группы: {group_number}")
        groups = await self._get_select_options("selGroup", "gr")
        return await self._fuzzy_search(group_number, groups)

    async def search_department(self, department_name: str) -> Optional[Dict[str, str]]:
        """
        Ищет кафедру по названию

        Args:
            department_name: Название кафедры

        Returns:
            Словарь с данными кафедры или None
        """
        logger.info(f"Поиск кафедры: {department_name}")
        departments = await self._get_select_options("selChair", "ch")
        return await self._fuzzy_search(department_name, departments)

    async def search_room(self, room_number: str) -> Optional[Dict[str, str]]:
        """
        Ищет аудиторию по номеру

        Args:
            room_number: Номер аудитории

        Returns:
            Словарь с данными аудитории или None
        """
        logger.info(f"Поиск аудитории: {room_number}")
        rooms = await self._get_select_options("selRoom", "ad")
        return await self._fuzzy_search(room_number, rooms)

    async def get_schedule(
        self,
        group_id: Optional[str] = None,
        teacher_id: Optional[str] = None,
        department_id: Optional[str] = None,
        room_id: Optional[str] = None,
        context_info: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Получает расписание по заданным параметрам

        Args:
            group_id: ID группы
            teacher_id: ID преподавателя
            department_id: ID кафедры
            room_id: ID аудитории
            context_info: Дополнительная информация для контекста (имена, номера)

        Returns:
            Словарь с расписанием
        """
        params = {}
        if group_id:
            params["gr"] = group_id
        if teacher_id:
            params["pr"] = teacher_id
        if department_id:
            params["ch"] = department_id
        if room_id:
            params["ad"] = room_id

        logger.info(f"Получение расписания с параметрами: {params}")

        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            schedule = self._parse_schedule(soup)

            result = {
                "schedule": schedule,
                "fetched_at": datetime.now().isoformat(),
                "params": params,
            }

            if context_info:
                result.update(context_info)

            return result

        except Exception as e:
            logger.error(f"Ошибка при получении расписания: {e}")
            return {"schedule": [], "error": str(e), "params": params}

    async def get_teacher_schedule(self, teacher_id: str, teacher_name: str) -> Dict[str, Any]:
        """
        Получает расписание преподавателя

        Args:
            teacher_id: ID преподавателя
            teacher_name: Имя преподавателя

        Returns:
            Словарь с расписанием
        """
        logger.info(f"Получение расписания для преподавателя: {teacher_name}")
        return await self.get_schedule(teacher_id=teacher_id, context_info={"teacher_name": teacher_name})

    async def get_group_schedule(self, group_id: str, group_number: str) -> Dict[str, Any]:
        """
        Получает расписание группы

        Args:
            group_id: ID группы
            group_number: Номер группы

        Returns:
            Словарь с расписанием
        """
        logger.info(f"Получение расписания для группы: {group_number}")
        return await self.get_schedule(group_id=group_id, context_info={"group_number": group_number})

    async def get_department_schedule(self, department_id: str, department_name: str) -> Dict[str, Any]:
        """
        Получает расписание кафедры

        Args:
            department_id: ID кафедры
            department_name: Название кафедры

        Returns:
            Словарь с расписанием
        """
        logger.info(f"Получение расписания для кафедры: {department_name}")
        return await self.get_schedule(department_id=department_id, context_info={"department_name": department_name})

    async def get_room_schedule(self, room_id: str, room_number: str) -> Dict[str, Any]:
        """
        Получает расписание аудитории

        Args:
            room_id: ID аудитории
            room_number: Номер аудитории

        Returns:
            Словарь с расписанием
        """
        logger.info(f"Получение расписания для аудитории: {room_number}")
        return await self.get_schedule(room_id=room_id, context_info={"room_number": room_number})

    def _parse_schedule(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Парсит HTML расписания

        Args:
            soup: BeautifulSoup объект

        Returns:
            Список занятий
        """
        schedule = []

        try:
            # Ищем заголовки с днями недели
            day_headers = soup.find_all("h4", class_="text-danger")

            if not day_headers:
                logger.warning("Дни недели не найдены в расписании")
                return schedule

            for day_header in day_headers:
                current_day = day_header.get_text().strip()

                # Находим все элементы между текущим днем и следующим днем (или концом)
                current_element = day_header.find_next_sibling()

                while current_element:
                    # Если встретили следующий день - останавливаемся
                    classes = current_element.get("class") or []
                    if current_element.name == "h4" and "text-danger" in classes:
                        break

                    # Ищем блоки с временем пары
                    if current_element.name == "div" and "text-danger" in classes:
                        time_text = current_element.get_text().strip()

                        # Следующий div содержит информацию о паре
                        lesson_block = current_element.find_next_sibling("div", class_="mb-3")

                        if lesson_block:
                            # Извлекаем информацию о паре
                            lesson = self._parse_lesson_block(lesson_block, current_day, time_text)
                            if lesson:
                                schedule.append(lesson)

                    current_element = current_element.find_next_sibling()

            logger.info(f"Распарсено {len(schedule)} занятий")

        except Exception as e:
            logger.error(f"Ошибка при парсинге расписания: {e}", exc_info=True)

        return schedule

    def _parse_lesson_block(self, lesson_block, day: str, time_text: str) -> Optional[Dict[str, Any]]:
        """
        Парсит блок с информацией о паре

        Args:
            lesson_block: BeautifulSoup элемент с информацией о паре
            day: День недели
            time_text: Текст с временем пары

        Returns:
            Словарь с информацией о паре или None
        """
        try:
            # Тип занятия
            lesson_type_elem = lesson_block.find("div", class_="fs-6")
            lesson_type = lesson_type_elem.get_text().strip() if lesson_type_elem else ""

            # Название предмета
            subject_elem = lesson_block.find("div", class_="lead")
            subject = subject_elem.get_text().strip() if subject_elem else ""

            # Дополнительная информация (аудитория, кафедра, преподаватель, группа)
            details_elem = lesson_block.find("div", class_="opacity-75")

            room = ""
            teacher = ""
            group = ""

            if details_elem:
                # Аудитория
                room_link = details_elem.find("a", href=lambda x: x and "ad=" in x)
                if room_link:
                    room = room_link.get_text().strip()

                # Преподаватель
                teacher_link = details_elem.find("a", href=lambda x: x and "pr=" in x)
                if teacher_link:
                    teacher = teacher_link.get_text().strip()

                # Группа
                group_link = details_elem.find("a", href=lambda x: x and "gr=" in x)
                if group_link:
                    group = group_link.get_text().strip()

            lesson = {
                "day": day,
                "time": time_text,
                "type": lesson_type,
                "subject": subject,
                "room": room,
                "teacher": teacher,
                "group": group,
            }

            return lesson

        except Exception as e:
            logger.error(f"Ошибка при парсинге блока пары: {e}")
            return None

    async def format_schedule_for_llm(self, schedule_data: Dict[str, Any]) -> str:
        """
        Форматирует расписание в текст для передачи в LLM

        Args:
            schedule_data: Данные расписания

        Returns:
            Отформатированный текст
        """
        schedule = schedule_data.get("schedule", [])

        # Определяем, что именно показываем
        title_parts = []
        if "teacher_name" in schedule_data:
            title_parts.append(f"преподавателя {schedule_data['teacher_name']}")
        if "group_number" in schedule_data:
            title_parts.append(f"группы {schedule_data['group_number']}")
        if "department_name" in schedule_data:
            title_parts.append(f"кафедры {schedule_data['department_name']}")
        if "room_number" in schedule_data:
            title_parts.append(f"аудитории {schedule_data['room_number']}")

        title = "Расписание " + ", ".join(title_parts) if title_parts else "Расписание"

        if not schedule:
            return f"{title} не найдено или пусто."

        text_parts = [f"{title}\n"]

        # Группируем по дням
        days_schedule: Dict[str, List[Dict]] = {}
        for lesson in schedule:
            day = lesson.get("day")
            if not day or day == "None":
                day = "Не указан"
            if day not in days_schedule:
                days_schedule[day] = []
            days_schedule[day].append(lesson)

        # Форматируем каждый день
        for day, lessons in days_schedule.items():
            text_parts.append(f"\n{day}:")
            for lesson in lessons:
                time = lesson.get("time", "")
                subject = lesson.get("subject", "")
                group = lesson.get("group", "")
                room = lesson.get("room", "")
                teacher = lesson.get("teacher", "")
                lesson_type = lesson.get("type", "")

                lesson_text = f"  {time} - {subject}"
                if lesson_type:
                    lesson_text += f" [{lesson_type}]"
                if teacher:
                    lesson_text += f", преп: {teacher}"
                if group:
                    lesson_text += f", группа {group}"
                if room:
                    lesson_text += f", ауд. {room}"

                text_parts.append(lesson_text)

        return "\n".join(text_parts)


# Глобальный экземпляр сервиса
guap_schedule_service = GuapScheduleService()
