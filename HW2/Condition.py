import threading
import time

condition = threading.Condition()
stick_with = None  # у кого сейчас палочка


def runner(runner_id):

    global stick_with

    with condition:
        # жду когда палочка будет у меня
        while stick_with != runner_id:
            print(f"Бегун {runner_id}: жду палочку...")
            condition.wait()  # жду notify()

        # Получил палочку!
        print(f"Бегун {runner_id}: ПОЛУЧИЛ палочку!")
        time.sleep(1)  # бегу с палочкой

        # передаю палочку другому
        if runner_id == 1:
            stick_with = 2
        else:
            stick_with = 1

        print(f"Бегун {runner_id}: передаю палочку другому")
        condition.notify()  # бужу другого одного рандомного бегуна


# начинаем с бегуна 1
stick_with = 1

# запускаем двух бегунов
t1 = threading.Thread(target=runner, args=(1,))
t2 = threading.Thread(target=runner, args=(2,))

t1.start()
t2.start()

time.sleep(5)

print("Забег завершен!")