from multiforks import loader
from os import environ
import sys

def get_fork_name():
    fork_name = environ.get("CHIA_FORK")
    if fork_name is None:
        fork_name = "chia-mainnet"
    return fork_name


def main(fork_name):
    print(sys.argv)
    loader.get_fork_package(fork_name)
    from chia.cmds import chia

    chia.main()



if __name__ == "__main__":
     main(get_fork_name())
