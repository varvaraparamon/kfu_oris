import threading
import time

class TicketBookingSystem:
    def __init__(self, total_tickets):
        self.total_tickets = total_tickets
        self.available_tickets = total_tickets
        self.booking_lock = threading.Lock()

    def check_availability(self):
        with self.booking_lock:
            return self.available_tickets 

    def book_ticket(self, customer_name, tickets_count):
        with self.booking_lock:
            if self.available_tickets >= tickets_count:
                self.available_tickets -= tickets_count
                print(f"{customer_name} забронировал {tickets_count} билетов")
            else:
                print(f"{customer_name}: нет {tickets_count} билетов, всего {self.available_tickets}")

    def cancel_booking(self, customer_name, tickets_count):
        with self.booking_lock:
            self.available_tickets += tickets_count
            print(f"{customer_name} вернул {tickets_count} билетов")



# Тестирование системы
def test_booking_system():
    # Создаем систему с 10 билетами
    booking_system = TicketBookingSystem(10)

    print("=== СИСТЕМА БРОНИРОВАНИЯ БИЛЕТОВ ===")
    print(f"Всего билетов: {booking_system.total_tickets}")
    print(f"Доступно билетов: {booking_system.check_availability()}")
    print()

    # Функции для потоков
    def customer1():
        print(" Клиент 1 начинает бронирование...")
        booking_system.book_ticket("Клиент 1", 3)

    def customer2():
        print(" Клиент 2 начинает бронирование...")
        booking_system.book_ticket("Клиент 2", 5)

    def customer3():
        print(" Клиент 3 начинает бронирование...")
        booking_system.book_ticket("Клиент 3", 4)

    def customer4():
        print(" Клиент 4 отменяет бронь...")
        booking_system.cancel_booking("Клиент 4", 2)

    # Запускаем потоки одновременно
    threads = []

    # Потоки для бронирования
    threads.append(threading.Thread(target=customer1))
    threads.append(threading.Thread(target=customer2))
    threads.append(threading.Thread(target=customer3))

    # Поток для отмены (запустим чуть позже)
    time.sleep(0.5)
    threads.append(threading.Thread(target=customer4))

    # Запускаем все потоки
    for thread in threads:
        thread.start()
        time.sleep(0.1)  # Небольшая задержка между запусками

    # Ждем завершения всех потоков
    for thread in threads:
        thread.join()

    print(f"\n=== ИТОГИ ===")
    print(f"Осталось билетов: {booking_system.check_availability()}")

# ТЕСТЫ

# Ожидаемый выход первого теста:
# Начало: 5 билетов
# Алиса забронировал 2 билетов
# После Алисы: 3 билетов
# Боб: нет 4 билетов (доступно 3)
# После Боба: 3 билетов
# Алиса вернул 1 билетов
# После отмены: 4 билетов

def test_single_thread():
    """Тест в одном потоке"""
    print("=== ТЕСТ 1: Один поток ===")
    system = TicketBookingSystem(5)

    print(f"Начало: {system.check_availability()} билетов")

    system.book_ticket("Алиса", 2)
    print(f"После Алисы: {system.check_availability()} билетов")

    system.book_ticket("Боб", 4)
    print(f"После Боба: {system.check_availability()} билетов")

    system.cancel_booking("Алиса", 1)
    print(f"После отмены: {system.check_availability()} билетов")

# Ожидаемый выход второго теста:
# Начало: 3 билетов
# Клиент 1 забронировал 2 билетов
# Клиент 2: нет 2 билетов (доступно 1)
# Конец: 1 билетов

def test_two_threads():
    """Тест с двумя потоками"""
    print("\n=== ТЕСТ 2: Два потока ===")
    system = TicketBookingSystem(3)

    def client1():
        system.book_ticket("Клиент 1", 2)

    def client2():
        system.book_ticket("Клиент 2", 2)

    print(f"Начало: {system.check_availability()} билетов")

    t1 = threading.Thread(target=client1)
    t2 = threading.Thread(target=client2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print(f"Конец: {system.check_availability()} билетов")

# Ожидаемый выход третьего теста:
# Начало: 2 билетов
# Клиент 1 забронировал 1 билетов
# Клиент 2 забронировал 1 билетов
# Клиент 3: нет 1 билетов (доступно 0)
# Конец: 0 билетов

def test_three_threads_race():
    """Тест гонки за билетами"""
    print("\n=== ТЕСТ 3: Гонка 3 потоков ===")
    system = TicketBookingSystem(2)  # Всего 2 билета

    def client(name, tickets):
        system.book_ticket(name, tickets)

    print(f"Начало: {system.check_availability()} билетов")

    # Три клиента хотят по 1 билету, но всего 2 билета
    threads = []
    for i in range(3):
        t = threading.Thread(target=client, args=(f"Клиент {i + 1}", 1))
        threads.append(t)

    # Запускаем всех одновременно
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print(f"Конец: {system.check_availability()} билетов")

# Ожидаемый выход четвертого теста:
# Начало: 2 билетов
# Алиса забронировал 1 билетов
# Боб: нет 2 билетов (доступно 1)
# Алиса вернул 1 билетов
# Конец: 2 билетов

def test_cancel_and_book():
    """Тест отмены и повторного бронирования"""
    print("\n=== ТЕСТ 4: Отмена + бронь ===")
    system = TicketBookingSystem(2)

    print(f"Начало: {system.check_availability()} билетов")

    def book():
        system.book_ticket("Боб", 2)

    def cancel():
        time.sleep(0.2)  # Ждем немного
        system.cancel_booking("Алиса", 1)

    # Сначала Алиса бронирует 1 билет
    system.book_ticket("Алиса", 1)

    # Параллельно: Боб пытается забронировать 2 билета (не получится)
    # и Алиса отменяет свой билет
    t1 = threading.Thread(target=book)
    t2 = threading.Thread(target=cancel)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print(f"Конец: {system.check_availability()} билетов")

test_cancel_and_book()