#!/usr/bin/env python2
"""Simple load object representation"""

import re # for checking the SSN format

### custom exceptions

class FormatSSNError(Exception):
    pass

class InvalidSSNError(Exception):
    pass

class InvalidLoanValueError(Exception):
    pass

class InvalidPropertyValueError(Exception):
    pass

class ExcessLoanToValueError(Exception):
    pass

###

class Loan:
    """Loan information"""

    # for style, we're making SSNs always look like ###-##-####
    _SSN_RE  = re.compile("^\d{3}-\d{2}-\d{4}$")

    # maximum loan-to-value amount is 40%
    _MAX_LTV = 0.40

    def __init__(self, payer_ssn, prop_value, loan_value, loan_id=None):
        """A loan amount is assigned to a payer (by SSN) for a given property value. A
        unique loan_id is designated when the loan is saved."""
        self.payer_ssn   = payer_ssn
        self.prop_value  = prop_value
        self.loan_value  = loan_value

        self.loan_status = None
        self.loan_id     = loan_id


    def validate(self):
        """More rigorous checking of the loan data than the basic UI validation"""

        if self.payer_ssn is None or self._SSN_RE.match(self.payer_ssn) is None:
            raise FormatSSNError

        """SSN rejection has changed over the years. This would probably be
           better served in its own specialized class, in case the
           business rules shift again for what is/is not valid. In
           real life, the SSN would be kicked off to a credit
           reporting service and a bad number would be rejected out of
           hand, but we can try to eliminate some of the more obvious
           junk data and be nicer to the agencies.

           AAA-GG-SSSS

           A = Area
           G = Group
           S = Serial

           Area cannot be: 000, 666, 9xx

           Ref:
           https://www.ssa.gov/employer/randomization.html

        """

        if self.payer_ssn[0] == "9":
            raise InvalidSSNError

        if self.payer_ssn[0:3] in ("000","666"):
            raise InvalidSSNError

        if self.prop_value <= 0:
            raise InvalidPropertyValueError

        if self.loan_value <= 0:
            raise InvalidLoanValueError

        if self.loan_value/self.prop_value > self._MAX_LTV:
            raise ExcessLoanToValueError


    def save(self, conn):
        """Store the loan to the given database connection"""
        stmt = conn.cursor()

        if self.loan_id is None:
            # save a new one
            stmt.execute("INSERT INTO loans (payer_ssn, prop_value, loan_value, loan_status) VALUES (?, ?, ?, ?)",
                         (self.payer_ssn, self.prop_value, self.loan_value, self.loan_status))

            for row in stmt.execute("SELECT last_insert_rowid() LIMIT 1"):
                self.loan_id = row[0]

            conn.commit()
            #

        else:
            # replace an existing loan
            stmt.execute("UPDATE loans SET payer_ssn = ?, prop_value = ?, loan_value = ?, loan_status = ? WHERE loan_id = ?",
                         (self.payer_ssn, self.prop_value, self.loan_value, self.loan_status, self.loan_id))

            conn.commit()


    def load(self, conn):
        """Fetch a loan by id from the given database connection"""
        stmt = conn.cursor()

        if self.loan_id is not None:
            for row in stmt.execute("SELECT payer_ssn, prop_value, loan_value, loan_status FROM loans WHERE loan_id = ? LIMIT 1",(self.loan_id,)):
                self.payer_ssn, self.prop_value, self.loan_value, self.loan_status = row

            conn.commit()
