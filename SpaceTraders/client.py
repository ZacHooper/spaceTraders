import requests
import logging

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

    def generic_api_call(self, method, endpoint, params=None, token=None):
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
        r = make_request(method, URL + endpoint, headers, params)  
        if r.ok:
            return r.json()
        # If an error occurred handle
        else:
            error = r.json()
            code = error['error']['code']
            message = error['error']['message']
            logging.warning(f"An error has occurred when hitting: {r.request.method} {r.url} with parameters: {params}. Error: " + str(error))
            # Check if the error was due to throttline
            if str(code) == '42901':
                # Handle Throttling errors by pausing and trying again
                logging.info("Throttle limit was reached. Pausing to wait for throttle")
                for n in track(range(10), description="Pausing..."):
                    time.sleep(1)
                # Recall this method to make the request again. 
                return generic_api_call(method, endpoint, params, token)
            # If not due to throttling raise exception
            else:
                logging.exception(f"Something broke the script. Code: {code} Error Message: {message} ")
                return (error, code, message)

    

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
        logging.info(f"Buying ship of type: {type} at location: {location}")
        try:
            res = self.generic_api_call("POST", endpoint, params=params, token=self.token)
            if isinstance(res, tuple):
                logging.warning(F"Unable to buy ship type: {type}, at location: {location}. Code: {res[1]} Message: {res[2]}")
                return False
            # Return res as a json
            return res.json()
        except Exception as e:
            return e


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
        logging.info(f"Scrapping ship: {shipId}")
        try:
            res = self.generic_api_call("DELETE", endpoint, token=self.token)
            if 'success' in res:
                return res
            if 'error' in res:
                logging.info(f"Failed to scrap ship ({shipId}). {res['error']['message']}")
            else:
                return False
        except Exception as e:
            return e

class FlightPlans(Client):
    def new_flight_plan(self, shipId, destination):
        """Submit a new flight plan for a ship

        Args:
            shipId (str): ID of the ship to fly
            destination (str): Symbol of the locatino to fly the ship to
        """
        endpoint = f"users/{self.username}/flight-plans"
        params = {"shipId": shipId, "destination": destination}
        logging.info(f"Creating flight plan for ship: {shipId} to destination: {destination}")
        try:
            res = self.generic_api_call("POST", endpoint, params=params, token=self.token)
            print(res)
            # If there was an error with the request the res will be a tuple
            if isinstance(res, tuple):
                logging.warning(F"Unable to create Flight Plan for ship: {shipId}. Code: {res[1]} Message: {res[2]}")
                return False
            # Return res as a json
            return res.json()

        except Exception as e:
            return e

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
        try:
            res = self.generic_api_call("POST", endpoint, params=params, token=self.token)
            # If there was an error with the request the res will be a tuple
            if isinstance(res, tuple):
                logging.warning(F"Unable to make purchase order for ship: {shipId}, good: {good} & quantity: {quantity}. Code: {res[1]} Message: {res[2]}")
                return False
            # Return res as a json
            return res.json()

        except Exception as e:
            return e
        

class Api ():
    def __init__(self, username, token=None):
        self.username = username
        self.token = token
        self.ships = Ships(username, token)
        self.flightplans = FlightPlans(username, token)
        self.purchaseOrders = PurchaseOrders(username, token)





if __name__ == "__main__":
    token = "4c9f072a-4e95-48d6-bccd-54f1569bd3c5"
    username = "JimHawkins"
    shipId = "cknppgtu510080651bs6hc90sb4s"

    api = Api(username, token)
    # api.purchaseOrders.new_purchase_order(shipId, "FUEL", 50)
    # api.flightplans.new_flight_plan(shipId, "OE-PM-TR")
    api.ships.scrap_ship(shipId)
    # api.ships.buy_ship('OE-UC-AD', 'HM-MK-III')
