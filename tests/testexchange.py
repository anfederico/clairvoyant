import unittest

# Local imports
import sys
sys.path.append("../.")
from clairvoyant import exchange, helpers

class Methods(unittest.TestCase):

    def test_errors(self):
        a = exchange.Account(1000)
        self.assertRaises(ValueError, a.EnterPosition, 'Long',  2000, 10)
        self.assertRaises(ValueError, a.EnterPosition, 'Long',  -500, 10)       
        self.assertRaises(ValueError, a.EnterPosition, 'Long', 500, -10)
        # Enter valid position
        a.EnterPosition('Long', 250, 10)
        a.EnterPosition('Short', 250, 10)
        Long  = a.Positions[0]
        Short = a.Positions[1]
        self.assertRaises(ValueError, a.ClosePosition, Long, 0.5, -20)
        self.assertRaises(ValueError, a.ClosePosition, Long, 1.01, 20)
        self.assertRaises(ValueError, a.ClosePosition, Long, -0.5, 20)
        self.assertRaises(ValueError, a.ClosePosition, Short, 1.01, 20)
        self.assertRaises(ValueError, a.ClosePosition, Short, -0.5, 20)

    def test_long(self):
        a = exchange.Account(1000)
        # Win on a long
        a.EnterPosition('Long', 500, 10)
        a.EnterPosition('Long', 500, 10)
        self.assertEqual(a.BuyingPower, 0)
        self.assertEqual(a.TotalValue(10), 1000)
        L0 = a.Positions[0]
        L1 = a.Positions[1]
        a.ClosePosition(L0, 0.5, 20)
        a.ClosePosition(L1, 0.5, 20)
        self.assertEqual(a.BuyingPower, 1000)
        self.assertEqual(a.TotalValue(20), 2000)
        a.ClosePosition(L0, 0.5, 40)
        a.ClosePosition(L1, 0.5, 40)
        self.assertEqual(a.BuyingPower, 2000)
        self.assertEqual(a.TotalValue(40), 3000)
        # Lose on a long
        a.EnterPosition('Long', 1000, 50)
        L2 = a.Positions[2]
        a.ClosePosition(L2, 0.5, 25)
        self.assertEqual(a.BuyingPower, 1250)
        self.assertEqual(a.TotalValue(25), 2125)

    def test_short(self):
        a = exchange.Account(1000)
        # Win on a short        
        a.EnterPosition('Short', 500, 10)
        a.EnterPosition('Short', 500, 10)
        self.assertEqual(a.BuyingPower, 0)
        self.assertEqual(a.TotalValue(10), 1000)
        S0 = a.Positions[0]
        S1 = a.Positions[1]
        a.ClosePosition(S0, 0.5, 5)
        a.ClosePosition(S1, 0.5, 5)
        self.assertEqual(a.BuyingPower, 750)
        self.assertEqual(a.TotalValue(5), 1500)
        a.ClosePosition(S0, 0.5, 2.5)
        a.ClosePosition(S1, 0.5, 2.5)
        self.assertEqual(a.BuyingPower, 1187.5)
        self.assertEqual(a.TotalValue(2.5), 1625)
        # Lose on a short   
        a.EnterPosition('Short', 1000, 2)
        S2 = a.Positions[2]
        a.ClosePosition(S2, 0.5, 4)
        self.assertEqual(a.BuyingPower, 187.5)
        self.assertEqual(a.TotalValue(4), 587.5)

    def test_both(self):
        a = exchange.Account(1000)
        a.EnterPosition('Long',  200, 20)
        a.EnterPosition('Short', 250, 25)
        self.assertEqual(a.BuyingPower, 550)
        self.assertEqual(a.TotalValue(25), 1050)
        Long  = a.Positions[0]
        Short = a.Positions[1]
        a.ClosePosition(Long,  0.5, 40)
        a.ClosePosition(Short, 0.5, 12.5)
        self.assertEqual(a.BuyingPower, 937.5)
        self.assertEqual(a.TotalValue(12.5), 1187.5)
        a.ClosePosition(Long,  1.0, 50)
        a.ClosePosition(Short, 1.0, 50)
        self.assertEqual(a.BuyingPower, 1187.5)
        self.assertEqual(a.TotalValue(100), 1187.5)

    def test_decimals(self):
        # Long with decimals
        a = exchange.Account(2)
        a.EnterPosition('Long', 1, 0.00000001)
        self.assertEqual(a.TotalValue(0.00000002), 3)
        a.ClosePosition(a.Positions[0], 1, 0.00000002)
        self.assertEqual(a.BuyingPower, 3)
        # Short with decimals 
        a = exchange.Account(2)
        a.EnterPosition('Short', 1, 0.00000002)
        self.assertEqual(a.TotalValue(0.00000001), 2.5)
        a.ClosePosition(a.Positions[0], 1, 0.00000001)
        self.assertEqual(a.BuyingPower, 2.5)

if __name__ == '__main__':
    unittest.main()