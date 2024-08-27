#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from datetime import datetime
from typing import Any, Dict, List

from fragment.calculations.models import JobStatus

from .common import FragmentBaseModel


class Registration(FragmentBaseModel):
    hostname: str
    cores: int
    info: Dict[str, Any]


class ServerConfig(FragmentBaseModel):
    # Connection info
    hostname: str = "localhost"  # How workers will see the server
    bind_to: str = "0.0.0.0"  # Address requested by the server
    port: int = 8000

    # Paths
    basepath: str

    # Logging
    log_level: str = "INFO"
    uvicorn_log_level: str = "WARNING"

    # Shared worker conf
    heartbeat_freq: int = 5
    heartbeat_skips = 3
    status_poll_freq: float = 0.5

    # App timeouts
    workerless_timeout: int = 30
    server_startup_timeout: int = 30
    server_shutdown_timeout: int = 30
    server_unreachable_timeout: int = 30

    # Queue configuration
    rerun_failed: bool = False
    batch_queue_size: int = 5
    batch_size: int = 1
    batch_size_min: int = 1
    batch_size_max: int = 50


class WorkerAssignment(FragmentBaseModel):
    id: int
    name: str
    server_config: ServerConfig


class WorkerStatus(FragmentBaseModel):
    id: int
    hostname: str
    last_seen: datetime
    got: int
    reported: int

    # Maybe keep track of job stats?


class ServerStatus(FragmentBaseModel):
    jobs: Dict[JobStatus, int]
    workers: List[WorkerStatus]
    batch_size: int
    jobs_prepaired: int
    batch_queue_items: int
    jobs_reported: int
    report_queue_items: int
    async_queue_length: int

    work_done: bool


class ServerState(FragmentBaseModel):
    """A more abreviated version of the status"""

    work_done: bool
    active_workers: int
    jobs_prepaired: int
    jobs_reported: int
