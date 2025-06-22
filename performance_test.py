#!/usr/bin/env python3
"""
Performance Testing Suite for LAIT Platform
Tests API performance, ML model inference, and system scalability
"""

import asyncio
import aiohttp
import time
import statistics
import json
import psutil
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# Configuration
BACKEND_URL = "http://localhost:5003"
FRONTEND_URL = "http://localhost:3000"
TEST_TIMEOUT = 30

class PerformanceTester:
    def __init__(self):
        self.results = {
            "api_tests": {},
            "ml_tests": {},
            "load_tests": {},
            "memory_usage": {},
            "system_info": {}
        }
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    async def test_api_endpoint(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Test a single API endpoint and measure performance"""
        url = f"{BACKEND_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)) as response:
                    response_time = time.time() - start_time
                    return {
                        "endpoint": endpoint,
                        "method": method,
                        "status_code": response.status,
                        "response_time": response_time,
                        "success": response.status == 200
                    }
            elif method == "POST":
                async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)) as response:
                    response_time = time.time() - start_time
                    return {
                        "endpoint": endpoint,
                        "method": method,
                        "status_code": response.status,
                        "response_time": response_time,
                        "success": response.status == 200
                    }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": None,
                "response_time": response_time,
                "success": False,
                "error": str(e)
            }
    
    async def test_api_performance(self):
        """Test performance of all major API endpoints"""
        self.log("Testing API Performance", "PERF")
        
        endpoints = [
            ("/api/health", "GET"),
            ("/api/ml/status", "GET"),
            ("/api/legal-intelligence/test", "GET"),
            ("/api/analytics/dashboard/metrics", "GET"),
            ("/api/vendors", "GET"),
            ("/api/invoices", "GET"),
            ("/api/legal-intelligence/verify-attorney", "POST", {
                "attorney_name": "John Smith",
                "law_firm": "Test Law Firm",
                "bar_number": "12345",
                "state": "CA"
            })
        ]
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for endpoint_info in endpoints:
                if len(endpoint_info) == 2:
                    endpoint, method = endpoint_info
                    task = self.test_api_endpoint(session, endpoint, method)
                else:
                    endpoint, method, data = endpoint_info
                    task = self.test_api_endpoint(session, endpoint, method, data)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # Analyze results
            successful_results = [r for r in results if r["success"]]
            response_times = [r["response_time"] for r in successful_results]
            
            if response_times:
                self.results["api_tests"] = {
                    "total_endpoints": len(endpoints),
                    "successful_requests": len(successful_results),
                    "success_rate": len(successful_results) / len(endpoints) * 100,
                    "avg_response_time": statistics.mean(response_times),
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "median_response_time": statistics.median(response_times),
                    "endpoint_details": results
                }
            else:
                self.results["api_tests"] = {
                    "error": "No successful API requests"
                }
    
    async def test_ml_model_performance(self):
        """Test ML model inference performance"""
        self.log("Testing ML Model Performance", "PERF")
        
        async with aiohttp.ClientSession() as session:
            # Test ML status endpoint multiple times
            start_time = time.time()
            response_times = []
            
            for i in range(10):
                result = await self.test_api_endpoint(session, "/api/ml/status", "GET")
                if result["success"]:
                    response_times.append(result["response_time"])
                await asyncio.sleep(0.1)  # Small delay between requests
            
            total_time = time.time() - start_time
            
            if response_times:
                self.results["ml_tests"] = {
                    "total_requests": 10,
                    "successful_requests": len(response_times),
                    "success_rate": len(response_times) / 10 * 100,
                    "avg_response_time": statistics.mean(response_times),
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "total_test_time": total_time,
                    "requests_per_second": len(response_times) / total_time
                }
            else:
                self.results["ml_tests"] = {
                    "error": "No successful ML model requests"
                }
    
    async def test_concurrent_load(self, concurrent_users: int = 10):
        """Test system performance under concurrent load"""
        self.log(f"Testing Concurrent Load ({concurrent_users} users)", "PERF")
        
        async def simulate_user():
            async with aiohttp.ClientSession() as session:
                endpoints = [
                    "/api/health",
                    "/api/ml/status",
                    "/api/analytics/dashboard/metrics"
                ]
                
                results = []
                for endpoint in endpoints:
                    result = await self.test_api_endpoint(session, endpoint, "GET")
                    results.append(result)
                    await asyncio.sleep(0.1)
                
                return results
        
        # Run concurrent user simulations
        start_time = time.time()
        tasks = [simulate_user() for _ in range(concurrent_users)]
        all_results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Flatten results
        flat_results = [result for user_results in all_results for result in user_results]
        successful_results = [r for r in flat_results if r["success"]]
        response_times = [r["response_time"] for r in successful_results]
        
        if response_times:
            self.results["load_tests"] = {
                "concurrent_users": concurrent_users,
                "total_requests": len(flat_results),
                "successful_requests": len(successful_results),
                "success_rate": len(successful_results) / len(flat_results) * 100,
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "total_test_time": total_time,
                "requests_per_second": len(successful_results) / total_time,
                "throughput": len(successful_results) / total_time
            }
        else:
            self.results["load_tests"] = {
                "error": "No successful requests under load"
            }
    
    def measure_memory_usage(self):
        """Measure current memory usage"""
        self.log("Measuring Memory Usage", "PERF")
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        self.results["memory_usage"] = {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent(),
            "available_memory_mb": psutil.virtual_memory().available / 1024 / 1024,
            "total_memory_mb": psutil.virtual_memory().total / 1024 / 1024
        }
    
    def get_system_info(self):
        """Get system information"""
        self.log("Gathering System Information", "PERF")
        
        self.results["system_info"] = {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "platform": os.uname().sysname,
            "python_version": os.sys.version
        }
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        self.log("Generating Performance Report", "REPORT")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "api_success_rate": self.results["api_tests"].get("success_rate", 0),
                "ml_success_rate": self.results["ml_tests"].get("success_rate", 0),
                "load_success_rate": self.results["load_tests"].get("success_rate", 0),
                "avg_api_response_time": self.results["api_tests"].get("avg_response_time", 0),
                "avg_ml_response_time": self.results["ml_tests"].get("avg_response_time", 0),
                "load_throughput": self.results["load_tests"].get("throughput", 0)
            },
            "detailed_results": self.results
        }
        
        # Save report
        with open("performance_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("PERFORMANCE TEST RESULTS SUMMARY")
        print("="*60)
        print(f"API Success Rate: {report['summary']['api_success_rate']:.1f}%")
        print(f"ML Success Rate: {report['summary']['ml_success_rate']:.1f}%")
        print(f"Load Success Rate: {report['summary']['load_success_rate']:.1f}%")
        print(f"Avg API Response Time: {report['summary']['avg_api_response_time']:.3f}s")
        print(f"Avg ML Response Time: {report['summary']['avg_ml_response_time']:.3f}s")
        print(f"Load Throughput: {report['summary']['load_throughput']:.1f} req/s")
        print(f"Memory Usage: {self.results['memory_usage'].get('rss_mb', 0):.1f} MB")
        print("="*60)
        print("Detailed report saved to: performance_test_report.json")
        
        return report
    
    async def run_all_tests(self):
        """Run all performance tests"""
        self.log("Starting Comprehensive Performance Testing", "START")
        
        # Get system info
        self.get_system_info()
        self.measure_memory_usage()
        
        # Run tests
        await self.test_api_performance()
        await self.test_ml_model_performance()
        await self.test_concurrent_load(10)
        
        # Generate report
        self.generate_report()

async def main():
    """Main function to run performance tests"""
    tester = PerformanceTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 