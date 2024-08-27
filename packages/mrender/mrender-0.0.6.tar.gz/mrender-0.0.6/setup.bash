#!/usr/bin/env bash

echo "Starting setup script..."


# Install dependencies
if [[ "$(uname)" == "Linux" ]]; then
  sudo apt remove -y python3-lxml
  sudo apt remove -y libxml2
  sudo apt remove -y libxml2-dev
  sudo apt remove -y libxslt-dev
  pip uninstall -y lxml html5-parser
  sudo apt-get update
  sudo apt-get install -y libxml2 libxml2-dev
  sudo apt-get install -y libxslt1-dev libxslt1.1
fi
pip install --no-binary lxml html5-parser
echo "Setup script completed."
