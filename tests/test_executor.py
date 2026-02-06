"""Test suite for Nexus Orchestrator"""
import pytest
import asyncio

from thalos_prime.warp_executor import NexusOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_engage():
    """Test orchestrator engagement"""
    orchestrator = NexusOrchestrator(max_strands=2)
    await orchestrator.engage()
    
    assert orchestrator.warp_active is True
    assert orchestrator.photon_pool is not None
    
    await orchestrator.disengage()


@pytest.mark.asyncio
async def test_dispatch_coroutine():
    """Test dispatching coroutines"""
    orchestrator = NexusOrchestrator(max_strands=2)
    await orchestrator.engage()
    
    async def quantum_compute(n):
        await asyncio.sleep(0.01)
        return n * 2
    
    result = await orchestrator.dispatch(quantum_compute, 7)
    assert result == 14
    
    await orchestrator.disengage()


@pytest.mark.asyncio
async def test_dispatch_synchronous_function():
    """Test dispatching blocking functions"""
    orchestrator = NexusOrchestrator(max_strands=2)
    await orchestrator.engage()
    
    def classical_compute(x, y):
        return x + y
    
    result = await orchestrator.dispatch(classical_compute, 3, 5)
    assert result == 8
    
    await orchestrator.disengage()


@pytest.mark.asyncio
async def test_concurrent_photon_streams():
    """Test multiple concurrent dispatches"""
    orchestrator = NexusOrchestrator(max_strands=3)
    await orchestrator.engage()
    
    async def quantum_square(n):
        await asyncio.sleep(0.01)
        return n ** 2
    
    streams = [orchestrator.dispatch(quantum_square, i) for i in range(5)]
    results = await asyncio.gather(*streams)
    
    assert results == [0, 1, 4, 9, 16]
    
    await orchestrator.disengage()


@pytest.mark.asyncio
async def test_graceful_disengage():
    """Test graceful shutdown"""
    orchestrator = NexusOrchestrator(max_strands=2)
    await orchestrator.engage()
    
    async def slow_quantum_op():
        await asyncio.sleep(0.05)
        return "complete"
    
    task = asyncio.create_task(orchestrator.dispatch(slow_quantum_op))
    
    await asyncio.sleep(0.01)
    await orchestrator.disengage(drain_photons=True, deadline=1.0)
    
    result = await task
    assert result == "complete"


@pytest.mark.asyncio
async def test_dispatch_before_engage():
    """Test dispatch fails when not engaged"""
    orchestrator = NexusOrchestrator(max_strands=2)
    
    async def test_op():
        return "done"
    
    with pytest.raises(RuntimeError):
        await orchestrator.dispatch(test_op)


@pytest.mark.asyncio
async def test_exception_propagation():
    """Test exceptions are propagated correctly"""
    orchestrator = NexusOrchestrator(max_strands=2)
    await orchestrator.engage()
    
    async def failing_photon():
        await asyncio.sleep(0.01)
        raise ValueError("photon collision")
    
    with pytest.raises(ValueError, match="photon collision"):
        await orchestrator.dispatch(failing_photon)
    
    await orchestrator.disengage()
