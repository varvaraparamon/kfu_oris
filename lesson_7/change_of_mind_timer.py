import threading
import time

# мы хотим только через 10 секунд отправить важное сообщение
def send_important_message():
    print("Отправляю важное сообщение")

timer = threading.Timer(10.0, send_important_message)
timer.start()

# через 5 секунд решили передумать...
time.sleep(5)
print("Передумал отправлять!")
timer.cancel()  # сообщение не отправится :)