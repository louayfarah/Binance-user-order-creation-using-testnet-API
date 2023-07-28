import sys
import os
import random
from math import ceil

from binance.client import Client
from binance.exceptions import *

from dotenv import load_dotenv

# Load environmental variables in .env file
load_dotenv()

"""
This function receives the frontend data with all entries as str type.
The function checks that all the entries are valid and converts each entry to its logical type.
If one of the entries is incorrect, the function will print an error message and return an empty dictionary.
"""


def refine_data(data):
    # Checking volume
    try:
        data["volume"] = float(data["volume"])
    except TypeError:
        print("The volume entry is invalid.")
        return {}
    # Checking number
    try:
        data["number"] = int(data["number"])
    except TypeError:
        print("The number of orders is invalid.")
        return {}
    # Checking amountDif
    try:
        data["amountDif"] = float(data["amountDif"])
    except TypeError:
        print("The amount difference is invalid.")
        return {}
    # Checking side
    if data["side"] != "SELL" and data["side"] != "BUY":
        print("The trading side is invalid.")
    # Checking the minimum price
    try:
        data["priceMin"] = float(data["priceMin"])
    except TypeError:
        print("The minimum price is invalid.")
        return {}
    # Checking the maximum price
    try:
        data["priceMax"] = float(data["priceMax"])
    except TypeError:
        print("The maximum price is invalid.")
        return {}
    # Checking that the maximum price is greater or equal than the minimum price
    if data["priceMin"] > data["priceMax"]:
        print("The minimum price can not be greater than the maximum price.")
        return {}
    return data


"""
This function receives data from the frontend as a python dictionary
and create orders on the Binance exchange accordingly.
The data dictionary consists of 7 keys: 
"volume", "number", "amountDif", "side", "priceMin", "priceMax", and "tradingPair".
The function will return a message to the user that indicates whether the requests were successfully handled
and describe the error otherwise.
We use spot trading option through a testnet.binance.vision demo account.
"""


def create_orders(data):
    try:
        # API authentication
        binance_api_token = os.getenv("BINANCE_TESTNET_API_KEY")
        binance_api_secret = os.getenv("BINANCE_TESTNET_SECRET_KEY")
        account = Client(binance_api_token, binance_api_secret, testnet=True)
        account.API_URL = "https://testnet.binance.vision/api"
        # Calculating the base volume
        base_volume = data["volume"] / data["number"]
        # Creating the orders
        for request in range(1, data["number"]+1):
            real_volume = ceil(base_volume + ((-1) ** random.randint(1, 2)) * data["amountDif"])
            random_price = ceil(random.uniform(data["priceMin"], data["priceMax"]))
            # Creating the limit order request
            response = account.create_order(symbol=data["tradingPair"], type="LIMIT", timeInForce="GTC",
                                            quantity=real_volume, price=random_price, side=data["side"])
            print(response)
        # Returning a success message
        return "The orders were successfully created!"
    except BinanceOrderException:
        return ("""There was an error when creating the orders. 
        Please, check that the trading pair is valid and that you have enough funding for the orders.""")
    except BinanceAPIException as error:
        return error


# Function testing:

# Reading data from a test file
# The test file must have exactly 7 lines, each containing one of the frontend pieces of information in this order:
# "volume", "number", "amountDif", "side", "priceMin", "priceMax", "tradingPair"
print("Reading the data from the test file...")
f = open("tests/input1.txt", "r")
lines = f.readlines()
f.close()
if len(lines) != 7:  # The data file is invalid or corrupted
    sys.exit("The data file is invalid or corrupted")

# Creating the dictionary as mentioned in the task statement
print("Creating the data dictionary...")
# Removing the line escape in the end of each line
lines = [i[:len(i) - 1] for i in lines]
# Creating the data dictionary
user_data = {
    "volume": lines[0],
    "number": lines[1],
    "amountDif": lines[2],
    "side": lines[3],
    "priceMin": lines[4],
    "priceMax": lines[5],
    "tradingPair": lines[6]
}

# Printing the parameters of the orders request
print("The data dictionary creation was successful! Here is the data received from the frontend:")
for key in user_data.keys():
    print("{} : {}".format(key, user_data[key]))

# Refining data and ensuring that all the user entries are valid
print("Attempt to refine data...")
user_data = refine_data(user_data)
if user_data == {}:
    sys.exit("The orders can not be created due to the error above.")
print("Data dictionary was successfully refined!")

# Creating the orders
print("Creating the orders...")
message = create_orders(user_data)

# Printing the result message
print(message)
