"""Модуль для парсинга данных с сайта с помощью Selenium"""

import time

from rich import print
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import constants
import utils


# MARK: CAPTCHA
def exists_captcha(driver: WebDriver) -> bool:
    """
    Проверяет, есть ли капча на странице

    Args:
        driver (WebDriver): Веб-драйвер

    Returns:
        bool: True, если капча есть, False - в противном случае
    """

    try:
        WebDriverWait(driver, constants.DEFAULT_PARSE_TIMEOUT).until(
            EC.visibility_of_element_located((By.ID, "recaptcha-widget"))
        )

        return True

    except TimeoutException:
        return False


# MARK: Авторизация
def check_auth(driver: WebDriver) -> bool:
    """
    Проверяет, авторизован ли пользователь на сайте

    Args:
        driver (WebDriver): Веб-драйвер

    Returns:
        bool: True, если пользователь авторизован, False - в противном случае
    """

    try:
        WebDriverWait(driver, constants.DEFAULT_PARSE_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "li.col.notification-list")
            )
        )

        return False

    except TimeoutException:
        return True


# MARK: Страны
def parse_countries(driver: WebDriver) -> list[str]:
    """
    Нажимает на кнопку "Выбрать страну" и парсит список стран.


    Args:
        driver (WebDriver): Веб-драйвер

    Returns:
        list[str]: Список стран
    """

    try:
        button = WebDriverWait(driver, constants.DEFAULT_PARSE_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "button.btn.btn-light.border.dropdown-toggle.text-truncate.btn-sm",
                )
            )
        )
        time.sleep(constants.DEFAULT_PARSE_TIMEOUT)
        button.click()

        WebDriverWait(driver, constants.DEFAULT_PARSE_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.dropdown-menu"))
        )
        time.sleep(2)

        countries_a_tag = driver.find_elements(
            By.CSS_SELECTOR,
            "a.dropdown-item.d-block",
        )

        return [country.text for country in countries_a_tag]

    except TimeoutException:
        return []


def press_country_button(driver: WebDriver, country: str):
    """
    Выбирает страну из выпадающего списка.

    Args:
        driver (WebDriver): Веб-драйвер
        country (str): Страна
    """

    countries_a_tag = driver.find_elements(
        By.CSS_SELECTOR,
        "a.dropdown-item.d-block",
    )

    for country_a_tag in countries_a_tag:
        if country_a_tag.text == country:
            country_a_tag.click()
            return


# MARK: Категории
def parse_categories(driver: WebDriver) -> list[dict]:
    """
    Парсит список категорий на сайте.

    Args:
        driver (WebDriver): Веб-драйвер

    Returns:
        list[dict]: Список категорий, где каждая категория содержит название и ссылку на страницу категории
    """
    containers_div = WebDriverWait(driver, constants.DEFAULT_PARSE_TIMEOUT).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.container-fluid.px-2.px-md-3")
        )
    )

    categories_container = None
    for container in containers_div.find_elements(By.TAG_NAME, "div"):
        try:
            label = (
                container.find_element(By.CSS_SELECTOR, "div.h4.text-dark")
                .text.strip()
                .lower()
            )

        except NoSuchElementException:
            continue

        if label == "все категории":
            categories_container = container
            break

    if not categories_container:
        return []

    categories = []
    for category_a_tag in categories_container.find_elements(
        By.CSS_SELECTOR, "a.text-dark"
    ):
        category_name = category_a_tag.get_attribute("innerHTML").strip()
        category_url = category_a_tag.get_attribute("href")

        if category_name not in [category["название"] for category in categories]:
            categories.append({"название": category_name, "ссылка": category_url})

    return categories


