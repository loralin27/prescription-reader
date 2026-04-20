#!/usr/bin/env bash
set -e

apt-get update -y
apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
pip install -r requirements.txt