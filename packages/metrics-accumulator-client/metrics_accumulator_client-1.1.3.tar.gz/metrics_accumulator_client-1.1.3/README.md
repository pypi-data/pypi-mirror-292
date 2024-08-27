<h1 align="center" style="border-bottom: none">
   <img alt="Metrics Accumulator" src="https://apoole-personal-bucket.s3.amazonaws.com/images_used_by_links/github/Logo+for+metrics+Accumulator.svg" width="600"><br>Metrics Accumulator
</h1>


# metrics-accumulator-client
This is the official Python client for [metric accumulator](https://github.com/bpoole6/metrics-accumulator).


## Get Started

Start an instance of metric-accumulator

```bash
docker run \ 
 -p 8080:8080 \ 
 bpoole6/metrics-accumulator
```

It is highly advised that you disable the created metrics. The Metrics accumulator doesn't handle the created metrics at this time.

```python
from prometheus_client import metrics
metrics.disable_created_metrics()
```



Create main.js file
```python
from Client import Client, strip_forward_slash
from prometheus_client import exposition, Counter,Gauge, CollectorRegistry, metrics
metrics.disable_created_metrics()
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
```

Please see [metric accumulator](https://github.com/bpoole6/metrics-accumulator) for official documentation.