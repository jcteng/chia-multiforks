from multiprocessing import freeze_support

from multiforks import loader
import os

if __name__ == "__main__":
    fork_name = os.environ["CHIA_FORK"]
    print(f"patched launcher {__file__} fork ",fork_name)
    loader.get_fork_package(fork_name)
    freeze_support()
    from chia.simulator.start_simulator import main
    main()
