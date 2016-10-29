#!/usr/bin/env python2

import sqlite3

from loansubmit.Loan import *

#

def print_one(loan):
    print " Id: {} SSN: {} Property: {} Loan: {} Status: {}".format(loan.loan_id, loan.payer_ssn,
                                                                    loan.prop_value, loan.loan_value,
                                                                    loan.loan_status)

#

db  = sqlite3.connect("./data/loansubmit.db")
cmd = ""

while cmd <> "quit":
    cmd = raw_input('Enter a command, ? or "help": ')
    cmd = cmd.strip().lower()

    loan = Loan(None, None, None)

    if cmd in ("","?","help"):
        print """
        new:    enter a new loan
        find:   find an existing loan, by id
        edit:   change the status of an existing loan, by id
        quit:   quit the tool
        help:   this list
        """

    elif cmd == "new":

        # SSN input
        valid = False
        while not valid:
            try:
                raw = raw_input(" Enter an SSN as ###-##-####: ")
                loan.payer_ssn = raw.strip()
                loan.validate_payer_ssn()
            except FormatSSNError as e:
                print " > Please format the SSN as ###-##-####"
            except InvalidSSNError as e:
                print " > That's not a valid SSN, sorry"
            else:
                valid = True

        # property value input
        valid = False
        while not valid:
            try:
                raw = raw_input(" Enter the value of the property as dollars: ")
                raw = raw.strip()

                if raw.isdigit():
                    loan.prop_value = int(raw)
                else:
                    loan.prop_value = 0

                loan.validate_prop_value()
            except InvalidPropertyValueError as e:
                print " > That's not a valid property value"
            else:
                valid = True

        # loan value input
        valid = False
        while not valid:
            try:
                raw = raw_input(" Enter the desired loan amount as dollars: ")
                raw = raw.strip()

                if raw.isdigit():
                    loan.loan_value = int(raw)
                else:
                    loan.loan_value = 0

                loan.validate_loan_value()
            except InvalidLoanValueError as e:
                print " > That's not a valid loan amount"
            else:
                valid = True

        try:
            loan.validate_ltv()
        except ExcessLoanToValueError as e:
            print " > The loan amount exceeds the allowable for this property"
            loan.loan_status = "Denied"
            loan.save(db)
            print " Loan denied, saved as: id",loan.loan_id
        else:
            loan.loan_status = "Approved"
            loan.save(db)
            print
            print " New loan saved as: id",loan.loan_id
        print

    elif cmd == "find":
        raw = raw_input("Enter the loan id: ")

        if raw.isdigit():
            loan.loan_id = int(raw)
            loan.load(db)

        if loan.payer_ssn is None:
            print " > Could not find a loan with that id"
        else:
            print_one(loan)

        print

    elif cmd == "edit":
        raw = raw_input("Enter the loan id: ")

        if raw.isdigit():
            loan.loan_id = int(raw)
            loan.load(db)

        if loan.payer_ssn is None:
            print " > Could not find a loan with that id"
        else:
            print_one(loan)

            valid = False
            while not valid:
                try:
                    raw = raw_input(" Enter a new status: ")
                    raw = raw.strip().title()
                    loan.loan_status = raw
                    loan.validate_loan_status()
                except InvalidLoanStatusError as e:
                    print " > Legal values: New, Approved, Denied, Review"
                else:
                    loan.save(db)
                    print
                    print " Changes saved"
                    print_one(loan)
                    valid = True

db.close()
