import threading
import multiprocessing
import hashlib


class CreateMessage:
    def __init__(self, size):
        self.size = size
