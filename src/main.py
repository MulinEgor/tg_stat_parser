"""Модуль для запуска программы"""

import questionary
from rich import print

import constants
import parse
import utils


def main():
    try:
        driver = parse.get_driver()

        driver.maximize_window()
        driver.get(constants.WEBSITE_BASE_URL)

        if parse.exists_captcha(driver):
            utils.prompt_to_solve_captcha(driver)

        # MARK: Авторизация
        print(
            "[yellow]Авторизуйтесь на сайте, чтобы получить полный список каналов[/yellow]"
        )
        input("Нажмите Enter, когда авторизуетесь...")

        if not parse.check_auth(driver):
            print(
                "[red]Вы не авторизовались на сайте, полное количество каналов не будет получено[/red]"
            )
            return
        else:
            print("[green]Авторизация прошла успешно[/green]")

        # MARK: Страны
        print("[yellow]Получение списка стран...[/yellow]")
        countries = parse.parse_countries(driver)

        if not countries:
            print("[red]Страницы с выбором стран не загружены[/red]")
            return

        print(f"[blue]Найдено {len(countries)} стран:[/blue]")

        country = questionary.select("Выберите страну:", choices=countries).ask()

        parse.press_country_button(driver, country)

        if parse.exists_captcha(driver):
            utils.prompt_to_solve_captcha(driver)

        # MARK: Категории
        print("[yellow]Получение списка категорий...[/yellow]")
        categories = parse.parse_categories(driver)

        if not categories:
            print("[red]Страницы с выбором категорий не загружены[/red]")
            return

        print(f"[blue]Найдено {len(categories)} категорий:[/blue]")

        category_names = [cat["название"] for cat in categories]
        category_name = questionary.select(
            "Выберите категорию:", choices=category_names
        ).ask()

        category = next(cat for cat in categories if cat["название"] == category_name)

        driver.get(category["ссылка"])

        if parse.exists_captcha(driver):
            utils.prompt_to_solve_captcha(driver)

        # MARK: Тип контента
        print(f"[blue]Найдено {len(constants.CONTENT_TYPES)} типов контента:[/blue]")

        content_type = questionary.select(
            "Выберите тип контента:", choices=constants.CONTENT_TYPES
        ).ask()

        parse_channel_info = False
        if content_type == "канал":
            parse_channel_info = questionary.confirm(
                "Хотите получить подробную информацию о канале?"
            ).ask()

        min_subscribers = questionary.text(
            "Введите минимальное количество подписчиков (оставьте пустым, если ограничение не требуется):"
        ).ask()

        min_subscribers = int(min_subscribers) if min_subscribers.strip() else None

        max_subscribers = questionary.text(
            "Введите максимальное количество подписчиков (оставьте пустым, если ограничение не требуется):"
        ).ask()

        max_subscribers = int(max_subscribers) if max_subscribers.strip() else None

        keywords = questionary.text(
            "Введите ключевые слова через пробел по которым будет происходить поиск (оставьте пустым, если не требуется):"
        ).ask()

        keywords = keywords.split()

        print(f"[yellow]Получение списка {content_type}ов...[/yellow]")
        parse.parse_and_save_data(
            driver,
            content_type,
            keywords,
            min_subscribers,
            max_subscribers,
            parse_channel_info,
        )

    except KeyboardInterrupt:
        print("[red]Программа завершена пользователем[/red]")

    except Exception as e:
        print(f"[red]Произошла ошибка: {e}[/red]")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
