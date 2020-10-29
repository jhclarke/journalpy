#!/usr/bin/env bash

echo "Installing required Python modules..."
python -m pip install {requests,bs4,touch}
echo "Finished"
