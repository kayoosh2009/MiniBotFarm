import time
import datetime
import random
import requests
import os
from selenium import webdriver
from selenium.webdriver.chromium.options import ChromiumOptions

# Твой URL на GitHub Pages
CONFIG_URL = "https://kayoosh2009.github.io/MiniBotFarm/task.json"

def get_config():
    """Скачивает актуальные настройки с GitHub"""
    try:
        # Устанавливаем таймаут 5 секунд, чтобы бот не зависал при проблемах с сетью
        response = requests.get(CONFIG_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Ошибка загрузки конфига: {e}")
    return None

def keep_awake():
    """Сигнализирует системе о том, что компьютер занят работой, чтобы экран не гас"""
    try:
        # Имитируем ложное обращение к монитору сессии Gnome/Mutter, чтобы сбросить таймер сна
        os.system("busctl --user call org.gnome.Mutter.IdleMonitor /org/gnome/Mutter/IdleMonitor/Core org.gnome.Mutter.IdleMonitor GetIdletime > /dev/null 2>&1")
    except Exception:
        pass

def is_within_working_hours(start_time_str, end_time_str):
    """Проверяет, входит ли текущее время в рабочий интервал из JSON"""
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    return start_time_str <= current_time < end_time_str

def simulate_human_visit(url, start_time, end_time):
    """Один визит на сайт со случайной длительностью и ежеминутной проверкой гитхаба"""
    options = ChromiumOptions()
    options.add_argument("--headless=new") # Скрытый режим (без окон)
    options.add_argument("--mute-audio")    # Без звука
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Маскируемся под обычный браузер
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    session_duration = random.randint(30, 300)
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Открываю сайт в фоне на {session_duration} сек...")
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        start_session = time.time()
        last_github_check = time.time()

        while time.time() - start_session < session_duration:
            keep_awake()
            
            # Каждую 1 минуту (60 секунд) проверяем, не изменился ли конфиг на гитхабе
            if time.time() - last_github_check >= 60:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Плановая проверка гитхаба во время визита...")
                new_config = get_config()
                if new_config:
                    # Если изменился URL или рабочее время — мгновенно прерываем сессию, чтобы обновиться
                    if new_config.get("target_url") != url or new_config.get("start_time") != start_time or new_config.get("end_time") != end_time:
                        print("Конфиг изменился! Срочно закрываю браузер для обновления параметров.")
                        break
                last_github_check = time.time()

            time.sleep(5) # Короткий сон для поддержки отзывчивости цикла
            
    except Exception as e:
        print(f"Ошибка во время сессии браузера: {e}")
    finally:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Закрываю браузер.")
        try:
            driver.quit()
        except:
            pass

def main():
    print("Бот успешно запущен. Начинаю опрос гитхаба раз в минуту...")
    last_github_check = 0

    while True:
        # Проверяем гитхаб раз в минуту вне активных визитов
        if time.time() - last_github_check >= 60:
            config = get_config()
            last_github_check = time.time()
        else:
            config = None

        if config:
            start_time = config.get("start_time")
            end_time = config.get("end_time")
            url = config.get("target_url")
            
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Успешно прочитан конфиг. Текущее задание: {start_time}-{end_time} -> {url}")

            if is_within_working_hours(start_time, end_time):
                # Запускаем визит (внутри него тоже есть проверка гитхаба раз в минуту)
                simulate_human_visit(url, start_time, end_time)
                
                if not is_within_working_hours(start_time, end_time):
                    print("Рабочее время закончилось. Ухожу на покой.")
                    continue
                
                # Отдых между заходами
                rest_duration = random.randint(100, 200)
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Отдыхаю {rest_duration} сек перед следующим заходом...")
                
                start_rest = time.time()
                last_rest_check = time.time()
                while time.time() - start_rest < rest_duration:
                    keep_awake()
                    
                    # Проверка гитхаба раз в минуту во время отдыха
                    if time.time() - last_rest_check >= 60:
                        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Плановая проверка гитхаба во время отдыха...")
                        new_config = get_config()
                        if new_config and (new_config.get("target_url") != url or new_config.get("start_time") != start_time or new_config.get("end_time") != end_time):
                            print("Конфиг изменился во время отдыха! Прерываем отдых.")
                            break
                        last_rest_check = time.time()

                    time.sleep(5)
                continue
            else:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Сейчас вне рабочего времени расписания.")

        # Если отдыхаем или вне рабочего времени — бережем ресурсы, спим по 5 сек
        keep_awake()
        time.sleep(5)

if __name__ == "__main__":
    main()