CREATE TABLE product (
    code character varying(10), 
    name character varying(100), 
    units character varying(10),
    PRIMARY KEY (code)
);
        
CREATE TABLE customer (
    customer_code character varying(10), 
    name character varying(100), 
    address character varying(100), 
    credit_limit numeric, 
    country character varying(20),
    PRIMARY KEY (customer_code)
); 
        
CREATE TABLE invoice (
    invoice_no character varying(10), 
    date date, 
    customer_code character varying(10), 
    due_date date, total numeric(18,2), 
    vat numeric(18,2), 
    amount_due numeric(18,2),
    PRIMARY KEY (invoice_no),
    CONSTRAINT invoice_customer_customer_code_fkey FOREIGN KEY (customer_code)
        REFERENCES customer (customer_code) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION
);  

CREATE TABLE invoice_line_item (
    invoice_no character varying(10), 
    product_code character varying(10), 
    quantity integer, 
    unit_price numeric(18,2), 
    extended_price numeric(18,2),
    PRIMARY KEY (invoice_no,product_code),
    CONSTRAINT invoice_line_item_product_product_code_fkey FOREIGN KEY (product_code)
        REFERENCES product (code) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION
);  
        