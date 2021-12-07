from multiforks.launchers import forkcli
from os import environ


def get_fork_name():
    fork_name = "chia-mainnet"
    environ["CHIA_FORK"]= fork_name
    return fork_name


def main(fork_name):
    forkcli.main(fork_name)


if __name__ == "__main__":
     main(get_fork_name())
