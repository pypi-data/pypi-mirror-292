import os
import time
import uuid
import requests

import click
from kubernetes import client
from pkg_resources import resource_filename

from tensorkube.constants import ADDON_NAME, REGION, Events, DEFAULT_NAMESPACE, get_cluster_name, BUILD_TOOL, PodStatus
from tensorkube.constants import get_mount_driver_role_name, get_mount_policy_name, get_base_login_url
from tensorkube.helpers import create_mountpoint_driver_role_with_policy, sanitise_name, sanitise_assumed_role_arn, \
    track_event, extract_command_from_dockerfile, extract_workdir_from_dockerfile, verify_user
from tensorkube.tensorkube_token_server import run_server
from tensorkube.migration_service.migration_manager.migration_service import set_current_cli_version_to_cluster, \
    migrate_tensorkube
from tensorkube.services.aws_service import get_aws_account_id, get_credentials, get_bucket_name, get_aws_user_arn, \
    are_credentials_valid
from tensorkube.services.cloudformation_service import delete_cloudformation_stack, delete_launch_templates, \
    cloudformation
from tensorkube.services.ecr_service import delete_all_tensorkube_ecr_repositories
from tensorkube.services.eks_service import install_karpenter, apply_knative_crds, apply_knative_core, \
    delete_knative_crds, delete_knative_core, delete_karpenter_from_cluster, apply_nvidia_plugin, create_eks_addon, \
    delete_eks_addon, update_eks_kubeconfig
from tensorkube.services.eksctl_service import create_base_tensorkube_cluster_eksctl, delete_cluster
from tensorkube.services.environment_service import create_new_environment, list_environments, delete_environment, \
    check_environment_exists
from tensorkube.services.filesystem_service import cleanup_filesystem_resources, configure_efs
from tensorkube.services.iam_service import create_mountpoint_iam_policy, detach_role_policy, delete_role, delete_policy
from tensorkube.services.istio import check_and_install_istioctl, install_istio_on_cluster, install_net_istio, \
    install_default_domain, remove_domain_server, uninstall_istio_from_cluster
from tensorkube.services.k8s_service import apply_k8s_buildkit_config, create_aws_secret, create_build_pv_and_pvc, \
    find_and_delete_old_job, check_pod_status, start_streaming_pod, start_streaming_service, get_image_tags_to_retain, \
    apply_image_cleanup_job, get_pod_name_corresponing_to_job, get_pod_status_from_job, \
    get_tensorkube_cluster_context_name
from tensorkube.services.karpenter_service import apply_karpenter_configuration
from tensorkube.services.knative_service import enable_knative_selectors_pv_pvc_capabilities, cleanup_knative_resources, \
    delete_knative_services, apply_knative_service_with_podman, apply_virtual_service_for_routing
from tensorkube.services.local_service import check_and_install_cli_tools
from tensorkube.services.logging_service import configure_cloudwatch, teardown_cloudwatch
from tensorkube.services.rich_service import list_tensorkube_deployments, describe_deployment, display_deployment_logs, \
    ssh_into_deployed_service
from tensorkube.services.s3_service import create_s3_bucket, delete_s3_bucket, upload_files_in_parallel, empty_s3_folder


@click.group()
def tensorkube():
    pass


@tensorkube.group()
def list():
    """
    List Tensorkube apps that are currently deployed.
    """
    pass


@tensorkube.group()
def deployment():
    pass


@list.command()
@click.option('--env', default=None, type=str, help='Environment to list the services from.')
@click.option('--all', is_flag=True, help='List all services from all environments.')
@click.option('--old', is_flag=True, help='List older sslip urls for using as hosts if you are on an older version.')
def deployments(env, all, old):
    list_tensorkube_deployments(env_name=env, all=all, old=old)


@tensorkube.command()
def init():
    click.echo("Initializing Tensorfuse runtime for your cloud...")
    # create cloudformation stack
    cloudformation()


@tensorkube.command()
def install_prerequisites():
    check_and_install_cli_tools()


@tensorkube.command()
def upgrade():
    # upgrade karpenter nodepool to the new configuration
    migrate_tensorkube()


