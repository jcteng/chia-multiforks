
from os import environ
import sys
import inquirer





from multiforks.utils import fork_list
from multiforks import loader

def get_fork_name():
    fork_name = environ.get("CHIA_FORK")
    
    if fork_name is None:
        fork_name = inquirer.prompt([inquirer.List('fork',
                message="select fork to run?",
                choices=fork_list,
            )]).get("fork","chia-mainnet")
 
    print("selected fork as=>",fork_name)
    return fork_name


def main(fork_name):        
    loader.get_fork_package(fork_name)
    from chia.cmds import chia

    chia.main()

if __name__ == "__main__":
    
    
    if len(sys.argv)>1 and sys.argv[1] in fork_list:        
        environ["CHIA_FORK"]=sys.argv[1]
        sys.argv.pop(1)
    
    main(get_fork_name())
