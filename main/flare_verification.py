import asyncio
import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web3 import Web3
from eth_account import Account
import requests


class FlareVerification:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("FLARE_RPC_URL")))
        self.contract_address = os.getenv("CUPID_CONTRACT_ADDRESS")
        self.private_key = os.getenv("PRIVATE_KEY")
        self.account = Account.from_key(self.private_key)

        self.first_voting_round_start_ts = 1658429955
        self.voting_epoch_duration_seconds = 90
        self.jq_verifier_url = os.getenv("JQ_VERIFIER_URL_TESTNET")
        self.da_layer_url = os.getenv("DA_LAYER_URL_COSTON")
        self.jq_api_key = os.getenv("JQ_API_KEY")

    def to_hex(self, data):
        result = "".join(hex(ord(char))[2:].zfill(2) for char in data)
        return result.ljust(64, "0")

    async def prepare_request(self, conversation_data):
        attestation_type = "0x" + self.to_hex("IJsonApi")
        source_type = "0x" + self.to_hex("WEB2")

        request_data = {
            "attestationType": attestation_type,
            "sourceId": source_type,
            "requestBody": {
                "url": conversation_data,
                "postprocessJq": {
                    "match_person_1": ".match_person_1",
                    "match_person_2": ".match_person_2",
                    "compatibility_verdict": ".compatibility_verdict",
                    "compatibility_score": ".compatibility_score",
                    "conversation_id": ".conversation_id",
                    "timestamp": ".timestamp",
                    "conversation_hash": ".conversation_hash",
                },
                "abi_signature": json.dumps(
                    {
                        "components": [
                            {
                                "internalType": "uint256",
                                "name": "match_person_1",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "match_person_2",
                                "type": "uint256",
                            },
                            {
                                "internalType": "string",
                                "name": "compatibility_verdict",
                                "type": "string",
                            },
                            {
                                "internalType": "uint256",
                                "name": "compatibility_score",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "conversation_id",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "timestamp",
                                "type": "uint256",
                            },
                            {
                                "internalType": "bytes32",
                                "name": "conversationHash",
                                "type": "bytes32",
                            },
                        ],
                        "name": "conversation_result",
                        "type": "tuple",
                    }
                ),
            },
        }

        response = requests.post(
            f"{self.jq_verifier_url}JsonApi/prepareRequest",
            headers={"X-API-KEY": self.jq_api_key, "Content-Type": "application/json"},
            json=request_data,
        )
        return response.json()

    async def submit_request(self, request_data):
        contract = self.w3.eth.contract(
            address=self.contract_address, abi=self.get_contract_abi()
        )

        tx = contract.functions.requestAttestation(
            request_data["abiEncodedRequest"]
        ).build_transaction(
            {
                "from": self.account.address,
                "value": self.w3.to_wei(1, "ether"),
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
            }
        )

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        block = self.w3.eth.get_block(receipt["blockNumber"])
        round_id = (
            block["timestamp"] - self.first_voting_round_start_ts
        ) // self.voting_epoch_duration_seconds

        return round_id

    async def get_proof(self, round_id, request_data):
        response = requests.post(
            f"{self.da_layer_url}fdc/get-proof-round-id-bytes",
            headers={"Content-Type": "application/json"},
            json={
                "votingRoundId": round_id,
                "requestBytes": request_data["abiEncodedRequest"],
            },
        )
        return response.json()

    async def submit_proof(self, proof_data):
        contract = self.w3.eth.contract(
            address=self.contract_address, abi=self.get_contract_abi()
        )

        tx = contract.functions.verifyConversation(
            proof_data["proof"], proof_data["response"]
        ).build_transaction(
            {
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
            }
        )

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return receipt
