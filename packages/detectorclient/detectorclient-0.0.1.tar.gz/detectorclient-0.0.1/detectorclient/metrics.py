import os
import time
import threading
import psutil
from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TransactionMetrics:
    true_positives: int = 0
    true_negatives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    total_transactions: int = 0
    transacted_amount: float = 0
    blocked_amount: float = 0
    lost_to_fraud: float = 0


@dataclass
class PerformanceMetrics:
    processing_time: float = 0
    avg_cpu_usage: float = 0.0
    avg_mem_usage: float = 0.0


@dataclass
class StepResult:
    transaction_metrics: TransactionMetrics = field(default_factory=TransactionMetrics)
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.transaction_metrics.__dict__,
            **self.performance_metrics.__dict__,
            'timestamp': self.timestamp.isoformat(),
        }


class PerformanceMonitor:
    def __init__(self):
        self._start_time: float = 0
        self._stop_event: threading.Event = threading.Event()
        self._monitor_thread: threading.Thread | None = None
        self._cpu_usages: list = []
        self._mem_usages: list = []

    def __enter__(self):
        self._start_time = time.perf_counter()
        psutil.cpu_percent()  # Start monitoring CPU usage
        self._monitor_thread = threading.Thread(target=self._monitor_resources)
        self._monitor_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join()

    def _monitor_resources(self):
        process = psutil.Process(os.getpid())
        while not self._stop_event.is_set():
            self._cpu_usages.append(process.cpu_percent())
            self._mem_usages.append(process.memory_percent())

    def get_metrics(self) -> PerformanceMetrics:
        processing_time = time.perf_counter() - self._start_time
        avg_cpu_usage = sum(self._cpu_usages) / len(self._cpu_usages) if self._cpu_usages else 0
        avg_mem_usage = sum(self._mem_usages) / len(self._mem_usages) if self._mem_usages else 0
        return PerformanceMetrics(processing_time, avg_cpu_usage, avg_mem_usage)
