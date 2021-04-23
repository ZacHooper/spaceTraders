import unittest
import logging
from SpaceTraders.client import *

TOKEN = "4c9f072a-4e95-48d6-bccd-54f1569bd3c5"
USERNAME = "JimHawkins"

class TestMakeRequestFunction(unittest.TestCase):
    def setUp(self):
        logging.disable()
    
    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_make_request_get(self):
        res = make_request("GET", "https://api.spacetraders.io/game/status", None, None)
        self.assertEqual(res.status_code, 200, "Either game is down or GET request failed to fire properly")
    
    def test_make_request_post(self):
        res = make_request("POST", "https://api.spacetraders.io/users/JimHawkins/token", None, None)
        # Want the user already created error to be returned
        self.assertEqual(res.status_code, 409, "POST request failed to fire properly")
    
    def test_make_request_bad_method(self):
        self.assertRaises(KeyError, make_request, "BLAH", "https://api.spacetraders.io/users/JimHawkins/token", None, None)

class TestClientClassInit(unittest.TestCase):
    def test_client_with_token_init(self):
        self.assertIsInstance(Client("JimHawkins", "12345"), Client, "Failed to initiate the Client Class")
        self.assertEqual(Client("JimHawkins", "12345").username, "JimHawkins", "Did not set the username attribute correctly")
        self.assertEqual(Client("JimHawkins", "12345").token, "12345", "Did not set the token attribute correctly")

class TestShipInit(unittest.TestCase):
    def test_ships_init(self):
        self.assertIsInstance(Ships("JimHawkins", "12345"), Ships, "Failed to initiate the Ships Class")
        self.assertEqual(Ships("JimHawkins", "12345").username, "JimHawkins", "Did not set the username attribute correctly")
        self.assertEqual(Ships("JimHawkins", "12345").token, "12345", "Did not set the token attribute correctly")

class TestShipMethods(unittest.TestCase):
    def setUp(self):
        logging.disable()
        self.ships = Ships(USERNAME, TOKEN)
    
    def tearDown(self):
        logging.disable(logging.NOTSET)
    
    def test_ships_scrap_ship(self):
        # This should fail as expected and return false
        self.assertEqual(self.ships.scrap_ship("12345"), False, "API call didn't fail when expected to")
    
    def test_ships_buy_ship(self):
        self.assertEqual(self.ships.buy_ship("OE-BO", "HM-MK-III"), False, "API call didn't fail when expected to")

class TestFlightPlanInit(unittest.TestCase):
    def test_flight_plan_init(self):
        self.assertIsInstance(FlightPlans("JimHawkins", "12345"), FlightPlans, "Failed to initiate the FlightPlans Class")
        self.assertEqual(FlightPlans("JimHawkins", "12345").username, "JimHawkins", "Did not set the username attribute correctly")
        self.assertEqual(FlightPlans("JimHawkins", "12345").token, "12345", "Did not set the token attribute correctly")

class TestFlightPlanMethods(unittest.TestCase):
    def setUp(self):
        logging.disable()
        self.fp = FlightPlans(USERNAME, TOKEN)
    
    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_submit_flight_plan_fail(self):
        self.assertEqual(self.fp.new_flight_plan("12345", "OE-PM-TR"), False, "API call didn't fail when expected to")

    def test_get_active_flight_plans_fail(self):
        self.assertEqual(self.fp.get_active_flight_plans("OEV"), False, "API call didn't fail when expected to")

    def test_get_active_flight_plan(self):
        self.assertEqual(self.fp.get_flight_plan("456789"), False, "API call didn't fail when expected to")

class TestPurchaseOrderInit(unittest.TestCase):
    def test_purchase_order_init(self):
        self.assertIsInstance(PurchaseOrders("JimHawkins", "12345"), PurchaseOrders, "Failed to initiate the PurchaseOrders Class")
        self.assertEqual(PurchaseOrders("JimHawkins", "12345").username, "JimHawkins", "Did not set the username attribute correctly")
        self.assertEqual(PurchaseOrders("JimHawkins", "12345").token, "12345", "Did not set the token attribute correctly")

class TestPurchaseOrderMethods(unittest.TestCase):
    def setUp(self):
        logging.disable()
        self.po = PurchaseOrders(USERNAME, TOKEN)
    
    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_submit_flight_plan_fail(self):
        self.assertEqual(self.po.new_purchase_order("12345", "FUEL", 5), False, "API call didn't fail when expected to")

class TestGameInit(unittest.TestCase):
    def test_game_init(self):
        self.assertIsInstance(Game("JimHawkins", "12345"), Game, "Failed to initiate the Game Class")
        self.assertEqual(Game("JimHawkins", "12345").username, "JimHawkins", "Did not set the username attribute correctly")
        self.assertEqual(Game("JimHawkins", "12345").token, "12345", "Did not set the token attribute correctly")

class TestGameMethods(unittest.TestCase):
    def setUp(self):
        logging.disable()
        self.game = Game(USERNAME, TOKEN)
    
    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_get_game_status(self):
        self.assertIsInstance(self.game.get_game_status(), dict, "API did not return dict as expected")

class TestGetUserToken(unittest.TestCase):
    def test_get_user_token(self):
        self.assertIsNone(get_user_token("JimHawkins"), "Failed to handle a username that already exists")

