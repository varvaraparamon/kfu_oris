import threading

class NumberFileProcessor:
    def __init__(self, num_workers=2):
        self.num_workers = num_workers
        self.total_sum = 0  # общая сумма всех чисел
        self.files_processed = 0  # количество обработанных файлов
        self.lock = threading.Lock()  # блокировка для синхронизации
        self.processing_barrier = threading.Barrier(num_workers, action=self._all_files_processed) # action можно убрать, но так симпатичнее

    def _all_files_processed(self):
        print(f"Обработка завершена, всего {self.total_sum} сумма чисел")

    def process_number_file(self, filename, worker_id):
        file_sum = 0
        with open(filename, 'r') as f:
            for line in f:
                file_sum += int(line.strip())
        with self.lock:
            self.total_sum += file_sum
            self.files_processed += 1

    def worker(self, file_list, worker_id):
        for filename in file_list:
            self.process_number_file(filename, worker_id)

        self.processing_barrier.wait()

    def process_files(self, file_list):
        workers = [[] for i in range(self.num_workers)]
        
        for i, filename in enumerate(file_list):
            workers[i % self.num_workers].append(filename)

        threads = []
        for worker_id in range(self.num_workers):
            t = threading.Thread(target=self.worker, args=(workers[worker_id], worker_id))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()


def main():
    files = ['number_files/numbers_1.txt', 'number_files/numbers_2.txt', 'number_files/numbers_3.txt', \
             'number_files/numbers_4.txt', 'number_files/numbers_5.txt', 'number_files/numbers_6.txt']
    processor = NumberFileProcessor(num_workers=2)
    processor.process_files(files)

if __name__ == "__main__":
    main()