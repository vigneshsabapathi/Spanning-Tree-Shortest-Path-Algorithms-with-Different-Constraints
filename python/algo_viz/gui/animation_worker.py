from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition

from algo_viz.models.step import AlgorithmStep


class AnimationWorker(QThread):
    step_ready = pyqtSignal(object)  # emits AlgorithmStep
    finished_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._iterator = None
        self._speed = 1.0        # multiplier
        self._paused = True
        self._stop = False
        self._mutex = QMutex()
        self._condition = QWaitCondition()

    def set_iterator(self, iterator):
        self._iterator = iterator
        self._paused = True
        self._stop = False

    def set_speed(self, speed: float):
        self._speed = max(0.1, min(10.0, speed))

    def pause(self):
        self._mutex.lock()
        self._paused = True
        self._mutex.unlock()

    def resume(self):
        self._mutex.lock()
        self._paused = False
        self._condition.wakeAll()
        self._mutex.unlock()

    def stop(self):
        self._mutex.lock()
        self._stop = True
        self._paused = False
        self._condition.wakeAll()
        self._mutex.unlock()

    def run(self):
        if not self._iterator:
            return
        for step in self._iterator:
            self._mutex.lock()
            while self._paused and not self._stop:
                self._condition.wait(self._mutex)
            if self._stop:
                self._mutex.unlock()
                break
            self._mutex.unlock()

            self.step_ready.emit(step)
            delay_ms = int(500 / self._speed)
            self.msleep(max(50, delay_ms))

        self.finished_signal.emit()
