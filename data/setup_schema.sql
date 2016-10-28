DROP TABLE IF EXISTS loans;

CREATE TABLE loans (
       loan_id INTEGER PRIMARY KEY ASC,
       payer_ssn CHARACTER(12),
       prop_value INTEGER,
       loan_value INTEGER,
       loan_status CHARACTER(20)
);
