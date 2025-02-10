"""Модуль для утилит"""

import os
from datetime import datetime

import pandas as pd

import constants as constants


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
