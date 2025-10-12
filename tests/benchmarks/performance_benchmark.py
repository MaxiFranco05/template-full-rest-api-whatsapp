# Performance Benchmarking Suite

"""
Comprehensive performance benchmarking suite for Business API Template
"""

import asyncio
import aiohttp
import time
import statistics
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import concurrent.futures
from pathlib import Path

logger = logging.getLogger(__name__)

class BenchmarkType(Enum):
    """Types of benchmarks"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    CONCURRENT_USERS = "concurrent_users"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DATABASE_PERFORMANCE = "database_performance"

@dataclass
class BenchmarkResult:
    """Result of a benchmark test"""
    test_name: str
    benchmark_type: BenchmarkType
    duration: float
    requests_count: int
    success_count: int
    error_count: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    details: Dict[str, Any]

class PerformanceBenchmark:
    """Main performance benchmarking class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.token = None
        self.benchmark_results: List[BenchmarkResult] = []
        
    async def setup(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
        # Authenticate
        await self.authenticate()
    
    async def teardown(self):
        """Cleanup HTTP session"""
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
    
    async def make_request(self, method: str, endpoint: str, 
                          json_data: Optional[Dict] = None,
                          params: Optional[Dict] = None) -> Tuple[int, float, bool]:
        """Make a single HTTP request"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        start_time = time.time()
        
        try:
            async with self.session.request(
                method, url, json=json_data, params=params, headers=headers
            ) as response:
                response_time = time.time() - start_time
                success = response.status < 400
                return response.status, response_time, success
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Request failed: {e}")
            return 500, response_time, False
    
    async def benchmark_latency(self, endpoint: str, method: str = "GET",
                               requests_count: int = 100,
                               json_data: Optional[Dict] = None,
                               params: Optional[Dict] = None) -> BenchmarkResult:
        """Benchmark latency for a specific endpoint"""
        test_name = f"Latency Benchmark - {endpoint}"
        start_time = time.time()
        
        response_times = []
        success_count = 0
        error_count = 0
        
        # Make requests sequentially for latency testing
        for i in range(requests_count):
            status, response_time, success = await self.make_request(
                method, endpoint, json_data, params
            )
            
            response_times.append(response_time)
            
            if success:
                success_count += 1
            else:
                error_count += 1
            
            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.01)
        
        duration = time.time() - start_time
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p50_response_time = statistics.median(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)]
        
        requests_per_second = requests_count / duration
        error_rate = (error_count / requests_count) * 100
        
        return BenchmarkResult(
            test_name=test_name,
            benchmark_type=BenchmarkType.LATENCY,
            duration=duration,
            requests_count=requests_count,
            success_count=success_count,
            error_count=error_count,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p50_response_time=p50_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            details={
                "endpoint": endpoint,
                "method": method,
                "response_times": response_times
            }
        )
    
    async def benchmark_throughput(self, endpoint: str, method: str = "GET",
                                  duration_seconds: int = 60,
                                  concurrent_requests: int = 10,
                                  json_data: Optional[Dict] = None,
                                  params: Optional[Dict] = None) -> BenchmarkResult:
        """Benchmark throughput for a specific endpoint"""
        test_name = f"Throughput Benchmark - {endpoint}"
        start_time = time.time()
        
        response_times = []
        success_count = 0
        error_count = 0
        requests_count = 0
        
        async def worker():
            nonlocal success_count, error_count, requests_count
            while time.time() - start_time < duration_seconds:
                status, response_time, success = await self.make_request(
                    method, endpoint, json_data, params
                )
                
                response_times.append(response_time)
                requests_count += 1
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
        
        # Run concurrent workers
        workers = [worker() for _ in range(concurrent_requests)]
        await asyncio.gather(*workers)
        
        actual_duration = time.time() - start_time
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p50_response_time = statistics.median(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
            p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p50_response_time = p95_response_time = p99_response_time = 0
        
        requests_per_second = requests_count / actual_duration
        error_rate = (error_count / requests_count) * 100 if requests_count > 0 else 0
        
        return BenchmarkResult(
            test_name=test_name,
            benchmark_type=BenchmarkType.THROUGHPUT,
            duration=actual_duration,
            requests_count=requests_count,
            success_count=success_count,
            error_count=error_count,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p50_response_time=p50_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            details={
                "endpoint": endpoint,
                "method": method,
                "concurrent_requests": concurrent_requests,
                "response_times": response_times
            }
        )
    
    async def benchmark_concurrent_users(self, endpoint: str, method: str = "GET",
                                        user_counts: List[int] = [1, 5, 10, 25, 50],
                                        requests_per_user: int = 10,
                                        json_data: Optional[Dict] = None,
                                        params: Optional[Dict] = None) -> List[BenchmarkResult]:
        """Benchmark performance with different concurrent user counts"""
        results = []
        
        for user_count in user_counts:
            test_name = f"Concurrent Users Benchmark - {user_count} users"
            start_time = time.time()
            
            response_times = []
            success_count = 0
            error_count = 0
            
            async def user_simulation():
                nonlocal success_count, error_count
                for _ in range(requests_per_user):
                    status, response_time, success = await self.make_request(
                        method, endpoint, json_data, params
                    )
                    
                    response_times.append(response_time)
                    
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
            
            # Run concurrent user simulations
            users = [user_simulation() for _ in range(user_count)]
            await asyncio.gather(*users)
            
            duration = time.time() - start_time
            requests_count = user_count * requests_per_user
            
            # Calculate statistics
            if response_times:
                avg_response_time = statistics.mean(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)
                p50_response_time = statistics.median(response_times)
                p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
                p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)]
            else:
                avg_response_time = min_response_time = max_response_time = 0
                p50_response_time = p95_response_time = p99_response_time = 0
            
            requests_per_second = requests_count / duration
            error_rate = (error_count / requests_count) * 100
            
            result = BenchmarkResult(
                test_name=test_name,
                benchmark_type=BenchmarkType.CONCURRENT_USERS,
                duration=duration,
                requests_count=requests_count,
                success_count=success_count,
                error_count=error_count,
                avg_response_time=avg_response_time,
                min_response_time=min_response_time,
                max_response_time=max_response_time,
                p50_response_time=p50_response_time,
                p95_response_time=p95_response_time,
                p99_response_time=p99_response_time,
                requests_per_second=requests_per_second,
                error_rate=error_rate,
                details={
                    "endpoint": endpoint,
                    "method": method,
                    "user_count": user_count,
                    "requests_per_user": requests_per_user,
                    "response_times": response_times
                }
            )
            
            results.append(result)
        
        return results
    
    async def benchmark_endpoints(self) -> List[BenchmarkResult]:
        """Benchmark various endpoints"""
        print("🚀 Running Endpoint Benchmarks")
        print("=" * 50)
        
        endpoints_to_test = [
            ("/health", "GET", None, None),
            ("/performance", "GET", None, None),
            ("/api/v1/users/", "GET", None, {"page": 1, "size": 20}),
            ("/api/v1/products/", "GET", None, {"page": 1, "size": 20}),
            ("/api/v1/products/", "POST", {"name": "Benchmark Product", "price": 100, "stock_quantity": 10}, None),
            ("/api/v1/whatsapp/conversations/", "GET", None, {"page": 1, "size": 20})
        ]
        
        results = []
        
        for endpoint, method, json_data, params in endpoints_to_test:
            print(f"Benchmarking {method} {endpoint}...")
            
            # Latency benchmark
            latency_result = await self.benchmark_latency(
                endpoint, method, requests_count=50, json_data=json_data, params=params
            )
            results.append(latency_result)
            
            # Throughput benchmark
            throughput_result = await self.benchmark_throughput(
                endpoint, method, duration_seconds=30, concurrent_requests=5,
                json_data=json_data, params=params
            )
            results.append(throughput_result)
            
            print(f"  ✅ Latency: {latency_result.avg_response_time:.3f}s avg")
            print(f"  ✅ Throughput: {throughput_result.requests_per_second:.1f} req/s")
        
        return results
    
    async def benchmark_concurrent_scaling(self) -> List[BenchmarkResult]:
        """Benchmark concurrent user scaling"""
        print("👥 Running Concurrent User Scaling Benchmarks")
        print("=" * 50)
        
        # Test with different user counts
        user_counts = [1, 5, 10, 25, 50, 100]
        
        # Test health endpoint (lightweight)
        health_results = await self.benchmark_concurrent_users(
            "/health", "GET", user_counts, requests_per_user=20
        )
        
        # Test API endpoint (more complex)
        api_results = await self.benchmark_concurrent_users(
            "/api/v1/users/", "GET", user_counts, requests_per_user=10,
            params={"page": 1, "size": 20}
        )
        
        results = health_results + api_results
        
        for result in results:
            user_count = result.details.get("user_count", 0)
            print(f"  👥 {user_count} users: {result.requests_per_second:.1f} req/s, "
                  f"{result.avg_response_time:.3f}s avg, {result.error_rate:.1f}% errors")
        
        return results
    
    async def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all benchmark tests"""
        print("📊 Running Performance Benchmarks")
        print("=" * 60)
        
        # Setup
        await self.setup()
        
        all_results = []
        
        try:
            # Run endpoint benchmarks
            endpoint_results = await self.benchmark_endpoints()
            all_results.extend(endpoint_results)
            
            # Run concurrent scaling benchmarks
            scaling_results = await self.benchmark_concurrent_scaling()
            all_results.extend(scaling_results)
            
        finally:
            # Teardown
            await self.teardown()
        
        self.benchmark_results = all_results
        return all_results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate benchmark report"""
        if not self.benchmark_results:
            return {"error": "No benchmark results available"}
        
        # Calculate overall statistics
        total_tests = len(self.benchmark_results)
        total_requests = sum(result.requests_count for result in self.benchmark_results)
        total_success = sum(result.success_count for result in self.benchmark_results)
        total_errors = sum(result.error_count for result in self.benchmark_results)
        
        # Calculate performance metrics
        avg_response_times = [result.avg_response_time for result in self.benchmark_results]
        requests_per_second = [result.requests_per_second for result in self.benchmark_results]
        
        overall_avg_response_time = statistics.mean(avg_response_times) if avg_response_times else 0
        overall_requests_per_second = statistics.mean(requests_per_second) if requests_per_second else 0
        
        # Group by benchmark type
        by_type = {}
        for result in self.benchmark_results:
            benchmark_type = result.benchmark_type.value
            if benchmark_type not in by_type:
                by_type[benchmark_type] = []
            by_type[benchmark_type].append(result)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "total_requests": total_requests,
                "total_success": total_success,
                "total_errors": total_errors,
                "success_rate": (total_success / total_requests * 100) if total_requests > 0 else 0,
                "overall_avg_response_time": overall_avg_response_time,
                "overall_requests_per_second": overall_requests_per_second
            },
            "by_type": {
                benchmark_type: {
                    "count": len(results),
                    "avg_response_time": statistics.mean([r.avg_response_time for r in results]),
                    "avg_requests_per_second": statistics.mean([r.requests_per_second for r in results]),
                    "avg_error_rate": statistics.mean([r.error_rate for r in results])
                }
                for benchmark_type, results in by_type.items()
            },
            "detailed_results": [asdict(result) for result in self.benchmark_results],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return report
    
    def save_results(self, filename: str):
        """Save benchmark results to file"""
        report = self.generate_report()
        
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Benchmark results saved to: {filename}")

async def main():
    """Main function for performance benchmarking"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance Benchmarking Suite")
    parser.add_argument("--url", "-u", default="http://localhost:8000", help="Base URL to benchmark")
    parser.add_argument("--output", "-o", default="tests/benchmarks/results.json", help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    # Run benchmarks
    benchmark = PerformanceBenchmark(args.url)
    results = await benchmark.run_all_benchmarks()
    
    # Generate and save report
    benchmark.save_results(args.output)
    
    # Print summary
    report = benchmark.generate_report()
    
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE BENCHMARK REPORT")
    print("=" * 60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Total Requests: {report['summary']['total_requests']}")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    print(f"Overall Avg Response Time: {report['summary']['overall_avg_response_time']:.3f}s")
    print(f"Overall Requests/Second: {report['summary']['overall_requests_per_second']:.1f}")
    print()
    
    # Print by type
    print("By Benchmark Type:")
    for benchmark_type, stats in report['by_type'].items():
        print(f"  {benchmark_type.upper()}:")
        print(f"    Tests: {stats['count']}")
        print(f"    Avg Response Time: {stats['avg_response_time']:.3f}s")
        print(f"    Avg RPS: {stats['avg_requests_per_second']:.1f}")
        print(f"    Avg Error Rate: {stats['avg_error_rate']:.1f}%")
        print()
    
    return 0

if __name__ == "__main__":
    import sys
    asyncio.run(main())
