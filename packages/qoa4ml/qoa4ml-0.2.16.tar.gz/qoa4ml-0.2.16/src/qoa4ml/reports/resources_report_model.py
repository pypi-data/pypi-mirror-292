from __future__ import annotations

from pydantic import BaseModel


class ProcessMetadata(BaseModel):
    pid: str
    user: str


class SystemMetadata(BaseModel):
    node_name: str
    model: str | None = None


class ResourceReport(BaseModel):
    metadata: dict | None = None
    usage: dict


class ProcessReport(BaseModel):
    metadata: ProcessMetadata
    timestamp: float
    cpu: ResourceReport
    gpu: ResourceReport | None = None
    mem: ResourceReport


class SystemReport(BaseModel):
    metadata: SystemMetadata
    timestamp: float
    cpu: ResourceReport
    gpu: ResourceReport | None = None
    mem: ResourceReport


class DockerContainerMetadata(BaseModel):
    id: str
    image: str


class DockerContainerReport(BaseModel):
    metadata: DockerContainerMetadata
    timestamp: float
    cpu: ResourceReport
    gpu: ResourceReport | None = None
    mem: ResourceReport
