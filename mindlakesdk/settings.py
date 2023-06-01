GATEWAY = 'http://sdk.mindnetwork.xyz/node'
WEB3API = 'https://goerli.infura.io/v3/744c0ade89464e4b867ca1b002a10231'
CONTRACT_ADDRESS = '0xF5932e67e84F08965DC6D62C2B67f47a6826E5a7'
CONTRACT_ABI = [
        {
                "anonymous": False,
                "inputs": [
                        {
                                "indexed": True,
                                "internalType": "address",
                                "name": "wallet",
                                "type": "address"
                        },
                        {
                                "indexed": False,
                                "internalType": "bytes",
                                "name": "MK",
                                "type": "bytes"
                        },
                        {
                                "indexed": False,
                                "internalType": "bytes",
                                "name": "SK",
                                "type": "bytes"
                        }
                ],
                "name": "KeysUpdated",
                "type": "event"
        },
        {
                "inputs": [
                        {
                                "internalType": "bytes",
                                "name": "_mk",
                                "type": "bytes"
                        },
                        {
                                "internalType": "bytes",
                                "name": "_sk",
                                "type": "bytes"
                        }
                ],
                "name": "setKeys",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
        },
        {
                "inputs": [
                        {
                                "internalType": "address",
                                "name": "_wallet",
                                "type": "address"
                        }
                ],
                "name": "getKeys",
                "outputs": [
                        {
                                "internalType": "bytes",
                                "name": "MK",
                                "type": "bytes"
                        },
                        {
                                "internalType": "bytes",
                                "name": "SK",
                                "type": "bytes"
                        }
                ],
                "stateMutability": "view",
                "type": "function"
        }
]
VERSION = 'v1.0.0'