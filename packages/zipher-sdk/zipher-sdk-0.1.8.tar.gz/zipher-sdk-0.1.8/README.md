
# Zipher SDK

The Zipher SDK is a Python library for interacting with Zipher's APIs.

## Installation

You can install the Zipher SDK using pip:

```bash
pip install zipher-sdk
```

## Usage

Here are some basic examples of how you can use the Zipher SDK to optimize your databricks clusters using Zipher's ML-powered optimization engine:

### Update Existing Configuration

You can update an existing configuration by initializing a zipher Client and sending a JSON payload to the `update_existing_conf` function. Here's how you can do it:

```python
from zipher import Client

client = Client(customer_id="my_customer_id")  # assuming the zipher API key is stored in ZIPHER_API_KEY environment variable

# Your existing cluster config:
config_payload = {
    "new_cluster": {
        "autoscale": {
            "min_workers": 1,
            "max_workers": 30
        },
        "cluster_name": "my-cluster",
        "spark_version": "10.4.x-scala2.12",
        "spark_conf": {
            "spark.driver.maxResultSize": "4g"
        },
        "aws_attributes": {
            "first_on_demand": 0,
            "availability": "SPOT",
            "zone_id": "auto",
            "spot_bid_price_percent": 100,
            "ebs_volume_count": 0
        },
        "node_type_id": "rd-fleet.2xlarge",
        "driver_node_type_id": "rd-fleet.xlarge",
        "spark_env_vars": {},
        "enable_elastic_disk": "false"
    }
}

# Update configuration
optimized_cluster = client.update_existing_conf(job_id="my-job-id", existing_conf=config_payload)

# Continue with sending the optimized configuration to Databricks via the Databricks python SDK, Airflow operator, etc.

```
