from eth_account import Account
import secrets  
from web3 import Web3
web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/7dfc896d86f74d9d893df50fcd04024a'))


while True:
    p = secrets.token_hex(32)
    private_key = "0x" + p
    acct = Account.from_key(private_key)
    balance = web3.eth.get_balance(acct.address)
    print(private_key, acct.address, "Balance = "+ str(balance))
    if (balance != 0):
        break 