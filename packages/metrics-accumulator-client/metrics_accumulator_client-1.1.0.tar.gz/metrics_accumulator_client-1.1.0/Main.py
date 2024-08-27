from Client import Client, strip_forward_slash
from prometheus_client import exposition, Counter,Gauge, CollectorRegistry
registry = CollectorRegistry()
c = Counter("hello_total", "dock", labelnames=['application'], registry=registry)
c.labels(["app"]).inc()

g = Gauge("man", "dock", labelnames=['application'], registry=registry)
g.labels(["app"]).inc()

client = Client("http://localhost:8080", "0d98f65f-074b-4d56-b834-576e15a3bfa5")
client.update_metrics("default", registry)
print(client.get_metric_group("default").content.decode())
print(client.reload_configurations().status_code)
print(client.reset_metric_group("default").status_code)
print(client.service_discovery().status_code)
print(client.current_configurations().status_code)