@tensorkube.command()
def configure():
    """
    Configure the Tensorkube runtime on your private cloud
    """
    click.echo("Configuring the Tensorfuse runtime for your cloud...")
    start_time = time.time() * 1000
    can_track = track_event(Events.CONFIGURE_START.value, {"start_time": start_time})
    if can_track == False:
        click.echo("You need to login to Tensorfuse to configure Tensorkube.")
        click.echo("Please login using the command: " + click.style("tensorkube login", fg='cyan'))
        return
    check_and_install_cli_tools()
    # TODO!: add helm annotations

    # create cloudformation stack
    cloudformation()
    # create eks cluster
    create_base_tensorkube_cluster_eksctl(cluster_name=get_cluster_name())
    # install karpenter
    install_karpenter()
    # # apply karpenter configuration
    apply_karpenter_configuration()
    configure_cloudwatch()
    #
    # install istio networking plane
    check_and_install_istioctl()
    install_istio_on_cluster()

    # install knative crds
    apply_knative_crds()
    # install knative core
    apply_knative_core()

    # install nvidia plugin
    apply_nvidia_plugin()
    #
    # install net istio
    install_net_istio()
    # install default domain
    install_default_domain()

    # create s3 bucket for build
    bucket_name = get_bucket_name()
    create_s3_bucket(bucket_name)

    # create mountpoint policy to mount bucket to eks cluster
    create_mountpoint_iam_policy(get_mount_policy_name(get_cluster_name()), bucket_name)

    # create s3 csi driver role and attach mountpoint policy to it
    create_mountpoint_driver_role_with_policy(cluster_name=get_cluster_name(), account_no=get_aws_account_id(),
                                              role_name=get_mount_driver_role_name(get_cluster_name()),
                                              policy_name=get_mount_policy_name(get_cluster_name()))

    # create eks addon to mount s3 bucket to eks cluster
    create_eks_addon(get_cluster_name(), ADDON_NAME, get_aws_account_id(),
                     get_mount_driver_role_name(get_cluster_name()))

    # create aws credentials cluster secret
    # TODO!: figure out how to update credentials in case of token expiry
    create_aws_secret(get_credentials())

    # create pv and pvc claims for build
    create_build_pv_and_pvc(bucket_name)

    # update knative to use pod labels
    enable_knative_selectors_pv_pvc_capabilities()
    end_time = time.time() * 1000

    # enable Network files system for the cluster
    click.echo("Configuring EFS for the cluster...")
    configure_efs()

    # set current cli version to the cluster
    set_current_cli_version_to_cluster()

    track_event(Events.CONFIGURE_END.value,
                {"start_time": start_time, "end_time": end_time, "duration": end_time - start_time})
    click.echo("Your tensorfuse cluster is ready and you are good to go.")


@tensorkube.command()
def account():
    """Get the AWS account ID."""
    click.echo(get_aws_account_id())


# The following commands can tear down all the resources that you have created and configured using the CLI.

# uninstall knative
# uninstall istio
# uninstall karpenter
# delete cluster

