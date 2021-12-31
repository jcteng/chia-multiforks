
from os import environ
import sys
import inquirer





from multiforks.utils import fork_list
from multiforks import loader
from multiforks.launchers.forkcli import main,get_fork_name


if __name__ == "__main__":   
    if len(sys.argv)>1 and sys.argv[1] in fork_list:        
        environ["CHIA_FORK"]=sys.argv[1]
        sys.argv.pop(1)
    
    main(get_fork_name())
