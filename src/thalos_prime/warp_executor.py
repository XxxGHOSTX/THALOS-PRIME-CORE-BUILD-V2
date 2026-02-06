"""
Nexus Orchestrator - Saga-based task orchestration with cascading failure prevention.
Uses photon batching and adaptive throttling instead of simple priority queues.
"""

import asyncio
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class PhotonPriority(Enum):
    """Priority spectrum for photon tasks."""
    HYPERDRIVE = 1
    LIGHTSPEED = 2
    IMPULSE = 3
    SUBLIGHT = 4
    DRIFT = 5


class FluxState(Enum):
    """Flux regulator states for cascade prevention."""
    NOMINAL = "nominal"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"


@dataclass
class PhotonTask:
    """A photon task in the orchestration nexus."""
    priority: int
    task_uid: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    callable_obj: Optional[Callable] = None
    positional_args: tuple = field(default_factory=tuple)
    named_args: dict = field(default_factory=dict)
    is_coroutine: bool = False
    spawn_time: float = field(default_factory=time.time)
    
    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.spawn_time < other.spawn_time
    
    def __le__(self, other):
        return self < other or self == other


class FluxRegulator:
    """
    Adaptive flux regulator using sliding window error tracking.
    Prevents cascade failures through dynamic throttling.
    """
    
    def __init__(self, window_size: int = 20, critical_threshold: float = 0.5):
        self.window_size = window_size
        self.critical_threshold = critical_threshold
        self.outcome_window: deque = deque(maxlen=window_size)
        self.flux_state = FluxState.NOMINAL
        self.total_successes = 0
        self.total_failures = 0
        self.throttle_factor = 1.0
        self.last_state_change = time.time()
        self.mutex = threading.Lock()
    
    def record_outcome(self, success: bool) -> None:
        """Record task outcome and update flux state."""
        with self.mutex:
            self.outcome_window.append(1 if success else 0)
            
            if success:
                self.total_successes += 1
            else:
                self.total_failures += 1
            
            self._recompute_flux_state()
    
    def _recompute_flux_state(self) -> None:
        """Recompute flux state based on sliding window."""
        if len(self.outcome_window) < self.window_size // 2:
            return
        
        success_rate = sum(self.outcome_window) / len(self.outcome_window)
        
        previous_state = self.flux_state
        
        if success_rate >= 0.9:
            self.flux_state = FluxState.NOMINAL
            self.throttle_factor = 1.0
        elif success_rate >= 0.7:
            self.flux_state = FluxState.DEGRADED
            self.throttle_factor = 0.7
        elif success_rate >= self.critical_threshold:
            self.flux_state = FluxState.DEGRADED
            self.throttle_factor = 0.4
        else:
            self.flux_state = FluxState.CRITICAL
            self.throttle_factor = 0.1
        
        if previous_state != self.flux_state:
            self.last_state_change = time.time()
    
    def should_throttle(self) -> bool:
        """Determine if execution should be throttled."""
        with self.mutex:
            if self.flux_state == FluxState.CRITICAL:
                time_since_change = time.time() - self.last_state_change
                if time_since_change < 30.0:
                    return True
            
            return False
    
    def get_throttle_delay(self) -> float:
        """Get current throttle delay in seconds."""
        with self.mutex:
            if self.flux_state == FluxState.NOMINAL:
                return 0.0
            elif self.flux_state == FluxState.DEGRADED:
                return 0.05
            else:
                return 0.2
    
    def query_state(self) -> Dict[str, Any]:
        """Query current flux state."""
        with self.mutex:
            return {
                'flux_state': self.flux_state.value,
                'throttle_factor': self.throttle_factor,
                'success_rate': sum(self.outcome_window) / len(self.outcome_window) if self.outcome_window else 0.0,
                'total_successes': self.total_successes,
                'total_failures': self.total_failures
            }


class PhotonBatcher:
    """Batches photon tasks for efficient processing."""
    
    def __init__(self, batch_threshold: int = 5, max_wait_time: float = 0.5):
        self.batch_threshold = batch_threshold
        self.max_wait_time = max_wait_time
        self.pending_batch: List[PhotonTask] = []
        self.batch_start_time: Optional[float] = None
        self.mutex = threading.Lock()
    
    def add_to_batch(self, task: PhotonTask) -> Optional[List[PhotonTask]]:
        """Add task to batch, return batch if ready."""
        with self.mutex:
            self.pending_batch.append(task)
            
            if self.batch_start_time is None:
                self.batch_start_time = time.time()
            
            if len(self.pending_batch) >= self.batch_threshold:
                return self._flush_batch()
            
            elapsed = time.time() - self.batch_start_time
            if elapsed >= self.max_wait_time and len(self.pending_batch) > 0:
                return self._flush_batch()
            
            return None
    
    def _flush_batch(self) -> List[PhotonTask]:
        """Flush current batch."""
        batch = self.pending_batch.copy()
        self.pending_batch.clear()
        self.batch_start_time = None
        return batch
    
    def force_flush(self) -> List[PhotonTask]:
        """Force flush remaining batch."""
        with self.mutex:
            return self._flush_batch()


