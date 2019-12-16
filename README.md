# Project 1

Web Programming with Python and JavaScript

set DATABASE_URL=postgres://gdrlyzboleqgcj:332a5ea4c02684e60b938cf12022e6703ecc50a81de4195395fb099c715f5a4b@ec2-174-129-254-249.compute-1.amazonaws.com:5432/d7k75p161er914



For Goodreads api key:
key: Hl9uw740Ex3dG9VaX8L2CQ
secret: Yqy2Jk0WtpFHYIR31hLWy6pRG7Guo7M6XRwOOgMEYE

Heroku API key to Authorize Travis CI: 72b6a2df-28f3-4ae4-a85b-184fb10d9695

Google API key    AIzaSyC22N7548uoXsns9QtYg49C64G2O7d1qto


Reviews Table:
CREATE TABLE reviews(
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    isbn VARCHAR REFERENCES books,
    rating INTEGER NOT NULL,
    opinion VARCHAR NOT NULL
);

CREATE TABLE books (
     isbn VARCHAR  PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
 );

 CREATE TABLE users (
     id SERIAL PRIMARY KEY,
     name VARCHAR NOT NULL,
     username VARCHAR NOT NULL,
     email VARCHAR NOT NULL,
     password VARCHAR NOT NULL
 );