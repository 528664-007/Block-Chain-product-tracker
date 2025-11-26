import json
import os
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1337"))

def load_contract(web3: Web3, info_path: str = None):
    if info_path is None:
        info_path = Path(__file__).parent / "contract_info.json"
    else:
        info_path = Path(info_path)
    if not info_path.exists():
        raise FileNotFoundError("contract_info.json not found. Deploy the contract first (see deploy_contract.py).")
    info = json.loads(info_path.read_text())
    abi = info["abi"]
    address = info["address"]
    contract = web3.eth.contract(address=web3.to_checksum_address(address), abi=abi)
    return contract

def web3_provider():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise ConnectionError(f"Not connected to RPC at {RPC_URL}")
    return w3