class NexusOrchestrator:
    """
    Saga-based orchestrator with adaptive flux regulation.
    Uses photon batching for efficient execution.
    """
    
    def __init__(self, concurrency_limit: int = 8, enable_flux_control: bool = True):
        self.concurrency_limit = concurrency_limit
        self.enable_flux_control = enable_flux_control
        
        self.nexus_online = False
        self.photon_queue: Optional[asyncio.PriorityQueue] = None
        self.flux_regulator = FluxRegulator() if enable_flux_control else None
        self.photon_batcher = PhotonBatcher()
        
        self.saga_registry: Dict[str, Dict[str, Any]] = {}
        self.completed_sagas: List[Dict[str, Any]] = []
        self.failed_sagas: List[Dict[str, Any]] = []
        
        self.orchestrator_workers: List[asyncio.Task] = []
        self.registry_lock = threading.Lock()
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
    
    async def engage(self) -> None:
        """Engage the nexus orchestrator."""
        if self.nexus_online:
            return
        
        self.nexus_online = True
        self.photon_queue = asyncio.PriorityQueue()
        self.event_loop = asyncio.get_running_loop()
        
        for worker_idx in range(self.concurrency_limit):
            worker_task = asyncio.create_task(
                self._orchestrator_worker(worker_idx)
            )
            self.orchestrator_workers.append(worker_task)
    
    async def disengage(self, force_shutdown: bool = False) -> None:
        """Disengage the nexus orchestrator."""
        self.nexus_online = False
        
        if not force_shutdown:
            await self.photon_queue.join()
        
        for worker in self.orchestrator_workers:
            worker.cancel()
        
        if self.orchestrator_workers:
            await asyncio.gather(*self.orchestrator_workers, return_exceptions=True)
        
        self.orchestrator_workers.clear()
    
    async def dispatch(self, callable_obj: Callable, *args,
                      priority: PhotonPriority = PhotonPriority.IMPULSE,
                      **kwargs) -> str:
        """
        Dispatch photon task to nexus.
        
        Args:
            callable_obj: Function to execute
            *args: Positional arguments
            priority: Task priority
            **kwargs: Named arguments
            
        Returns:
            Task UID for tracking
        """
        if not self.nexus_online:
            raise RuntimeError("Nexus not engaged. Call engage() first.")
        
        is_coro = asyncio.iscoroutinefunction(callable_obj)
        
        task = PhotonTask(
            priority=priority.value,
            callable_obj=callable_obj,
            positional_args=args,
            named_args=kwargs,
            is_coroutine=is_coro
        )
        
        await self.photon_queue.put((task.priority, task.spawn_time, task))
        
        return task.task_uid
    
    async def _orchestrator_worker(self, worker_idx: int) -> None:
        """Worker coroutine for orchestrating photon tasks."""
        while self.nexus_online:
            try:
                priority, spawn_time, task = await asyncio.wait_for(
                    self.photon_queue.get(), 
                    timeout=0.8
                )
            except asyncio.TimeoutError:
                continue
            
            try:
                await self._execute_saga(task, worker_idx)
            finally:
                self.photon_queue.task_done()
    
    async def _execute_saga(self, task: PhotonTask, worker_idx: int) -> None:
        """Execute a photon task saga."""
        if self.enable_flux_control and self.flux_regulator.should_throttle():
            await asyncio.sleep(self.flux_regulator.get_throttle_delay())
        
        saga_start = time.time()
        saga_id = f"{task.task_uid}_{worker_idx}"
        
        with self.registry_lock:
            self.saga_registry[saga_id] = {
                'task_uid': task.task_uid,
                'worker_idx': worker_idx,
                'start_time': saga_start,
                'state': 'EXECUTING'
            }
        
        try:
            if task.is_coroutine:
                outcome = await task.callable_obj(*task.positional_args, **task.named_args)
            else:
                outcome = await asyncio.to_thread(
                    task.callable_obj, 
                    *task.positional_args, 
                    **task.named_args
                )
            
            saga_duration = time.time() - saga_start
            self._log_saga_success(task, outcome, saga_duration, worker_idx)
            
            if self.enable_flux_control:
                self.flux_regulator.record_outcome(True)
            
        except Exception as ex:
            saga_duration = time.time() - saga_start
            self._log_saga_failure(task, str(ex), saga_duration, worker_idx)
            
            if self.enable_flux_control:
                self.flux_regulator.record_outcome(False)
        
        finally:
            with self.registry_lock:
                if saga_id in self.saga_registry:
                    del self.saga_registry[saga_id]
    
    def _log_saga_success(self, task: PhotonTask, outcome: Any,
                         duration: float, worker_idx: int) -> None:
        """Log successful saga completion."""
        with self.registry_lock:
            self.completed_sagas.append({
                'task_uid': task.task_uid,
                'priority': task.priority,
                'duration': duration,
                'worker_idx': worker_idx,
                'spawn_time': task.spawn_time,
                'outcome': outcome
            })
    
    def _log_saga_failure(self, task: PhotonTask, error_msg: str,
                         duration: float, worker_idx: int) -> None:
        """Log saga failure."""
        with self.registry_lock:
            self.failed_sagas.append({
                'task_uid': task.task_uid,
                'priority': task.priority,
                'duration': duration,
                'worker_idx': worker_idx,
                'spawn_time': task.spawn_time,
                'error': error_msg
            })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retrieve orchestrator telemetry."""
        with self.registry_lock:
            metrics = {
                'nexus_online': self.nexus_online,
                'completed_sagas': len(self.completed_sagas),
                'failed_sagas': len(self.failed_sagas),
                'pending_tasks': self.photon_queue.qsize() if self.photon_queue else 0,
                'active_workers': len(self.orchestrator_workers),
                'concurrency_limit': self.concurrency_limit
            }
            
            if self.enable_flux_control:
                flux_state = self.flux_regulator.query_state()
                metrics.update(flux_state)
            
            if self.completed_sagas:
                avg_duration = sum(s['duration'] for s in self.completed_sagas) / len(self.completed_sagas)
                metrics['avg_saga_duration'] = avg_duration
            
            return metrics
    
    def purge_history(self) -> None:
        """Purge saga history."""
        with self.registry_lock:
            self.completed_sagas.clear()
            self.failed_sagas.clear()
