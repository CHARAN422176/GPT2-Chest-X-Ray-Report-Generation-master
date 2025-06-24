# ordered_enqueuer_patch.py
import threading
import numpy as np
import time
import queue

class OrderedEnqueuer:
    def __init__(self, sequence, use_multiprocessing=False):
        self.sequence = sequence
        self.use_multiprocessing = use_multiprocessing
        self._stop_event = threading.Event()
        self._queue = queue.Queue()
        self._workers = []
        self._batch_index = 0

    def start(self, workers=1, max_queue_size=10):
        def data_generator():
            while not self._stop_event.is_set():
                if self._batch_index >= len(self.sequence):
                    self._batch_index = 0
                self._queue.put(self.sequence[self._batch_index])
                self._batch_index += 1

        for _ in range(workers):
            worker = threading.Thread(target=data_generator)
            worker.daemon = True
            worker.start()
            self._workers.append(worker)

    def get(self):
        while not self._stop_event.is_set():
            try:
                yield self._queue.get(timeout=5)
            except queue.Empty:
                continue

    def stop(self):
        self._stop_event.set()
        for worker in self._workers:
            worker.join()
