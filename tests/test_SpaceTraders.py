import unittest
import logging
from SpaceTraders import Ship, Location, Game

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
            "x": 23,
            "y": -28
        }
}

class TestShipInit(unittest.TestCase):
    # Does a docked ship Class Initiate when given a valid JSON
    def test_init_docked_ship(self):
        self.assertIsInstance(Ship(DOCKED_SHIP), Ship, "Failed to initiate a docked ship")

    # Does a docked ship Class Initiate when given a valid JSON
    def test_init_transit_ship(self):
        self.assertIsInstance(Ship(TRANSIT_SHIP), Ship, "Failed to initiate a ship in transit")

class TestShipMethods(unittest.TestCase):
    def setUp(self):
        self.ship = Ship(DOCKED_SHIP)
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
        self.ship.update_location(LOCATIONS['OE-PM-TR']['x'], LOCATIONS['OE-PM-TR']['y'], LOCATIONS['OE-PM-TR']['symbol'])
        # Check that the x co-ord updated
        self.assertEqual(self.ship.x, LOCATIONS['OE-PM-TR']['x'], "X coordinate did not update correctly")
        # Check that the y co-ord updated
        self.assertEqual(self.ship.y, LOCATIONS['OE-PM-TR']['y'], "Y coordinate did not update correctly")
        # Check that the location symbol updated
        self.assertEqual(self.ship.location, LOCATIONS['OE-PM-TR']['symbol'], "Location symbol did not update correctly")

     # Tests the 'calculate_fuel_usage' method
     # This test is only checking that an integer is returned & an impossible value
     # As I don't even know what the exact formula is yet there is no point to test for exact values
    def test_calculate_fuel_usage(self):
        self.assertIsInstance(self.ship.calculate_fuel_usage(LOCATIONS['OE-PM-TR']['x'], 
                                                             LOCATIONS['OE-PM-TR']['y']), 
                              int, "Fuel wasn't returned as an integer")
        self.assertLess(self.ship.calculate_fuel_usage(LOCATIONS['OE-PM-TR']['x'], LOCATIONS['OE-PM-TR']['y']), 
                        500, "An impossible value was returned for fuel amount")
    
    # Tests the distance calculator - See https://chortle.ccsu.edu/VectorLessons/vch04/vch04_4.html for the 2D vector length formula
    def test_calculate_distance(self):
        self.assertEqual(self.ship.calculate_distance(LOCATIONS['OE-PM-TR']['x'], LOCATIONS['OE-PM-TR']['y']),4)

    # Tests the get_closest_location method
    def test_get_closest_location(self):
        closet_location = self.ship.get_closest_location()
        # make sure the closest location isn't where the ship already is
        self.assertNotEqual(closet_location[0].symbol, self.ship.location, "Returned the location the ship is already located at as the closet location...")
        # Make sure the clostest location isn't an impossible value
        self.assertLess(closet_location[1], 100, "Returned a distance that would not be expected as the closet location")

class TestGameInit(unittest.TestCase):
    # Try to init a Game class
    def test_init_game(self):
        self.assertIsInstance(Game(), Game, "Failed to initiate a Game")
if __name__ == '__main__':
    unittest.main()
  