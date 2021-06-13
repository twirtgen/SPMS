#! /bin/sh -e

PYTHONPATH=.. pytest -vv --cov=../util --cov=../pv/binding_manager --cov=../pv/mt_manager --cov=../pv/user_gateway --cov-report term-missing 
