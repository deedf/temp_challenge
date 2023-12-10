# Room temperature API

## Basics

### Running

* This has been developed and tested on [minikube](https://github.com/kubernetes/minikube).
It should work on GKE, AKS, etc with minimum changes.

* Install `minikube`and make sure it's in your path.
* Install `kubectl`and make sure it's in your path.

Then, this should open the Swagger UI for the API in your browser and let you test the API interactively:

```sh
minikube start
kubectl config use-context minikube
./push.sh
minikube service  -n temp-test api-service
```

This should open the Prometheus UI in your browser and let you view and graph the data, run queries, etc...:

```sh
minikube service  -n temp-test  prometheus-service
```

### Building

The `build.sh` script builds and pushes the API Docker image but you won't have the permission to push to the existing path, you can adapt it in `build.sh` and `config.yaml` if you want.

### Testing

The `unit_test.sh` runs simple unit tests against the API implementation.

## Decisions and choices

### Prometheus

* [Prometheus](https://prometheus.io/) is the industry standard for storing and retrieving time series.
* It runs on kubernetes natively and can scale practically without limits.
* It is cost efficient in terms of storage and computing costs.
* It supports alerting based on rules.
* It is integrated with many tools, for example [Grafana](https://grafana.com/) for dashboarding and graphing.
* To my knowledge there is no equivalent alternative in terms of scaling and cost efficiency.

Since the problem statement required a push model (where the target calls the API to push its data), the [Prometheus push gateway](https://github.com/prometheus/pushgateway) was added to the setup, but the recommended pattern is to use a pull model where Prometheus pulls data from the target.

### FastAPI

* [FastAPI](https://fastapi.tiangolo.com/) is to my knowledge the best existing framework for implementing APIs in Python.
* It automatically generates an OpenAPI definition and a Swagger UI with the minimal amount of configuration.
* It is fully asynchronous, which is the state of the art way of implementing high performance Python APIs.
* It supports automatic validation of parameters.

## Limitations

This is only a small prototype so it has a number of limitations and simplifications

* Data storage: the Prometheus data is stored on the pod's local disk, so it will be lost when the pod is evicted or destroyed. In reality a storage solution like [GCP managed Prometheus](https://cloud.google.com/managed-prometheus?hl=en), [Cortex](https://cortexmetrics.io/) or [Thanos](https://thanos.io/) should be used.
* Simplified k8s config: the prometheus server, push gateway and API server are colocated in the same pod for simplicity. In reality they would have to be separate deployments and services.
* The wiring between the different components is hardcoded, in reality it should be passed in via parameters.
* It uses the `latest` tag to reference Docker images, which is an [antipattern](https://vsupalov.com/docker-latest-tag/). In reality each config file should reference the exact version of the Docker image it needs.
* It does not let the time be explicitly specified and uses the current time for both writing and reading data. In reality the time should be explicitly specifiable, which would allow integration testing by injecting known data and verifying the results. For now the testing is limited to simple unit testing using the `unit_test.sh` script, or manual testing.

## CI/CD

The proposed CI/CD setup would be based on a stack of git branches, like `dev -> test -> preprod -> prod`.

When merging on the `dev` branch, the `unit_test.sh` script should be run by the CI pipeline, and then the `build.sh` script to build a new Docker image with the latest changes.
The `config.yaml` file should be updated in the `dev` branch with the exact tag of this new version.
This should be automatic.

When merging to the next branches in the stack, increasingly extensive integration and manual tests should be done, and then the next branch should be updated with the changes, until we reach `prod`.
