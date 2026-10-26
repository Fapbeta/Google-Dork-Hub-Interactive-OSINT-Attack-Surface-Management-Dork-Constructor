#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GOOGLE DORK HUB v1.0 (Release Edition)
Interactive OSINT & Attack Surface Management Dork Constructor
Author: github.com/Fapbeta
"""

import os
import re
import sys
import json
import shutil
import subprocess
import urllib.parse
from datetime import datetime

VERSION = "1.0 Release"
AUTHOR_GITHUB = "https://github.com/Fapbeta"

# Цветовая палитра ANSI
R   = "\033[0m"
B   = "\033[1m"
DIM = "\033[2m"
G   = "\033[1;32m"
C   = "\033[1;36m"
Y   = "\033[1;33m"
RED = "\033[1;31m"
M   = "\033[1;35m"
W   = "\033[1;37m"

# Базовые константы фильтрации
NO_AUTH_FILTER = '-inurl:login -inurl:logon -inurl:auth -inurl:signin -intitle:login -intitle:"sign in"'
IP_ONLY_FILTER = 'site:*.*.*.* -site:com -site:net -site:org -site:ua -site:ru -site:gov -site:edu'
NOISE_FILTER   = '-site:github.com -site:stackoverflow.com -site:w3schools.com -inurl:blog -inurl:news -inurl:forum'

# Пути сохранения файлов
BASE_DIR = os.path.expanduser("~")
TXT_FILE = os.path.join(BASE_DIR, "dorks.txt")
MD_FILE  = os.path.join(BASE_DIR, "dork_hub_vault.md")
JSON_FILE = os.path.join(BASE_DIR, "dork_hub_history.json")

SEARCH_ENGINES = {
    "1": ("Google",      "https://www.google.com/search?q="),
    "2": ("DuckDuckGo",  "https://duckduckgo.com/?q="),
    "3": ("Bing",        "https://www.bing.com/search?q="),
    "4": ("Brave",       "https://search.brave.com/search?q="),
    "5": ("Yandex",      "https://yandex.com/search/?text="),
    "6": ("Wayback URL", "https://web.archive.org/web/*/")
}


def cls():
    os.system("clear" if os.name != "nt" else "cls")
    print(f"{C}╔════════════════════════════════════════════════════════════╗{R}")
    print(f"{C}║{B}{W}              GOOGLE DORK HUB — v{VERSION:<26}{R}{C}║{R}")
    print(f"{C}║{Y}       OSINT & Perimeter Audit Constructor (2026 Spec)      {R}{C}║{R}")
    print(f"{C}║{DIM}{W}               GitHub: {AUTHOR_GITHUB:<36}{R}{C}║{R}")
    print(f"{C}╚════════════════════════════════════════════════════════════╝{R}")


def copy_to_clipboard(text):
    """Кроссплатформенное копирование в буфер обмена (Termux / Linux X11 / Wayland)."""
    try:
        if shutil.which("termux-clipboard-set"):
            subprocess.run(["termux-clipboard-set", text], check=False)
            return True
        elif shutil.which("wl-copy"):
            subprocess.run(["wl-copy", text], check=False)
            return True
        elif shutil.which("xclip"):
            p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode("utf-8"))
            return True
        elif shutil.which("xsel"):
            p = subprocess.Popen(["xsel", "-b", "-i"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode("utf-8"))
            return True
    except Exception:
        pass
    return False


def open_url(url):
    """Кроссплатформенное открытие ссылки в браузере."""
    try:
        if shutil.which("termux-open-url"):
            subprocess.run(["termux-open-url", url], check=False)
            return True
        elif shutil.which("xdg-open"):
            subprocess.run(["xdg-open", url], check=False)
            return True
    except Exception:
        pass
    return False


def or_grp(op, items):
    cl = [i.strip() for i in items if i.strip()]
    if not cl:
        return ""
    fmt = lambda x: f'"{x}"' if (" " in x and not x.startswith('"')) else x
    res = [f"{op}:{fmt(i)}" if op else fmt(i) for i in cl]
    return res[0] if len(res) == 1 else "(" + " OR ".join(res) + ")"


def count_operators(dork_str):
    """Подсчет активных операторов для контроля деградации запроса (лимит 2026 года)."""
    ops = re.findall(r'\b(?:site|filetype|ext|intitle|allintitle|inurl|allinurl|intext|allintext|before|after|AROUND)\b', dork_str)
    exclusions = re.findall(r'(?:^|\s)-[a-zA-Z0-9_"]', dork_str)
    return len(ops) + len(exclusions)


def convert_inurl_to_site(dork_str):
    """Адаптация Октябрь 2026: конвертация inurl:путь в site:*/путь."""
    def repl(match):
        val = match.group(1).strip('"').lstrip("/")
        return f"site:*/{val}"
    return re.sub(r'\binurl:("[^"]+"|[^\s\)]+)', repl, dork_str)


# --- 1. ФАЙЛЫ И ДОКУМЕНТЫ ---
def prof_files():
    cls()
    print(f"\n{Y}[1: Поиск файлов и документов]{R}")
    print(" 1. Документы (pdf, doc, docx, rtf, odt)")
    print(" 2. Таблицы и реестры (xls, xlsx, csv, ods)")
    print(" 3. Презентации и отчеты (ppt, pptx, pdf)")
    print(" 4. Технические файлы и конфиги (json, xml, yaml, txt, conf, log)")
    print(" 5. Архивы и бэкапы (zip, rar, 7z, tar, gz, bak, sql)")
    print(" 6. Ввести свои расширения")
    ch = input(f"\n{G}Выбор (1-6): {R}").strip()
    pr = {
        "1": ["pdf", "doc", "docx", "rtf", "odt"],
        "2": ["xls", "xlsx", "csv", "ods"],
        "3": ["ppt", "pptx", "pdf"],
        "4": ["json", "xml", "yaml", "txt", "conf", "log"],
        "5": ["zip", "rar", "7z", "tar", "gz", "bak", "sql"]
    }
    exts = pr.get(ch) or [e.strip().lstrip(".") for e in input("Расширения через запятую: ").split(",") if e.strip()]
    pts = [or_grp("filetype", exts)] if exts else []
    kw = input("Ключевая тема/название (Enter - пропустить): ").strip()
    if kw:
        pts.append(f'"{kw}"' if input("Точная фраза в кавычках? (y/n): ").lower() == "y" else kw)
    return pts


# --- 2. САЙТЫ И IP-ХОСТЫ ---
def prof_sites():
    cls()
    print(f"\n{Y}[2: Сайты, поддомены и прямые IP-адреса]{R}")
    print(" 1. Конкретный домен (напр. example.com)")
    print(" 2. Все поддомены (исключая основной www)")
    print(" 3. Доменная зона (gov.ua, edu.ua, org.ua, com.ua)")
    print(" 4. Несколько сайтов через OR")
    print(" 5. Только IP-адреса (убрать обычные домены .com/.ua и т.д.)")
    print(" 6. Поиск по маске IP-подсети (напр. 185.* или 195.64.*)")
    print(" 7. Хосты на нестандартных портах (8080, 8081, 8443, 8888)")
    ch = input(f"\n{G}Выбор (1-7): {R}").strip()
    pts = []
    if ch == "1":
        d = input("Домен (напр. gov.ua): ").strip()
        if d:
            pts.append(f"site:{d}")
    elif ch == "2":
        d = input("Базовый домен (напр. example.com): ").strip()
        if d:
            pts.extend([f"site:*.{d}", f"-site:www.{d}"])
    elif ch == "3":
        z = {"1": "gov.ua", "2": "edu.ua", "3": "org.ua", "4": "com.ua"}.get(
            input("1)gov.ua 2)edu.ua 3)org.ua 4)com.ua 5)Другая: ").strip()
        ) or input("Введите зону: ").strip()
        if z:
            pts.append(f"site:{z.lstrip('.')}")
    elif ch == "4":
        pts.append(or_grp("site", input("Домены через запятую: ").split(",")))
    elif ch == "5":
        pts.append(IP_ONLY_FILTER)
    elif ch == "6":
        sub = input("Введите начало IP (напр. 185. или 194.44.): ").strip().rstrip(".")
        if sub:
            pts.append(f"site:{sub}.* -site:com -site:net -site:org")
    elif ch == "7":
        pts.append("(inurl:8080 OR inurl:8081 OR inurl:8443 OR inurl:8000 OR inurl:8888)")
    kw = input("Ключевой запрос (Enter - пропустить): ").strip()
    if kw:
        pts.append(kw)
    return pts


# --- 3. ОТКРЫТЫЕ API ---
def prof_api():
    cls()
    print(f"\n{Y}[3: Поиск открытых API и спецификаций]{R}")
    print(" 1. Swagger UI / OpenAPI (интерактивные панели)")
    print(" 2. Файлы схем API (swagger.json, openapi.yaml, api-docs)")
    print(" 3. REST API эндпоинты в URL (/api/v1, /api/v2, /rest)")
    print(" 4. GraphQL песочницы и схемы (GraphiQL, /graphql)")
    print(" 5. Метрики и статус без авторизации (/actuator, /metrics, /health)")
    print(" 6. Документация разработчика и схемы WSDL/WADL")
    ch = input(f"\n{G}Выбор (1-6): {R}").strip()
    m = {
        "1": '(intitle:"Swagger UI" OR inurl:swagger-ui OR inurl:/swagger/index.html)',
        "2": '(inurl:swagger.json OR inurl:swagger.yaml OR inurl:openapi.json OR inurl:openapi.yaml OR inurl:api-docs)',
        "3": '(inurl:"/api/v1" OR inurl:"/api/v2" OR inurl:"/api/v3" OR inurl:"/rest/")',
        "4": '(inurl:graphql OR inurl:graphiql OR intitle:"GraphiQL" OR intitle:"GraphQL Playground")',
        "5": f'(inurl:"/actuator/health" OR inurl:"/actuator/env" OR inurl:"/metrics") {NO_AUTH_FILTER}',
        "6": '(inurl:apidocs OR inurl:developer OR intitle:"API Documentation" OR filetype:wsdl)'
    }
    pts = [m[ch]] if ch in m else []
    t = input("Целевой домен или ключевое слово (Enter - искать везде): ").strip()
    if t:
        pts.insert(0, f"site:{t}" if ("." in t and " " not in t) else f'"{t}"')
    return pts


# --- 4. ОТКРЫТЫЕ КАМЕРЫ И IOT/SCADA ---
def prof_cams():
    cls()
    print(f"\n{Y}[4: Поиск открытых веб-камер и видеопотоков]{R}")
    print(" 1. Камеры Axis — прямой просмотр без логина (view.shtml)")
    print(" 2. Серверы WebcamXP / Webcam 7 (открытые трансляции)")
    print(" 3. Прямые MJPEG видеопотоки без пароля (mjpg/video.mjpg)")
    print(" 4. Сетевые камеры Panasonic / Sony / Mobotix (ViewerFrame)")
    print(" 5. Камеры с открытым веб-интерфейсом (Live View без login)")
    print(" 6. Камеры и встроенные серверы по IP (8080/8081, intitle:1766)")
    ch = input(f"\n{G}Выбор (1-6): {R}").strip()
    m = {
        "1": f'(intitle:"Live View / - AXIS" OR inurl:view/view.shtml OR inurl:view/index.shtml) {NO_AUTH_FILTER}',
        "2": f'(intitle:"webcamXP 5" OR intitle:"webcam 7" OR inurl:8080/view/view.shtml) {NO_AUTH_FILTER}',
        "3": '(inurl:"mjpg/video.mjpg" OR inurl:"axis-cgi/mjpg" OR inurl:"video.mjpg" OR inurl:"faststream.jpg")',
        "4": f'(inurl:"ViewerFrame?Mode=" OR inurl:"MultiCameraFrame?Mode=" OR intitle:"MOBOTIX") {NO_AUTH_FILTER}',
        "5": f'(intitle:"Live View" OR intitle:"Network Camera" OR inurl:LvAppl) {NO_AUTH_FILTER}',
        "6": f'(intitle:"Live View" OR intitle:1766 OR inurl:view/view.shtml) {IP_ONLY_FILTER} {NO_AUTH_FILTER}'
    }
    pts = [m[ch]] if ch in m else []
    loc = input("Уточнить локацию, домен или IP-префикс (Enter - пропустить): ").strip()
    if loc:
        pts.append(f"site:{loc}" if ("." in loc and " " not in loc) else f'"{loc}"')
    return pts


# --- 5. ВЕБ-ПАНЕЛИ, ДАШБОРДЫ И СЕТЕВОЕ ОБОРУДОВАНИЕ ---
def prof_admin():
    cls()
    print(f"\n{Y}[5: Поиск веб-панелей, дашбордов и шлюзов]{R}")
    print(" 1. Открытые дашборды БЕЗ авторизации (Grafana, Kibana, Prometheus, Zabbix)")
    print(" 2. Серверные статусы и мониторы БЕЗ логина (/server-status, /dashboard)")
    print(" 3. Панели управления на прямых IP-адресах БЕЗ авторизации")
    print(" 4. Тестовые контуры (UAT / Staging) и стандартные админки")
    print(" 5. Панели СУБД и хостинга (phpMyAdmin, Webmin, cPanel)")
    print(" 6. Сетевое оборудование и VPN (MikroTik WebFig, UniFi, Check Point SSL)")
    ch = input(f"\n{G}Выбор (1-6): {R}").strip()
    m = {
        "1": f'(intitle:"Grafana" OR intitle:"Kibana" OR intitle:"Prometheus" OR intitle:"Zabbix") {NO_AUTH_FILTER}',
        "2": f'(inurl:"/dashboard" OR inurl:"/server-status" OR intitle:"Dashboard") {NO_AUTH_FILTER}',
        "3": f'(intitle:"Dashboard" OR intitle:"Status" OR intitle:"Web Interface") {IP_ONLY_FILTER} {NO_AUTH_FILTER}',
        "4": '(site:uat.* OR site:stage.* OR site:dev.*) (intitle:login OR inurl:admin)',
        "5": f'(intitle:"phpMyAdmin" OR intitle:"Webmin" OR inurl:phpmyadmin/index.php) {NO_AUTH_FILTER}',
        "6": '(intitle:"RouterOS router configuration" OR inurl:webfig OR intitle:"UniFi OS" OR intitle:"SSL Network Extender Login" -site:checkpoint.com)'
    }
    pts = [m[ch]] if ch in m else []
    dom = input("Целевой домен или IP-префикс (Enter - пропустить): ").strip()
    if dom:
        pts.insert(0, f"site:{dom}" if ("." in dom and " " not in dom) else f'"{dom}"')
    return pts


# --- 6. ПОИСК ПО ФИО (OSINT) ---
def prof_pib():
    cls()
    print(f"\n{Y}[6: Поиск по ФИО / ПІБ (OSINT)]{R}")
    s = input("Фамилия: ").strip()
    n = input("Имя (Enter - если неизвестно): ").strip()
    p = input("Отчество (Enter - если неизвестно): ").strip()
    pts = []
    if s and n and p:
        ni, pi = n[0].upper(), p[0].upper()
        mode = input("1) Точное совпадение  2) Все вариации с инициалами  3) AROUND(3) [по умолч. 2]: ").strip() or "2"
        if mode == "1":
            pts.append(f'"{s} {n} {p}"')
        elif mode == "3":
            pts.append(f'"{s}" AROUND(3) "{n}"')
        else:
            pts.append(f'("{s} {n} {p}" OR "{n} {s}" OR "{s} {ni}. {pi}." OR "{s} {ni}.{pi}.")')
    elif s and n:
        pts.append(f'("{s} {n}" OR "{n} {s}")')
    elif s:
        pts.append(f'"{s}"')
    ctx = input("Город, организация, ЕГРПОУ/ЄДРПОУ или должность (Enter - пропустить): ").strip()
    if ctx:
        if input("Связать через AROUND(10)? (y/n): ").lower() == "y" and pts:
            pts.append(f'{pts.pop()} AROUND(10) "{ctx}"')
        else:
            pts.append(f'"{ctx}"' if " " in ctx else ctx)
    if input("Искать только в документах (pdf,doc,docx,xls,xlsx)? (y/n): ").lower() == "y":
        pts.append("(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx)")
    return pts


# --- 7. ОТКРЫТЫЕ ДИРЕКТОРИИ ---
def prof_idx():
    cls()
    print(f"\n{Y}[7: Открытые файловые каталоги (Index of)]{R}")
    print(" 1. Базовый поиск открытых папок (parent directory)")
    print(" 2. Конфигурации служб (proftpd.conf, dhcpd.conf, /etc/ssh)")
    print(" 3. Архивы, дампы и бэкапы в открытых каталогах")
    print(" 4. Снимки камер и медиафайлы (screenshot*.jpg, *.apk)")
    print(" 5. Указать свое имя файла или папки")
    ch = input(f"\n{G}Выбор (1-5): {R}").strip()
    if ch == "1":
        return ['intitle:"index of" "parent directory"']
    elif ch == "2":
        return ['intitle:"index of" ("proftpd.conf" OR "dhcpd.conf" OR "/etc/ssh")']
    elif ch == "3":
        return ['intitle:"index of" (backup OR dump OR ".sql" OR ".bak" OR ".zip")']
    elif ch == "4":
        return ['intitle:"index of" ("screenshot*.jpg" OR "*.apk")']
    f = input("Название папки или файла (напр. backup, docs, config): ").strip()
    return ['intitle:"index of"'] + ([f'"{f}"' if " " in f else f"inurl:{f}"] if f else [])


# --- 8. АУДИТ СЕКРЕТОВ, ЛОГОВ И КОНФИГОВ (ASM / GHDB) ---
def prof_secrets():
    cls()
    print(f"\n{Y}[8: Аудит логов, переменных окружения и конфигураций (ASM)]{R}")
    print(" 1. Файлы окружения .env и конфигурации подключений")
    print(" 2. Машинные журналы и логи инициализации (ext:log)")
    print(" 3. Манифесты инфраструктуры и пайплайнов (json, yaml, nix)")
    print(" 4. Открытые репозитории .git и истории коммитов")
    print(" 5. SQL-дампы и резервные копии баз данных (sql, bak, dump)")
    ch = input(f"\n{G}Выбор (1-5): {R}").strip()
    m = {
        "1": 'filetype:env ("DB_HOST" OR "DB_PASSWORD" OR "APP_ENV")',
        "2": 'ext:log ("START test_database" OR "Header for logs at time" OR "Exception")',
        "3": '(filetype:json OR filetype:yaml OR ext:nix) ("apiVersion" OR "config" OR "connection")',
        "4": 'intitle:"index of" ".git" "parent directory"',
        "5": '(filetype:sql OR filetype:bak) ("CREATE TABLE" OR "INSERT INTO")'
    }
    pts = [m[ch]] if ch in m else []
    dom = input("Целевой домен для аудита (рекомендуется, напр. example.com): ").strip()
    if dom:
        pts.insert(0, f"site:{dom}")
    return pts


# --- ЭТАП 2: КАСКАДНОЕ СУЖЕНИЕ ---
def refine(pts):
    while True:
        cls()
        dork = " ".join(pts)
        words_cnt = len(dork.split())
        ops_cnt = count_operators(dork)

        if ops_cnt <= 5:
            ops_status = f"{G}{ops_cnt}/6 (Оптимально){R}"
        elif ops_cnt <= 7:
            ops_status = f"{Y}{ops_cnt}/6 (Риск сброса условий){R}"
        else:
            ops_status = f"{RED}{ops_cnt}/6 (Перегрузка операторов!){R}"

        print(f"\n{M}ТЕКУЩИЙ ДОРК{R} [Слов: {W}{words_cnt}/32{R} | Операторов: {ops_status}]:")
        print(f"{B}{G}  {dork or '[пустой запрос]'}{R}")
        print(f"{C}────────────────────────────────────────────────────────────{R}")
        print("  1. [site:]         Ограничить доменом или доменной зоной")
        print("  2. [-исключить]    Отсечь слова или сайты (-site:, -слово)")
        print("  3. [intitle:]      Обязательное слово/фраза в заголовке")
        print("  4. [inurl:]        Обязательный фрагмент в URL")
        print("  5. [intext:]       Точная фраза в тексте страницы")
        print("  6. [AROUND(N)]     Два термина рядом на расстоянии N слов")
        print("  7. [filetype:]     Фильтр по типам файлов (pdf, json, xml...)")
        print("  8. [Даты]          Временные рамки after: / before: (YYYY-MM-DD)")
        print("  9. [OR группа]     Добавить список синонимов через OR")
        print(f" {Y}10. [Только IP]     Искать ссылки с IP-адресами / портами{R}")
        print(f" {Y}11. [Без логина]    Убрать страницы входа (открытые панели){R}")
        print(f" {Y}12. [Анти-шум]      Отсечь GitHub, форумы, блоги и новости{R}")
        print(f" {C}13. [Фикс 2026]     Заменить все inurl: на site:*/путь{R}")
        print(" 14. [Редактор]      Изменить строку дорка вручную")
        print(" 15. [Undo / Сброс]  Удалить последний шаг (или очистить всё)")
        print(f"  {G}0. [ГОТОВО]        Перейти к генерации ссылок и экспорту{R}")

        c = input(f"\n{C}Действие для сужения (0-15): {R}").strip()
        if c == "0":
            break
        elif c == "1":
            v = input("Домены через запятую: ").strip()
            if v:
                pts.append(or_grp("site", v.split(",")))
        elif c == "2":
            for s in input("Исключить домены (через запятую): ").split(","):
                if s.strip():
                    pts.append(f"-site:{s.strip()}")
            for w in input("Исключить слова (через запятую): ").split(","):
                w = w.strip()
                if w:
                    pts.append(f'-"{w}"' if " " in w else f"-{w}")
        elif c == "3":
            v = input("В заголовке (intitle): ").strip()
            if v:
                pts.append(or_grp("intitle", [v]))
        elif c == "4":
            v = input("В URL (через запятую для OR): ").strip()
            if v:
                pts.append(or_grp("inurl", v.split(",")))
        elif c == "5":
            v = input("Точная фраза в тексте: ").strip()
            if v:
                pts.append(or_grp("intext", [v]) if input("1) В кавычках  2) intext: (1/2): ").strip() == "2" else f'"{v}"')
        elif c == "6":
            w1, w2 = input("Первое слово: ").strip(), input("Второе слово: ").strip()
            d = input("Расстояние (по умолч. 5): ").strip() or "5"
            if w1 and w2:
                pts.append(f'"{w1}" AROUND({d}) "{w2}"')
        elif c == "7":
            v = input("Расширения через запятую: ").strip()
            if v:
                pts.append(or_grp("filetype", [e.strip().lstrip(".") for e in v.split(",")]))
        elif c == "8":
            a, b = input("После (YYYY-MM-DD): ").strip(), input("До (YYYY-MM-DD): ").strip()
            if a:
                pts.append(f"after:{a}")
            if b:
                pts.append(f"before:{b}")
        elif c == "9":
            v = input("Синонимы через запятую: ").strip()
            if v:
                pts.append(or_grp("", v.split(",")))
        elif c == "10":
            print(" 1) Все IP (site:*.*.*.* без .com/.org/.ua)\n 2) Конкретная подсеть (напр. 185.*)\n 3) Нестандартные порты (8080, 8443, 8888)")
            ip_m = input("Выбор (1-3): ").strip()
            if ip_m == "2":
                sub = input("Начало IP (напр. 185. или 195.64.): ").strip().rstrip(".")
                if sub:
                    pts.append(f"site:{sub}.* -site:com -site:net -site:org")
            elif ip_m == "3":
                pts.append("(inurl:8080 OR inurl:8081 OR inurl:8443 OR inurl:8000 OR inurl:8888)")
            else:
                pts.append(IP_ONLY_FILTER)
        elif c == "11":
            pts.append(NO_AUTH_FILTER)
        elif c == "12":
            pts.append(NOISE_FILTER)
        elif c == "13":
            pts = [convert_inurl_to_site(p) for p in pts]
        elif c == "14":
            edited = input(f"Новая строка [{dork}]: ").strip()
            if edited:
                pts = [edited]
        elif c == "15":
            sub_c = input("1) Удалить последний элемент  2) Очистить всё [1]: ").strip() or "1"
            if sub_c == "2":
                pts.clear()
            elif pts:
                pts.pop()
    return " ".join(pts)


# --- СОХРАНЕНИЕ И ИСТОРИЯ ---
def save_dork(dork, note=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    url = SEARCH_ENGINES["1"][1] + urllib.parse.quote_plus(dork)

    # 1. Сохранение в классический dorks.txt
    with open(TXT_FILE, "a", encoding="utf-8") as f:
        f.write(dork + "\n")

    # 2. Сохранение в Markdown-каталог (удобно для Obsidian)
    write_header = not os.path.exists(MD_FILE)
    with open(MD_FILE, "a", encoding="utf-8") as f:
        if write_header:
            f.write(f"# Google Dork HUB — Каталог запросов\n> Репозиторий: {AUTHOR_GITHUB}\n\n")
        title_line = f"### [{now}] {note if note else 'Поисковый шаблон'}\n"
        f.write(title_line)
        f.write(f"- **Дорк:** `{dork}`\n")
        f.write(f"- **Google:** [Открыть выдачу]({url})\n\n")

    # 3. Сохранение в JSON историю
    history = []
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append({"timestamp": now, "note": note, "dork": dork, "url": url})
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def view_saved():
    cls()
    print(f"\n{Y}[Сохраненные дорки и история]{R}")
    if not os.path.exists(JSON_FILE):
        print(f"\n{DIM}История пока пуста. Сохраните первый дорк после генерации.{R}")
        input(f"\n{C}Нажмите Enter для возврата в меню...{R}")
        return
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception:
        history = []

    if not history:
        print(f"\n{DIM}Записей не найдено.{R}")
        input(f"\n{C}Нажмите Enter для возврата...{R}")
        return

    for idx, item in enumerate(history[-15:], 1):
        note = f" ({item['note']})" if item.get("note") else ""
        print(f" {C}{idx:>2}.{R} [{item['timestamp']}]{Y}{note}{R}")
        print(f"     {G}{item['dork']}{R}")

    print(f"\n{DIM}Показаны последние {min(len(history), 15)} записей.{R}")
    print(f"Файлы: {W}{TXT_FILE}{R} | {W}{MD_FILE}{R}")
    ch = input(f"\nНомер для копирования/запуска (Enter - назад, C - очистить историю): ").strip()
    if ch.lower() == "c":
        if input("Точно очистить историю JSON? (y/n): ").lower() == "y":
            os.remove(JSON_FILE)
            print(f"{G}[✓] История очищена.{R}")
    elif ch.isdigit():
        subset = history[-15:]
        pos = int(ch) - 1
        if 0 <= pos < len(subset):
            handle_output(subset[pos]["dork"])


def handle_output(dork):
    while True:
        cls()
        if not dork.strip():
            return
        encoded = urllib.parse.quote_plus(dork)
        google_url = SEARCH_ENGINES["1"][1] + encoded

        print(f"\n{Y}ГОТОВЫЙ ДОРК:{R}")
        print(f"{C}────────────────────────────────────────────────────────────{R}")
        print(f"{B}{G}{dork}{R}")
        print(f"{C}────────────────────────────────────────────────────────────{R}")
        print(f"\n{Y}Google URL:{R} {google_url}\n")

        if copy_to_clipboard(dork):
            print(f"{G}[✓] Дорк автоматически скопирован в буфер обмена!{R}\n")

        print(" 1) Открыть в Google")
        print(" 2) Открыть в другом поисковике (DuckDuckGo, Bing, Brave, Yandex, Wayback)")
        print(" 3) Сохранить в базу (dorks.txt + Markdown Vault + JSON)")
        print(" 4) Доработать текущий дорк (вернуться в конструктор)")
        print(" 5) Новый запрос (главное меню)")
        print(" 0) Выход")

        act = input(f"\n{C}Ваш выбор (0-5): {R}").strip()
        if act == "1":
            if not open_url(google_url):
                print(f"{RED}[!] Не удалось вызвать браузер автоматически. Скопируйте ссылку выше.{R}")
                input("Enter для продолжения...")
        elif act == "2":
            print("\nВыберите поисковую систему:")
            for k, v in SEARCH_ENGINES.items():
                print(f"  {k}) {v[0]}")
            eng = input(f"{G}Выбор (1-6): {R}").strip()
            if eng in SEARCH_ENGINES:
                if eng == "6":
                    dom = input("Введите целевой домен/URL для Wayback Machine: ").strip() or dork
                    target_url = SEARCH_ENGINES["6"][1] + dom
                else:
                    target_url = SEARCH_ENGINES[eng][1] + encoded
                print(f"\n{Y}Ссылка ({SEARCH_ENGINES[eng][0]}):{R} {target_url}")
                open_url(target_url)
                input("\nНажмите Enter...")
        elif act == "3":
            note = input("Краткая заметка/тег (Enter - без заметки): ").strip()
            save_dork(dork, note)
            print(f"{G}[✓] Сохранено в TXT, Markdown ({MD_FILE}) и JSON!{R}")
            input("Нажмите Enter...")
        elif act == "4":
            dork = refine([dork])
        elif act == "5":
            break
        elif act == "0":
            sys.exit(0)


def main():
    profiles = {
        "1": prof_files,
        "2": prof_sites,
        "3": prof_api,
        "4": prof_cams,
        "5": prof_admin,
        "6": prof_pib,
        "7": prof_idx,
        "8": prof_secrets
    }
    try:
        while True:
            cls()
            print(f"\n{Y}ШАГ 1: Выберите базовое направление поиска:{R}")
            print("  1. Файлы и документы (pdf, xlsx, docx, конфиги, архивы)")
            print("  2. Сайты, поддомены и прямые IP-хосты")
            print("  3. Открытые API (Swagger, OpenAPI, GraphQL, метрики)")
            print("  4. Открытые камеры и видеопотоки (Axis, MJPEG, IP-камеры)")
            print("  5. Веб-панели, дашборды и шлюзы (Grafana, UAT, MikroTik, VPN)")
            print("  6. ФИО / ПІБ и OSINT (поиск людей, инициалов, упоминаний)")
            print("  7. Открытые каталоги (Index of / Directory Listing)")
            print("  8. Аудит секретов, логов и бэкапов (ASM: .env, .log, .git, .sql)")
            print("  9. Свободный конструктор (начать с чистого листа)")
            print(f" {C}10. История и сохраненные дорки (Vault){R}")
            print(f" {M}11. Открыть GitHub автора ({AUTHOR_GITHUB}){R}")
            print("  0. Выход")

            ch = input(f"\n{G}Ваш выбор (0-11): {R}").strip()
            if ch == "0":
                print(f"\n{C}Завершение работы Google Dork HUB.{R}")
                sys.exit(0)
            elif ch == "10":
                view_saved()
                continue
            elif ch == "11":
                open_url(AUTHOR_GITHUB)
                continue
            elif ch in profiles or ch == "9":
                initial_parts = profiles[ch]() if ch in profiles else []
                clean_parts = [p for p in initial_parts if p]
                final_dork = refine(clean_parts)
                if final_dork.strip():
                    handle_output(final_dork)
    except KeyboardInterrupt:
        print(f"\n\n{Y}[!] Выход из программы.{R}")
        sys.exit(0)


if __name__ == "__main__":
    main()
