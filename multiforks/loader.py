import os
import sys
import subprocess
from importlib import import_module
from pathlib import Path
import pkg_resources

from chia.consensus import block_rewards
from chia.util import default_root
from chia.consensus import default_constants
from chia.cmds import start_funcs

from chia.util import config as util_config
from chia.util.config import load_config, save_config

from typing import Any, Union, Tuple
from chia.daemon import server as daemon_server
from chia.ssl import create_ssl
from chia.util.path import mkdir


def patch_default_seeder_config(root_path: Path, filename="config.yaml") -> None:
    fork_name = os.environ.get("CHIA_FORK")
    if fork_name is None:
        fork_name = 'chia-mainnet'
    """
    Checks if the seeder: section exists in the config. If not, the default seeder settings are appended to the file
    """

    existing_config = load_config(root_path, "config.yaml")

    if "seeder" in existing_config:
        print("Chia Seeder section exists in config. No action required.")
        return

    print("Chia Seeder section does not exist in config. Patching...")
    config = load_config(root_path, "config.yaml")
    # The following ignores root_path when the second param is absolute, which this will be
    seeder_config = load_config(root_path,
                                pkg_resources.resource_filename("multiforks." + fork_name, "initial-config.yaml"))
    print("seeder_config", "multiforks." + fork_name)
    # Patch in the values with anchors, since pyyaml tends to change
    # the anchors to things like id001, etc
    config["seeder"] = seeder_config["seeder"]
    config["seeder"]["network_overrides"] = config["network_overrides"]
    config["seeder"]["selected_network"] = config["selected_network"]
    config["seeder"]["logging"] = config["logging"]

    # When running as crawler, we default to a much lower client timeout
    config["full_node"]["peer_connect_timeout"] = 2

    save_config(root_path, "config.yaml", config)


def initial_config_file(filename: Union[str, Path]) -> str:
    # print("util_config", "multiforks" + ".")
    fork_name = os.environ.get("CHIA_FORK")
    if fork_name is None:
        fork_name = 'chia-mainnet'

    return pkg_resources.resource_string("multiforks." + fork_name, f"initial-{filename}").decode()


def get_chia_ca_crt_key() -> Tuple[Any, Any]:
    fork_name = os.environ.get("CHIA_FORK")
    if fork_name is None:
        fork_name = 'chia-mainnet'

    crt = pkg_resources.resource_string("multiforks." + fork_name + ".ssl", "chia_ca.crt")
    key = pkg_resources.resource_string("multiforks." + fork_name + ".ssl", "chia_ca.key")
    return crt, key


def get_mozilla_ca_crt() -> str:
    fork_name = os.environ.get("CHIA_FORK")
    if fork_name is None:
        fork_name = 'chia-mainnet'

    mozilla_path = Path(__file__).absolute() / (fork_name + "/mozilla-ca/cacert.pem")
    return str(mozilla_path)


def launch_start_daemon(root_path: Path) -> subprocess.Popen:
    os.environ["CHIA_ROOT"] = str(root_path)
    # TODO: use startupinfo=subprocess.DETACHED_PROCESS on windows
    chia = sys.argv[0]
    print("chia args", chia)
    if chia.endswith(".py"):
        chia = sys.executable + " -m multiforks.launchers.forkcli"
    print("chia patched", chia)
    process = subprocess.Popen(f"{chia} run_daemon --wait-for-unlock".split(), shell=True, stdout=subprocess.PIPE)
    return process


def launch_service(root_path: Path, service_command) -> Tuple[subprocess.Popen, Path]:
    """
    Launch a child process.
    """
    # set up CHIA_ROOT
    # invoke correct script
    # save away PID
    print("patched launch_service:", service_command, getattr(sys, "frozen", False))

    # we need to pass on the possibly altered CHIA_ROOT
    os.environ["CHIA_ROOT"] = str(root_path)

    name_map = {
        "chia": "chia",
        "chia_wallet": "start_wallet",
        "chia_full_node": "start_full_node",
        "chia_harvester": "start_harvester",
        "chia_farmer": "start_farmer",
        "chia_introducer": "start_introducer",
        "chia_timelord": "start_timelord",
        "chia_timelord_launcher": "timelord_launcher",
        "chia_full_node_simulator": "start_simulator",
        "chia_seeder": "chia_seeder",
        "chia_seeder_crawler": "chia_seeder_crawler",
        "chia_seeder_dns": "chia_seeder_dns",
    }

    daemon_server.log.debug(f"Launching service with CHIA_ROOT: {os.environ['CHIA_ROOT']}")

    # Insert proper e
    service_array = service_command.split()
    service_executable = name_map[service_array[0]]
    service_array = [sys.executable, "-m", f"multiforks.launchers.{service_executable}"] + service_array[1:]

    if service_command == "chia_full_node_simulator":
        # Set the -D/--connect_to_daemon flag to signify that the child should connect
        # to the daemon to access the keychain
        service_array.append("-D")

    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()  # type: ignore
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore

    # CREATE_NEW_PROCESS_GROUP allows graceful shutdown on windows, by CTRL_BREAK_EVENT signal
    if sys.platform == "win32" or sys.platform == "cygwin":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        creationflags = 0
    environ_copy = os.environ.copy()

    process = subprocess.Popen(
        service_array, shell=False, startupinfo=startupinfo, creationflags=creationflags, env=environ_copy
    )
    pid_path = daemon_server.pid_path_for_service(root_path, service_command)
    try:
        mkdir(pid_path.parent)
        with open(pid_path, "w") as f:
            f.write(f"{process.pid}\n")
    except Exception:
        pass
    print("process, pid_path", process, pid_path)
    return process, pid_path


def get_fork_package(fork_name):
    if fork_name is None:
        fork_name = 'chia-mainnet'
    os.environ["CHIA_FORK"] = fork_name

    print("apply fork patch:" + fork_name)
    try:
        package_root_name = "multiforks" + "." + fork_name + "."

        print('0. monkey patch default_config')
        util_config.initial_config_file = initial_config_file
        try:
            from chia.seeder.util import config as seeder_util_config
            seeder_util_config.patch_default_seeder_config = patch_default_seeder_config
        except ModuleNotFoundError:
            print("older version chia found,skip seeder patching")

        print('1. monkey patch block_rewards_package')
        block_rewards_package = import_module(package_root_name + "block_rewards")
        block_rewards.calculate_base_farmer_reward = block_rewards_package.calculate_base_farmer_reward
        block_rewards.calculate_pool_reward = block_rewards_package.calculate_pool_reward

        print('2. monkey patch default_root')
        default_root_package = import_module(package_root_name + "default_root")
        default_root.DEFAULT_ROOT_PATH = default_root_package.DEFAULT_ROOT_PATH
        default_root.DEFAULT_KEYS_ROOT_PATH = default_root_package.DEFAULT_KEYS_ROOT_PATH

        print('3. monkey patch default_constants')
        default_constants_package = import_module(package_root_name + "default_constants")
        default_constants.DEFAULT_CONSTANTS = default_constants_package.DEFAULT_CONSTANTS
        default_constants.testnet_kwargs = default_constants_package.testnet_kwargs

        print('4. monkey patch start_funcs')
        start_funcs.launch_start_daemon = launch_start_daemon

        print('5. monkey patch ssl cert')
        create_ssl.get_chia_ca_crt_key = get_chia_ca_crt_key
        create_ssl.get_mozilla_ca_crt = get_mozilla_ca_crt

        print("6. monkey patch daemon launcher")
        daemon_server.launch_service = launch_service

    except Exception as e:
        print("Error on loading plugin..." + e)
