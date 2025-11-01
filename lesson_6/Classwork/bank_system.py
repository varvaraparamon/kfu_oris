import threading

class BankAccount:
    def __init__(self, balance, owner=None):
        self.balance = balance
        self.owner = owner
        self.lock = threading.RLock()
        self.is_frozen = False

    def security_check(self, amount=0):
        with self.lock:
            return (not self.is_frozen) and (self.balance >= amount)

    def deposit(self, amount):
        with self.lock:
            if self.security_check():
                self.balance += amount

    def transfer(self, to_account, amount):
        with self.lock:
            if self.security_check(amount) and to_account.security_check():
                self.balance -= amount
                to_account.deposit(amount)

    def get_balance(self):
        with self.lock:
            return self.balance
        
    def freeze_account(self):
        with self.lock:
            self.is_frozen = True

# ТЕСТ

def test_bank_system():
    # Создаем счета
    account1 = BankAccount(1000)
    account2 = BankAccount(500)

    def client1():
        account1.transfer(account2, 200)

    def client2():
        account2.transfer(account1, 100)

    # Запускаем переводы одновременно
    t1 = threading.Thread(target=client1)
    t2 = threading.Thread(target=client2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print(f"Итог: account1={account1.get_balance()}, account2={account2.get_balance()}")

test_bank_system()