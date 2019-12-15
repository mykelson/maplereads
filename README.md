# Project 1

Web Programming with Python and JavaScript

set DATABASE_URL=postgres://eonnovvbhingoh:3cf40f96881376932ea2d5fee7e583a8e7b117b9073b8b437a66e69c9083433a@ec2-174-129-18-247.compute-1.amazonaws.com:5432/dctbtl2u19d2qp


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