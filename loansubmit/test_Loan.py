#!/usr/bin/env python2
"""Test cases for Loan class"""

import unittest
import sqlite3

from Loan import *

###

TEST_DB = "../data/loansubmit_t.db"

class Test_Loan(unittest.TestCase):

    def test_creates(self):
        LOAN1 = Loan("123-45-6789", 12345, 67890)

        self.assertTrue("123-45-6789" == LOAN1.payer_ssn, "SSN issue")
        self.assertTrue(12345 == LOAN1.prop_value, "Property value issue")
        self.assertTrue(67890 == LOAN1.loan_value, "Loan value issue")

        self.assertIsNone(LOAN1.loan_status, "Loan should not have a status")
        self.assertIsNone(LOAN1.loan_id, "Loan should not have an id")

        #

        LOAN2 = Loan("012-34-5678", 300, 400, "abc-def-ghijkl")

        self.assertTrue("012-34-5678" == LOAN2.payer_ssn, "SSN issue")
        self.assertTrue(300 == LOAN2.prop_value, "Property value issue")
        self.assertTrue(400 == LOAN2.loan_value, "Loan value issue")

        self.assertIsNone(LOAN2.loan_status, "Loan should not have a status")
        self.assertTrue("abc-def-ghijkl" == LOAN2.loan_id, "Loan should have an id")

    #

    def test_ssn_validation(self):
        LOAN1 = Loan(None, None, None)

        # SSN should look like AAA-GG-SSSS where A/G/S are 0-9...
        #
        for ssn in ("1234", "foo", "123456789", "329487240948372039487231", None):
            LOAN1.payer_ssn = ssn
            with self.assertRaises(FormatSSNError) as context:
                LOAN1.validate_payer_ssn()

        # ...except A cannot be 000, 666, or any 9xx
        #
        for ssn in ("000-12-3456","666-77-8888","900-12-6473","999-12-6473"):
            LOAN1.payer_ssn = ssn
            with self.assertRaises(InvalidSSNError) as context:
                LOAN1.validate_payer_ssn()


    def test_property_value_validation(self):
        LOAN1 = Loan(None, None, None)

        for amt in (0, -10, None):
            LOAN1.prop_value = amt
            with self.assertRaises(InvalidPropertyValueError) as context:
                LOAN1.validate_prop_value()

    #

    def test_loan_value_validation(self):
        LOAN1 = Loan(None, None, None)

        for amt in (0, -10, None):
            LOAN1.loan_value = amt
            with self.assertRaises(InvalidLoanValueError) as context:
                LOAN1.validate_loan_value()

    #

    def test_ltv_validation(self):
        LOAN1 = Loan(None, None, None)

        LOAN1.prop_value = 5000

        # 100% loan amount, too high!
        #
        LOAN1.loan_value = LOAN1.prop_value

        with self.assertRaises(ExcessLoanToValueError) as context:
            LOAN1.validate_ltv()

        # 50% loan amount, still too much
        #
        LOAN1.loan_value = LOAN1.prop_value * 0.5

        with self.assertRaises(ExcessLoanToValueError) as context:
            LOAN1.validate_ltv()

        # 40% loan amount is the cap
        #
        LOAN1.loan_value = LOAN1.prop_value * 0.4
        LOAN1.validate_ltv()

        # And lower is OK, too
        #
        LOAN1.loan_value = LOAN1.prop_value * 0.1
        LOAN1.validate_ltv()

    #

    def test_status_validation(self):
        LOAN1 = Loan(None, None, None)

        for txt in ("Bad", "FOO", "Invalid", "approved", None):
            LOAN1.loan_status = txt
            with self.assertRaises(InvalidLoanStatusError) as context:
                LOAN1.validate_loan_status()

    #

    def test_db_setup(self):
        """Just verifies the db connection is OK, and cleans out tables"""
        db = sqlite3.connect(TEST_DB)
        stmt = db.cursor()
        stmt.execute("DELETE FROM loans")
        db.commit()
        db.close()

    #

    def test_db_save(self):
        LOAN1 = Loan("123-45-6789", 12345, 67890)

        db = sqlite3.connect(TEST_DB)

        self.assertIsNone(LOAN1.loan_id, "Loan should not have an id")
        LOAN1.save(db)
        self.assertIsNotNone(LOAN1.loan_id, "Loan should have an id after saving")

        # with the id stored, a different branch is executed
        #
        # just validating that it doesn't fail in this test, load test checks values

        LOAN1.save(db)

        db.close()

    #

    def test_db_load(self):
        LOAN1 = Loan("123-45-6789", 12345, 67890)

        db = sqlite3.connect(TEST_DB)

        LOAN1.loan_status = "Awesome"
        LOAN1.save(db)

        LOAN2 = Loan(None, None, None, LOAN1.loan_id)
        self.assertTrue(LOAN2.loan_id == LOAN1.loan_id, "Loan id issue")

        LOAN2.load(db)

        self.assertTrue(LOAN2.payer_ssn == LOAN1.payer_ssn, "SSN issue")
        self.assertTrue(LOAN2.prop_value == LOAN1.prop_value, "Property value issue")
        self.assertTrue(LOAN1.loan_value == LOAN1.loan_value, "Loan value issue")
        self.assertTrue(LOAN2.loan_status == LOAN1.loan_status, "Loan status issue")

        db.close()

    # 
        
    def test_to_jsonable(self):
        LOAN1 = Loan("123-45-6789", 12345, 67890, 987)
        LOAN1.loan_status = "New"

        # just making sure this executes, don't need to check that json package works
        encode_me = LOAN1.to_jsonable()
        self.assertTrue(len(encode_me) > 0,"JSON encoding should exist")
#

if __name__ == '__main__':
    unittest.main()
