import web3.eth
from web3 import Web3, AsyncWeb3
from eth_account import Account
from eth_account.signers.local import LocalAccount
import asyncio
from web3.exceptions import InvalidAddress, Web3Exception, TimeExhausted


class Client:
    def __init__(self, private_key: str, rpc_url: str, proxy: str = None):
        self.account: LocalAccount = Account.from_key(private_key)
        self.rpc_url = rpc_url
        self.proxy = proxy
        self.web3 = None

    async def connect_web3(self) -> None:
        try:
            request_kwargs ={
                "proxy": f"http://{self.proxy}"
            } if self.proxy else {}
            self.web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self.rpc_url, request_kwargs))

            if await self.web3.is_connected():
                print("Соеденение установлено.")
            else:
                print("Не удалось установить соеденение.")
            return
        except Exception as e:
            print(f"Ошибка?: {e}")

    async def get_balance(self, address: str):
        try:
            balance_wei = await self.web3.eth.get_balance(self.web3.to_checksum_address(address))
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            return f"{balance_eth}"
        except InvalidAddress:
            print("Указан невалидный адрес!")

    async def send_transaction(self, to: str, value: int|float = 0):

        transaction = {
            'to': AsyncWeb3.to_checksum_address(to),
            'value': self.web3.to_wei(value, 'ether'),
            'gasPrice': int((await self.web3.eth.gas_price) * 1.25),
            'nonce': await self.web3.eth.get_transaction_count(self.account.address),
            'chainId': await self.web3.eth.chain_id
        }
        transaction['gas'] = int((await self.web3.eth.estimate_gas(transaction)) * 1.5)


        signed_tx = self.account.sign_transaction(transaction).raw_transaction
        tx_hash = await self.web3.eth.send_raw_transaction(signed_tx)
        try:
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=240)
            if receipt["status"] == 1:
                print(f"Транзакция отправлена! Хэш транзакции: https://sepolia.etherscan.io/tx/0x{tx_hash.hex()}")
            else:
                print("Ошибка отправки!")
        except TimeExhausted:
            print("Превышено время ожидания транзакции.")

    async def check_sufficient_balance(self, required_eth: int) -> None:
        balance_wei = await self.web3.eth.get_balance(self.account.address)
        required_wei = self.web3.to_wei(required_eth, 'ether')
        if balance_wei < required_wei:
            required_eth = self.web3.from_wei(required_wei, 'ether')
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            error_msg = (f"Недостаточный баланс. Требуется: {required_eth:.3f} ETH, "
                         f"доступно: {balance_eth:.3f} ETH")
            print(error_msg)
            raise Web3Exception(error_msg)