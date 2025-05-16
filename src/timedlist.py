import time
import threading

class TimedList:
    def __init__(self):
        self._data = {}  # {element: expiration_timestamp}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._cleaner_thread = threading.Thread(target=self._clean_expired_elements, daemon=True)
        self._cleaner_thread.start()

    def add(self, item, delay=1):
        with self._lock:
            self._data[item] = time.time() + delay

    def __contains__(self, item):
        with self._lock:
            return item in self._data and self._data[item] > time.time()

    def __len__(self):
        with self._lock:
            return sum(1 for timestamp in self._data.values() if timestamp > time.time())

    def __iter__(self):
        with self._lock:
            current_time = time.time()
            active_items = [item for item, timestamp in self._data.items() if timestamp > current_time]
            return iter(active_items)

    def get_all_active(self):
        with self._lock:
            current_time = time.time()
            return [item for item, timestamp in self._data.items() if timestamp > current_time]
        
    def clear(self):
        with self._lock:
            self._data.clear()

    def _clean_expired_elements(self):
        while not self._stop_event.is_set():
            time.sleep(0.1)  # Check for expired elements every 100 milliseconds
            with self._lock:
                expired_items = [item for item, timestamp in self._data.items() if timestamp <= time.time()]
                for item in expired_items:
                    del self._data[item]

    # only if list of tuples
    def get_separate_lists(self):
        with self._lock:
            current_time = time.time()
            active_data = [(x, y) for (x, y), timestamp in self._data.items() if timestamp > current_time]
            x_values = [coord[0] for coord in active_data]
            y_values = [coord[1] for coord in active_data]
            return x_values, y_values

    def stop(self):
        self._stop_event.set()
        self._cleaner_thread.join()