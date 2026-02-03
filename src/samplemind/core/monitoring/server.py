"""
Monitoring HTTP server for exposing metrics.

This module provides an HTTP server that exposes metrics in Prometheus format.
"""
import asyncio
import json
import signal
import time
from http import HTTPStatus
from typing import Any, Dict, Optional

from aiohttp import web
from loguru import logger

from .monitor import Monitor


class MonitoringServer:
    """HTTP server for exposing monitoring metrics."""
    
    def __init__(self, monitor: Monitor, host: str = '0.0.0.0', port: int = 8000) -> None:
        """Initialize the monitoring server."""
        self.monitor = monitor
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        
        # Setup routes
        self.app.router.add_get('/metrics', self.handle_metrics)
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/status', self.handle_status)
    
    async def start(self) -> None:
        """Start the monitoring server."""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        # Handle graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
        
        logger.info(f"Monitoring server started at http://{self.host}:{self.port}")
    
    async def stop(self) -> None:
        """Stop the monitoring server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("Monitoring server stopped")
    
    async def handle_metrics(self, request: web.Request) -> web.Response:
        """Handle requests to /metrics endpoint (Prometheus format)."""
        try:
            metrics = self.monitor.export_prometheus()
            return web.Response(
                text=metrics,
                content_type='text/plain; version=0.0.4'
            )
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return web.Response(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                text=f"Error generating metrics: {e}"
            )
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """Handle health check requests."""
        return web.json_response({
            'status': 'ok',
            'timestamp': time.time(),
            'service': self.monitor.service_name,
            'uptime_seconds': time.time() - self.monitor.start_time
        })
    
    async def handle_status(self, request: web.Request) -> web.Response:
        """Handle status requests with detailed metrics."""
        return web.json_response(self.monitor.get_metrics_dict())


def start_monitoring_server(
    monitor: Monitor,
    host: str = '0.0.0.0',
    port: int = 8000,
    run_async: bool = False
) -> Optional[MonitoringServer]:
    """
    Start the monitoring server.
    
    Args:
        monitor: Monitor instance to use
        host: Host to bind to
        port: Port to listen on
        run_async: If True, run the server in a background task
        
    Returns:
        MonitoringServer instance if run_async is False, else None
    """
    server = MonitoringServer(monitor, host=host, port=port)
    
    if run_async:
        # Start the server in a background task
        loop = asyncio.get_event_loop()
        loop.create_task(server.start())
        return None
    else:
        # Run the server in the current event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(server.start())
        return server


def run_standalone(host: str = '0.0.0.0', port: int = 8000) -> None:
    """Run the monitoring server as a standalone application."""
    monitor = Monitor(service_name='samplemind-audio-standalone')
    server = MonitoringServer(monitor, host=host, port=port)
    
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(server.start())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        loop.run_until_complete(server.stop())
        loop.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='SampleMind Monitoring Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    
    args = parser.parse_args()
    run_standalone(host=args.host, port=args.port)
