# bugster/login/base_login_strategy.py

from abc import ABC, abstractmethod


class BaseLoginStrategy(ABC):
    @abstractmethod
    def login(self, page, credentials):
        pass
