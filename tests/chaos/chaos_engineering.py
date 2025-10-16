# Chaos Engineering Suite

"""
Chaos engineering suite for testing system resilience
"""

import asyncio
import aiohttp
import time
import random
import psutil
import os
import signal
import subprocess
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ChaosType(Enum):
    """Types of chaos experiments"""
    NETWORK_LATENCY = "network_latency"
    NETWORK_PACKET_LOSS = "network_packet_loss"
    NETWORK_DISCONNECT = "network_disconnect"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_FULL = "disk_full"
    PROCESS_KILL = "process_kill"
    SERVICE_RESTART = "service_restart"
    DATABASE_CONNECTION_LOSS = "database_connection_loss"
    RATE_LIMIT_OVERLOAD = "rate_limit_overload"

@dataclass
class ChaosExperiment:
    """Chaos experiment configuration"""
    name: str
    chaos_type: ChaosType
    duration: int  # seconds
    intensity: float  # 0.0 to 1.0
    target: str  # target service/component
    description: str
    expected_behavior: str
    recovery_time: int  # expected recovery time in seconds

@dataclass
class ChaosResult:
    """Result of a chaos experiment"""
    experiment_name: str
    chaos_type: ChaosType
    start_time: float
    end_time: float
    duration: float
    success: bool
    system_recovered: bool
    recovery_time: float
    error_message: Optional[str] = None
    metrics_before: Dict[str, Any] = None
    metrics_during: Dict[str, Any] = None
    metrics_after: Dict[str, Any] = None
    details: Dict[str, Any] = None

