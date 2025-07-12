"""
Monitoring System for A2A Agent Networking

Comprehensive monitoring using W&B Weave for tracking agent performance,
collaboration metrics, and system health.
"""

import time
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import wandb
import os

logger = logging.getLogger(__name__)

@dataclass
class CollaborationMetrics:
    """Metrics for agent collaboration."""
    task_id: str
    users_involved: List[str]
    start_time: float
    end_time: float
    consensus_reached: bool
    negotiation_rounds: int
    user_satisfaction: Optional[float] = None
    response_time_ms: Optional[float] = None
    restaurants_found: int = 0
    collaboration_success: bool = False
    error_message: Optional[str] = None

@dataclass
class SystemMetrics:
    """System-level metrics."""
    timestamp: float
    total_users: int
    active_collaborations: int
    vector_store_queries: int
    restaurant_searches: int
    avg_response_time_ms: float
    system_health: str
    memory_usage_mb: float
    cpu_usage_percent: float

@dataclass
class AgentMetrics:
    """Individual agent metrics."""
    agent_id: str
    agent_type: str
    tasks_completed: int
    avg_response_time_ms: float
    success_rate: float
    error_count: int
    last_active: float

class A2AMonitor:
    """
    Comprehensive monitoring system for A2A Agent Networking.
    """
    
    def __init__(self, project_name: str = "agent-networking-a2a"):
        """
        Initialize the monitoring system.
        
        Args:
            project_name: W&B project name
        """
        self.project_name = project_name
        self.is_wandb_initialized = False
        self.metrics_buffer = []
        self.collaboration_metrics = {}
        self.system_metrics_history = []
        self.agent_metrics = {}
        
        # Initialize W&B if API key is available
        self._initialize_wandb()
        
        # Performance tracking
        self.start_time = time.time()
        self.request_count = 0
        self.response_times = []
        
    def _initialize_wandb(self):
        """Initialize W&B monitoring."""
        try:
            if os.getenv("WANDB_API_KEY"):
                wandb.init(
                    project=self.project_name,
                    name=f"a2a-monitor-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    config={
                        "system": "A2A Agent Networking",
                        "monitoring_version": "1.0.0",
                        "components": ["gateway", "vector_store", "exa_client", "agents"]
                    }
                )
                self.is_wandb_initialized = True
                logger.info("W&B monitoring initialized successfully")
            else:
                logger.warning("WANDB_API_KEY not found, W&B monitoring disabled")
        except Exception as e:
            logger.error(f"Failed to initialize W&B: {e}")
    
    def start_collaboration_tracking(self, task_id: str, users: List[str]) -> str:
        """
        Start tracking a collaboration session.
        
        Args:
            task_id: Unique task identifier
            users: List of users involved
            
        Returns:
            Collaboration tracking ID
        """
        collaboration_id = f"{task_id}_{int(time.time())}"
        
        self.collaboration_metrics[collaboration_id] = CollaborationMetrics(
            task_id=task_id,
            users_involved=users,
            start_time=time.time(),
            end_time=0,
            consensus_reached=False,
            negotiation_rounds=0
        )
        
        logger.info(f"Started collaboration tracking: {collaboration_id}")
        
        if self.is_wandb_initialized:
            wandb.log({
                "collaboration_started": True,
                "collaboration_id": collaboration_id,
                "users_count": len(users),
                "timestamp": time.time()
            })
        
        return collaboration_id
    
    def end_collaboration_tracking(self, collaboration_id: str, success: bool = True, 
                                 error_message: Optional[str] = None):
        """
        End collaboration tracking and log results.
        
        Args:
            collaboration_id: Collaboration tracking ID
            success: Whether collaboration was successful
            error_message: Error message if failed
        """
        if collaboration_id not in self.collaboration_metrics:
            logger.warning(f"Unknown collaboration ID: {collaboration_id}")
            return
        
        metrics = self.collaboration_metrics[collaboration_id]
        metrics.end_time = time.time()
        metrics.collaboration_success = success
        metrics.error_message = error_message
        metrics.response_time_ms = (metrics.end_time - metrics.start_time) * 1000
        
        # Log to W&B
        if self.is_wandb_initialized:
            wandb.log({
                "collaboration_completed": True,
                "collaboration_success": success,
                "response_time_ms": metrics.response_time_ms,
                "users_count": len(metrics.users_involved),
                "negotiation_rounds": metrics.negotiation_rounds,
                "consensus_reached": metrics.consensus_reached,
                "timestamp": time.time()
            })
        
        logger.info(f"Collaboration {collaboration_id} completed: {success}")
        
        # Move to history
        self.metrics_buffer.append(metrics)
        del self.collaboration_metrics[collaboration_id]
    
    def log_restaurant_search(self, query: str, results_count: int, response_time_ms: float):
        """
        Log restaurant search metrics.
        
        Args:
            query: Search query
            results_count: Number of results found
            response_time_ms: Response time in milliseconds
        """
        self.request_count += 1
        self.response_times.append(response_time_ms)
        
        if self.is_wandb_initialized:
            wandb.log({
                "restaurant_search": True,
                "query_length": len(query),
                "results_count": results_count,
                "response_time_ms": response_time_ms,
                "timestamp": time.time()
            })
        
        logger.debug(f"Restaurant search: {results_count} results in {response_time_ms:.2f}ms")
    
    def log_vector_search(self, query: str, results_count: int, response_time_ms: float):
        """
        Log vector search metrics.
        
        Args:
            query: Search query
            results_count: Number of results found
            response_time_ms: Response time in milliseconds
        """
        self.request_count += 1
        self.response_times.append(response_time_ms)
        
        if self.is_wandb_initialized:
            wandb.log({
                "vector_search": True,
                "query_length": len(query),
                "results_count": results_count,
                "response_time_ms": response_time_ms,
                "timestamp": time.time()
            })
        
        logger.debug(f"Vector search: {results_count} results in {response_time_ms:.2f}ms")
    
    def log_agent_task(self, agent_id: str, agent_type: str, task_type: str, 
                      response_time_ms: float, success: bool):
        """
        Log agent task completion.
        
        Args:
            agent_id: Agent identifier
            agent_type: Type of agent
            task_type: Type of task
            response_time_ms: Response time in milliseconds
            success: Whether task was successful
        """
        # Update agent metrics
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                agent_type=agent_type,
                tasks_completed=0,
                avg_response_time_ms=0,
                success_rate=0,
                error_count=0,
                last_active=time.time()
            )
        
        agent_metrics = self.agent_metrics[agent_id]
        agent_metrics.tasks_completed += 1
        agent_metrics.last_active = time.time()
        
        if not success:
            agent_metrics.error_count += 1
        
        # Update average response time
        total_time = agent_metrics.avg_response_time_ms * (agent_metrics.tasks_completed - 1)
        agent_metrics.avg_response_time_ms = (total_time + response_time_ms) / agent_metrics.tasks_completed
        
        # Update success rate
        agent_metrics.success_rate = (agent_metrics.tasks_completed - agent_metrics.error_count) / agent_metrics.tasks_completed
        
        if self.is_wandb_initialized:
            wandb.log({
                "agent_task": True,
                "agent_id": agent_id,
                "agent_type": agent_type,
                "task_type": task_type,
                "response_time_ms": response_time_ms,
                "success": success,
                "timestamp": time.time()
            })
        
        logger.debug(f"Agent {agent_id} completed {task_type}: {success}")
    
    def log_system_metrics(self, total_users: int, active_collaborations: int, 
                          system_health: str = "healthy"):
        """
        Log system-level metrics.
        
        Args:
            total_users: Total number of users in system
            active_collaborations: Number of active collaborations
            system_health: System health status
        """
        try:
            # Get system resource usage
            import psutil
            memory_usage = psutil.virtual_memory().used / 1024 / 1024  # MB
            cpu_usage = psutil.cpu_percent()
        except ImportError:
            memory_usage = 0
            cpu_usage = 0
        
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        system_metrics = SystemMetrics(
            timestamp=time.time(),
            total_users=total_users,
            active_collaborations=active_collaborations,
            vector_store_queries=self.request_count,
            restaurant_searches=self.request_count,
            avg_response_time_ms=avg_response_time,
            system_health=system_health,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage
        )
        
        self.system_metrics_history.append(system_metrics)
        
        if self.is_wandb_initialized:
            wandb.log({
                "system_metrics": True,
                "total_users": total_users,
                "active_collaborations": active_collaborations,
                "avg_response_time_ms": avg_response_time,
                "system_health": system_health,
                "memory_usage_mb": memory_usage,
                "cpu_usage_percent": cpu_usage,
                "timestamp": time.time()
            })
        
        logger.info(f"System metrics logged: {total_users} users, {active_collaborations} active collaborations")
    
    def log_hallucination_detection(self, agent_id: str, response: str, validation_score: float, 
                                  sources_cited: int):
        """
        Log hallucination detection results.
        
        Args:
            agent_id: Agent identifier
            response: Agent response
            validation_score: Validation score (0-1)
            sources_cited: Number of sources cited
        """
        if self.is_wandb_initialized:
            wandb.log({
                "hallucination_check": True,
                "agent_id": agent_id,
                "response_length": len(response),
                "validation_score": validation_score,
                "sources_cited": sources_cited,
                "timestamp": time.time()
            })
        
        logger.debug(f"Hallucination check for {agent_id}: score={validation_score:.3f}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        uptime = time.time() - self.start_time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        summary = {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "avg_response_time_ms": avg_response_time,
            "p95_response_time_ms": self._calculate_percentile(self.response_times, 0.95),
            "p99_response_time_ms": self._calculate_percentile(self.response_times, 0.99),
            "active_collaborations": len(self.collaboration_metrics),
            "completed_collaborations": len(self.metrics_buffer),
            "agent_count": len(self.agent_metrics),
            "system_health": "healthy" if avg_response_time < 3000 else "degraded"
        }
        
        return summary
    
    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def export_metrics(self, filename: str):
        """Export metrics to JSON file."""
        try:
            export_data = {
                "performance_summary": self.get_performance_summary(),
                "collaboration_metrics": [asdict(m) for m in self.metrics_buffer],
                "agent_metrics": {k: asdict(v) for k, v in self.agent_metrics.items()},
                "system_metrics": [asdict(m) for m in self.system_metrics_history[-100:]],  # Last 100 entries
                "export_timestamp": time.time()
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Metrics exported to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
    
    def cleanup(self):
        """Cleanup monitoring resources."""
        if self.is_wandb_initialized:
            wandb.finish()
        
        logger.info("Monitoring system cleaned up")

# Global monitor instance
monitor = A2AMonitor()

# Decorator for monitoring functions
def monitor_function(func_name: str, agent_id: str = None, agent_type: str = None):
    """
    Decorator to monitor function performance.
    
    Args:
        func_name: Name of the function
        agent_id: Agent identifier
        agent_type: Agent type
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                response_time_ms = (time.time() - start_time) * 1000
                
                if agent_id and agent_type:
                    monitor.log_agent_task(agent_id, agent_type, func_name, response_time_ms, success)
                
                if not success:
                    logger.error(f"Function {func_name} failed: {error}")
        
        return wrapper
    return decorator

# Context manager for collaboration tracking
class CollaborationTracker:
    """Context manager for tracking collaborations."""
    
    def __init__(self, task_id: str, users: List[str]):
        self.task_id = task_id
        self.users = users
        self.collaboration_id = None
    
    def __enter__(self):
        self.collaboration_id = monitor.start_collaboration_tracking(self.task_id, self.users)
        return self.collaboration_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        monitor.end_collaboration_tracking(self.collaboration_id, success, error_message)

if __name__ == "__main__":
    # Example usage
    async def test_monitoring():
        # Test collaboration tracking
        with CollaborationTracker("lunch_planning", ["alice", "bob"]) as collab_id:
            await asyncio.sleep(0.1)  # Simulate work
            monitor.collaboration_metrics[collab_id].consensus_reached = True
            monitor.collaboration_metrics[collab_id].negotiation_rounds = 2
        
        # Test search logging
        monitor.log_restaurant_search("Italian restaurants", 5, 150.5)
        monitor.log_vector_search("similar users", 3, 85.2)
        
        # Test agent task logging
        monitor.log_agent_task("agent-001", "personal", "preference-matching", 120.0, True)
        
        # Test system metrics
        monitor.log_system_metrics(10, 2, "healthy")
        
        # Get performance summary
        summary = monitor.get_performance_summary()
        print("Performance Summary:")
        print(json.dumps(summary, indent=2))
        
        # Export metrics
        monitor.export_metrics("test_metrics.json")
        
        # Cleanup
        monitor.cleanup()
    
    asyncio.run(test_monitoring()) 