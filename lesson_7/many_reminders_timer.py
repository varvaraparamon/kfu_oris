import threading

def reminder(what):
    print(f"Напоминание: {what}")

# ставим кучу напоминаний
reminders = [
    ("Позвонить маме", 2),
    ("Купить молоко", 5),
    ("Забрать посылку", 8),
    ("Оплатить Яндекс подписку", 12)
]

for what, seconds in reminders:
    threading.Timer(seconds, reminder, args=(what,)).start()

print("Все напоминания установлены, живем спокойно...")