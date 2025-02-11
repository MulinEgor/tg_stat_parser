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

    df = pd.DataFrame(data)
    output_path = (
        f"{constants.OUTPUT_FOLDER}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    )
    df.pop("ссылка для парсинга")
    df.to_excel(output_path, index=False, engine="openpyxl")
