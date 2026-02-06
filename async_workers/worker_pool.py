"""
Asynchronous Task Processing Pool
Custom worker pool for concurrent execution
"""

import threading as thr
import queue
import time
import uuid


class WorkUnit(thr.Thread):
    """Worker thread unit"""
    
    def __init__(self, job_q, res_map, unit_id):
        super().__init__(daemon=True)
        self.job_q = job_q
        self.res_map = res_map
        self.unit_id = unit_id
        self.alive = True
        self.jobs_done = 0
        
    def run(self):
        """Worker loop"""
        while self.alive:
            try:
                job = self.job_q.get(timeout=1)
                
                if job is None:
                    break
                    
                job_id, fn, args, kwargs = job
                
                try:
                    t_start = time.time()
                    outcome = fn(*args, **kwargs)
                    t_elapsed = time.time() - t_start
                    
                    self.res_map[job_id] = {
                        'status': 'done',
                        'outcome': outcome,
                        'elapsed': t_elapsed,
                        'unit': self.unit_id
                    }
                    
                except Exception as ex:
                    self.res_map[job_id] = {
                        'status': 'error',
                        'error': str(ex),
                        'unit': self.unit_id
                    }
                    
                finally:
                    self.jobs_done += 1
                    self.job_q.task_done()
                    
            except queue.Empty:
                continue
                
    def halt(self):
        """Stop worker"""
        self.alive = False


class AsyncPool:
    """Asynchronous worker pool"""
    
    def __init__(self, worker_cnt=4):
        self.worker_cnt = worker_cnt
        self.job_q = queue.Queue()
        self.res_map = {}
        self.workers = []
        self.lock = thr.Lock()
        self.submit_hist = []
        
        self._spawn_workers()
        
    def _spawn_workers(self):
        """Create worker threads"""
        for i in range(self.worker_cnt):
            unit_id = f"unit_{i+1}"
            worker = WorkUnit(self.job_q, self.res_map, unit_id)
            worker.start()
            self.workers.append(worker)
            
    def dispatch(self, fn, *args, **kwargs):
        """Dispatch job"""
        
        job_id = str(uuid.uuid4())
        
        with self.lock:
            self.submit_hist.append({
                'job_id': job_id,
                'fn_name': fn.__name__
            })
            
        self.job_q.put((job_id, fn, args, kwargs))
        
        return job_id
    
    def fetch_result(self, job_id, wait_time=None):
        """Fetch job result"""
        
        t_start = time.time()
        
        while True:
            with self.lock:
                if job_id in self.res_map:
                    return self.res_map[job_id]
                    
            if wait_time and (time.time() - t_start) > wait_time:
                return None
                
            time.sleep(0.1)
    
    def dispatch_many(self, job_list):
        """
        Dispatch multiple jobs
        job_list: List of (fn, args, kwargs) tuples
        """
        
        job_ids = []
        
        for job in job_list:
            if len(job) == 3:
                fn, args, kwargs = job
            elif len(job) == 2:
                fn, args = job
                kwargs = {}
            else:
                fn = job[0]
                args = ()
                kwargs = {}
                
            job_id = self.dispatch(fn, *args, **kwargs)
            job_ids.append(job_id)
            
        return job_ids
    
    def await_many(self, job_ids, wait_time=None):
        """Wait for multiple jobs"""
        
        outcomes = {}
        
        for job_id in job_ids:
            outcome = self.fetch_result(job_id, wait_time)
            outcomes[job_id] = outcome
            
        return outcomes
    
    def pending_cnt(self):
        """Get pending job count"""
        return self.job_q.qsize()
    
    def pool_stats(self):
        """Get pool statistics"""
        
        jobs_done = sum(w.jobs_done for w in self.workers)
        alive_workers = sum(1 for w in self.workers if w.is_alive())
        
        return {
            'workers': self.worker_cnt,
            'alive': alive_workers,
            'pending': self.pending_cnt(),
            'submitted': len(self.submit_hist),
            'processed': jobs_done,
            'completed': len(self.res_map)
        }
    
    def terminate(self):
        """Terminate pool"""
        
        # Send stop signals
        for _ in self.workers:
            self.job_q.put(None)
            
        # Wait for workers
        for worker in self.workers:
            worker.join(timeout=5)
            
        self.workers.clear()
