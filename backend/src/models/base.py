from typing import Dict, Type

from abc import ABC, abstractmethod


class CommunicationStrategy(ABC):

    @abstractmethod
    async def execute(self, data: Dict):
        raise NotImplementedError
