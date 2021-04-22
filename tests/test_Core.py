import unittest
import logging
import json
from SpaceTraders.core import Ship, Location, Game, User
from pandas import DataFrame

TOKEN = "4c9f072a-4e95-48d6-bccd-54f1569bd3c5"

DOCKED_SHIP = {
    'id': 'cknoj34cd6480541ds6mlnvsxh2', 
    'manufacturer': 'Gravager', 
    'class': 'MK-I', 
    'type': 'GR-MK-I', 
    'location': 'OE-PM', 
    'x': 20, 
    'y': -25, 
    'speed': 1, 
    'plating': 10, 
    'weapons': 5, 
    'maxCargo': 100, 
    'spaceAvailable': 5, 
    'cargo': [
        {
            'good': 'SHIP_PLATING', 
            'quantity': 47, 
            'totalVolume': 94
        }, 
        {
            'good': 'FUEL', 
            'quantity': 1, 
            'totalVolume': 1
        }
    ]
}

TRANSIT_SHIP = {
    'id': 'cknoj34cd6480541ds6mlnvsxh2', 
    'manufacturer': 'Gravager', 
    'class': 'MK-I', 
    'type': 'GR-MK-I', 
    'location': "IN-TRANSIT", 
    'x': None, 
    'y': None, 
    'speed': 1, 
    'plating': 10, 
    'weapons': 5, 
    'maxCargo': 100, 
    'spaceAvailable': 5, 
    'cargo': [
        {
            'good': 'SHIP_PLATING', 
            'quantity': 47, 
            'totalVolume': 94
        }, 
        {
            'good': 'FUEL', 
            'quantity': 1, 
            'totalVolume': 1
        }
    ]
}

NEW_CARGO = [
    {
        'good': 'SHIP_PLATING', 
        'quantity': 47, 
        'totalVolume': 94
    }, 
    {
        'good': 'RESEARCH', 
        'quantity': 1, 
        'totalVolume': 2        
    },
    {
        'good': 'FUEL', 
        'quantity': 1, 
        'totalVolume': 1
    }
]

NEW_SPACE_AVAILABLE = 97

LOCATIONS = {
    "OE-PM-TR" : 
        {
            "symbol": "OE-PM-TR",
            "type": "MOON",
            "name": "Tritus",
            "x": 23,
            "y": -28,
            "allowsConstruction": True,
            "ships": [
                {
                    "shipId": "ckno99rqo01411ds6dccwchfj",
                    "username": "joel",
                    "shipType": "JW-MK-I"
                }
            ],
            "structures": [
                {
                    "id": "cknoqq0vm6628641ds6le688tcv",
                    "type": "MINE",
                    "location": "OE-PM-TR",
                    "ownedBy": {
                        "username": "Foonisher"
                    }
                },
                {
                    "id": "cknoxwxbq11283341ds6hfuxsar9",
                    "type": "CHEMICAL_PLANT",
                    "location": "OE-PM-TR",
                    "ownedBy": {
                        "username": "Foonisher"
                    }
                },
                {
                    "id": "cknoxwxq211284071ds6i1duoruk",
                    "type": "FARM",
                    "location": "OE-PM-TR",
                    "ownedBy": {
                        "username": "Foonisher"
                    }
                }
            ]
        }
}

USER = {
        "username": "JimHawkins",
        "credits": 244288,
        "ships": [
            {
                "id": "cknoj8i776706221ds6cs4n42m0",
                "location": "OE-PM",
                "x": 20,
                "y": -25,
                "cargo": [
                    {
                        "good": "FUEL",
                        "quantity": 49,
                        "totalVolume": 49
                    }
                ],
                "spaceAvailable": 1,
                "type": "JW-MK-I",
                "class": "MK-I",
                "maxCargo": 50,
                "speed": 1,
                "manufacturer": "Jackshaw",
                "plating": 5,
                "weapons": 5
            },
            {
                "id": "cknoj34cd6480541ds6mlnvsxh2",
                "cargo": [
                    {
                        "good": "METALS",
                        "quantity": 95,
                        "totalVolume": 95
                    },
                    {
                        "good": "FUEL",
                        "quantity": 3,
                        "totalVolume": 3
                    }
                ],
                "spaceAvailable": 2,
                "type": "GR-MK-I",
                "class": "MK-I",
                "maxCargo": 100,
                "speed": 1,
                "manufacturer": "Gravager",
                "plating": 10,
                "weapons": 5
            },
            {
                "id": "cknoj8eu56698741ds65uiuy9mi",
                "cargo": [
                    {
                        "good": "FUEL",
                        "quantity": 11,
                        "totalVolume": 11
                    }
                ],
                "spaceAvailable": 39,
                "type": "JW-MK-I",
                "class": "MK-I",
                "maxCargo": 50,
                "speed": 1,
                "manufacturer": "Jackshaw",
                "plating": 5,
                "weapons": 5
            },
            {
                "id": "cknpjmxt54378181bs6gbptfs9q",
                "cargo": [
                    {
                        "good": "SHIP_PARTS",
                        "quantity": 23,
                        "totalVolume": 92
                    },
                    {
                        "good": "FUEL",
                        "quantity": 1,
                        "totalVolume": 1
                    }
                ],
                "spaceAvailable": 7,
                "type": "GR-MK-I",
                "class": "MK-I",
                "maxCargo": 100,
                "speed": 1,
                "manufacturer": "Gravager",
                "plating": 10,
                "weapons": 5
            },
            {
                "id": "cknppm8el10590111bs6dmm0o7z8",
                "location": "OE-PM-TR",
                "x": 23,
                "y": -28,
                "cargo": [],
                "spaceAvailable": 50,
                "type": "JW-MK-I",
                "class": "MK-I",
                "maxCargo": 50,
                "speed": 1,
                "manufacturer": "Jackshaw",
                "plating": 5,
                "weapons": 5
            },
            {
                "id": "cknppgtu510080651bs6hc90sb4s",
                "location": "OE-UC-AD",
                "x": -82,
                "y": 82,
                "cargo": [],
                "spaceAvailable": 300,
                "type": "GR-MK-II",
                "class": "MK-II",
                "maxCargo": 300,
                "speed": 1,
                "manufacturer": "Gravager",
                "plating": 10,
                "weapons": 5
            }
        ],
        "loans": [
            {
                "id": "cknoj2ix26449261ds6pl7v41x5",
                "due": "2021-04-21T11:41:34.403Z",
                "repaymentAmount": 280000,
                "status": "CURRENT",
                "type": "STARTUP"
            }
        ]
    }


