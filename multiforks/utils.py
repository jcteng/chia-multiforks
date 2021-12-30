from multiforks import forks 
from pkgutil import iter_modules

from importlib import import_module
from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.rpc.farmer_rpc_client import FarmerRpcClient
from chia.util.config import load_config
fork_list = list(map(lambda x:x.name, iter_modules(forks.__path__)))

def load_fork_module(forkname):
    return import_module("multiforks.forks."  + forkname )  

def get_fork_default_root(forkname):
    return load_fork_module(forkname+".default_root").DEFAULT_ROOT_PATH

def get_fork_rpc_client_full_node(forkname):
    config = load_config(get_fork_default_root(forkname),"config.yaml")    
    return FullNodeRpcClient.create("localhost",config.get("full_node").get("rpc_port"),root_path=get_fork_default_root(forkname),net_config=config)

def get_fork_rpc_client_farmer(forkname):
    config = load_config(get_fork_default_root(forkname),"config.yaml")    
    return FarmerRpcClient.create("localhost",config.get("farmer").get("rpc_port"),root_path=get_fork_default_root(forkname),net_config=config)