# MARK: Каналы и чаты
def parse_channel_info(driver: WebDriver, data: dict):
    """
    Парсит информацию о канале, дообавляет ее в словарь

    Args:
        driver (WebDriver): Веб-драйвер
        data (dict): Словарь с данными канала
    """

    driver.get(data["ссылка для парсинга"])
    # Проверяем наличие капчи, если она есть, то просим пользователя решить её
    if exists_captcha(driver):
        utils.prompt_to_solve_captcha(driver)

    # Получаем ссылки из описания
    links = []
    for link in driver.find_elements(By.CSS_SELECTOR, "a[rel='nofollow']"):
        text = link.get_attribute("text")
        if text.startswith("@") and text not in links:
            links.append(text.strip())

    data["ссылки"] = ", ".join(links)

    posts_container = WebDriverWait(driver, constants.DEFAULT_PARSE_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.posts-list"))
    )
    posts = posts_container.find_elements(By.CSS_SELECTOR, "div.card.card-body")
    likes, views, comments = 0, 0, 0

    # Парсим последние NUMBER_OF_POSTS_TO_PARSE постов
    for i, post in enumerate(posts[: constants.NUMBER_OF_POSTS_TO_PARSE]):
        if i == 0:
            try:
                data["дата последнего поста"] = post.find_element(
                    By.CSS_SELECTOR, "small"
                ).text

            except NoSuchElementException:
                data["дата последнего поста"] = None
                break

        try:
            views_text = post.find_element(
                By.CSS_SELECTOR,
                "a.btn.btn-light.btn-rounded.py-05.px-13.mr-1.popup_ajax.font-12.font-sm-13",
            ).text
            views += int(
                views_text.replace("m", "0" * (5 if "." in views_text else 6))
                .replace("k", "0" * (2 if "." in views_text else 3))
                .replace(".", "")
            )

        except NoSuchElementException:
            pass

        try:
            likes_text = post.find_element(
                By.CSS_SELECTOR,
                "span[data-original-title^='Количество реакций к публикации']",
            ).text

            likes += int(
                likes_text.replace("m", "0" * (5 if "." in likes_text else 6))
                .replace("k", "0" * (2 if "." in likes_text else 3))
                .replace(".", "")
            )

        except NoSuchElementException:
            pass

        try:
            comments_text = post.find_element(
                By.CSS_SELECTOR,
                "span[data-original-title='Количество комментариев к публикации']",
            ).text

            comments += int(
                comments_text.replace("m", "0" * (5 if "." in comments_text else 6))
                .replace("k", "0" * (2 if "." in comments_text else 3))
                .replace(".", "")
            )

        except NoSuchElementException:
            pass

    # Парсим все посты за последние 10 дней
    recent_posts_count, offset = 0, 0
    while True:
        is_last_post_in_10_days = True
        for post in posts[offset:]:
            post_date = post.find_element(By.CSS_SELECTOR, "small").text
            if utils.is_date_in_the_last_10_days(post_date):
                recent_posts_count += 1
            else:
                is_last_post_in_10_days = False
                break

        if not is_last_post_in_10_days:
            break

        # Прокрутка вниз
        try:
            offset = int(
                driver.find_element(By.CSS_SELECTOR, "strong.lm-current-loaded").text
            )
            button = WebDriverWait(driver, constants.DEFAULT_PARSE_TIMEOUT).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "button.btn.btn-light.border.lm-button.py-1.min-width-220px",
                    )
                )
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            driver.execute_script("arguments[0].click();", button)
            # Обновляем список постов
            posts_container = WebDriverWait(
                driver, constants.DEFAULT_PARSE_TIMEOUT
            ).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.posts-list")))
            posts = posts_container.find_elements(By.CSS_SELECTOR, "div.card.card-body")

        except Exception:
            break

    data[
        f"среднее количество лайков за последние {constants.NUMBER_OF_POSTS_TO_PARSE} постов"
    ] = int(likes / len(posts))
    data[
        f"среднее количество просмотров за последние {constants.NUMBER_OF_POSTS_TO_PARSE} постов"
    ] = int(views / len(posts))
    data[
        f"среднее количество комментариев за последние {constants.NUMBER_OF_POSTS_TO_PARSE} постов"
    ] = int(comments / len(posts))
    data[
        f"наличие комментариев за последние {constants.NUMBER_OF_POSTS_TO_PARSE} постов"
    ] = "да" if comments > 0 else "нет"
    data["среднее количество постов за последние 10 дней"] = recent_posts_count / 10


