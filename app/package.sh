#!/bin/bash

# Pakkeringsskript for Boliganalyseverktøy
# Dette skriptet pakker applikasjonen for distribusjon

echo "Pakker Boliganalyseverktøy for distribusjon..."
echo "=============================================="

# Opprett distribusjonsmappen hvis den ikke eksisterer
mkdir -p dist

# Pakk prosjektet som en zip-fil
echo "Oppretter zip-arkiv..."
zip -r dist/boliganalyseverktoy.zip . -x "*.git*" -x "*.pyc" -x "__pycache__/*" -x "dist/*" -x "*.zip"

echo ""
echo "Pakking fullført!"
echo "Distribusjonsfilen er tilgjengelig i: dist/boliganalyseverktoy.zip"
echo ""
echo "For å installere på en ny maskin:"
echo "1. Pakk ut zip-filen"
echo "2. Naviger til den utpakkede mappen"
echo "3. Kjør ./install.sh"
echo "4. Følg instruksjonene i README.md"
