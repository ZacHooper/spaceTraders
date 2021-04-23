import requests
import logging
import json


URL = "https://api.spacetraders.io/"
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def make_request(method, url, headers, params):
    """Checks which method to use and then makes the actual request to Space Traders API

    Args:
        method (str): The HTTP method to use
        url (str): The URL of the request
        headers (dict): the request headers holding the Auth
        params (dict): parameters of the request

    Returns:
        Request: Returns the request

    Exceptions:
        Exception: Invalid method - must be GET, POST or PUT
    """
    # Define the different HTTP methods
    methods = {
        "POST": requests.post(url, headers=headers, params=params),
        "GET": requests.get(url, headers=headers, params=params),
        "PUT": requests.put(url, headers=headers, params=params),
        "DELETE": requests.delete(url, headers=headers, params=params)
    }

    # If an Invalid method provided throw exception
    if method not in methods:
        logging.exception(f'Invalid method provided: {method}')

    return methods[method]   

def get_user_token(username):
    """Trys to create a new user and return their token

    Args:
        username (str): Username to user

    Returns:
        str: Token if user valid else None
    """
    url = f"https://api.spacetraders.io/users/{username}/loans"
    try:
        res = make_request("POST", url, None, None)
        if res.ok:
            return res.json()['token']
        else:
            logging.exception(f"Code: {res.json()['error']['code']}, Message: {res.json()['error']['message']}")
            return None
    except Exception as e:
        return e

class Client ():
    def __init__(self, username, token=None):
        """The Client class handles all user interaction with the Space Traders API. 
        The class is initiated with the username and token of the user. 
        If the user does not provide a token the 'create_user' method will attempt to fire and create a user with the username provided. 
        If a user with the name already exists an exception will fire. 

        Args:
            username (str): Username of the user
            token ([type]): The personal auth token for the user. If None will invoke the 'create_user' method
        """
        self.username = username
        self.token = token

    def generic_api_call(self, method, endpoint, params=None, token=None, warning_log=None):
        """Function to make consolidate parameters to make an API call to the Space Traders API. 
        Handles any throttling or error returned by the Space Traders API. 

        Args:
            method (str): The HTTP method to use. GET, POST, PUT or DELETE
            endpoint (str): The API endpoint
            params (dict, optional): Any params required for the endpoint. Defaults to None.
            token (str, optional): The token of the user. Defaults to None.

        Returns:
            Any: depends on the return from the API but likely JSON
        """
        headers = {'Authorization': 'Bearer ' + token}
        # Make the request to the Space Traders API
        try:
            r = make_request(method, URL + endpoint, headers, params) 
            # If an error returned from api 
            if 'error' in r.json():
                error = r.json()
                code = error['error']['code']
                message = error['error']['message']
                logging.warning(f"An error has occurred when hitting: {r.request.method} {r.url} with parameters: {params}. Error: " + str(error))
                
                # If throttling error
                if code == 42901:
                    logging.info("Throttle limit was reached. Pausing to wait for throttle")
                    time.sleep(10)
                    # Recall this method to make the request again. 
                    return generic_api_call(method, endpoint, params, token, warning_log)
                # Retry if server error
                if code == 500 or code == 409:
                    logging.info("Server errors. Pausing before trying again.")
                    time.sleep(10)
                    # Recall this method to make the request again. 
                    return generic_api_call(method, endpoint, params, token, warning_log)
                
                # Unknown handling for error
                logging.warning(warning_log)
                logging.exception(f"Something broke the script. Code: {code} Error Message: {message} ")
                return False
            # If successful return r
            return r
        except Exception as e:
            return e

class FlightPlans(Client):
    # Get all active flights
    def get_active_flight_plans(self, symbol):
        """Get all the currently active flight plans in the system given. This is for all global accounts

        Args:
            symbol (str): Symbol of the system. OE or XV

        Returns:
            dict : dict containing a list of flight plans for each system as the key
        """
        endpoint = f"game/systems/{symbol}/flight-plans"
        warning_log = F"Unable to get flight plans for system: {symbol}."
        logging.info(f"Getting the flight plans in the {symbol} system")
        res = self.generic_api_call("GET", endpoint, token=self.token, warning_log=warning_log)
        return res.json() if res else False

    # Get Existing Flight
    def get_flight_plan(self, flightPlanId):
        """Get the details of a currently active flight plan

        Args:
            flightPlanId (str): ID of the flight plan

        Returns:
            dict : dict containing the details of the flight plan
        """
        endpoint = f"users/{self.username}/flight-plans/{flightPlanId}"
        warning_log = F"Unable to get flight plan: {flightPlanId}."
        logging.info(f"Getting flight plan: {flightPlanId}")
        res = self.generic_api_call("GET", endpoint, token=self.token, warning_log=warning_log)
        return res.json() if res else False

    # Create Flight Plan
    def new_flight_plan(self, shipId, destination):
        """Submit a new flight plan for a ship

        Args:
            shipId (str): ID of the ship to fly
            destination (str): Symbol of the locatino to fly the ship to
        """
        endpoint = f"users/{self.username}/flight-plans"
        params = {"shipId": shipId, "destination": destination}
        warning_log = F"Unable to create Flight Plan for ship: {shipId}."
        logging.info(f"Creating flight plan for ship: {shipId} to destination: {destination}")
        res = self.generic_api_call("POST", endpoint, params=params, token=self.token, warning_log=warning_log)
        return res.json() if res else False

