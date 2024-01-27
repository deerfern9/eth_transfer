import time

from web3 import Web3
from loguru import logger

normal_gwei = 24
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))


def wait_normal_gwei():
    while (gwei_now := w3.from_wei(w3.eth.gas_price, 'gwei')) > normal_gwei:
        logger.debug(f'Gwei({gwei_now}) > max_gwei({normal_gwei}). Sleeping for 17 sec.')
        time.sleep(17)


def send_eth(private, address_to, remainder):
    address_from = w3.eth.account.from_key(private).address

    # gas_price = int(w3.eth.gas_price * 1.1)
    gas_price = w3.eth.gas_price
    print(gas_price)
    balance = w3.eth.get_balance(address_from) - (21000 * gas_price) - w3.to_wei(remainder, 'ether')
    if balance <= 0:
        logger.error(f'{address_from} | Error: Balance too low')
        return
    tx = {
        'from': address_from,
        'to': w3.to_checksum_address(address_to),
        'value': balance,
        'nonce': w3.eth.get_transaction_count(address_from),
        'maxFeePerGas': gas_price,
        'maxPriorityFeePerGas': w3.to_wei(0.1, 'gwei'),
        'gas': 21000,
        'chainId': w3.eth.chain_id
    }

    tx_create = w3.eth.account.sign_transaction(tx, private)
    tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    open('hashes.txt', 'a').write(f'{private};{address_from};{address_to};{tx_hash.hex()}\n')
    logger.success(f"{address_from};{address_to};{tx_hash.hex()}")


def main():
    for line in open('info.txt').readlines():
        private, address_to, remainder = line.strip().split(';')

        try:
            wait_normal_gwei()
            send_eth(private, address_to, remainder)
        except Exception as e:
            logger.exception(e)
            open('errors.txt', 'a').write(f'{private};{address_to};{remainder};{e}')


if __name__ == '__main__':
    main()


