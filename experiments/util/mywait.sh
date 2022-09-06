#!/bin/bash

# Check only once per 10 minutes
while [ "$(ps -ef | awk '$2 == '${1:-X})" ]; do sleep 600; done
