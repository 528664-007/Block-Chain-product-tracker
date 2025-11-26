import json
import os
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
import solcx

load_dotenv()

# configs
RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1337"))
CONTRACT_PATH = Path(__file__).parent.parent / "contracts" / "ProductTracker.sol"

# choose solc version (must be compatible)
SOLC_VERSION = "0.8.17"

def compile_contract():
    solcx.install_solc(SOLC_VERSION)
    solcx.set_solc_version(SOLC_VERSION)
    source = CONTRACT_PATH.read_text()

    compiled = solcx.compile_standard({
        "language": "Solidity",
        "sources": {"ProductTracker.sol": {"content": source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        }
    }, allow_paths=str(CONTRACT_PATH.parent))
    contract_interface = compiled["contracts"]["ProductTracker.sol"]["ProductTracker"]
    abi = contract_interface["abi"]
    bytecode = contract_interface["evm"]["bytecode"]["object"]
    return abi, bytecode

def deploy():
    if not PRIVATE_KEY:
        raise RuntimeError("PRIVATE_KEY not set in .env")

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    acct = w3.eth.account.from_key(PRIVATE_KEY)
    abi, bytecode = compile_contract()
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    # build tx
    nonce = w3.eth.get_transaction_count(acct.address)
    transaction = contract.constructor().build_transaction({
        "from": acct.address,
        "nonce": nonce,
        "gas": 6000000,
        "gasPrice": w3.eth.gas_price,
        "chainId": CHAIN_ID
    })

    signed = acct.sign_transaction(transaction)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"Deploying... tx hash: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = receipt.contractAddress
    print("Contract deployed at:", contract_address)

    # Write ABI + address to a local JSON for easier use by Flask client
    out = {
        "address": contract_address,
        "abi": abi
    }
    out_path = Path(__file__).parent / "contract_info.json"
    out_path.write_text(json.dumps(out, indent=2))
    print("Wrote contract_info.json ->", out_path)
    return contract_address, abi

if __name__ == "__main__":
    deploy()
