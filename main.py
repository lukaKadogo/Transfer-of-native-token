import asyncio
from web3 import Web3, AsyncWeb3, AsyncHTTPProvider, HTTPProvider
from client import Client

address_out = input("Введите адрес отправителя: ")
private_key = input("Введите приватный ключ отправителя: ")
address_in = input("Введите адрес получателя:  ")
amount_eth = input("Введите количество для отправки (ETH): ")

rpc_url = "https://ethereum-sepolia-rpc.publicnode.com"



async def main():
    client = Client(private_key, rpc_url)
    await client.connect_web3()
    balance_client1 = await client.get_balance(address_out)
    print(f"Баланс отправителя до: {float(balance_client1):.5f}")
    balance_client2 = await client.get_balance(address_in)
    print(f"Баланс получателя до: {float(balance_client2):.5f}")
    await client.check_sufficient_balance(amount_eth)
    await client.send_transaction(address_in, amount_eth)
    balance_client1 = await client.get_balance(address_out)
    print(f"Баланс отправителя после: {float(balance_client1):.5f}")
    balance_client2 = await client.get_balance(address_in)
    print(f"Баланс получателя после: {float(balance_client2):.5f}")

if __name__ == "__main__":
    asyncio.run(main())