@tensorkube.command()
def teardown():
    click.echo("Tearing down all resources...")

    # TODO?: add logic to delete any other resources
    click.echo("Deleting all ECR repositories...")
    delete_all_tensorkube_ecr_repositories()

    # delete all services
    try:
        delete_knative_services()
    except Exception as e:
        click.echo("Error while deleting Knative services.")
    try:
        cleanup_filesystem_resources()
    except Exception as e:
        click.echo(f"Error while cleaning up filesystem resources: {e}")

    # EKS addon
    try:
        click.echo("Deleting EKS addon...")
        delete_eks_addon(get_cluster_name(), ADDON_NAME)
    except Exception as e:
        click.echo(f"Error while deleting EKS addon: {e}")

    # teardown cloudwatch
    try:
        teardown_cloudwatch()
    except Exception as e:
        click.echo(f"Error while tearing down Cloudwatch: {e}")

    click.echo("Deleting Enviroments...")
    try:
        environments = list_environments()
        for env in environments:
            click.echo(f"Deleting environment: {env}")
            delete_environment(env_name=env)
    except Exception as e:
        click.echo(f"Error while deleting environments: {e}")

    # Detach policy from role, delete role, delete policy
    click.echo("Deleting mountpoint driver role and policy...")
    click.echo("Detaching policy from role...")
    try:
        detach_role_policy(get_aws_account_id(), get_mount_driver_role_name(get_cluster_name()),
                           get_mount_policy_name(get_cluster_name()))
        click.echo("Deleting role...")
        delete_role(get_mount_driver_role_name(get_cluster_name()))
        click.echo("Deleting policy...")
        delete_policy(get_aws_account_id(), get_mount_policy_name(get_cluster_name()))
    except Exception as e:
        click.echo(f"Error while deleting role and policy: {e}")

    # delete s3 bucket
    click.echo("Deleting S3 bucket...")
    try:
        delete_s3_bucket(get_bucket_name())
    except Exception as e:
        click.echo(f"Error while deleting S3 bucket: {e}")

    click.echo("Uninstalling domain server...")
    try:
        remove_domain_server()
    except Exception as e:
        click.echo(f"Error while uninstalling domain server: {e}")

    click.echo("Uninstalling Knative resources")
    try:
        cleanup_knative_resources()
    except Exception as e:
        click.echo(f"Error while cleaning up Knative resources: {e}")

    click.echo("Uninstalling and deleting Istio resources")
    try:
        uninstall_istio_from_cluster()
    except Exception as e:
        click.echo(f"Error while uninstalling Istio: {e}")
    click.echo("Uninstalling Knative core")
    try:
        delete_knative_core()
        click.echo("Uninstalling Knative CRDs")
        delete_knative_crds()
        click.echo("Successfully uninstalled Knative and Istio.")
    except Exception as e:
        click.echo(f"Error while uninstalling Knative: {e}")

    # remove karpenter
    click.echo("Uninstalling Karpenter...")
    try:
        delete_karpenter_from_cluster()
        click.echo("Successfully uninstalled Karpenter.")
    except Exception as e:
        click.echo(f"Error while uninstalling Karpenter: {e}")
    # delete cluster
    try:
        click.echo("Deleting cluster...")
        delete_cluster()
        click.echo("Successfully deleted cluster.")
    except Exception as e:
        click.echo(f"Error while deleting cluster.: {e}")
    try:
        # delete cloudformation stack
        click.echo("Deleting cloudformation stack...")
        delete_cloudformation_stack(get_cluster_name())
        click.echo("Successfully deleted cloudformation stack.")
    except Exception as e:
        click.echo(f"Error while deleting cloudformation stack: {e}")

    # delete launch templates
    click.echo("Deleting launch templates...")
    delete_launch_templates()
    click.echo("Successfully deleted launch templates.")
    click.echo("Tensorfuse has been successfully disconnected from your cluster.")


@tensorkube.command()
def clear():
    print(delete_cloudformation_stack(get_cluster_name()))


