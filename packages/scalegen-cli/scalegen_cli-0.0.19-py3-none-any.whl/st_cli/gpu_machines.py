from typing import Any, Dict, List, Optional
import click
from rich import box
from rich.console import Console
from rich.table import Table

from .client import send_request

# from .utils import display_event_logs
# from .stop import stop
# from .view import view
# from .launch import launch


@click.group(name="gpu_machines")
def gpu_machines():
    """
    ScaleGen commands for managing fine-tuning deployments
    """
    pass


def get_available_machines(
    gpu_type: Optional[str], num_gpus: Optional[int]
) -> Optional[List[Dict[str, Any]]]:
    response = send_request(
        "GET",
        "/gpu_machines/list_available",
        params={
            "gpu_type": gpu_type,
            "num_gpus": num_gpus or 1 if gpu_type else num_gpus,
        },
    )
    if response.status_code != 200:
        click.echo(f"Error: {response.content.decode('utf-8')}")
        return
    return response.json()


@gpu_machines.command(name="list")
def list_gpu_machines():
    """
    List all GPU machines
    """
    response = send_request("GET", "/gpu_machines")
    gpu_machines = response.json()
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Machine ID", style="dim", width=12)
    table.add_column("Machine Name", style="dim", width=12)
    table.add_column("Machine Type", style="dim", width=12)
    table.add_column("Status", style="dim", width=12)
    table.add_column("Region", style="dim", width=12)
    table.add_column("Created At", style="dim", width=12)
    for gpu_machine in gpu_machines:
        table.add_row(
            gpu_machine["id"],
            gpu_machine["name"],
            gpu_machine["machine_type"],
            gpu_machine["status"],
            gpu_machine["region"],
            gpu_machine["created_at"],
        )
    console.print(table)


@gpu_machines.command(name="list_available")
@click.option("--gpu_type", type=click.STRING, required=False, help="GPU Type to use")
@click.option(
    "--num_gpus", type=click.INT, required=False, help="Number of GPUs to use"
)
@click.option("-p", "--plain", is_flag=True)
def list_available_gpu_machines(
    gpu_type: Optional[str], num_gpus: Optional[int], plain: bool
):

    table = Table(
        show_header=True,
        title="Available GPU Machines",
        box=None if plain else box.DOUBLE_EDGE,
    )

    col_names = [
        "GPU Type",
        "GPU Count",
        "Cloud ID",
        "Cloud Type",
        "Price Per Hour (USD)",
        "Region",
        "Region ID",
        "Memory (GB)",
        "vCPUS",
    ]

    for col in col_names:
        table.add_column(col)

    data = get_available_machines(gpu_type, num_gpus)
    if not data:
        return

    for machine in data:
        # print(set(map(lambda x: x["sg_region"], machine["availability"])))
        # regions_str = ",".join(set(map(lambda x: x["sg_region"], machine["availability"])))

        for region_data in machine["availability"]:

            table.add_row(
                machine["gpu_type"],
                str(machine["num_gpus"]),
                machine["provider_id"],
                machine["cloud"],
                str(machine["hourly_price"]),
                region_data["sg_region"],
                region_data["region"],
                str(machine["memory_in_gb"]),
                str(machine["vcpus"]),
            )

    console = Console()

    if table.row_count <= 15 or plain:
        console.print(table, justify="left")
    else:
        with console.pager():
            console.print(table, justify="left")


@gpu_machines.command(name="create")
@click.option("--gpu_type", type=click.STRING, required=True, help="GPU Type to use")
@click.option("--num_gpus", type=click.INT, required=True, help="Number of GPUs to use")
@click.option("--region", type=click.STRING, required=True, help="Region")
@click.option(
    "--cloud_provider", type=click.STRING, required=True, help="Cloud Provider"
)
@click.option("--hourly_price", type=click.FLOAT, required=True, help="Hourly price")
@click.option(
    "--virtual_mount_name",
    type=click.STRING,
    required=True,
    help="Virtual Mount store name to be used",
)
@click.option(
    "--artifacts_store_name",
    type=click.STRING,
    required=True,
    help="Artifacts Store name to be used",
)
def create_gpu_machine(
    gpu_type: str,
    num_gpus: int,
    region: str,
    cloud_provider: str,
    hourly_price: float,
    virtual_mount_name: str,
    artifacts_store_name: str,
):
    """
    Create a new GPU machine
    """
    if cloud_provider not in ["SCALEGEN_OWN", "SCALEGEN_PARTNER"]:
        click.echo(
            "Error: Invalid cloud provider. cloud provider should be either SCALEGEN_OWN or SCALEGEN_PARTNER",
            err=True,
        )
        return

    # Get available machines and search for the machine with lowest cost with the given specs
    available_machines = get_available_machines(gpu_type, num_gpus)
    if not available_machines:
        return

    available_machines = list(
        filter(lambda x: x["cloud"] == cloud_provider, available_machines)
    )

    payload: Dict[str, Any] = {
        "num_gpus": num_gpus,
        "gpu_type": gpu_type,
        "instance_type": "string",
        "cloud": "string",
        "provider_reference": "string",
        "hourly_price": 0,
        "reference_hourly_price": 0,
        "availability": {"region": "string", "sg_region": "string", "available": True},
        "virtual_mount_name": virtual_mount_name,
        "artifacts_store_name": artifacts_store_name,
    }

    # response = send_request("POST", "/gpu_machines", json={
    #     "gpu_type": gpu_type,
    #     "num_gpus": num_gpus,
    #     "machine_name": machine_name,
    #     "cloud_provider": cloud_provider,
    #     "region": region,
    #     "virtual_mount_name": virtual_mount_name,
    #     "artifacts_store_name": artifacts_store_name
    # })
    # if response.status_code == 201:
    #     click.echo("Machine created successfully")
    # else:
    #     click.echo(f"Error: {response.content.decode('utf-8')}")
