# Многопоточность

## Потоки

**Потоки** - это наименьшая единица выполнения внутри одного процесса. Они позволяют выполнять несколько задач "одновременно" в рамках работы одного приложения

Каждый поток имеет свой собственный стек вызовов для локальных переменных, но делит память, глобальные переменные и ресурсы с другими потоками в процессе

Потоки полезны для задач, где много ожидания (например, сетевые запросы, чтение файлов и тд), но на самом деле не всегда эффективны...

```python
import threading
import time

def worker(name): # функция, которую будут выполнять оба потока "параллельно"
    print(f"Поток {name} начал работу")
    time.sleep(2)
    print(f"Поток {name} завершил работу")

t1 = threading.Thread(target=worker, args=("Diana",))
t2 = threading.Thread(target=worker, args=("Veronika",))

t1.start() # запускаем наши потоки
t2.start()

t1.join() # просим main дождаться выполнения потока (иначе он завершится раньше и поток может не успеть полностью выполнить код в функции)
t2.join()
```
## Конкурентность и параллелизм

Почему же выше везде слова "параллельно" и "одновременно" стояли в кавычках? Потому что в питоне нет как таковой параллельности работы потоков...

Ответ очень прост - GIL в Python

**GIL (Global Interpreter Lock)** - это глобальная блокировка интерпретатора, которая гарантирует, что в любой момент времени выполняется только один поток байткода Python

**Интересный факт:** в начальных версиях Python, GIL не существовал. Однако, когда Python начал использоваться для многопоточных приложений, стало очевидным, что возникают проблемы с одновременным доступом к общим ресурсам. Он был введен не как намеренное ограничение, а крайняя необходимость :)

**Конкурентность** - возможность выполнять несколько задач почти одновременно
Здесь система быстро переключается между потоками, именно поэтому создается иллюзия одновременного выполнения
В основном потоки лучше юзать для I/O задач (ожидание сети, пользовательский ввод и тд)

**Параллелизм** - РЕАЛЬНО одновременное выполнение задач
По факту достигается параллельность здесь за счет того, что каждая задача выполняется на отдельных CPU ядрах(библиотека multiprocessing, где мы создаем не thread а process)
Здесь каждая задача выполняется на отдельном процессоре, что действительно ускоряет вычисления
Вот тут уже можно разгуляться с задачами (огромные математические вычисления, обработка больших данных и другие CPU-bound задачи)

## Основные проблемы многопоточности

1. Race Condition (Состояние гонки) - состояние, которое возникает, когда несколько потоков одновременно обращаются к общим данным и хотя бы один из них изменяет их
   (Пример race condition есть в файлах с кодом)

На помощь тут приходят блокировки, которые мы с вами уже знаем :)

## Lock

**Lock** - самая простая блокировка с двумя состояниями: заблокирован/свободен

Методы:
* acquire() — захватить блокировку (если занята - ждать)
* release() — освободить блокировку

```python
import threading

bank_balance = 100
lock = threading.Lock()

def safe_withdraw(amount):
    global bank_balance
    lock.acquire()  # захватываем блокировку
    try:
        # блок в try выполняет только один поток за раз
        current_balance = bank_balance
        new_balance = current_balance - amount
        bank_balance = new_balance
        print(f"Снято {amount}, остаток: {new_balance}")
    finally:
        lock.release()  # всегда освобождаем в finally блокировку, что бы ни произошло
```

Ну или мы уже видели другой способ реализации с контекстным менеджером:

```python
import threading

bank_balance = 100
lock = threading.Lock()

def safe_withdraw_better(amount):
    global bank_balance
    with lock:  # тут уже автоматически acquire/release
        current_balance = bank_balance
        new_balance = current_balance - amount
        bank_balance = new_balance
        print(f"Снято {amount}, остаток: {new_balance}")
# после блока автоматически освобождается блокировка
```

2. Deadlock (Взаимная блокировка) - ситуация, когда два или более потока заблокированы навсегда, потому что ожидают ресурсы друг друга
   (Пример deadlock есть в файлах с кодом)

Решить эту проблему можно несколькими способами:
* Всегда захватывать блокировки в одном порядке, а не чередовать в зависимости от сторон 
* Использовать RLock для вложенных вызовов

## RLock

**RLock** - advanced версия Lock (потому что с помощью нее поток может захватить блокировку несколько раз)