class TestShipInit(unittest.TestCase):
    # Does a docked ship Class Initiate when given a valid JSON
    def test_init_docked_ship(self):
        self.assertIsInstance(Ship(TOKEN, DOCKED_SHIP), Ship, "Failed to initiate a docked ship")

    # Does a docked ship Class Initiate when given a valid JSON
    def test_init_transit_ship(self):
        self.assertIsInstance(Ship(TOKEN, TRANSIT_SHIP), Ship, "Failed to initiate a ship in transit")

class TestShipMethods(unittest.TestCase):
    def setUp(self):
        self.ship = Ship(TOKEN, DOCKED_SHIP)
        self.location = Location(TOKEN, LOCATIONS['OE-PM-TR'])
        # Load the constant systems json file to stop API call
        with open('./SpaceTraders/constants/systems.json', 'r') as infile:
            systems = json.load(infile)
        self.game = Game(TOKEN, systems)
        logging.disable(logging.INFO)
    
    def tearDown(self):
        logging.disable(logging.NOTSET)

    # Tests the return Ship as a dict method
    def test_return_ship_as_dict(self):
        self.assertIsInstance(self.ship.as_dict(), dict, "Failed to return a Ship object as a dict")

    # Tests the 'cargo_to_sell' method
    def test_get_cargo_to_sell(self):
        cargo = self.ship.get_cargo_to_sell()
        # If cargo isn't a list
        self.assertIsInstance(cargo, list, "Failed to return cargo as a list object")
        # if the FUEL good is in the list
        for good in cargo:
            self.assertNotEqual(good['good'], "FUEL", "FUEL was returned as a potential good to sell")

    # Tests the 'get_fuel_level' method
    def test_get_fuel_level(self):
        self.assertIsInstance(self.ship.get_fuel_level(), int, "Returned a fuel level that was an integer value")

    # Tests the 'update_cargo' method
    def test_update_cargo(self):
        # Update the cargo
        self.ship.update_cargo(NEW_CARGO, NEW_SPACE_AVAILABLE)
        # Check that space available is correct
        self.assertEqual(self.ship.spaceAvailable, NEW_SPACE_AVAILABLE, "Space Available did not update correctly")
        # Check the cargo list is now 3
        self.assertEqual(len(self.ship.cargo), 3, "Cargo did not update correctly - length of list is not correct")
    
     # Tests the 'update_location' method
    def test_update_location(self):
        # Update the cargo
        self.ship.update_location(self.location.x, self.location.y, self.location.symbol)
        # Check that the x co-ord updated
        self.assertEqual(self.ship.x, self.location.x, "X coordinate did not update correctly")
        # Check that the y co-ord updated
        self.assertEqual(self.ship.y, self.location.y, "Y coordinate did not update correctly")
        # Check that the location symbol updated
        self.assertEqual(self.ship.location, self.location.symbol, "Location symbol did not update correctly")

     # Tests the 'calculate_fuel_usage' method
     # This test is only checking that an integer is returned & an impossible value
     # As I don't even know what the exact formula is yet there is no point to test for exact values
    def test_calculate_fuel_usage(self):
        fuel_usage = self.ship.calculate_fuel_usage(from_loc=self.game.locations[self.ship.location], to_loc=self.location)
        self.assertIsInstance(fuel_usage, int, "Fuel wasn't returned as an integer")
        self.assertLess(fuel_usage, 500, "An impossible value was returned for fuel amount")
        self.assertEqual(fuel_usage, 4, "Incorrect calculation for fuel required")
    
    # Tests the distance calculator - See https://chortle.ccsu.edu/VectorLessons/vch04/vch04_4.html for the 2D vector length formula
    def test_calculate_distance(self):
        self.assertEqual(self.ship.calculate_distance(self.location.x, self.location.y),4)

    # Tests the get_closest_location method
    def test_get_closest_location(self):
        closet_location = self.ship.get_closest_location()
        # make sure the closest location isn't where the ship already is
        self.assertNotEqual(closet_location[0].symbol, self.ship.location, "Returned the location the ship is already located at as the closet location...")
        # Make sure the clostest location isn't an impossible value
        self.assertLess(closet_location[1], 100, "Returned a distance that would not be expected as the closet location")

