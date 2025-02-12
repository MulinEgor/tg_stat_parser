"""Модуль для запуска программы"""

import questionary
import undetected_chromedriver as uc
from rich import print
from selenium.common.exceptions import SessionNotCreatedException

import constants
import parse
import utils


def main():
    # MARK: Инициализация
    try:
        driver = uc.Chrome()
    except SessionNotCreatedException as e:
        broswer_version = int(e.msg.split(" ")[-1].split(".")[0])
        driver = uc.Chrome(version_main=broswer_version)

    try:
        driver.maximize_window()
        driver.get(constants.WEBSITE_BASE_URL)

        # Проверяем наличие капчи, если она есть, то просим пользователя решить её
        if parse.exists_captcha(driver):
            utils.prompt_to_solve_captcha(driver)

        # MARK: Авторизация
        print(
            "[yellow]Авторизуйтесь на сайте, чтобы получить полный список каналов[/yellow]"
        )
        input("Нажмите Enter, когда авторизуетесь...")

        # Проверяем авторизацию
        if not parse.check_auth(driver):
            print(
                "[red]Вы не авторизовались на сайте, полное количество каналов не будет получено[/red]"
            )
            return
        else:
            print("[green]Авторизация прошла успешно[/green]")

        # MARK: Страны
        # Получаем список стран
        print("[yellow]Получение списка стран...[/yellow]")
        countries = parse.parse_countries(driver)

        if not countries:
            print("[red]Страницы с выбором стран не загружены[/red]")
            return

        print(f"[blue]Найдено {len(countries)} стран:[/blue]")

        # Выбираем страну
        country = questionary.select("Выберите страну:", choices=countries).ask()

        # Переходим на страницу с выбранной страной
        parse.press_country_button(driver, country)

        # Проверяем наличие капчи, если она есть, то просим пользователя решить её
        if parse.exists_captcha(driver):
            utils.prompt_to_solve_captcha(driver)

        # MARK: Категории
        # Получаем список категорий
        print("[yellow]Получение списка категорий...[/yellow]")
        categories = parse.parse_categories(driver)

        if not categories:
            print("[red]Страницы с выбором категорий не загружены[/red]")
            return

        print(f"[blue]Найдено {len(categories)} категорий:[/blue]")

        # Выбираем категорию
        category_names = [cat["название"] for cat in categories]
        category_name = questionary.select(
            "Выберите категорию:", choices=category_names
        ).ask()

        category = next(cat for cat in categories if cat["название"] == category_name)

        # Переходим на страницу с категорией
        driver.get(category["ссылка"])

        # Проверяем наличие капчи, если она есть, то просим пользователя решить её
        if parse.exists_captcha(driver):
            utils.prompt_to_solve_captcha(driver)

        # MARK: Тип контента
        print(f"[blue]Найдено {len(constants.CONTENT_TYPES)} типов контента:[/blue]")

        # Выбираем тип контента
        content_type = questionary.select(
            "Выберите тип контента:", choices=constants.CONTENT_TYPES
        ).ask()

        min_subscribers = questionary.text(
            "Введите минимальное количество подписчиков (оставьте пустым, если ограничение не требуется):"
        ).ask()

        # Преобразуем введенное значение в число или None
        min_subscribers = int(min_subscribers) if min_subscribers.strip() else None

        # MARK: Каналы и чаты
        print(f"[yellow]Получение списка {content_type}ов...[/yellow]")
        data = parse.parse_data(driver, content_type, min_subscribers)

        print(f"[blue]Найдено {len(data)} {content_type}ов[/blue]")

        # MARK: Сохранение данных
        utils.save_data(data)

        print(
            f"[green]Данные успешно сохранены в директорию {constants.OUTPUT_FOLDER}[/green]"
        )

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