class Game (Client):
    # Get game status
    def get_game_status(self):
        """Check to see if game is up
        """
        endpoint = f"game/status"
        warning_log = F"Game is currently down"
        logging.info(f"Checking if game is up")
        res = self.generic_api_call("GET", endpoint, token=self.token, warning_log=warning_log)
        return res.json() if res else False

class Loans (Client):
    pass
    # Get available loans

    # Get your loans

    # Pay off loan

    # Request new loan

class Locations (Client):
    pass
    # Get Location

    # Get Ships at Location

    # Get System's Locations

class Marketplace (Client):
    pass
    # Get Location's marketplace

class PurchaseOrders (Client):
    def new_purchase_order(self, shipId, good, quantity):
        """Makes a purchase order to the location the ship is currently located at. 

        Args:
            shipId (str): ID of the ship to load the goods onto
            good (str): Symbol of the good to purchase
            quantity (int): How many units of the good to purchase
        """
        endpoint = f"users/{self.username}/purchase-orders"
        params = {"shipId": shipId, "good": good, "quantity": quantity}
        warning_log = F"Unable to make purchase order for ship: {shipId}, good: {good} & quantity: {quantity}"
        res = self.generic_api_call("POST", endpoint, params=params, token=self.token, warning_log=warning_log)
        return res.json() if res else False

class SellOrders (Client):
    pass
    # Sell Orders

class Ships (Client):
    def buy_ship(self, location, type):
        """Buys a ship of the type provided and at the location provided. 
        Certain ships can only be bought from specific locations. Use get_available_ships to see full list.

        Args:
            location (str): symbol of the location the ship to buy is
            type (str): type of ship you want to buy e.g. GR-MK-III
        """
        endpoint = f"users/{self.username}/ships"
        params = {"location": location, "type": type}
        warning_log = F"Unable to buy ship type: {type}, at location: {location}."
        logging.info(f"Buying ship of type: {type} at location: {location}")
        res = self.generic_api_call("POST", endpoint, params=params, token=self.token, warning_log=warning_log)
        return res.json() if res else False

    # Get available ships

    # Get Ship

    # Get Users ships

    # Jettison Cargo

    def scrap_ship(self, shipId):
        """Scraps the shipId for a small amount of credits. 
        Ships need to be scraped at a location with a Shipyard.
        Known Shipyards:
            - OE-PM-TR

        Args:
            shipId (str): ID of the ship to scrap

        Returns:
            bool: True if the ship was scrapped

        Raises:
            Exception: If something went wrong during the scrapping process
        """
        endpoint = f"users/{self.username}/ships/{shipId}/"
        warning_log = f"Failed to scrap ship ({shipId})."
        logging.info(f"Scrapping ship: {shipId}")
        res = self.generic_api_call("DELETE", endpoint, token=self.token, warning_log=warning_log)
        return res

    # Transfer Cargo

class Structures (Client):
    pass

    # Create a new structure

    # Deposit Goods

    # Get your structure info

    # Get your strucutres

    # Transfer goods

class Systems (Client):
    pass
    # Get system info

class Users (Client):
    pass
    # Get user


class Api ():
    def __init__(self, username, token=None):
        self.username = username
        self.token = token if token is not None else get_user_token(username)
        self.flightplans = FlightPlans(username, token)
        self.game = Game(username, token)
        self.loans = Loans(username, token)
        self.locations = Locations(username, token)
        self.marketplace = Marketplace(username, token)
        self.purchaseOrders = PurchaseOrders(username, token)
        self.sellOrders = SellOrders(username, token)
        self.ships = Ships(username, token)
        self.structures = Structures(username, token)
        self.systems = Systems(username, token)
        self.users = Users(username, token)


if __name__ == "__main__":
    token = "4c9f072a-4e95-48d6-bccd-54f1569bd3c5"
    username = "JimHawkins"
    shipId = "cknppgtu510080651bs6hc90sb4s"

    api = Api(username, token)
    # api.purchaseOrders.new_purchase_order(shipId, "FUEL", 50)
    # api.flightplans.new_flight_plan(shipId, "OE-PM-TR")
    api.ships.scrap_ship(shipId)
    # api.ships.buy_ship('OE-UC-AD', 'HM-MK-III')
