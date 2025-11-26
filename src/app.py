import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from web3 import Web3
from contract_utils import web3_provider, load_contract
from eth_account import Account

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1337"))

app = Flask(__name__)

w3 = web3_provider()
acct = Account.from_key(PRIVATE_KEY)
contract = load_contract(w3)

def build_and_send_tx(tx):
    nonce = w3.eth.get_transaction_count(acct.address)
    tx.update({
        "from": acct.address,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "gasPrice": w3.eth.gas_price
    })
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

@app.route("/create_product", methods=["POST"])
def create_product():
    data = request.json or {}
    name = data.get("name")
    manufacturer = data.get("manufacturer", "")
    if not name:
        return jsonify({"error": "name required"}), 400
    tx = contract.functions.createProduct(name, manufacturer).build_transaction({"gas": 300000})
    receipt = build_and_send_tx(tx)
    # get event logs or read contract state: we can parse logs, but easiest is to read productCount
    # The contract emits ProductCreated event - parse logs:
    events = contract.events.ProductCreated().process_receipt(receipt)
    new_id = None
    if events:
        new_id = events[0]["args"]["productId"]
    return jsonify({"tx": receipt.transactionHash.hex(), "productId": new_id})

@app.route("/add_status", methods=["POST"])
def add_status():
    data = request.json or {}
    product_id = data.get("productId")
    status = data.get("status")
    location = data.get("location", "")
    if not product_id or not status:
        return jsonify({"error": "productId and status are required"}), 400
    tx = contract.functions.addStatus(int(product_id), status, location).build_transaction({"gas": 200000})
    receipt = build_and_send_tx(tx)
    events = contract.events.StatusAdded().process_receipt(receipt)
    idx = None
    if events:
        idx = events[0]["args"]["statusIndex"]
    return jsonify({"tx": receipt.transactionHash.hex(), "statusIndex": idx})

@app.route("/get_product/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        info = contract.functions.getProductInfo(product_id).call()
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    pid, name, manufacturer, createdAt, statusCount = info
    statuses = []
    for i in range(statusCount):
        st = contract.functions.getProductStatus(product_id, i).call()
        statuses.append({
            "status": st[0],
            "location": st[1],
            "timestamp": st[2]
        })
    return jsonify({
        "id": pid,
        "name": name,
        "manufacturer": manufacturer,
        "createdAt": createdAt,
        "statusCount": statusCount,
        "statuses": statuses
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "connected": w3.is_connected()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
