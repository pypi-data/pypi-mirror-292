import torch
import torch.nn as nn
from typing import List, Dict, Optional, Tuple


class LogManager:
    _logs: Dict[str, List[Tuple[torch.Tensor, Optional[str]]]] = {}

    @staticmethod
    def log_tensor(namespace: str, tensor: torch.Tensor, name: Optional[str] = None) -> None:
        """
        Log the tensor under a specific namespace with an optional name.

        Args:
            namespace (str): The namespace under which the tensor should be logged.
            tensor (torch.Tensor): The tensor to log.
            name (Optional[str]): An optional name for the tensor to identify where it was logged.
        """
        if namespace not in LogManager._logs:
            LogManager._logs[namespace] = []
        LogManager._logs[namespace].append((tensor, name))

    @staticmethod
    def clear_logs(namespace: Optional[str] = None) -> None:
        """
        Clear the logs for a specific namespace, or all logs if no namespace is specified.

        Args:
            namespace (Optional[str]): The namespace whose logs should be cleared. If None, all logs will be cleared.
        """
        if namespace is None:
            LogManager._logs.clear()
        else:
            LogManager._logs.pop(namespace, None)

    @property
    def logs(self) -> Dict[str, List[Tuple[torch.Tensor, Optional[str]]]]:
        """
        A property to access all logged tensors across all namespaces.

        Returns:
            Dict[str, List[Tuple[torch.Tensor, Optional[str]]]]: A dictionary where the keys are namespaces and 
            the values are lists of tuples, each containing a tensor and its optional name.
        """
        return self._logs

class Logger(nn.Module):
    def __init__(self, name_space: str):
        super(Logger, self).__init__()
        self.name_space = name_space

    def forward(self, input_tensor: torch.Tensor, name: Optional[str] = None) -> torch.Tensor:
        """
        Log the input tensor with an optional name and return it unchanged.

        Args:
            input_tensor (torch.Tensor): The tensor to be logged.
            name (Optional[str]): An optional name for the tensor, used for identification in logging.

        Returns:
            torch.Tensor: The input tensor unchanged.
        """
        detached_tensor = input_tensor.detach().clone()
        LogManager.log_tensor(self.name_space, detached_tensor, name)
        return input_tensor