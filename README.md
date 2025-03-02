# Tg start parser 

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Selenium](https://img.shields.io/badge/-selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white)

## Description

This is a simple parser for channels and chats with Selenium from https://tgstat.ru/ website that saves outputs to .xlsx file.

After starting parser, you will be able to select country, category and whather it should parse channels or chats.

If you select a chat, the fields will be:
```bash
название (name0
ссылка (url)
подписчики (subscribers)
```
If you select to parse a channel, there will be the same fields as the chat ones, but with some additional ones:
```bash
дата последнего поста (last post date)
среднее количество лайков за последние 10 постов (average number of likes for last 10 posts)
среднее количество лайков за последние 10 постов (average number of views for last 10 posts)
``` 

## Project Setup and launch

- With .exe file:

```bash
.\dist\main.exe
```

- Manual launch:

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).

2. Install dependencies:

```bash
uv sync 
```

5. Launch:

```bash
uv run -m src.main
```

> [!NOTE]  
> After running the script, you need to manually log in to the site in the Chrome browser opened by Selenium, then press Enter in the console. This is necessary because the site requires authentication to get the full list of channels/chats.
>
> The script results are saved to the outputs folder with .xlsx extension.
>
> The script may throw an OSError when closing the browser. This is an error in the undetected-chromedriver library that does not affect the script's operation.
