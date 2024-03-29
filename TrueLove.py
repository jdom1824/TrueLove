from web3 import Web3
from eth_account import Account 
import secrets 
import time
import json

# Load DeadRingers data from JSON-like string
DeadRingers = [
        "0x7c958c1229a4eb1301b19b8a9623dbe39bdc254b",
        "0x19fc5c4de8b3c861cd27f2d270660fe4105e2c10",
        "0xe3a8ce6195b17685921bcfbfd538b9372faa7c4a",
        "0xb3c6ae35693643eebd199003a0d433a17c6735bf",
        "0x6d8fb34ca8d0678e9199c6c35916c7b9e3a09663",
        "0x24d298fece3ac78bb0e77ddafed77deee302d325",
        "0x9e2b17e13b2f722481b3de0634534b960627ce0e",
        "0x0b56001bf84e7f61beffacf3d41b9897d2a185ea",
        "0xb5173341c9c21138174c4f4057fa32eeb5ec5dce",
        "0xee26b8840a776eb438175a2af90359821417b2a0",
        "0xfc97a98382e18325fd0e9e49fa89ca9d9fc0993b",
        "0x8269467c032b82974ffce5bf9a510eafecd088fe",
        "0xa020c89ef96d1d909047539ac2c7a444b98fbb54",
        "0xf3418b4430816bcf8fbc3ebdac3fdc6fca0af4fc",
        "0x130fb17b898d86047e969fbb321169236c03d494",
        "0x02d1308fc6bcc91c781e5f6d0f7cc34410ae61dd",
        "0xd7e05344a1102f3ed4b8394eef90f0ac698d2b2b",
        "0xb8eee95270e4128bd1b086e6cc77870b479e2bb8",
        "0x78c5b3f378fbfad4e3b5eebaf118236917fe690e",
        "0xd1e19e1b9ef5e80db687870c5b5f2a435155cabc",
        "0x4b264350cb60de8f6f9caecc6aceea3c2f259dde",
        "0x7a8564146674e649aecc2e6bd1b154ace9f3db66",
        "0x25a04ef75e96f5cb00ea8fe03b9353c730680599",
        "0x0099ab99edb52c9fa104a6e54aad4d16b026082e",
        "0x77abac433329ab5bea87498f3c9737a08d3f1334",
        "0xa70fb7e2068eb939d2de59655b1485993023639a",
        "0xd412d7a4732c27073c6659f6a7f6316363f49146",
        "0x63df2ede4cdc25e9daf4cbdfe0d3d3e7530f3b44",
        "0x32d27dd3c78371e838c48288e982a4ec693f107d",
        "0xb4435b4b1b711b66fe3286a34325132832fd7bd7",
        "0x2fa2e2668b4c203927584fa85f2deae437274c4b"
]

counter = 0
elapsed1 = 0

while True:
    t = time.time()
    counter += 1
    private_key = "0x" + secrets.token_hex(32)
    acct = Account.from_key(private_key)
    keyval = acct.address

    # Check if the generated address matches any address in DeadRingers
    if keyval in DeadRingers:
        print(f"Private Key: {private_key}, Address: {acct.address}, Status: LifeRinger")
        break
    else:
        elapsed = time.time() - t
        elapsed1 += elapsed
        elapsed2 = round(elapsed1, 2)
        walletxsecond =  counter / elapsed1
        walletxsecond2 = round(walletxsecond, 2)
        print(f"Iteration: {counter}, Private Key: {private_key}, Address: {acct.address}, Time: {elapsed2}, W/s: {walletxsecond2}")

