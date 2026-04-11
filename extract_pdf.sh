#!/bin/bash
# Extract tables and images from PDF using MinerU

INPUT_PDF="/Users/vinothkumar/CIT/hyp/3M_2018_10K.pdf"
OUTPUT_DIR="/Users/vinothkumar/CIT/hyp/3M_2018_extracted"

mkdir -p "$OUTPUT_DIR"

echo "Extracting from: $INPUT_PDF"
echo "Output to: $OUTPUT_DIR"

mineru -p "$INPUT_PDF" -o "$OUTPUT_DIR" -m auto -b pipeline -l en

echo ""
echo "=== Extraction complete ==="
echo "Output structure:"
find "$OUTPUT_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.md" -o -name "*.json" \) | head -30
