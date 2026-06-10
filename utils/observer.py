from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def notify(self):
        pass


class Subject(ABC):
    def __init__(self):
        self.observers = []

    def add_observer(self, observer: Observer):
        self.observers.append(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.notify()
