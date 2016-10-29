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
        
@app.route("/new/", methods = ['POST']) # accept payer_ssn, prop_val, loan_val
def cmd_new():
    pass

@app.route("/find/<int:loan_id>", methods = ['GET','PUT'])
def cmd_find(loan_id):
    db = get_db()
    loan = Loan(None, None, None, loan_id = loan_id)
    loan.load(db)

    errors = []
    reply = {}
    
    if loan.payer_ssn is None:
        reply['status'] = 404
        reply['message'] = 'command failed: find ' + str(loan_id)
        errors.append({"field": "loan_id",
                       "message": "Could not find a loan with that id"})
    else:
        reply['status'] = 200
        reply['message'] = 'command succeeded: find ' + str(loan_id)
        reply['loan'] = loan.__dict__ # not very elegant

    if len(errors):
        reply['errors'] = errors

    resp = jsonify(reply)
    resp.status_code = reply['status']

    return resp
        
        
@app.route("/edit/<int:loan_id>", methods = ['POST']) # accept loan_status text
def cmd_edit():
    db = get_db()
    loan = Loan(None, None, None, loan_id = loan_id)
    loan.load(db)

    errors = []
    reply = {}
    
    if loan.payer_ssn is None:
        reply['status'] = 404
        reply['message'] = 'command failed: edit ' + str(loan_id)
        errors.append({"field": "loan_id",
                       "message": "Could not find a loan with that id"})

        resp = jsonify(reply)
        resp.status_code = reply['status']

        return resp

    # validate the new status (with some cleanup)
    
    if 'loan_status' not in request.args:
        reply['status'] = 404
        reply['message'] = 'command failed: edit ' + str(loan_id)
        errors.append({"field": "loan_id",
                       "message": "Could not find a loan with that id"})

        resp = jsonify(reply)
        resp.status_code = reply['status']

        return resp



        
        raw = request.args['loan_status']
        raw = raw.strip().title()
        loan.validate_loan_status()
    


        
        reply['status'] = 200
        reply['message'] = 'command succeeded: find ' + str(loan_id)
        reply['loan'] = loan.__dict__ # not very elegant

    if len(errors):
        reply['errors'] = errors

    resp = jsonify(reply)
    resp.status_code = reply['status']

    return resp

#

if __name__ == "__main__":
    app.run(host="0.0.0.0")
