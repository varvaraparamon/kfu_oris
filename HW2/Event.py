import threading
import time

# cоздаем Event - изначально выключен (False)
event = threading.Event()


def worker(worker_id):
    print(f"Поток {worker_id} запустился и ждет сигнала...")

    # ждем сигнала от главного потока
    event.wait()

    print(f"Поток {worker_id} получил сигнал и начал работу!")
    time.sleep(2)
    print(f"Поток {worker_id} завершил работу")


def monitor():
    while True:
        status = "ВКЛЮЧЕН" if event.is_set() else "ВЫКЛЮЧЕН"
        print(f"Монитор: Event сейчас {status}")
        time.sleep(1)

monitor_thread = threading.Thread(target=monitor)
monitor_thread.start()

print("Запускаем потоки...")
workers = []
for i in range(3):
    t = threading.Thread(target=worker, args=(i,))
    t.start()
    workers.append(t)

# даем поработать 3 секунды (рабочие ждут)
time.sleep(3)

# ВКЛЮЧАЕМ Event - будим всех рабочих
print("Главный поток: ВКЛЮЧАЮ Event!")
event.set()

time.sleep(1)
print(f"Проверяем состояние: Event сейчас = {event.is_set()}")

# ВЫКЛЮЧАЕМ Event
print("Главный поток: ВЫКЛЮЧАЮ Event!")
event.clear()
print(f"Проверяем состояние: Event сейчас = {event.is_set()}")