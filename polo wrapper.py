# poloniex api wrapper
# based on the pastebin given by polo in the api page
# poloniex is a bitcoin / altcoin exchange that was founded by a guy who studied classical music at uni
# then he tried to make a living composing stuff for orchestra and writing fiction
# then that failed so he decided to create a bitcoin / altcoin cryptocurrency exchange with zero coding experience
# somehow it made its way to become the biggest altcoin exchange in the world after the death of cryptsy
# interface and API are good, but it has the shittiest servers in the entire history of the observable universe, even worse than mtgox

# this thing puts a buy or sell order along a line of your choice and moves it along the line
# trading along a line is a common thing in technical analysis of price markets
# this supposedly lets you do it automatically

# polo's servers are so crappy it'd be faster for them to trade by physically mailing crypto paper wallets to and from their office instead

# TODO:
# market buy when price moves above a line
# market sell when price moves below a line
# trade (limit buy/sell) on a line when price moves above or below (respectively) a different line

import urllib, urllib2, json, time, hmac, hashlib
from datetime import datetime

key = raw_input('key? ')

secret = raw_input('secret? ')

# really should put all this in a class if i want to do more with it

def ticker(coin): # example of a public command
    thing = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=returnTicker'))
    return json.loads(thing.read())['BTC_'+coin]

def balances():
    complete=query('returnCompleteBalances', {'account': 'all'})
    print 'coin | available | btc value'
    for i in complete:
        if i=='USDT' or float(complete[i]['btcValue'])>0:
            print i, complete[i]['available'], complete[i]['btcValue']


# trading-enabled API commands
# i have no idea what any of this means, it's mainly copied from the pastebin. the hell is a hexdigest? it sounds like a biscuit
# need to learn this stuff
def query(command, stuff={}):
    stuff['command']=command
    stuff['nonce']=int(time.time()*1000)
    sign=hmac.new(secret, urllib.urlencode(stuff), hashlib.sha512).hexdigest()
    something = {'Sign': sign, 'Key': key}
    thing = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi', urllib.urlencode(stuff), something))
    return json.loads(thing.read())

# football really needs video technology everywhere, not just goal-line

def buy(currency, rate, amount):
    order = query('buy', {'currencyPair': 'BTC_'+currency, 'rate': rate, 'amount': amount})
    if 'orderNumber' in order:
        print 'Placed buy order for', amount, currency, 'at', rate
        return order['orderNumber']
    else:
        print order
        return False

def sell(currency, rate, amount):
    order = query('sell', {'currencyPair': 'BTC_'+currency, 'rate': rate, 'amount': amount})
    if 'orderNumber' in order:
        print 'Placed sell order for', amount, currency, 'at', rate
        return order['orderNumber']
    else:
        print order
        return False

def cancel(ordernumber):
    thingy = query('cancelOrder', {'orderNumber': ordernumber})
    if thingy['success']==1:
        print 'Successfully cancelled order', ordernumber
        return True
    else:
        print thingy
        return False

def move(ordernumber, rate):
    thing = query('moveOrder', {'orderNumber': ordernumber, 'rate': rate})
    if thing['success']==1:
        print 'Successfully moved order to', rate
        return thing['orderNumber']
    else:
        if 'error' in thing:
            print thing['error']
        return False

def datetime_to_unix(d):
    return int(time.mktime(d.timetuple()))

def kangaroo(apples, bananas, cherries, dragonfruits): # returns step per second you need to move the line
    return float(dragonfruits - bananas) / (datetime_to_unix(cherries) - datetime_to_unix(apples))

def movingbuy(currency, amount, apples, bananas, cherries, dragonfruits, timeinterval=60, iterations=4): # places a buy order that moves along a line
    panda = kangaroo(apples, bananas, cherries, dragonfruits)
    my_head_hurts = int(time.time())
    hamster = my_head_hurts - datetime_to_unix(cherries) # time diff since cherries
    santa_claus = panda*hamster + dragonfruits # current rate
    life=0
    ordernumber = buy(currency, santa_claus, amount)
    while life!=int(iterations): # could use for loop, but still want to have -1 for "unlimited"
        time.sleep(timeinterval)
        santa_claus += panda*timeinterval
        try:
            ordernumber = move(ordernumber, santa_claus)
        except:
            print 'oops: something happened' # this shouldn't happen
            return
        if not ordernumber:
            print 'order got filled (yay?) or there was an error. I don\'t know which'
            return
        life+=1
    # last iteration
    time.sleep(timeinterval)
    cancel(ordernumber)
    return

def movingbuyinput(): # same as above but takes parameters as raw inputs
    currency=raw_input('currency name? ').upper()
    amount=float(raw_input('amount of '+currency+'? '))
    apples=eval('datetime('+raw_input('date and time of 1st point (comma separated)? ')+')')
    bananas=float(raw_input('price of 1st point? '))
    cherries=eval('datetime('+raw_input('date and time of 2nd point (comma separated)? ')+')')
    dragonfruits=float(raw_input('price of 2nd point? '))
    timeinterval=int(raw_input('time interval between price retarget (seconds)? '))
    iterations=int(raw_input('number of retargets (set -1 for never-ending)? '))
    movingbuy(currency, amount, apples, bananas, cherries, dragonfruits, timeinterval, iterations)

# testing
"""
>>> movingbuyinput()
currency name? dash
amount of DASH? 0.01
date and time of 1st point (comma separated)? 2017,4,10,20,30
price of 1st point? 0.03
date and time of 2nd point (comma separated)? 2017,4,10,20,40
price of 2nd point? 0.04
time interval between price retarget (seconds)? 60
number of retargets (set -1 for never-ending)? 10
Placed buy order for 0.01 DASH at 0.05145
Successfully moved order to 0.05245
Successfully moved order to 0.05345
Invalid order number, or you are not the person who placed the order.
order got filled (yay?) or there was an error. I don't know which
>>>
"""

# i sold 32000 gamecredits in 2014 for 0.06btc (about £15 back then)
# today they'd be worth about 20btc (about £27000)
# i hate this game