class ChaosEngineer:
    """Main chaos engineering class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.token = None
        self.experiments: List[ChaosExperiment] = []
        self.results: List[ChaosResult] = []
        self.monitoring_active = False
        self.metrics_history: List[Dict[str, Any]] = []
        
    async def setup(self):
        """Setup HTTP session and authentication"""
        connector = aiohttp.TCPConnector(limit=100)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
        # Authenticate
        await self.authenticate()
        
        # Load predefined experiments
        self._load_experiments()
    
    async def teardown(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> bool:
        """Authenticate and get token"""
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": "testuser", "password": "testpassword"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.token = data["data"]["access_token"]
                        return True
            return False
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def _load_experiments(self):
        """Load predefined chaos experiments"""
        self.experiments = [
            ChaosExperiment(
                name="Network Latency Injection",
                chaos_type=ChaosType.NETWORK_LATENCY,
                duration=60,
                intensity=0.5,
                target="api_endpoints",
                description="Inject network latency to test timeout handling",
                expected_behavior="System should handle timeouts gracefully",
                recovery_time=10
            ),
            ChaosExperiment(
                name="CPU Stress Test",
                chaos_type=ChaosType.CPU_STRESS,
                duration=120,
                intensity=0.8,
                target="system",
                description="Generate CPU load to test performance under stress",
                expected_behavior="System should maintain functionality with degraded performance",
                recovery_time=30
            ),
            ChaosExperiment(
                name="Memory Stress Test",
                chaos_type=ChaosType.MEMORY_STRESS,
                duration=90,
                intensity=0.7,
                target="system",
                description="Generate memory pressure to test memory management",
                expected_behavior="System should handle memory pressure gracefully",
                recovery_time=20
            ),
            ChaosExperiment(
                name="Rate Limit Overload",
                chaos_type=ChaosType.RATE_LIMIT_OVERLOAD,
                duration=180,
                intensity=1.0,
                target="api_endpoints",
                description="Generate excessive requests to test rate limiting",
                expected_behavior="Rate limiting should activate and protect the system",
                recovery_time=5
            ),
            ChaosExperiment(
                name="Database Connection Loss",
                chaos_type=ChaosType.DATABASE_CONNECTION_LOSS,
                duration=30,
                intensity=1.0,
                target="database",
                description="Simulate database connection loss",
                expected_behavior="System should handle database errors gracefully",
                recovery_time=15
            )
        ]
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get API metrics if available
            api_metrics = {}
            if self.token:
                try:
                    async with self.session.get(
                        f"{self.base_url}/performance",
                        headers={"Authorization": f"Bearer {self.token}"}
                    ) as response:
                        if response.status == 200:
                            api_metrics = await response.json()
                except Exception:
                    pass
            
            return {
                "timestamp": time.time(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
                "api_metrics": api_metrics
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {"timestamp": time.time(), "error": str(e)}
    
    async def monitor_system(self, duration: int):
        """Monitor system during chaos experiment"""
        self.monitoring_active = True
        start_time = time.time()
        
        while self.monitoring_active and (time.time() - start_time) < duration:
            metrics = await self.get_system_metrics()
            self.metrics_history.append(metrics)
            await asyncio.sleep(5)  # Monitor every 5 seconds
    
    async def test_system_health(self) -> bool:
        """Test if system is healthy"""
        try:
            # Test health endpoint
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status != 200:
                    return False
                
                data = await response.json()
                return data.get("status") == "healthy"
        except Exception:
            return False
    
    async def test_api_functionality(self) -> Dict[str, bool]:
        """Test API functionality"""
        results = {}
        
        if not self.token:
            return {"authenticated": False}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test various endpoints
        endpoints = [
            ("/api/v1/users/", "GET"),
            ("/api/v1/products/", "GET"),
            ("/api/v1/whatsapp/conversations/", "GET")
        ]
        
        for endpoint, method in endpoints:
            try:
                async with self.session.request(
                    method, f"{self.base_url}{endpoint}", headers=headers
                ) as response:
                    results[endpoint] = response.status < 500
            except Exception:
                results[endpoint] = False
        
        return results
    
    async def inject_network_latency(self, intensity: float, duration: int):
        """Inject network latency"""
        # This would typically use tools like tc (traffic control) on Linux
        # For this example, we'll simulate by adding delays in requests
        print(f"🌐 Injecting network latency (intensity: {intensity})")
        
        # Simulate network latency by adding delays
        delay = intensity * 2.0  # Up to 2 seconds delay
        
        async def delayed_request(*args, **kwargs):
            await asyncio.sleep(delay)
            return await self.session.request(*args, **kwargs)
        
        # Replace session request method temporarily
        original_request = self.session.request
        self.session.request = delayed_request
        
        try:
            await asyncio.sleep(duration)
        finally:
            # Restore original request method
            self.session.request = original_request
    
    async def inject_cpu_stress(self, intensity: float, duration: int):
        """Inject CPU stress"""
        print(f"🔥 Injecting CPU stress (intensity: {intensity})")
        
        # Calculate number of CPU-intensive processes
        cpu_count = psutil.cpu_count()
        process_count = int(cpu_count * intensity)
        
        processes = []
        
        try:
            # Start CPU-intensive processes
            for i in range(process_count):
                process = subprocess.Popen([
                    "python", "-c", 
                    "import time; [time.sleep(0) for _ in range(1000000)]"
                ])
                processes.append(process)
            
            # Let it run for the specified duration
            await asyncio.sleep(duration)
            
        finally:
            # Clean up processes
            for process in processes:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except Exception:
                    try:
                        process.kill()
                    except Exception:
                        pass
    
    async def inject_memory_stress(self, intensity: float, duration: int):
        """Inject memory stress"""
        print(f"💾 Injecting memory stress (intensity: {intensity})")
        
        # Calculate memory to allocate
        total_memory = psutil.virtual_memory().total
        memory_to_allocate = int(total_memory * intensity * 0.5)  # Use 50% of intensity
        
        memory_blocks = []
        
        try:
            # Allocate memory blocks
            block_size = min(memory_to_allocate // 10, 100 * 1024 * 1024)  # Max 100MB per block
            
            while len(memory_blocks) * block_size < memory_to_allocate:
                try:
                    block = bytearray(block_size)
                    memory_blocks.append(block)
                except MemoryError:
                    break
            
            # Hold memory for the specified duration
            await asyncio.sleep(duration)
            
        finally:
            # Release memory
            memory_blocks.clear()
    
    async def inject_rate_limit_overload(self, intensity: float, duration: int):
        """Inject rate limit overload"""
        print(f"⚡ Injecting rate limit overload (intensity: {intensity})")
        
        # Calculate number of concurrent requests
        request_rate = int(100 * intensity)  # Up to 100 requests per second
        
        async def spam_requests():
            while True:
                try:
                    async with self.session.get(f"{self.base_url}/health") as response:
                        pass
                except Exception:
                    pass
                await asyncio.sleep(1.0 / request_rate)
        
        # Start multiple spam tasks
        tasks = []
        for _ in range(10):  # 10 concurrent spam tasks
            task = asyncio.create_task(spam_requests())
            tasks.append(task)
        
        try:
            await asyncio.sleep(duration)
        finally:
            # Cancel all spam tasks
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def run_experiment(self, experiment: ChaosExperiment) -> ChaosResult:
        """Run a single chaos experiment"""
        print(f"🧪 Running Chaos Experiment: {experiment.name}")
        print(f"   Type: {experiment.chaos_type.value}")
        print(f"   Duration: {experiment.duration}s")
        print(f"   Intensity: {experiment.intensity}")
        print(f"   Target: {experiment.target}")
        
        start_time = time.time()
        
        # Get metrics before experiment
        metrics_before = await self.get_system_metrics()
        health_before = await self.test_system_health()
        api_before = await self.test_api_functionality()
        
        # Start monitoring
        monitor_task = asyncio.create_task(
            self.monitor_system(experiment.duration + 30)
        )
        
        try:
            # Run the chaos injection
            if experiment.chaos_type == ChaosType.NETWORK_LATENCY:
                await self.inject_network_latency(experiment.intensity, experiment.duration)
            elif experiment.chaos_type == ChaosType.CPU_STRESS:
                await self.inject_cpu_stress(experiment.intensity, experiment.duration)
            elif experiment.chaos_type == ChaosType.MEMORY_STRESS:
                await self.inject_memory_stress(experiment.intensity, experiment.duration)
            elif experiment.chaos_type == ChaosType.RATE_LIMIT_OVERLOAD:
                await self.inject_rate_limit_overload(experiment.intensity, experiment.duration)
            else:
                raise ValueError(f"Unsupported chaos type: {experiment.chaos_type}")
            
            # Get metrics during experiment
            metrics_during = await self.get_system_metrics()
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Chaos experiment failed: {e}")
        else:
            error_message = None
        
        # Stop monitoring
        self.monitoring_active = False
        monitor_task.cancel()
        
        # Wait for system to recover
        recovery_start = time.time()
        recovery_time = 0
        
        while recovery_time < experiment.recovery_time:
            health_after = await self.test_system_health()
            if health_after:
                break
            await asyncio.sleep(1)
            recovery_time = time.time() - recovery_start
        
        end_time = time.time()
        
        # Get final metrics
        metrics_after = await self.get_system_metrics()
        api_after = await self.test_api_functionality()
        
        # Determine if experiment was successful
        success = error_message is None
        system_recovered = health_after
        
        result = ChaosResult(
            experiment_name=experiment.name,
            chaos_type=experiment.chaos_type,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            success=success,
            system_recovered=system_recovered,
            recovery_time=recovery_time,
            error_message=error_message,
            metrics_before={
                "system_metrics": metrics_before,
                "health": health_before,
                "api_functionality": api_before
            },
            metrics_during={"system_metrics": metrics_during},
            metrics_after={
                "system_metrics": metrics_after,
                "health": health_after,
                "api_functionality": api_after
            },
            details={
                "intensity": experiment.intensity,
                "target": experiment.target,
                "expected_behavior": experiment.expected_behavior
            }
        )
        
        # Print results
        status = "✅ SUCCESS" if success else "❌ FAILED"
        recovery_status = "✅ RECOVERED" if system_recovered else "❌ NOT RECOVERED"
        
        print(f"   {status} - System {recovery_status}")
        print(f"   Recovery Time: {recovery_time:.1f}s")
        if error_message:
            print(f"   Error: {error_message}")
        
        return result
    
    async def run_all_experiments(self) -> List[ChaosResult]:
        """Run all chaos experiments"""
        print("🌪️  Running Chaos Engineering Experiments")
        print("=" * 60)
        
        # Setup
        await self.setup()
        
        try:
            for experiment in self.experiments:
                try:
                    result = await self.run_experiment(experiment)
                    self.results.append(result)
                    
                    # Wait between experiments
                    print("⏳ Waiting 30 seconds before next experiment...")
                    await asyncio.sleep(30)
                    
                except Exception as e:
                    logger.error(f"Experiment {experiment.name} failed: {e}")
                    print(f"❌ Experiment {experiment.name} failed: {e}")
        
        finally:
            # Teardown
            await self.teardown()
        
        return self.results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate chaos engineering report"""
        if not self.results:
            return {"error": "No chaos experiment results available"}
        
        total_experiments = len(self.results)
        successful_experiments = sum(1 for result in self.results if result.success)
        recovered_systems = sum(1 for result in self.results if result.system_recovered)
        
        avg_recovery_time = statistics.mean([result.recovery_time for result in self.results])
        
        # Group by chaos type
        by_type = {}
        for result in self.results:
            chaos_type = result.chaos_type.value
            if chaos_type not in by_type:
                by_type[chaos_type] = []
            by_type[chaos_type].append(result)
        
        report = {
            "summary": {
                "total_experiments": total_experiments,
                "successful_experiments": successful_experiments,
                "recovered_systems": recovered_systems,
                "success_rate": (successful_experiments / total_experiments * 100) if total_experiments > 0 else 0,
                "recovery_rate": (recovered_systems / total_experiments * 100) if total_experiments > 0 else 0,
                "avg_recovery_time": avg_recovery_time
            },
            "by_type": {
                chaos_type: {
                    "count": len(results),
                    "success_rate": sum(1 for r in results if r.success) / len(results) * 100,
                    "recovery_rate": sum(1 for r in results if r.system_recovered) / len(results) * 100,
                    "avg_recovery_time": statistics.mean([r.recovery_time for r in results])
                }
                for chaos_type, results in by_type.items()
            },
            "detailed_results": [asdict(result) for result in self.results],
            "metrics_history": self.metrics_history,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return report
    
    def save_results(self, filename: str):
        """Save chaos engineering results to file"""
        report = self.generate_report()
        
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Chaos engineering results saved to: {filename}")

async def main():
    """Main function for chaos engineering"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Chaos Engineering Suite")
    parser.add_argument("--url", "-u", default="http://localhost:8000", help="Base URL to test")
    parser.add_argument("--output", "-o", default="tests/chaos/results.json", help="Output file for results")
    parser.add_argument("--experiment", "-e", help="Run specific experiment by name")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    # Run chaos engineering
    chaos_engineer = ChaosEngineer(args.url)
    
    if args.experiment:
        # Run specific experiment
        await chaos_engineer.setup()
        try:
            experiment = next(
                (exp for exp in chaos_engineer.experiments if exp.name == args.experiment),
                None
            )
            if experiment:
                result = await chaos_engineer.run_experiment(experiment)
                chaos_engineer.results = [result]
            else:
                print(f"❌ Experiment '{args.experiment}' not found")
                return 1
        finally:
            await chaos_engineer.teardown()
    else:
        # Run all experiments
        results = await chaos_engineer.run_all_experiments()
    
    # Generate and save report
    chaos_engineer.save_results(args.output)
    
    # Print summary
    report = chaos_engineer.generate_report()
    
    print("\n" + "=" * 60)
    print("🌪️  CHAOS ENGINEERING REPORT")
    print("=" * 60)
    print(f"Total Experiments: {report['summary']['total_experiments']}")
    print(f"Successful: {report['summary']['successful_experiments']}")
    print(f"Systems Recovered: {report['summary']['recovered_systems']}")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    print(f"Recovery Rate: {report['summary']['recovery_rate']:.1f}%")
    print(f"Avg Recovery Time: {report['summary']['avg_recovery_time']:.1f}s")
    print()
    
    # Print by type
    print("By Chaos Type:")
    for chaos_type, stats in report['by_type'].items():
        print(f"  {chaos_type.upper()}:")
        print(f"    Experiments: {stats['count']}")
        print(f"    Success Rate: {stats['success_rate']:.1f}%")
        print(f"    Recovery Rate: {stats['recovery_rate']:.1f}%")
        print(f"    Avg Recovery Time: {stats['avg_recovery_time']:.1f}s")
        print()
    
    return 0

if __name__ == "__main__":
    import sys
    import statistics
    asyncio.run(main())