@tensorkube.command()
@click.option('--gpus', default=0, help='Number of GPUs needed for the service.')
@click.option('--gpu-type', type=click.Choice(['V100', 'A10G', 'T4', 'L4'], case_sensitive=False), help='Type of GPU.')
@click.option('--cpu', type=float, default=100, help='Number of CPU millicores. 1000 = 1 CPU')
@click.option('--memory', type=float, default=200, help='Amount of RAM in megabytes.')
@click.option('--min-scale', type=int, default=0, help='Minimum number of pods to run.')
@click.option('--max-scale', type=int, default=3, help='Maximum number of pods to run.')
@click.option('--env', default=None, type=str, help='Environment to deploy the service to.')
def deploy(gpus, gpu_type, cpu, memory, min_scale, max_scale, env):
    """
    Deploy your containerized application on Tensorkube. This command requires
    a dockerfile to be present in the current directory.
    """
    start_time = time.time() * 1000
    can_track = track_event(Events.DEPLOY_START.value, {"start_time": start_time})
    if can_track == False:
        click.echo("You need to login to Tensorfuse to run your deployment.")
        click.echo("Please login using the command: " + click.style("tensorkube login", fg='cyan'))
        return
    if env and not check_environment_exists(env_name=env):
        click.echo("Environment does not exist. Please create the environment first.")
        return
    if gpus not in [0, 1, 4, 8]:
        click.echo('Error: Invalid number of GPUs. Only supported values are 0, 1, 4, and 8.')
        return
    cwd = os.getcwd()
    is_dockerfile_present = False
    for root, dirs, files in os.walk(cwd):
        for file in files:
            local_file = os.path.join(root, file)
            if local_file == cwd + "/Dockerfile":
                is_dockerfile_present = True
    env_namespace = DEFAULT_NAMESPACE if not env else env
    if not is_dockerfile_present:
        click.echo("No Dockerfile found in current directory.")
        return
    else:
        bucket_name = get_bucket_name(env_name=env)
        non_sanitised_name = os.path.basename(cwd)
        sanitised_project_name = sanitise_name(non_sanitised_name)
        build_job_name = f'{BUILD_TOOL}-{sanitised_project_name}'
        old_cleanup_job = 'cleanup-{}'.format(sanitised_project_name)

        old_job_deleted = find_and_delete_old_job(job_name=build_job_name, namespace=env_namespace)
        old_cleanup_job_del = find_and_delete_old_job(job_name=old_cleanup_job, namespace=env_namespace)
        if not old_job_deleted:
            click.echo("Another deployment is already in progress. Please wait for the build to complete.")
            return

        # TODO!: add logic to update the aws-secret only if IAM Identity Center User
        credentials = get_credentials()
        if are_credentials_valid(credentials):
            click.echo("Credentials are up to date")
        else:
            click.echo("The AWS credentials have expired. Please update the credentials.")
            return

        # TODO: figure out how to upload only the updated files to the s3 bucket
        click.echo("Deleting any outdated files in the S3 bucket...")
        empty_s3_folder(bucket_name=bucket_name, folder_name="build/" + sanitised_project_name + "/")

        click.echo("Uploading the current directory to the S3 bucket...")
        upload_files_in_parallel(bucket_name=bucket_name, folder_path=cwd,
                                 s3_path="build/" + sanitised_project_name + "/")

        click.echo("Building the Docker image...")
        image_tag = uuid.uuid4().hex

        apply_k8s_buildkit_config(sanitised_project_name=sanitised_project_name, image_tag=image_tag, env_name=env)
        build_job_pod_name = get_pod_name_corresponing_to_job(job_name=build_job_name, namespace=env_namespace)

        # TODO: stream multiple lines instead of one by one
        start_streaming_pod(pod_name=build_job_pod_name, namespace=env_namespace, status=PodStatus.SUCCEEDED)

        transition_time = time.time()
        # wait for the pod to transition
        while True:
            try:
                pod_status = check_pod_status(pod_name=build_job_pod_name, namespace=env_namespace)
            except client.ApiException as e:
                if e.status == 404:
                    print('Pod not found.')
                    pod_status = get_pod_status_from_job(job_name=build_job_name, namespace=env_namespace)
                else:
                    pod_status = PodStatus.FAILED.value
            print('Waiting for pod to transition')
            if pod_status in ['Succeeded', 'Completed', 'Failed']:
                break
            if time.time() - transition_time > 60:  # 60 seconds have passed
                print("Timeout: Pod did not reach the desired state within 1 minute.")
                break
            time.sleep(5)

        # check for build pod to succeed
        if pod_status == 'Succeeded' or pod_status == 'Completed':
            click.echo("Successfully built and pushed the Docker image.")
            yaml_file_path = resource_filename('tensorkube', 'configurations/build_configs/knative_base_config.yaml')
            dockerfile_path = cwd + "/Dockerfile"
            workdir = extract_workdir_from_dockerfile(dockerfile_path)
            command = extract_command_from_dockerfile(dockerfile_path)
            service_name = f"{sanitised_project_name}-gpus-{gpus}-{str(gpu_type).lower()}"
            apply_knative_service_with_podman(service_name=service_name, yaml_file_path=yaml_file_path,
                                              sanitised_project_name=sanitised_project_name, image_tag=image_tag,
                                              workdir=workdir, command=command, gpus=gpus, gpu_type=gpu_type, cpu=cpu,
                                              memory=memory, min_scale=min_scale, max_scale=max_scale, env=env)
            virtual_service_yaml_file_path = resource_filename('tensorkube',
                                                               'configurations/build_configs/virtual_service.yaml')
            apply_virtual_service_for_routing(service_name=service_name, yaml_file_path=virtual_service_yaml_file_path,
                                              env=env, sanitised_project_name=sanitised_project_name)
            end_time = time.time() * 1000
            click.echo(
                f"The service {service_name} sent for deployment. Waiting for it to become ready. Time taken: {(end_time - start_time) / 1000} ms.")
            images_to_retain = get_image_tags_to_retain(sanitised_project_name=sanitised_project_name,
                                                        service_name=service_name, namespace=env_namespace)
            apply_image_cleanup_job(sanitised_project_name=sanitised_project_name, image_tags=images_to_retain, env=env)
            start_streaming_service(service_name=service_name, namespace=env_namespace)
            track_event(Events.DEPLOY_END.value,
                        {"start_time": start_time, "end_time": end_time, "duration": end_time - start_time})
        else:
            end_time = time.time() * 1000
            track_event(Events.DEPLOY_ERROR.value,
                        {"start_time": start_time, "end_time": end_time, "duration": end_time - start_time})
            click.echo(
                "Failed to build the Docker image. Please check the logs for more details. Pod status: {}".format(
                    pod_status))


