# Rate Limiting System

"""
Advanced rate limiting system with multiple algorithms and flexible rules
"""

import time
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

class RateLimitScope(Enum):
    """Rate limiting scope"""
    GLOBAL = "global"
    PER_USER = "per_user"
    PER_IP = "per_ip"
    PER_ENDPOINT = "per_endpoint"
    CUSTOM = "custom"

@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    name: str
    algorithm: RateLimitAlgorithm
    scope: RateLimitScope
    limit: int  # Number of requests allowed
    window: int  # Time window in seconds
    burst: Optional[int] = None  # Burst capacity for token bucket
    custom_key_func: Optional[callable] = None  # Custom key function
    enabled: bool = True
    message: str = "Rate limit exceeded"

@dataclass
class RateLimitResult:
    """Rate limiting result"""
    allowed: bool
    limit: int
    remaining: int
    reset_time: int
    retry_after: Optional[int] = None
    message: str = ""

class FixedWindowRateLimiter:
    """Fixed window rate limiter"""
    
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.windows: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "count": 0,
            "window_start": int(time.time())
        })
    
    def is_allowed(self, key: str) -> RateLimitResult:
        """Check if request is allowed"""
        current_time = int(time.time())
        window_data = self.windows[key]
        
        # Check if we're in a new window
        if current_time - window_data["window_start"] >= self.window:
            window_data["count"] = 0
            window_data["window_start"] = current_time
        
        # Check if limit is exceeded
        if window_data["count"] >= self.limit:
            reset_time = window_data["window_start"] + self.window
            retry_after = reset_time - current_time
            
            return RateLimitResult(
                allowed=False,
                limit=self.limit,
                remaining=0,
                reset_time=reset_time,
                retry_after=retry_after,
                message="Rate limit exceeded"
            )
        
        # Increment counter
        window_data["count"] += 1
        remaining = self.limit - window_data["count"]
        reset_time = window_data["window_start"] + self.window
        
        return RateLimitResult(
            allowed=True,
            limit=self.limit,
            remaining=remaining,
            reset_time=reset_time
        )

class SlidingWindowRateLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, key: str) -> RateLimitResult:
        """Check if request is allowed"""
        current_time = time.time()
        requests_queue = self.requests[key]
        
        # Remove old requests outside the window
        while requests_queue and requests_queue[0] <= current_time - self.window:
            requests_queue.popleft()
        
        # Check if limit is exceeded
        if len(requests_queue) >= self.limit:
            oldest_request = requests_queue[0]
            reset_time = int(oldest_request + self.window)
            retry_after = int(reset_time - current_time)
            
            return RateLimitResult(
                allowed=False,
                limit=self.limit,
                remaining=0,
                reset_time=reset_time,
                retry_after=retry_after,
                message="Rate limit exceeded"
            )
        
        # Add current request
        requests_queue.append(current_time)
        remaining = self.limit - len(requests_queue)
        reset_time = int(current_time + self.window)
        
        return RateLimitResult(
            allowed=True,
            limit=self.limit,
            remaining=remaining,
            reset_time=reset_time
        )

class TokenBucketRateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, limit: int, window: int, burst: Optional[int] = None):
        self.limit = limit
        self.window = window
        self.burst = burst or limit
        self.buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "tokens": self.burst,
            "last_refill": time.time()
        })
    
    def is_allowed(self, key: str) -> RateLimitResult:
        """Check if request is allowed"""
        current_time = time.time()
        bucket = self.buckets[key]
        
        # Refill tokens based on time passed
        time_passed = current_time - bucket["last_refill"]
        tokens_to_add = time_passed * (self.limit / self.window)
        bucket["tokens"] = min(self.burst, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time
        
        # Check if we have tokens
        if bucket["tokens"] < 1:
            # Calculate when next token will be available
            time_to_next_token = (1 - bucket["tokens"]) / (self.limit / self.window)
            reset_time = int(current_time + time_to_next_token)
            retry_after = int(time_to_next_token)
            
            return RateLimitResult(
                allowed=False,
                limit=self.limit,
                remaining=0,
                reset_time=reset_time,
                retry_after=retry_after,
                message="Rate limit exceeded"
            )
        
        # Consume token
        bucket["tokens"] -= 1
        remaining = int(bucket["tokens"])
        reset_time = int(current_time + self.window)
        
        return RateLimitResult(
            allowed=True,
            limit=self.limit,
            remaining=remaining,
            reset_time=reset_time
        )

class LeakyBucketRateLimiter:
    """Leaky bucket rate limiter"""
    
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "level": 0,
            "last_leak": time.time()
        })
    
    def is_allowed(self, key: str) -> RateLimitResult:
        """Check if request is allowed"""
        current_time = time.time()
        bucket = self.buckets[key]
        
        # Leak water from bucket
        time_passed = current_time - bucket["last_leak"]
        leaked = time_passed * (self.limit / self.window)
        bucket["level"] = max(0, bucket["level"] - leaked)
        bucket["last_leak"] = current_time
        
        # Check if bucket is full
        if bucket["level"] >= self.limit:
            # Calculate when bucket will have space
            time_to_space = (bucket["level"] - self.limit + 1) / (self.limit / self.window)
            reset_time = int(current_time + time_to_space)
            retry_after = int(time_to_space)
            
            return RateLimitResult(
                allowed=False,
                limit=self.limit,
                remaining=0,
                reset_time=reset_time,
                retry_after=retry_after,
                message="Rate limit exceeded"
            )
        
        # Add water to bucket
        bucket["level"] += 1
        remaining = int(self.limit - bucket["level"])
        reset_time = int(current_time + self.window)
        
        return RateLimitResult(
            allowed=True,
            limit=self.limit,
            remaining=remaining,
            reset_time=reset_time
        )

class RateLimiterFactory:
    """Factory for creating rate limiters"""
    
    @staticmethod
    def create_limiter(algorithm: RateLimitAlgorithm, limit: int, 
                      window: int, burst: Optional[int] = None):
        """Create rate limiter based on algorithm"""
        if algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return FixedWindowRateLimiter(limit, window)
        elif algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return SlidingWindowRateLimiter(limit, window)
        elif algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return TokenBucketRateLimiter(limit, window, burst)
        elif algorithm == RateLimitAlgorithm.LEAKY_BUCKET:
            return LeakyBucketRateLimiter(limit, window)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

