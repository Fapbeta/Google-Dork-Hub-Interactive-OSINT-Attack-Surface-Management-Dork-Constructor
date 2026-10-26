# 🎯 Google Dork HUB v1.0
**Interactive OSINT & Attack Surface Management Dork Constructor (2026 Spec)**

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Termux%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

**Google Dork HUB** — это интерактивный консольный конструктор для поисковой разведки и аудита периметра. Скрипт адаптирован под ограничения поисковых систем (октябрь 2026 года) и позволяет генерировать точные запросы без потери операторов.



![_20261026_123715.JPG](https://github.com/user-attachments/assets/6b70cbde-e720-4945-a635-b5559797abef)



## 🚀 Особенности
- **Архитектура 2026 года:** обход деградации оператора `inurl:`, контроль плотности операторов (лимит 6 фильтров).
- **Кроссплатформенность:** автоматическая работа с буфером обмена и браузером в Termux (Android) и десктопном Linux.
- **Мульти-экспорт:** автоматическое сохранение истории в `TXT`, `JSON` и `Markdown` (Obsidian Vault ready).
- **Анти-шум фильтры:** очистка выдачи от GitHub, блогов, новостей и форумов в один клик.

## 📦 Установка (Termux / Linux)

```bash
# 1. Клонирование репозитория
git clone https://github.com/Fapbeta/Google-Dork-Hub-Interactive-OSINT-Attack-Surface-Management-Dork-Constructor.git  
                                                    
cd
Google-Dork-Hub-Interactive-OSINT-Attack-Surface-Management-Dork-Constructor 
                            
# 2. Выдача прав на выполнение
chmod +x dork_hub.py

# 3. Запуск
python3 dork_hub.py






