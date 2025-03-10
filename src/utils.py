"""Модуль для утилит"""

import os
from datetime import datetime

import pandas as pd
from rich import print
from selenium.webdriver.remote.webdriver import WebDriver

import constants
import parse


def prompt_to_solve_captcha(driver: WebDriver):
    """
    Просит пользователя решить капчу

    Args:
        driver (WebDriver): Веб-драйвер
    """

    while True:
        print("[yellow]Капча обнаружена[/yellow]")
        input("Нажмите Enter, когда решите капчу...")

        if parse.exists_captcha(driver):
            print("[red]Капча не решена, попробуйте ещё раз[/red]")
        else:
            print("[green]Капча решена, работа парсера продолжается[/green]")
            break


def save_data(data: list[dict]):
    """
    Сохраняет данные в файл Excel

    Args:
        data (list[dict]): Данные для сохранения
    """
    if not os.path.exists(constants.OUTPUT_FOLDER):
        os.makedirs(constants.OUTPUT_FOLDER)

    if constants.OUTPUT_PATH is None:
        constants.OUTPUT_PATH = f"{constants.OUTPUT_FOLDER}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

    df = pd.DataFrame(data)
    df.pop("ссылка для парсинга")
    df.to_excel(constants.OUTPUT_PATH, index=False, engine="openpyxl")


def is_date_in_the_last_10_days(date: str) -> bool:
    """
    Проверяет, является ли дата последних 10 дней

    Args:
        date (str): Дата в формате "день месяц год(опционально)"

    Returns:
        bool: True, если дата последних 10 дней, False - иначе
    """

    date_parts = date.split(", ")[0].split()
    post_day = int(date_parts[0])
    post_month = datetime.strptime(date_parts[1], "%b").month

    # Получаем текущую дату
    current_date = datetime.now()
    # Создаем дату поста
    if len(date_parts) == 3:  # Если указан год
        post_year = int(date_parts[2])
    else:
        post_year = current_date.year

    post_datetime = datetime(post_year, post_month, post_day)

    # Вычисляем разницу в днях
    days_difference = (current_date - post_datetime).days

    return days_difference <= 10