class TestUserInit(unittest.TestCase):
    def test_init_user(self):
        self.assertIsInstance(User(TOKEN, USER), User, "Failed to initiate a User object")
        self.assertIsNotNone(User(TOKEN, USER).token, "Falied to initiate a User object, token not stored correctly")

class TestUserMethods(unittest.TestCase):
    def setUp(self):
        self.user = User(TOKEN, USER)
    
    # No filter, sorts or df applied
    # Should just return a list of Ship Objects
    def test_get_ships(self):
        ships = self.user.get_ships()
        # Check if list is returned
        self.assertIsInstance(ships, list, "Returned value is not a list")
        # Check if the list 
        self.assertTrue(all(isinstance(ship, Ship) for ship in ships), "Not all of the ships are a Ship Object")

    # Should return a DataFrame
    def test_get_ships_df(self):
        ships = self.user.get_ships(as_df=True)
        # Check if DataFrame is returned
        self.assertIsInstance(ships, DataFrame, "Returned value is not a DataFrame")

    # Should return a Filtered List of Ship Objects
    def test_get_ships_filter(self):
        ships = self.user.get_ships(filter_by=[('manufacturer', 'Gravager')])
        # Check if list is returned
        self.assertIsInstance(ships, list, "Returned value is not a list")
        # Check that the length of the list is correct - Note orginal is 6
        self.assertEqual(len(ships), 3, "Didn't filter the right number of ships")
        # Check that the right manufacturer of ships were returned
        self.assertTrue(all(ship.manufacturer == 'Gravager' for ship in ships), 
                        "Not all the ships in the filtered list were filtered correctly")
    
    # Should return a sorted list of Ship objects
    def test_get_ships_sort(self):
        ships = self.user.get_ships(sort_by=['manufacturer'])
        # Check if list is returned
        self.assertIsInstance(ships, list, "Returned value is not a list")
        # Check that the length of the list is correct - Note orginal is 6
        self.assertEqual(len(ships), 6, "Some ships were filtered when they shouldn't have been")
        # Check the the sort worked
        self.assertEqual(ships[0].manufacturer, 'Gravager', "The Max value wasn't what was expected")
        self.assertEqual(ships[5].manufacturer, 'Jackshaw', "The Min value wasn't what was expected")

    # Should return a DataFrame with a filtered columns
    def test_get_ships_fields(self):
        ships = self.user.get_ships(as_df=True, fields=['manufacturer'])
        # Check if list is returned
        self.assertIsInstance(ships, DataFrame, "Returned value is not a DataFrame")
        # Check if only the expected fields were returned
        self.assertEqual(len(ships.columns), 1, "More than the 1 expected fields were present")

    # Test the get_ship method
    def test_get_ship(self):
        self.assertEqual(self.user.get_ship('cknppgtu510080651bs6hc90sb4s').id, 
                        'cknppgtu510080651bs6hc90sb4s', "The correct ship object was not returned")

class TestGameInit(unittest.TestCase):
    def setUp(self):
        # Load the constant systems json file to stop API call
        with open('./SpaceTraders/constants/systems.json', 'r') as infile:
            self.systems = json.load(infile)
            
    # Try to init a Game class
    def test_init_game(self):
        self.assertIsInstance(Game(TOKEN, self.systems), Game, "Failed to initiate a Game")
        
class TestGameMethods(unittest.TestCase):
    def setUp(self):
        # Load the constant systems json file to stop API call
        with open('./SpaceTraders/constants/systems.json', 'r') as infile:
            systems = json.load(infile)
        self.game = Game(TOKEN, systems)

    def test_location(self):
        self.assertIsInstance(self.game.location('OE-PM'), Location, "Didn't return a Location Object")

    def test_load_locations(self):
        locations = self.game.load_locations()
        self.assertIsInstance(locations, dict, "Didn't return a dict object")
        self.assertTrue(all(isinstance(locations[loc], Location) for loc in locations), "Not all values in Dict are Location objects")

        

if __name__ == '__main__':
    unittest.main()
  