Посмотрим на обычный код с обычным Lock:
```python
import threading
import os

lock = threading.Lock()
processed_files = 0

# функция, которая обрабатывает один файл
def process_file(filepath):
    
    global processed_files
    
    print(f"Обрабатываем файл: {filepath}")
    processed_files += 1
    print(f"Обработано файлов: {processed_files}")

# функция, которая обрабатывает директорию с файлами + обрабатываем другие директории в этой директории
def process_directory(directory_path, depth=0):
    with lock:
        print(f"{'  ' * depth}Обрабатываем директорию: {directory_path}")
        
        # что-то тут делаем, хулиганим
        files = [f"file{i}.txt" for i in range(3)]
        subdirs = [f"subdir{i}" for i in range(2)] if depth < 2 else []
        
        # обрабатываем файлы в текущей директории
        for file in files:
            filepath = os.path.join(directory_path, file)
            process_file(filepath)  # вызываем верхнюю функцию для обработки конкретного файла
        
        # рекурсивно обрабатываем поддиректории в нашей директории
        for subdir in subdirs:
            subdir_path = os.path.join(directory_path, subdir)
            process_directory(subdir_path, depth + 1)
```

А вот и нюансы...

1. А если вы работаете в компании и кто-то вашу функцию process_file решит использовать отдельно?
Эта функция меняет глобальную переменную, которая, возможно, используется где-то еще

Вариант вызова 1:
```python
process_directory("/users/user/documents")
```
Тут вообще проблем нет, функция process_file запускается при блокировке

Вариант вызова 2:
```python
process_file("/users/user/documents/important.txt")
```
Опачки, вот и нюанс, тогда при редактировании общей переменной у нас блок не заблокирован и далее программа может работать некорретно

2. Обратите внимание, что мы рекурсивно вызываем нашу функцию process_directory, в которой находимся
Как только мы вызовем рекурсивно функцию, welcome to deadlock, блокировка заблокирована еще на прошлом вызове функции

Решение обеих проблем - использование RLock

```python
import threading
import os

rlock = threading.RLock()
processed_files = 0

# функция, которая обрабатывает один файл
def process_file(filepath):
    global processed_files
    
    with rlock:
        print(f"Обрабатываем файл: {filepath}")
        processed_files += 1
        print(f"Обработано файлов: {processed_files}")

# функция, которая обрабатывает директорию с файлами + обрабатываем другие директории в этой директории
def process_directory(directory_path, depth=0):
    with rlock:
        print(f"{'  ' * depth}Обрабатываем директорию: {directory_path}")
        
        # что-то тут делаем, хулиганим
        files = [f"file{i}.txt" for i in range(3)]
        subdirs = [f"subdir{i}" for i in range(2)] if depth < 2 else []
        
        # обрабатываем файлы в текущей директории
        for file in files:
            filepath = os.path.join(directory_path, file)
            process_file(filepath)  # вызываем верхнюю функцию для обработки конкретного файла
        
        # рекурсивно обрабатываем поддиректории в нашей директории
        for subdir in subdirs:
            subdir_path = os.path.join(directory_path, subdir)
            process_directory(subdir_path, depth + 1)
            
def main():
    # теперь мы можем вызывать разными способами:
    
    # обработать всю структуру
    process_directory("/users/user/documents")
    
    # обработать только один файл
    process_file("/users/user/documents/important.txt")

if __name__ == "__main__":
    main()
```

Такие вот дела :)

## Задание №1 - Система бронирования билетов

1. Создайте класс TicketBookingSystem с конструктором:
   * total_tickets - общее количество билетов
   * available_tickets - текущее количество доступных билетов
   * booking_lock - блокировка
2. Реализуйте методы:
   * check_availability() - проверить количество доступных билетов
   * book_ticket(customer_name, tickets_count) - забронировать указанное количество билетов
   * cancel_booking(customer_name, tickets_count) - вернуть билеты

## Задание №2 - Банковская система

1. Создайте класс BankAccount:
   * balance - текущий баланс счета 
   * lock - блокировка
   * is_frozen - заблокирован ли счет
2. Реализуйте методы:
   * deposit(amount) - внести деньги на счет 
   * security_check() - проверить безопасность операции (заблокирован ли счет, проверка баланса)
   * get_balance() - получить текущий баланс
   * transfer(to_account, amount) - перевести деньги на другой счет(внутри вызывает security_check() и to_account.deposit())



