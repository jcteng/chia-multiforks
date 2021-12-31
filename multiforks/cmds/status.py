import asyncio

from typing import final
from chia.rpc.farmer_rpc_client import FarmerRpcClient
from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.rpc.rpc_client import RpcClient

from chia.util.ws_message import create_payload_dict
from multiforks.utils import fork_list, get_fork_default_root, get_fork_rpc_client_farmer,  get_fork_rpc_client_full_node


from rich.console import Console
from rich.table import Column, Table
import os
import psutil
from rich.live import Live

import humanize
import time


def get_fork_pid_service(forkname, service_name):
    full_name = "chia_"+service_name+".pid"
    try:
        with open(os.path.join(get_fork_default_root(forkname), "run", full_name)) as f:
            return "running" if psutil.pid_exists(int(f.read())) else "stopped"
    except FileNotFoundError:
        return "stopped"


async def generate_table() -> Table:
    table = Table(show_header=True, header_style="magenta")
    table_columns = ["fork", "full_node",
                     "wallet", "farmer", "harvester", "height", "weight", "conn", "diff", "space", "syncd", "plots","plot_size"]

    for col in table_columns:
        table.add_column(col)

    for fork in fork_list:
        height = ""
        weight = ""
        conn_number = ""
        diff = ""
        space = ""
        sync = ""
        plots = ""
        plots_size = ""
        # print(get_fork_default_root(fork))
        if "running" == get_fork_pid_service(fork, "full_node"):
            ws_rpc_full_node: FullNodeRpcClient = await get_fork_rpc_client_full_node(fork)
            try:
                conn_number = len(await ws_rpc_full_node.get_connections())
                bs = (await ws_rpc_full_node.get_blockchain_state())
                diff = bs.get("difficulty", "")
                if bs.get("peak", None) != None:
                    height = str(bs.get("peak").height)
                    weight = humanize.naturalsize(bs.get("peak").weight)

                space = humanize.naturalsize(
                    bs.get("space", 0), binary=True, format="%.3f")
                sync = bs.get("sync", {"synced": False}).get("synced")
                ws_rpc_full_node.close()
            except Exception as e:
                print(e)
                pass
        if "running" == get_fork_pid_service(fork, "farmer"):
            ws_rpc_farmer: FarmerRpcClient = await get_fork_rpc_client_farmer(fork)
            try:
                havesters = await ws_rpc_farmer.get_harvesters()
                plots = str(
                    sum(
                        list(
                            map(lambda x: len(x["plots"]), havesters.get("harvesters")
                                )
                        )
                    )
                )

                plots_size = humanize.naturalsize(
                    sum(
                        list(
                            map(lambda x: sum(list(map(lambda y: y["file_size"], x["plots"]))), havesters.get("harvesters")
                                )
                        )
                    ), binary=True)
                # sync = bs.get("sync",{"synced":False}).get("synced")
                ws_rpc_farmer.close()
            except Exception as e:
                print(e)
                pass
        table.add_row(fork,
                      get_fork_pid_service(fork, "full_node"),
                      get_fork_pid_service(fork, "wallet"),
                      get_fork_pid_service(fork, "farmer"),
                      get_fork_pid_service(fork, "harvester"),
                      height,
                      weight,
                      str(conn_number),
                      str(diff),
                      space,
                      str(sync),
                      plots,
                      plots_size
                      )
    return table


async def show_status():
    Console().print(await generate_table())


if __name__ == "__main__":
    asyncio.run(show_status())
