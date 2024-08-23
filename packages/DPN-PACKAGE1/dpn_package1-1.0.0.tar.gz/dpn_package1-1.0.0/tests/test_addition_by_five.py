import unittest
from SRC.addition.addition_by_five import addition_by_five

class TestMultiplyByThree(unittest.TestCase):

    def test_addition_by_five(self):
        self.assertEqual(addition_by_five(3), 8)

unittest.main()