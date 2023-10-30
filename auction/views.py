from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Auction
from .forms import AuctionForm
from django.utils import timezone
import redis
import json
import hashlib
from web3 import Web3

def home_page(request):
    return render(request, 'auction/home_page.html', {})

client = redis.StrictRedis(host='127.0.0.1', port=6379,db=0)


# transaction of the json hash in the blockchain
def sendTransaction(message):
    # ganache data of provider and address
    w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))
    account_to = w3.eth.account.create()
    address_to = account_to.address
    address_from = '0xA6be3a0ec7f9dDC86A1044f148EA18CDE52bceE0'
    private_key_from = '0x0a246f0170365b6248f9100dfb786b4096a05bf27ef9b086fb905e59da043292'
    nonce = w3.eth.get_transaction_count(address_from)
    gasPrice = w3.eth.gas_price
    value = w3.to_wei(0, 'ether')
    signedTx = w3.eth.account.sign_transaction (dict(
        nonce = nonce,
        gasPrice = 20000000000,
        gas = 6721975,
        value = value,
        data = message,
        to = address_to
    ), private_key_from)

    tx = w3.eth.send_raw_transaction(signedTx.rawTransaction)
    txId = w3.to_hex(tx)
    return tx

def auctions(request):
    auctions = Auction.objects.all()
    for auction in auctions:
        client.hsetnx(str(auction.title),"Prezzo", str(auction.current_bid))
        client.hsetnx(str(auction.title),"Id", str(auction.pk))
        file_hash = hashlib.sha256()
        if auction.expiration_date <= timezone.now() :
            expire_auction = Auction.objects.get(pk=auction.pk)
            client.hsetnx(str(auction.title),"Asta", "Terminata")
            dictionary = {
                "Prodotto": client.keys(str(auction.title))[0].decode("utf-8"),
                "Vincitore": client.hget(str(auction.title), "Vincitore").decode("utf-8"),
                "Prezzo": client.hget(str(auction.title), "Prezzo").decode("utf-8"),
                "Id": client.hget(str(auction.title), "Id").decode("utf-8"),
                "Asta": client.hget(str(auction.title), "Asta").decode("utf-8"),
            }

            with open(f"Asta numero {auction.pk}", "w") as outfile:
                json.dump(dictionary, outfile, indent=4)
                file_hash.update(f"Asta numero {auction.pk}".encode('utf-8'))

            # end of the auction and key in redis
            expire_auction.delete()

            file_hash = file_hash.hexdigest()

            w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))

            sendTransaction(file_hash)
            transaction_hash = w3.to_hex(sendTransaction(file_hash))

            client.hsetnx(str(auction.title),"Hash Transazione", str(transaction_hash))

            return redirect ('auctions') 

    return render(request, 'auction/auctions.html', {'auctions': auctions})

def update_bid(request, pk):
    auction = Auction.objects.get(pk=pk)
    if request.method == 'POST':
        last_offer = request.POST['offer']
        file_hash = hashlib.sha256()
        if int(last_offer) >= 250:
            auction.current_bid = last_offer
            auction.save()

            # update price
            client.hset(str(auction.title), "Prezzo", str(auction.current_bid))
            
            # select a winner of the auction
            client.hsetnx(str(auction.title),"Vincitore", str(request.user))
            client.hsetnx(str(auction.title),"Asta", "Terminata")
            
            # dictionary written in json file
            dictionary = {
                "Prodotto": client.keys(str(auction.title))[0].decode("utf-8"),
                "Vincitore": client.hget(str(auction.title), "Vincitore").decode("utf-8"),
                "Prezzo": client.hget(str(auction.title), "Prezzo").decode("utf-8"),
                "Id": client.hget(str(auction.title), "Id").decode("utf-8"),
                "Asta": client.hget(str(auction.title), "Asta").decode("utf-8"),
            }

            with open(f"Asta numero {auction.pk}", "w") as outfile:
                json.dump(dictionary, outfile, indent=4)
                file_hash.update(f"Asta numero {auction.pk}".encode('utf-8'))

            # end of the auction and key in redis
            auction.delete()

            file_hash = file_hash.hexdigest()

            w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))

            transaction_hash = w3.to_hex(sendTransaction(file_hash))

            client.hsetnx(str(auction.title),"Hash Transazione", str(transaction_hash))

            return redirect ('auctions')

        else:
            auction.current_bid = last_offer
            auction.save()
            client.hset(str(auction.title), "Prezzo", str(auction.current_bid))
            client.hsetnx(str(auction.title),"Vincitore", str(request.user))
            return redirect ('auctions')
    else:
        return render(request, 'auction/update_bid.html', {'auction': auction})
