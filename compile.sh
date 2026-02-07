#!/bin/bash

# Thesis Compilation Script
# Compiles the LaTeX thesis with proper bibliography processing

set -e  # Exit on error

# Add MacTeX to PATH
export PATH="/Library/TeX/texbin:$PATH"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to script directory
cd "$(dirname "$0")"

echo -e "${YELLOW}=== Compiling Thesis ===${NC}"
echo ""

# First pass - generate aux files
echo -e "${YELLOW}[1/4]${NC} Running pdflatex (first pass)..."
pdflatex -interaction=nonstopmode thesis.tex > /dev/null 2>&1
echo -e "${GREEN}      Done${NC}"

# Process bibliography
echo -e "${YELLOW}[2/4]${NC} Running biber (bibliography)..."
biber thesis > /dev/null 2>&1
echo -e "${GREEN}      Done${NC}"

# Second pass - include bibliography
echo -e "${YELLOW}[3/4]${NC} Running pdflatex (second pass)..."
pdflatex -interaction=nonstopmode thesis.tex > /dev/null 2>&1
echo -e "${GREEN}      Done${NC}"

# Third pass - resolve references
echo -e "${YELLOW}[4/4]${NC} Running pdflatex (final pass)..."
pdflatex -interaction=nonstopmode thesis.tex > /dev/null 2>&1
echo -e "${GREEN}      Done${NC}"

echo ""
echo -e "${GREEN}=== Compilation Complete ===${NC}"
echo -e "Output: ${YELLOW}thesis.pdf${NC} ($(du -h thesis.pdf | cut -f1))"
echo ""

# Optionally open the PDF
if [[ "$1" == "--open" ]] || [[ "$1" == "-o" ]]; then
    open thesis.pdf
fi
