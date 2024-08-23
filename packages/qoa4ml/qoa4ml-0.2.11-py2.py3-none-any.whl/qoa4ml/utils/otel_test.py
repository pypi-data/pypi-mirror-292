from opentelemetry import metrics
from opentelemetry.instrumentation.system_metrics import SystemMetrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricsExporter

metrics.set_meter_provider(MeterProvider())
exporter = ConsoleMetricsExporter()
SystemMetrics(exporter)

# metrics are collected asynchronously
input("...")

# to configure custom metrics
configuration = {
    "system.memory.usage": ["used", "free", "cached"],
    "system.cpu.time": ["idle", "user", "system", "irq"],
    "system.network.io": ["transmit", "receive"],
    "runtime.memory": ["rss", "vms"],
    "runtime.cpu.time": ["user", "system"],
}
SystemMetrics(exporter, config=configuration)
