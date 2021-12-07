# chia-multiforks

Monkey patch for chia-blockchain to support compatible forks. 

## How it works
chia-multiforks runtime patch chia package for fork-chain's parameters.Such as: root directory, reward policy , network parameters.


## Highlight
1. share use chia's offical code release .
2. only patch fork-chain's parameters
3. More safty, easy to audit code change for each fork-chains. 
4. run testnet7 + mainnet without confliction.

## how to install 
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
## cli commands
python -m multiforks.xxxxcli equal to 'chia command'

```bash
python -m multiforks.ext9cli

Usage: chia show [OPTIONS]

Options:
  -p, --rpc-port INTEGER          Set the port where the Full Node is hosting
                                  the RPC interface. See the rpc_port under
                                  full_node in config.yaml

  -wp, --wallet-rpc-port INTEGER  Set the port where the Wallet is hosting the
                                  RPC interface. See the rpc_port under wallet
                                  in config.yaml

  -s, --state                     Show the current state of the blockchain
  -c, --connections               List nodes connected to this Full Node
  -e, --exit-node                 Shut down the running Full Node
  -a, --add-connection TEXT       Connect to another Full Node by ip:port
  -r, --remove-connection TEXT    Remove a Node by the first 8 characters of
                                  NodeID

  -bh, --block-header-hash-by-height TEXT
                                  Look up a block header hash by block height
  -b, --block-by-header-hash TEXT
                                  Look up a block by block header hash
  -h, --help                      Show this message and exit.
```

## how to use it

1. n-chain ext9 
```bash
python -m multiforks.ext9cli init
python -m multiforks.ext9cli start node 
```

2. flax 
```bash
python -m multiforks.flaxcli init
python -m multiforks.flaxcli start node 
```

3. chia mainnet
```bash
python -m multiforks.chiacli init
python -m multiforks.chiacli start node 
```

4. chia testnet7
```bash
python -m multiforks.chia-testnet7cli init
python -m multiforks.chia-testnet7cli start node 
```

