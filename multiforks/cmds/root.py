import asyncio
from multiforks.utils import fork_list, load_fork_module


from rich.console import Console
from rich.table import Column, Table


def get_fork_default_root(forkname):
    return load_fork_module(forkname+".default_root").DEFAULT_ROOT_PATH

async def show_root():
    console = Console()
    table = Table(show_header=True, header_style="magenta")
    table_columns = ["fork","path"]

    for col in table_columns:
        table.add_column(col)

    for fork in fork_list:        
        table.add_row(fork,str(get_fork_default_root(fork)))

    console.print(table)





if __name__=="__main__":    
    asyncio.run(show_root())