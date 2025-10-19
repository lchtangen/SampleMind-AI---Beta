"""
Monitoring and observability for SampleMind audio processing.

This module provides tools for monitoring the performance and health
of the distributed audio processing pipeline.
"""
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import psutil
from loguru import logger


class MetricType(str, Enum):
    """Types of metrics that can be collected."""
    COUNTER = 'counter'        # A cumulative metric that increases monotonically
    GAUGE = 'gauge'            # A metric that can go up and down
    HISTOGRAM = 'histogram'    # Samples observations into buckets
    SUMMARY = 'summary'        # Similar to histogram but with quantiles


@dataclass
class Metric:
    """Base class for all metrics."""
    name: str
    metric_type: MetricType
    description: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    value: Any = None
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metric to a dictionary."""
        return {
            'name': self.name,
            'type': self.metric_type.value,
            'description': self.description,
            'labels': self.labels,
            'value': self.value,
            'timestamp': self.timestamp,
            'timestamp_iso': datetime.fromtimestamp(self.timestamp).isoformat()
        }


class SystemMetricsCollector:
    """Collects system-level metrics."""
    
    def __init__(self):
        self.process = psutil.Process()
    
    def collect(self) -> List[Metric]:
        """Collect system metrics."""
        metrics = []
        
        # CPU metrics
        cpu_percent = self.process.cpu_percent(interval=0.1)
        metrics.append(Metric(
            name='process_cpu_percent',
            metric_type=MetricType.GAUGE,
            description='CPU usage percentage for the process',
            value=cpu_percent
        ))
        
        # Memory metrics
        mem_info = self.process.memory_info()
        metrics.extend([
            Metric(
                name='process_memory_rss_bytes',
                metric_type=MetricType.GAUGE,
                description='Resident Set Size (RSS) memory in bytes',
                value=mem_info.rss
            ),
            Metric(
                name='process_memory_vms_bytes',
                metric_type=MetricType.GAUGE,
                description='Virtual Memory Size (VMS) in bytes',
                value=mem_info.vms
            )
        ])
        
        # Disk I/O
        try:
            io_counters = self.process.io_counters()
            metrics.extend([
                Metric(
                    name='process_io_read_bytes',
                    metric_type=MetricType.COUNTER,
                    description='Number of bytes read from disk',
                    value=io_counters.read_bytes
                ),
                Metric(
                    name='process_io_write_bytes',
                    metric_type=MetricType.COUNTER,
                    description='Number of bytes written to disk',
                    value=io_counters.write_bytes
                )
            ])
        except (NotImplementedError, AttributeError):
            pass  # Not supported on all platforms
        
        # Thread count
        metrics.append(Metric(
            name='process_threads',
            metric_type=MetricType.GAUGE,
            description='Number of threads used by the process',
            value=self.process.num_threads()
        ))
        
        return metrics


class AudioProcessingMetrics:
    """Collects audio processing specific metrics."""
    
    def __init__(self):
        self._metrics = {}
    
    def record_processing_time(self, file_path: str, duration_seconds: float, 
                             feature_type: str, success: bool = True) -> None:
        """Record the time taken to process an audio file."""
        key = f'audio_processing_duration_seconds{{feature_type="{feature_type}", success="{success}"}}'
        if key not in self._metrics:
            self._metrics[key] = []
        self._metrics[key].append(duration_seconds)
    
    def record_file_size(self, file_path: str, size_bytes: int) -> None:
        """Record the size of a processed audio file."""
        key = f'audio_file_size_bytes{{file="{file_path}"}}'
        self._metrics[key] = size_bytes
    
    def record_feature_extraction(self, feature_type: str, duration_seconds: float) -> None:
        """Record the time taken to extract a specific feature."""
        key = f'feature_extraction_duration_seconds{{feature="{feature_type}"}}'
        if key not in self._metrics:
            self._metrics[key] = []
        self._metrics[key].append(duration_seconds)
    
    def get_metrics(self) -> List[Metric]:
        """Get all collected metrics."""
        metrics = []
        
        for key, values in self._metrics.items():
            # Parse labels from the key if present
            if '{' in key and '}' in key:
                name, label_str = key.split('{', 1)
                label_str = label_str.rstrip('}')
                labels = {}
                for pair in label_str.split(','):
                    k, v = pair.split('=')
                    labels[k.strip()] = v.strip('"\'')
            else:
                name = key
                labels = {}
            
            # Create appropriate metric type
            if isinstance(values, list):
                # For lists, create a histogram
                metrics.append(Metric(
                    name=name,
                    metric_type=MetricType.HISTOGRAM,
                    labels=labels,
                    value={
                        'count': len(values),
                        'sum': sum(values),
                        'avg': sum(values) / len(values) if values else 0,
                        'min': min(values) if values else 0,
                        'max': max(values) if values else 0,
                        'values': values
                    }
                ))
            else:
                # For single values, create a gauge or counter
                metric_type = MetricType.COUNTER if name.endswith('_total') else MetricType.GAUGE
                metrics.append(Metric(
                    name=name,
                    metric_type=metric_type,
                    labels=labels,
                    value=values
                ))
        
        return metrics


class Monitor:
    """Main monitoring class that coordinates metric collection and export."""
    
    def __init__(self, service_name: str = 'samplemind-audio'):
        self.service_name = service_name
        self.system_collector = SystemMetricsCollector()
        self.audio_metrics = AudioProcessingMetrics()
        self.start_time = time.time()
    
    def collect_metrics(self) -> List[Metric]:
        """Collect all metrics from all collectors."""
        metrics = []
        
        # System metrics
        metrics.extend(self.system_collector.collect())
        
        # Audio processing metrics
        metrics.extend(self.audio_metrics.get_metrics())
        
        # Uptime
        metrics.append(Metric(
            name='process_uptime_seconds',
            metric_type=MetricType.GAUGE,
            description='Process uptime in seconds',
            value=time.time() - self.start_time
        ))
        
        # Add service label to all metrics
        for metric in metrics:
            metric.labels['service'] = self.service_name
        
        return metrics
    
    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get all metrics as a dictionary."""
        return {
            'service': self.service_name,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': [m.to_dict() for m in self.collect_metrics()]
        }
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []
        
        for metric in self.collect_metrics():
            # Format metric name and labels
            labels = ','.join(f'{k}="{v}"' for k, v in metric.labels.items())
            metric_name = f'{metric.name}'
            
            if labels:
                metric_name = f'{metric.name}{{{labels}}}'
            
            # Format value based on metric type
            if metric.metric_type == MetricType.HISTOGRAM:
                # For histograms, export multiple metrics
                lines.append(f'# TYPE {metric.name} histogram')
                lines.append(f'{metric.name}_count{{{labels}}} {len(metric.value["values"])}')
                lines.append(f'{metric.name}_sum{{{labels}}} {metric.value["sum"]}')
                lines.append(f'{metric.name}_avg{{{labels}}} {metric.value["avg"]}')
                lines.append(f'{metric.name}_min{{{labels}}} {metric.value["min"]}')
                lines.append(f'{metric.name}_max{{{labels}}} {metric.value["max"]}')
            else:
                # For counters and gauges
                lines.append(f'# TYPE {metric.name} {metric.metric_type.value}')
                lines.append(f'{metric_name} {metric.value}')
        
        return '\n'.join(lines) + '\n'
