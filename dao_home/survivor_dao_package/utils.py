import json
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from .creds import *

def web3_connect(url):

    web3 = Web3(Web3.HTTPProvider(url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    connect_bool = web3.isConnected()

    if connect_bool:
        abi = _load_creds_(web3, contract_abi)
        return {"web3":web3, "connect_bool":connect_bool, "abi":abi}

    else:
        print(f"connect_bool: {connect_bool}")
        return {"web3":web3, "connect_bool":connect_bool}

def _load_creds_(web3, contract_abi):

    # web3.eth.defaultAccount = web3.eth.accounts[0]
    abi = json.loads(contract_abi)

    return abi

def get_contract(web3, abi, address):

    contract = web3.eth.contract(
        address = address, #contract address
        abi = abi
    )
    return contract

def minting(request, Data, Conn, Citizen):

    Data.sender_address = Conn.objects["web3"].eth.defaultAccount

    try:
        Data.tx_receipt = _mintNFT_func_(Conn.objects["web3"], Conn.contract, request.GET.get("name"))
        Citizen.citizen_id = getTokenID_func(Conn.contract, Data.sender_address)
        Citizen.new_citizen = search_citizen(Conn.contract, Citizen.citizen_id)
        return

    except web3.exceptions.ContractLogicError:
        Data.error_mint = "You're already a citizen"

def check_citizenship(request, Data, Conn, Citizen):

    try:
        Data.sender_address = request.GET.get("address")
        Citizen.current_citizen_id = str(getTokenID_func(Conn.contract, Data.sender_address))
        Citizen.current_citizen = Citizen.registry[Citizen.current_citizen_id]

    except web3.exceptions.ContractLogicError:
        Data.error_search = "This address does not have citizenship"
    except (web3.exceptions.InvalidAddress, web3.exceptions.ValidationError):
        Data.error_search = "We couldn't find that address"
    return

def organize_citizens(request, Data, Conn, Citizen):

    all_citizens = get_citizens(Conn.contract)
    for citizen in all_citizens:

        id = all_citizens.index(citizen) + 1
        Citizen.registry[str(id)] = dict(owner = ownerOf_func(Conn.contract, id))
        Citizen.registry[str(id)]["delegatee"] = get_delegates(Conn.contract, Citizen.registry[str(id)]["owner"])
        Citizen.registry[str(id)]["voting_power"] = get_voting_power(Conn.contract, Citizen.registry[str(id)]["owner"])
        Citizen.registry[str(id)]["img"] = img_dispenser(Data, Citizen, id)
        print(Citizen.registry[str(id)]["img"])

        keys = ["name", "rounds", "exiled"]
        for i in range(0, len(citizen)):
            Citizen.registry[str(id)][keys[i]] = citizen[i]

    return Citizen.registry

def _mintNFT_func_(web3, contract, name):
    tx_hash = contract.functions.mintNFT(name).transact()
    tx_receipt = web3.eth.getTransaction(tx_hash)

    return tx_receipt

def _balanceOf_func_(contract, address):
    return contract.functions.balanceOf(Web3.toChecksumAddress(address)).call()

def get_citizens(contract):
    return contract.functions.getCitizens().call()

def total_citizens(contract):
    return contract.functions.totalCitizens().call()

def _last_citizen_(contract):
    return get_citizens(contract)[-1]

def getTokenID_func(contract, address):
    return contract.functions.getTokenIdFromOwner(address).call()
    #minus one because indexes of id's and spot in array are off by one.

def ownerOf_func(contract, id):
    return contract.functions.ownerOf(id).call()

def delegates_func(contract, address):
    return contract.functions.delegates(address).call()

def getVotes_func(contract, address):
    return contract.functions.getVotes(address).call()

def search_citizen(contract, id):
    return contract.functions.citizens(id-1).call()

def name_check(name):
    if name and (len(name) > 1) and (name.isalpha()):
        return True
    else:
        return False

def address_check(address):
    if address and (len(address) == 42):
        return True
    else:
        return False

def get_delegates(contract, address):
    delegatee = contract.functions.delegates(address).call()
    if delegatee == "0x0000000000000000000000000000000000000000":
        return "N/A"
    else:
        return delegatee

def get_voting_power(contract, address):
    return contract.functions.getVotes(address).call()

def img_dispenser(Data, Citizen, id):
    i = id % 5
    print(Data.images)
    return Data.images[i]

def startGame_func(contract, Conn):
    web3 = Conn.objects["web3"]
    transaction = contract.functions.startGame().buildTransaction()
    transaction.update({ 'nonce' : web3.eth.get_transaction_count('0x9751436Dd7A76f7f226a6D60292b495ff8eb2d02') })
    signed_tx = web3.eth.account.sign_transaction(transaction, '<privateKey>')
    txn_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)

def gameStatus_func(contract):
    return contract.functions.gameStarted().call()

def resetGame_func(contract, Conn):
    web3 = Conn.objects["web3"]
    transaction = contract.functions.resetGame().buildTransaction()
    transaction.update({ 'nonce' : web3.eth.get_transaction_count('0x9751436Dd7A76f7f226a6D60292b495ff8eb2d02') })
    signed_tx = web3.eth.account.sign_transaction(transaction, '<privateKey>')
    txn_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
    return txn_receipt
