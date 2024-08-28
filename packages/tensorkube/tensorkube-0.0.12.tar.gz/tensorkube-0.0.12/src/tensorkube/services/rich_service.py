from typing import Optional

import click
import inquirer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from tensorkube.constants import DEFAULT_NAMESPACE
from tensorkube.services.k8s_service import start_streaming_pod, ssh_into_pod_with_podman
from tensorkube.services.knative_service import list_deployed_services, get_knative_service, get_ready_condition, \
    get_pods_for_service, get_istio_ingress_gateway_hostname


def list_tensorkube_deployments(env_name: Optional[str] = None, all: bool = False, old: bool = False):
    table = Table(title="Tensorkube Deployments")
    table.add_column("Name", style="magenta", no_wrap=True)
    table.add_column("URL", style="cyan", no_wrap=True)
    table.add_column("Latest Ready", style="green", no_wrap=False, overflow="fold")
    table.add_column("Ready", no_wrap=False, overflow="fold")
    table.add_column("Env", no_wrap=False, overflow="fold")
    table.add_column("Reason", no_wrap=False, overflow="fold")

    elb_url = get_istio_ingress_gateway_hostname()

    deployed_services = list_deployed_services(env_name=env_name, all=all)
    if not deployed_services:
        return
    services = deployed_services['items']
    for service in services:
        ready_condition = get_ready_condition(service)
        if 'latestReadyRevisionName' in service['status']:
            latest_ready_revision = service['status']['latestReadyRevisionName'][-4:]
        else:
            latest_ready_revision = "N/A"
        if old:
            service_url = service['status']['url']
        else:
            service_url = f'http://{elb_url}/svc/{service["metadata"]["namespace"]}/{service["metadata"]["name"]}/'
        table.add_row(service['metadata']['name'], service_url, latest_ready_revision, ready_condition['status'],
                      service['metadata']['namespace'], ready_condition.get('reason', None))

    console = Console()
    console.print(table)


def describe_deployment(service_name: str, env_name: Optional[str] = None):
    env_namespace = env_name if env_name else DEFAULT_NAMESPACE
    deployment = get_knative_service(service_name=service_name, namespace=env_namespace)
    ready_condition = get_ready_condition(deployment)

    if ready_condition['status'] == 'True':
        ready_status_color = "green"
    elif ready_condition['status'] == 'False':
        ready_status_color = "red"
    else:
        ready_status_color = "yellow"
    tree = Tree("[bold][bright_magenta]" + service_name)
    tree.add("[bold]URL:[/] [cyan]" + deployment['status']['url'])
    tree.add("[bold]Latest Created Revision:[/] " + deployment['status']['latestCreatedRevisionName'])
    tree.add("[bold]Latest Ready Revision:[/] [green]" + deployment['status']['latestReadyRevisionName'])
    tree.add(f"[bold]Ready Status:[/] [{ready_status_color}]" + ready_condition['status'])
    tree.add("[bold]Reason:[/] " + deployment['status']['conditions'][0].get('reason', ""))
    tree.add("[bold]Last Deployed At:[/] " + deployment['spec']['template']['metadata']['annotations']['deploy_time'])
    console = Console()
    console.print(tree)


def display_deployment_logs(service_name: str, namespace: str = "default"):
    services_in_namespaces = list_deployed_services(env_name=namespace)['items']
    # check if the service name is present in the namespace
    if service_name not in [service['metadata']['name'] for service in services_in_namespaces]:
        click.echo(f"Service {service_name} not found in environment {namespace}")
        return
    service_pods = get_pods_for_service(service_name=service_name, namespace=namespace)
    if len(service_pods.items) == 0:
        click.echo(f"No active pods found for service {service_name}.")
        return
    elif len(service_pods.items) == 1:
        pod_name = service_pods.items[0].metadata.name
    else:
        click.echo(f"Multiple pods found for service {service_name}. Please specify a pod name.")
        questions = [inquirer.List('pod', message="Please select a pod",
                                   choices=[pod.metadata.name for pod in service_pods.items], ), ]
        pod_name = inquirer.prompt(questions)['pod']

    start_streaming_pod(pod_name=pod_name, namespace=namespace, container_name="user-container")


def ssh_into_deployed_service(service_name: str, namespace: str = "default"):
    services_in_namespaces = list_deployed_services(env_name=namespace)['items']
    # check if the service name is present in the namespace
    if service_name not in [service['metadata']['name'] for service in services_in_namespaces]:
        click.echo(f"Service {service_name} not found in environment {namespace}")
        return
    service_pods = get_pods_for_service(service_name=service_name, namespace=namespace)
    if len(service_pods.items) == 0:
        click.echo(f"No pods found for service {service_name}")
        return
    elif len(service_pods.items) == 1:
        pod_name = service_pods.items[0].metadata.name
    else:
        click.echo(f"Multiple pods found for service {service_name}. Please specify a pod name.")
        questions = [inquirer.List('pod', message="Please select a pod",
                                   choices=[pod.metadata.name for pod in service_pods.items], ), ]
        pod_name = inquirer.prompt(questions)['pod']

    click.echo(f"SSHing into pod: {pod_name}")
    ssh_into_pod_with_podman(pod_name=pod_name, namespace=namespace)