def parse_and_save_data(
    driver: WebDriver,
    content_type: str,
    keywords: list[str],
    min_subscribers: int | None,
    max_subscribers: int | None,
):
    """
    Парсит данные в зависимости от типа контента.

    Args:
        driver (WebDriver): Веб-драйвер
        content_type (str): Тип контента(канал или чат)
        keywords (list[str]): Ключевые слова для фильтрации каналов и чатов
        min_subscribers (int | None): Минимальное количество подписчиков
        max_subscribers (int | None): Максимальное количество подписчиков
    """

    if content_type == "чат":
        button = WebDriverWait(driver, constants.DEFAULT_PARSE_TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "peer_type_chat"))
        )
        driver.execute_script("arguments[0].click();", button)

    data = []
    count_of_elments_per_page, i = None, 0
    while True:
        try:
            button = WebDriverWait(driver, constants.DEFAULT_PARSE_TIMEOUT).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "#category-list-form button.btn.btn-light.border.lm-button.py-1.min-width-220px",
                    )
                )
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", button)

            subscribers = float("inf")
            content_data = driver.find_elements(By.CSS_SELECTOR, ".peer-item-box")
            for item_data in (
                content_data[i * count_of_elments_per_page :]
                if count_of_elments_per_page
                else content_data
            ):
                description = item_data.find_element(
                    By.CSS_SELECTOR, "a.text-body"
                ).text
                # Фильтруем по ключевым словам
                if keywords and not any(
                    keyword.lower() in description.lower() for keyword in keywords
                ):
                    continue

                subscribers = int(
                    item_data.find_element(By.TAG_NAME, "b").text.replace(" ", "")
                )
                # Фильтруем по количеству подписчиков
                if min_subscribers is not None and subscribers < min_subscribers:
                    break

                if max_subscribers is not None and subscribers > max_subscribers:
                    continue

                url = item_data.find_element(
                    By.CSS_SELECTOR, "a.text-body"
                ).get_attribute("href")

                item_data = {
                    "название": description.split("\n")[0],
                    "ссылка": constants.TELEGRAM_BASE_URL
                    + url.split("/")[-1].replace("@", ""),
                    "подписчики": subscribers,
                    "ссылка для парсинга": url,
                }

                data.append(item_data)

            if min_subscribers is not None and subscribers < min_subscribers:
                break

            driver.execute_script("arguments[0].click();", button)
            i += 1
            if count_of_elments_per_page is None:
                count_of_elments_per_page = len(content_data)

        except TimeoutException:
            break

        except Exception as e:
            print(f"[red]Ошибка при парсинге данных:[/red] {e}")
            break

    print(f"[blue]Найдено {len(data)} {content_type}ов[/blue]")
    utils.save_data(data)
    print(
        f"[green]Данные о {len(data)} {content_type}ах записаны в выходной файл {constants.OUTPUT_PATH}[/green]"
    )

    if content_type == "канал" and data:
        print("[yellow]Парсинг данных о каналах...[/yellow]")
        for i, item_data in enumerate(data):
            try:
                parse_channel_info(driver, item_data)

            except Exception as e:
                print(f"[red]Ошибка при парсинге данных канала:[/red] {e}")

            # Каждые BATCH_SIZE итераций перезаписываем данные в файл
            if i != 0 and i % constants.BATCH_SAVE_SIZE == 0:
                utils.save_data(data)
                print(
                    f"[green]Подробная информация о {i} {content_type}ах добавлена в выходной файл {constants.OUTPUT_PATH}[/green]"
                )

        utils.save_data(data)
        print(
            f"[green]Подробная информация о {len(data)} {content_type}ах добавлена в выходной файл {constants.OUTPUT_PATH}[/green]"
        )
