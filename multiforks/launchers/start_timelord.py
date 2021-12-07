

import os
from multiforks import loader

if __name__ == "__main__":
    fork_name = os.environ["CHIA_FORK"]
    print(f"patched launcher {__file__} fork ",fork_name)
    loader.get_fork_package(fork_name)
    from chia.server.start_timelord import main
    main()
