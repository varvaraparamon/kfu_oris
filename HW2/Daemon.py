import threading
import time

# функция для демон-потока с мониторингом
def background_monitor():
    counter = 0
    while True:
        counter += 1
        print(f"ДЕМОН: работаю в фоне и кайфую... (цикл {counter})")
        time.sleep(1)

# функция для обычного потока-трудяжки
def normal_worker(worker_id, duration):
    print(f"ОБЫЧНЫЙ {worker_id}: начал работу на {duration} сек")
    for i in range(duration):
        print(f"ОБЫЧНЫЙ {worker_id}: задача {i+1}/{duration}")
        time.sleep(1)
    print(f"ОБЫЧНЫЙ {worker_id}: ЗАВЕРШИЛ работу!")

# запускаем демон-поток (фоновый мониторинг)
daemon_thread = threading.Thread(target=background_monitor, daemon=True)
daemon_thread.start()
print("Демон-монитор запущен!")

# даем демону поработать 2 секунды
print("Даем демону поработать 2 секунды...")
time.sleep(2)

# запускаем обычные рабочие потоки
print("Запускаем обычные потоки-трудяжки...")
worker1 = threading.Thread(target=normal_worker, args=(1, 3))
worker2 = threading.Thread(target=normal_worker, args=(2, 2))

worker1.start()
worker2.start()

print("Главный поток: 'Я завершаюсь, но программа ждет обычные потоки!'")
print("Демон: 'Я буду работать, пока есть обычные потоки...'")

# главный поток завершается, но программа продолжает работать пока обычные потоки worker1 и worker2 не закончат