@tensorkube.command()
def delete_project():
    click.echo("Deleting the project resources...")
    # TODO!: add logic to delete the ecr repository, s3 folder, build job, and any other resources
    click.echo("Successfully deleted the project resources.")


@tensorkube.command()
def get_permissions_command():
    # TODO: give details of cluster user as well
    click.echo(f"Ask the initial user to run this command to grant you the necessary"
               f" permissions to the {get_cluster_name()} EKS cluster:")

    user_arn = get_aws_user_arn()
    if 'assumed-role' in user_arn:
        final_arn = sanitise_assumed_role_arn(user_arn)
    else:
        final_arn = user_arn

    click.echo("""\
    eksctl create iamidentitymapping \\
    --cluster {} \\
    --region {} \\
    --arn {} \\
    --group system:masters \\
    --username <USERNAME_OF_YOUR_CHOICE>""".format(get_cluster_name(), REGION, final_arn))

    click.echo("Once you have access to the cluster, run the following command to sync the config files:")
    click.echo("tensorkube sync")


@tensorkube.command()
def sync():
    click.echo("Syncing config files for the tensorkube cluster...")
    click.echo("Updating kubeconfig...")
    update_eks_kubeconfig()
    click.echo("Successfully updated the kubeconfig file.")


@deployment.command()
@click.argument('service_name')
@click.option('--env', default=None, type=str, help='Environment to list the services from.')
def describe(service_name, env):
    """Describe a specific deployment..."""
    describe_deployment(service_name=service_name, env_name=env)


@deployment.command()
@click.argument('service_name')
@click.option('--env', default=None, type=str, help='Environment to list the services from.')
def logs(service_name, env):
    """Get logs for a specific deployment..."""
    env_namespace = env if env else DEFAULT_NAMESPACE
    display_deployment_logs(service_name=service_name, namespace=env_namespace)


@deployment.command()
@click.argument('service_name')
@click.option('--env', default=None, type=str, help='Environment to list the services from.')
def ssh(service_name, env):
    """SSH into a specific deployment..."""
    click.echo("SSH into the deployment...")
    env_namespace = env if env else DEFAULT_NAMESPACE
    ssh_into_deployed_service(service_name=service_name, namespace=env_namespace)


# all environment specific commands
@tensorkube.group()
def environment():
    pass


@environment.command()
@click.option('--env-name', help='Name of the environment to create.')
def create(env_name):
    click.echo("Creating a new environment...")
    create_new_environment(env_name=env_name)


@environment.command()
@click.option('--env-name', help='Name of the environment to delete.')
def delete(env_name):
    click.echo("Deleting the environment...")
    delete_environment(env_name=env_name)


@environment.command()
def list():
    environments = list_environments()
    for env in environments:
        click.echo(env)


@tensorkube.command()
def login():
    click.echo("Opening the Tensorfuse dashboard in your default browser...")
    base_url = get_base_login_url()
    click.launch( base_url + "/tensorfuse/login?tensorkube_login=True")
    run_server()


@tensorkube.command()
def test():
    click.echo("Running tests...")
