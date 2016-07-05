spoken-website
==============

Spoken tutorial website in django

## Getting Started

Make sure you have virtualenv and mysql server running locally.

```
$ git clone https://github.com/Spoken-tutorial/spoken-website.git
$ cd spoken-website

# Ask for sample database dump if you don't have already. You'll need to run the next step
$ ./bin/setup.sh

# Now run the local development server with:
$ ./bin/devserver.sh
```


## Running test

```
flake8
py.test
```
