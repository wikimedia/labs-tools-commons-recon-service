#!/bin/bash

set -euo pipefail

title()
{
    echo
    echo =============================================================================
    echo "$@"
    echo
}

got()
{
    command -v "$1" > /dev/null
}


title "pytest (unit and functional tests)"
pytest -v

title "flake8 (coding style checks)"
flake8 --count --show-source --statistics \
       --ignore=W503,W605,E501,E203,F401,E402,W293,E303 \
       --exclude=.git,.coverage,venv,service/__pycache__ .

title "All tests passed :D!"
exit 0