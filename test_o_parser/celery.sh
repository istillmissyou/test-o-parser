#!/bin/bash

if [[ "${1}" == "celery" ]]; then
  celery -A test_o_parser worker -l INFO
elif [[ "${1}" == "flower" ]]; then
  celery -A test_o_parser flower
 fi