class RateLimitManager:
    """Advanced rate limiting manager"""
    
    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.limiters: Dict[str, Any] = {}
        self.stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            "allowed": 0,
            "denied": 0,
            "total": 0
        })
    
    def add_rule(self, rule: RateLimitRule):
        """Add rate limiting rule"""
        self.rules[rule.name] = rule
        
        # Create limiter for the rule
        limiter = RateLimiterFactory.create_limiter(
            rule.algorithm, rule.limit, rule.window, rule.burst
        )
        self.limiters[rule.name] = limiter
        
        logger.info(f"Added rate limit rule: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Remove rate limiting rule"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            del self.limiters[rule_name]
            logger.info(f"Removed rate limit rule: {rule_name}")
    
    def get_key(self, rule: RateLimitRule, request_data: Dict[str, Any]) -> str:
        """Generate rate limiting key based on scope"""
        if rule.scope == RateLimitScope.GLOBAL:
            return "global"
        elif rule.scope == RateLimitScope.PER_USER:
            return f"user:{request_data.get('user_id', 'anonymous')}"
        elif rule.scope == RateLimitScope.PER_IP:
            return f"ip:{request_data.get('ip_address', 'unknown')}"
        elif rule.scope == RateLimitScope.PER_ENDPOINT:
            return f"endpoint:{request_data.get('endpoint', 'unknown')}"
        elif rule.scope == RateLimitScope.CUSTOM and rule.custom_key_func:
            return rule.custom_key_func(request_data)
        else:
            return "default"
    
    def check_rate_limit(self, rule_name: str, request_data: Dict[str, Any]) -> RateLimitResult:
        """Check if request is allowed by rate limit rule"""
        if rule_name not in self.rules:
            # No rule found, allow request
            return RateLimitResult(
                allowed=True,
                limit=0,
                remaining=0,
                reset_time=int(time.time())
            )
        
        rule = self.rules[rule_name]
        if not rule.enabled:
            return RateLimitResult(
                allowed=True,
                limit=rule.limit,
                remaining=rule.limit,
                reset_time=int(time.time())
            )
        
        # Generate key and check rate limit
        key = self.get_key(rule, request_data)
        limiter = self.limiters[rule_name]
        result = limiter.is_allowed(key)
        
        # Update statistics
        self.stats[rule_name]["total"] += 1
        if result.allowed:
            self.stats[rule_name]["allowed"] += 1
        else:
            self.stats[rule_name]["denied"] += 1
        
        # Set custom message if provided
        if rule.message:
            result.message = rule.message
        
        return result
    
    def get_stats(self, rule_name: Optional[str] = None) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        if rule_name:
            if rule_name in self.stats:
                stats = self.stats[rule_name]
                total = stats["total"]
                return {
                    "rule": rule_name,
                    "total_requests": total,
                    "allowed_requests": stats["allowed"],
                    "denied_requests": stats["denied"],
                    "allow_rate": stats["allowed"] / total if total > 0 else 0,
                    "deny_rate": stats["denied"] / total if total > 0 else 0
                }
            else:
                return {"error": f"Rule {rule_name} not found"}
        else:
            return dict(self.stats)
    
    def reset_stats(self, rule_name: Optional[str] = None):
        """Reset rate limiting statistics"""
        if rule_name:
            if rule_name in self.stats:
                self.stats[rule_name] = {"allowed": 0, "denied": 0, "total": 0}
        else:
            self.stats.clear()

# Global rate limit manager
rate_limit_manager = RateLimitManager()

# Predefined rate limiting rules
def setup_default_rules():
    """Setup default rate limiting rules"""
    
    # API rate limiting
    api_rule = RateLimitRule(
        name="api_global",
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        scope=RateLimitScope.GLOBAL,
        limit=1000,  # 1000 requests
        window=3600,  # per hour
        message="API rate limit exceeded. Please try again later."
    )
    rate_limit_manager.add_rule(api_rule)
    
    # User rate limiting
    user_rule = RateLimitRule(
        name="user_requests",
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        scope=RateLimitScope.PER_USER,
        limit=100,  # 100 requests
        window=3600,  # per hour
        burst=20,  # Allow burst of 20 requests
        message="User rate limit exceeded. Please slow down your requests."
    )
    rate_limit_manager.add_rule(user_rule)
    
    # IP rate limiting
    ip_rule = RateLimitRule(
        name="ip_requests",
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        scope=RateLimitScope.PER_IP,
        limit=200,  # 200 requests
        window=3600,  # per hour
        message="IP rate limit exceeded. Please try again later."
    )
    rate_limit_manager.add_rule(ip_rule)
    
    # Authentication rate limiting
    auth_rule = RateLimitRule(
        name="auth_attempts",
        algorithm=RateLimitAlgorithm.FIXED_WINDOW,
        scope=RateLimitScope.PER_IP,
        limit=5,  # 5 attempts
        window=900,  # per 15 minutes
        message="Too many authentication attempts. Please try again later."
    )
    rate_limit_manager.add_rule(auth_rule)
    
    # WhatsApp webhook rate limiting
    webhook_rule = RateLimitRule(
        name="whatsapp_webhook",
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        scope=RateLimitScope.PER_IP,
        limit=1000,  # 1000 requests
        window=3600,  # per hour
        burst=100,  # Allow burst of 100 requests
        message="WhatsApp webhook rate limit exceeded."
    )
    rate_limit_manager.add_rule(webhook_rule)

# Rate limiting decorator
def rate_limit(rule_name: str, request_data_func: Optional[callable] = None):
    """Decorator to apply rate limiting to functions"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # Get request data
            if request_data_func:
                request_data = request_data_func(*args, **kwargs)
            else:
                request_data = {}
            
            # Check rate limit
            result = rate_limit_manager.check_rate_limit(rule_name, request_data)
            
            if not result.allowed:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": result.message,
                        "retry_after": result.retry_after,
                        "limit": result.limit,
                        "remaining": result.remaining,
                        "reset_time": result.reset_time
                    },
                    headers={
                        "X-RateLimit-Limit": str(result.limit),
                        "X-RateLimit-Remaining": str(result.remaining),
                        "X-RateLimit-Reset": str(result.reset_time),
                        "Retry-After": str(result.retry_after) if result.retry_after else "0"
                    }
                )
            
            return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            # Get request data
            if request_data_func:
                request_data = request_data_func(*args, **kwargs)
            else:
                request_data = {}
            
            # Check rate limit
            result = rate_limit_manager.check_rate_limit(rule_name, request_data)
            
            if not result.allowed:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": result.message,
                        "retry_after": result.retry_after,
                        "limit": result.limit,
                        "remaining": result.remaining,
                        "reset_time": result.reset_time
                    },
                    headers={
                        "X-RateLimit-Limit": str(result.limit),
                        "X-RateLimit-Remaining": str(result.remaining),
                        "X-RateLimit-Reset": str(result.reset_time),
                        "Retry-After": str(result.retry_after) if result.retry_after else "0"
                    }
                )
            
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Rate limiting middleware for FastAPI
class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app, default_rule: str = "api_global"):
        self.app = app
        self.default_rule = default_rule
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract request information
        request_data = {
            "ip_address": self._get_client_ip(scope),
            "endpoint": scope.get("path", ""),
            "method": scope.get("method", "")
        }
        
        # Check rate limit
        result = rate_limit_manager.check_rate_limit(self.default_rule, request_data)
        
        if not result.allowed:
            # Send rate limit response
            response_body = json.dumps({
                "error": "Rate limit exceeded",
                "message": result.message,
                "retry_after": result.retry_after,
                "limit": result.limit,
                "remaining": result.remaining,
                "reset_time": result.reset_time
            }).encode()
            
            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"x-rate-limit-limit", str(result.limit).encode()),
                    (b"x-rate-limit-remaining", str(result.remaining).encode()),
                    (b"x-rate-limit-reset", str(result.reset_time).encode()),
                    (b"retry-after", str(result.retry_after).encode() if result.retry_after else b"0")
                ]
            })
            
            await send({
                "type": "http.response.body",
                "body": response_body
            })
            return
        
        # Add rate limit headers to response
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend([
                    (b"x-rate-limit-limit", str(result.limit).encode()),
                    (b"x-rate-limit-remaining", str(result.remaining).encode()),
                    (b"x-rate-limit-reset", str(result.reset_time).encode())
                ])
                message["headers"] = headers
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
    
    def _get_client_ip(self, scope) -> str:
        """Extract client IP from request scope"""
        # Try to get IP from headers first
        headers = dict(scope.get("headers", []))
        
        # Check for forwarded IP
        if b"x-forwarded-for" in headers:
            return headers[b"x-forwarded-for"].decode().split(",")[0].strip()
        
        # Check for real IP
        if b"x-real-ip" in headers:
            return headers[b"x-real-ip"].decode()
        
        # Fallback to client address
        client = scope.get("client")
        if client:
            return client[0]
        
        return "unknown"

# Utility functions
def get_rate_limit_stats(rule_name: Optional[str] = None) -> Dict[str, Any]:
    """Get rate limiting statistics"""
    return rate_limit_manager.get_stats(rule_name)

def reset_rate_limit_stats(rule_name: Optional[str] = None):
    """Reset rate limiting statistics"""
    rate_limit_manager.reset_stats(rule_name)

def add_rate_limit_rule(rule: RateLimitRule):
    """Add a new rate limiting rule"""
    rate_limit_manager.add_rule(rule)

def remove_rate_limit_rule(rule_name: str):
    """Remove a rate limiting rule"""
    rate_limit_manager.remove_rule(rule_name)

# Initialize default rules
setup_default_rules()
