from flask import Flask, g, request, jsonify
import sqlite3

from loansubmit.Loan import *

DB = 'data/loansubmit.db'

app = Flask(__name__)

# setup/teardown the db within the app

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# API handlers

@app.errorhandler(404)
def not_found(error=None):
    reply = {
        'status': 404,
        'message': 'Command not found: ' + request.url,
    }
    resp = jsonify(reply)
    resp.status_code = reply['status']

    return resp


@app.route("/new/", methods = ['GET','POST'])
def cmd_new():
    """/new command establishes a new loan given payer_ssn, prop_value, loan_value (GET or POST)"""
    db = get_db()
    loan = Loan(None, None, None)

    errors = []
    reply = {}

    # three parameters are required: payer_ssn, prop_value, and loan_value

    # payer_ssn
    #
    if 'payer_ssn' not in request.args:
        errors.append({"field": "payer_ssn",
                       "message": "Must supply payer_ssn in request"})
    else:
        try:
            raw = request.args['payer_ssn']
            loan.payer_ssn = raw.strip()
            loan.validate_payer_ssn()
        except FormatSSNError as e:
            errors.append({"field": "payer_ssn",
                           "message": "Format payer_ssn as ###-##-####"})
        except InvalidSSNError as e:
            errors.append({"field": "payer_ssn",
                           "message": "Invalid payer_ssn value"})

    # prop_value
    #
    if 'prop_value' not in request.args:
        errors.append({"field": "prop_value",
                       "message": "Must supply prop_value in request"})
    else:
        try:
            raw = request.args['prop_value']
            raw = raw.strip()

            if raw.isdigit():
                loan.prop_value = int(raw)
            else:
                loan.prop_value = 0

            loan.validate_prop_value()
        except InvalidPropertyValueError as e:
            errors.append({"field": "prop_value",
                           "message": "Invalid prop_value, must be integer > 0"})

    # loan_value
    #
    if 'loan_value' not in request.args:
        errors.append({"field": "loan_value",
                       "message": "Must supply loan_value in request"})
    else:
        try:
            raw = request.args['loan_value']
            raw = raw.strip()

            if raw.isdigit():
                loan.loan_value = int(raw)
            else:
                loan.loan_value = 0

            loan.validate_loan_value()
        except InvalidLoanValueError as e:
            errors.append({"field": "loan_value",
                           "message": "Invalid loan_value, must be integer > 0"})


    # loan-to-value check
    #
    # not a fatal error, just an automatic denial

    if loan.prop_value and loan.loan_value:
        try:
            loan.validate_ltv()
        except ExcessLoanToValueError as e:
            loan.loan_status = "Denied"
            reply['message'] = "Loan-to-value exceeds limit, loan is Denied"
            loan.save(db)
        else:
            loan.loan_status = "Accepted"
            reply['message'] = "Loan is Accepted"
            loan.save(db)


    if len(errors):
        reply['errors'] = errors
        reply['status'] = 404
        reply['message'] = 'Command failed: new'
    else:
        reply['status'] = 200
        reply['loan'] = loan.to_jsonable()


    resp = jsonify(reply)
    resp.status_code = reply['status']

    return resp


@app.route("/find/<int:loan_id>", methods = ['GET','PUT'])
def cmd_find(loan_id):
    """/find/<loan_id> command looks up the loan in the database and returns it if found (GET or PUT)"""
    db = get_db()
    loan = Loan(None, None, None, loan_id = loan_id)
    loan.load(db)

    errors = []
    reply = {}

    if loan.payer_ssn is None:
        reply['status'] = 404
        reply['message'] = 'Command failed: find ' + str(loan_id)
        errors.append({"field": "loan_id",
                       "message": "Could not find a loan with that id"})
    else:
        reply['status'] = 200
        reply['message'] = 'command succeeded: find ' + str(loan_id)
        reply['loan'] = loan.to_jsonable()

    if len(errors):
        reply['errors'] = errors

    resp = jsonify(reply)
    resp.status_code = reply['status']

    return resp


@app.route("/edit/<int:loan_id>", methods = ['GET','POST'])
def cmd_edit(loan_id):
    """/edit/<loan_id> accepts a new loan_status value (GET or POST)"""
    db = get_db()
    loan = Loan(None, None, None, loan_id = loan_id)
    loan.load(db)

    errors = []
    reply = {}

    # bad id, loan not found
    #
    if loan.payer_ssn is None:
        reply['status'] = 404
        reply['message'] = 'Command failed: edit ' + str(loan_id)
        errors.append({"field": "loan_id",
                       "message": "Could not find a loan with that id"})

        reply['errors'] = errors
        resp = jsonify(reply)
        resp.status_code = reply['status']

        return resp

    # no status passed
    #
    if 'loan_status' not in request.args:
        reply['status'] = 404
        reply['message'] = 'Command failed: edit ' + str(loan_id)
        errors.append({"field": "loan_status",
                       "message": "Must supply loan_status in request"})

        reply['errors'] = errors
        resp = jsonify(reply)
        resp.status_code = reply['status']

        return resp

    # cleanup/check passed status and apply
    #
    raw = request.args['loan_status']
    raw = raw.strip().title()
    loan.loan_status = raw

    try:
        loan.validate_loan_status()
        loan.save(db)
    except InvalidLoanStatusError as e:
        reply['status'] = 404
        reply['message'] = 'Command failed: edit ' + str(loan_id)

        errors.append({"field": "loan_status",
                       "message": "Legal values: New, Approved, Denied, Review"})

    else:
        reply['status'] = 200
        reply['message'] = 'command succeeded: edit ' + str(loan_id)
        reply['loan'] = loan.to_jsonable()

    if len(errors):
        reply['errors'] = errors

    resp = jsonify(reply)
    resp.status_code = reply['status']

    return resp

#

if __name__ == "__main__":
    app.run(host="0.0.0.0")
