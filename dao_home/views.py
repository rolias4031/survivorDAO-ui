from django.shortcuts import render
from web3 import Web3
import web3
from .survivor_dao_package.utils import *
from .survivor_dao_package.creds import *
from .models import Project

class Conn():
    objects = web3_connect(ganache_url)
    contract = get_contract(objects["web3"], objects["abi"], contract_address)

class Data():
    tx_receipt = None
    sender_address = None
    balance = None
    error_mint = None
    error_search = None
    error_registry = None
    images = Project.objects.all()

    def error_reset(self):
        self.error_mint, self.error_search, self.error_registry = None, None, None

class Citizen():
    citizens = None
    new_citizen = None
    current_citizen = None
    current_citizen_id = None
    #exiled status, name, rounds, id, owner, delegates, voting power
    registry = {}

    def var_reset(self):
        self.current_citizen, self.current_citizen_id, self.new_citizen = None, None, None

# Create your views here.
def survivor_dao(request):

    game_status = gameStatus_func(Conn.contract)
    print(get_citizens(Conn.contract))
    print(game_status)
    Data.error_reset(Data)

    Citizen.registry = organize_citizens(request, Data, Conn, Citizen)
    Citizen.registry["1"]["exiled"]=True

    if request.GET.get("mint_submit") and Conn.objects["connect_bool"]:
        Citizen.var_reset(Citizen)
        if name_check(request.GET.get("name")):
            minting(request, Data, Conn, Citizen)
            Citizen.registry = organize_citizens(request, Data, Conn, Citizen)
        else:
            Data.error_mint = "Enter a valid name"

    elif request.GET.get("check_submit") and Conn.objects["connect_bool"]:
        Citizen.var_reset(Citizen)
        if address_check(request.GET.get("address")):
            check_citizenship(request, Data, Conn, Citizen)
        else:
            Data.error_search = "Enter a valid address to search"

    elif request.GET.get("startGame") and Conn.objects["connect_bool"]:
        startGame_func(Conn.contract, Conn)

    elif request.GET.get("resetGame") and Conn.objects["connect_bool"]:
        resetGame_func(Conn.contract, Conn)

    return render(request, "dao_home/dao_ui.html",
                  {'Data': Data,
                   'Citizen': Citizen,
                   'game_status':game_status
                   }
                  )
