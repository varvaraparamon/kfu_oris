import threading
import queue
import time
import random
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    COOKING = "cooking"
    READY = "ready"
    COMPLETED = "completed"

class OrderSystem:
    def __init__(self):
        # сигнал, что кухня готова к работе (типа ресторан открывается)
        self.kitchen_ready = threading.Event()

        # для управления доступом к плите (ограниченное количество мест)
        self.stove_condition = threading.Condition()
        self.available_stoves = 2  # всего 2 конфорки :( Мы бедный ресторан

        # очередь заказов
        self.order_queue = queue.Queue(maxsize=10)

        # статистика
        self.stats = {
            "total_orders": 0,
            "completed_orders": 0,
            "failed_orders": 0,
            "cooking_time_total": 0
        }
        self.stats_lock = threading.Lock()

        # флаг работы системы
        self.system_running = False

        # потоки
        self.producers = []
        self.consumers = []
        self.monitor_thread = None

    # функция подготовки кухни, при открытии ресторана, кухня сначала готовится
    def kitchen_preparation(self):
        print("ПОВАР: Начинаю подготовку кухни...")

        # имитация подготовки
        tasks = [
            "Проверяю оборудование",
            "Настраиваю температуру плит",
            "Подготавливаю ингредиенты",
            "Запускаю вытяжку"
        ]

        # DONE: Выполняем подготовительные действия и сообщаем поварам и официантам "ОТКРЫВАЕМСЯ!!!"
        for task in tasks:
            print(task)
            time.sleep(1)
        print('Кухня готова, начинаем работу')
        self.kitchen_ready.set()

    # функция для генерации заказов (то есть наши официанты). Не забываем, что ресторан должен быть открыт!
    def order_producer(self, producer_id):

        self.kitchen_ready.wait()

        menu_items = [
            # придумайте пулл блюд, с которыми будут генерироваться заказы
            "борщ",
            "котлетка с пюрешкой",
            "плов",
            "макароны по флотски",
            "кофе",
            "чай"
        ]

        while self.system_running:
            order = {
                "order_id": random.randint(1000, 9999),
                "customer_id": random.randint(1, 100),
                "dish": random.choice(menu_items),
                "complexity": random.randint(1, 5),  # сложность приготовления 1-5
                "status": OrderStatus.PENDING.value,
                "created_time": datetime.now(),
                "producer_id": producer_id
            }
            # DONE: Официант принимает заказ (мы его генерируем), отправляет поварам (не забываем про подсчет статистики)

            try:
                self.order_queue.put(order, timeout=0.5)
                print(f"Официант {producer_id} принял заказ")
                with self.stats_lock:
                    self.stats['total_orders'] += 1
            except Exception:
                continue 

            time.sleep(random.uniform(0.5, 2))

    # функция для обработки заказов (наши поварята) - повар спрашивает повара... Не забываем, что ресторан должен быть открыт!
    def chef_consumer(self, chef_id):

        # DONE: Повар забирает заказ, проверяет есть ли свободная конфорка (если нет, то ждет, естественно), готовит по
        #  длительности в зависимости от сложности блюда cook_time = order["complexity"] * 0.5. Не забываем про статистику и статусы блюд!
        self.kitchen_ready.wait()
        
        while self.system_running:
            try:
                order = self.order_queue.get(timeout=1)
            except Exception:
                continue

            with self.stove_condition:
                while self.available_stoves == 0:
                    print(f"Повар {chef_id} ждет пока освободится конфорка")
                    self.stove_condition.wait()
                self.available_stoves -= 1
                
            print(f"Повар {chef_id} начал готовить")
            order['status'] = OrderStatus.COOKING.value
            cooking_time = order['complexity'] * 0.5
            time.sleep(cooking_time)

            order['status'] = OrderStatus.COMPLETED.value

            with self.stats_lock:
                self.stats['completed_orders'] += 1
                self.stats['cooking_time_total'] += cooking_time

            with self.stove_condition:
                self.available_stoves += 1
                self.stove_condition.notify()

            print(f"Повар {chef_id} отдал заказ")


    # Функция для демон-потока
    def monitoring(self):

        # DONE: Если рестик работает, каждые 5 секунд забираем статистику по параметрам:
        #  "Всего заказов",
        #  "Выполнено",
        #  "В очереди",
        #  "Среднее время приготовления блюд",
        #  "Количество свободных конфорок" и записываем статистику в файл со временем когда эта статистика была записана
            while self.system_running:
                stats_time = datetime.now(tz=ZoneInfo('Europe/Moscow'))
                total_orders = self.stats['total_orders']
                completed_orders = self.stats['completed_orders']
                pending_orders = self.order_queue.qsize()
                avg_cooking_time = self.stats['cooking_time_total'] / completed_orders if completed_orders > 0 else 0
                available_stoves = self.available_stoves

                stats_dict = {
                    "Время" : str(stats_time),
                    "Всего заказов" : total_orders,
                    "Выполнено" : completed_orders,
                    "В очереди" : pending_orders,
                    "Среднее время приготовления блюд" : f"{avg_cooking_time:.2f}",
                    "Количество свободных конфорок" : available_stoves
                }
                with open('HW2/stats.txt', 'a', encoding='utf-8') as f:
                    json.dump(stats_dict, f, indent=2, ensure_ascii=False)

                time.sleep(5)

    def start_system(self):
        print("ЗАПУСК СИСТЕМЫ РЕСТОРАНА...")
        self.system_running = True

        # DONE: Запускаем нашу подготовку ресторана в отдельном потоке, ждем завершения и запускаем официантов и
        #  поваров, а также нашего демон-потока для статистики

        t_prep = threading.Thread(target=self.kitchen_preparation)
        t_prep.start()

        self.monitor_thread = threading.Thread(target=self.monitoring, daemon=True)
        self.monitor_thread.start()
        #t_prep.join() не обязательно, тк повара и официанты и так ждут event, для показательности выключим

        for i in range(5):
            t_prod = threading.Thread(target=self.order_producer, args=(i,))
            t_cons = threading.Thread(target=self.chef_consumer, args=(i,))
            t_prod.start()
            t_cons.start()
            self.producers.append(t_prod)
            self.consumers.append(t_cons)



    def stop_system(self):
        print("ЗАКРЫТИЕ РЕСТОРАНА...")


        # DONE: ждем когда все освободятся, выводим в консоль итоги рабочего дня:
        #  "Всего принято заказов",
        #  "Успешно выполнено",
        #  "Среднее время приготовления

        self.system_running = False

        for t in self.producers:
            t.join()
        
        for t in self.consumers:
            t.join()


        with self.stats_lock:
            total_orders = self.stats["total_orders"]
            completed_orders = self.stats["completed_orders"]
            avg_cooking_time = self.stats["cooking_time_total"] / completed_orders if completed_orders > 0 else 0

        print(f'''
Всего принято заказов: {total_orders}
Успешно выполнено: {completed_orders}
Среднее время приготовления: {avg_cooking_time:.2f}
              ''')

        print("РЕСТОРАН ЗАКРЫТ!")


# Запуск системы
if __name__ == "__main__":
    restaurant = OrderSystem()

    try:
        restaurant.start_system()

        # работаем 60 секунд
        time.sleep(60)

        restaurant.stop_system()

    except KeyboardInterrupt:
        print("!ЭКСТРЕННОЕ ЗАКРЫТИЕ!")
        restaurant.stop_system()