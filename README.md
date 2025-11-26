# Blockchain Product Tracker

# Blockchain Product Tracker (Python + Solidity)

A simple product tracking smart contract and Python backend (Flask + web3.py). This project demonstrates:
- A Solidity contract that stores products and their status history.
- Python scripts to compile & deploy the contract (using `py-solc-x`).
- A small Flask API to create products, add statuses, and read product history.

---

## Repo structure

contracts/
ProductTracker.sol
src/
deploy_contract.py # compile & deploy contract
contract_utils.py # helper to load contract
app.py # Flask API
.env.example
requirements.txt


---

## Prerequisites

- Python 3.9+ (adjust if necessary)
- pip
- Node/Ganache (optional) or access to an Ethereum RPC (Infura, Alchemy, QuickNode)
- If using Ganache (recommended for local dev), download Ganache GUI or `ganache-cli`.

---

## Setup (local - recommended)

1. Clone repo:

git clone <your-repo-url>
cd blockchain-product-tracker
Create & activate virtualenv:

python -m venv venv
source venv/bin/activate    # Linux/macOS

# .\venv\Scripts\activate  # Windows


Install requirements:

pip install -r requirements.txt


Create .env from .env.example and fill values:

cp .env.example .env
# then edit .env and set
# RPC_URL (e.g., http://127.0.0.1:8545 for Ganache)
# PRIVATE_KEY (deployer account private key)
# CHAIN_ID (e.g., 1337 or 5777)


Start Ganache (or ensure RPC_URL is accessible). For Ganache CLI:

ganache-cli --deterministic
# or run Ganache GUI and copy RPC URL


Deploy contract:

python src/deploy_contract.py


This writes src/contract_info.json containing the deployed contract address and ABI.

Run Flask API:

python src/app.py


Example requests:

Create product:

curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"Product A", "manufacturer":"Acme Ltd"}' \
  http://127.0.0.1:5000/create_product


Add status:

curl -X POST -H "Content-Type: application/json" \
  -d '{"productId":1, "status":"Shipped", "location":"Mumbai Warehouse"}' \
  http://127.0.0.1:5000/add_status


Get product:

curl http://127.0.0.1:5000/get_product/1

<img width="1536" height="1024" alt="ChatGPT Image Nov 26, 2025, 11_01_59 AM" src="https://github.com/user-attachments/assets/ff7ea922-a3fd-441c-a2a9-857d512c3172" />
