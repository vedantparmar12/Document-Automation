#!/bin/bash
# chunk-diff.sh - Chunk large PR diffs into manageable pieces
# Usage: ./chunk-diff.sh <PR_NUMBER> <REPO> [MAX_LINES_PER_CHUNK]

set -e

PR_NUMBER=$1
REPO=$2
MAX_LINES=${3:-200}

if [ -z "$PR_NUMBER" ] || [ -z "$REPO" ]; then
  echo "Usage: ./chunk-diff.sh <PR_NUMBER> <REPO> [MAX_LINES_PER_CHUNK]"
  echo "Example: ./chunk-diff.sh 123 owner/repo 200"
  exit 1
fi

echo "Analyzing PR #$PR_NUMBER in $REPO"
echo "Maximum lines per chunk: $MAX_LINES"
echo ""

# Get list of changed files
FILES=$(gh pr diff $PR_NUMBER --repo $REPO --name-only)
FILE_COUNT=$(echo "$FILES" | wc -l)

echo "Files changed: $FILE_COUNT"
echo ""

CHUNK_NUM=1
TEMP_DIR=$(mktemp -d)

for file in $FILES; do
  echo "Processing: $file"

  # Get diff for this file
  DIFF=$(gh pr diff $PR_NUMBER --repo $REPO -- "$file")

  # Count lines in diff
  LINE_COUNT=$(echo "$DIFF" | wc -l)

  if [ $LINE_COUNT -le $MAX_LINES ]; then
    echo "  Size: $LINE_COUNT lines (single chunk)"

    # Save as single chunk
    echo "$DIFF" > "$TEMP_DIR/chunk_${CHUNK_NUM}_${file//\//_}.diff"
    echo "$file" > "$TEMP_DIR/chunk_${CHUNK_NUM}_${file//\//_}.info"
    echo "Lines: $LINE_COUNT" >> "$TEMP_DIR/chunk_${CHUNK_NUM}_${file//\//_}.info"
    CHUNK_NUM=$((CHUNK_NUM + 1))
  else
    echo "  Size: $LINE_COUNT lines (splitting into chunks)"

    # Split into chunks
    echo "$DIFF" | split -l $MAX_LINES -d - "$TEMP_DIR/chunk_${CHUNK_NUM}_${file//\//_}_part_"

    # Count how many chunks were created
    PART_COUNT=$(ls "$TEMP_DIR/chunk_${CHUNK_NUM}_${file//\//_}_part_"* 2>/dev/null | wc -l)
    echo "  Created $PART_COUNT chunks"

    # Rename chunks and create info files
    PART_NUM=1
    for chunk_file in "$TEMP_DIR/chunk_${CHUNK_NUM}_${file//\//_}_part_"*; do
      NEW_NAME="$TEMP_DIR/chunk_${CHUNK_NUM}_${file//\//_}_${PART_NUM}.diff"
      mv "$chunk_file" "$NEW_NAME"

      echo "$file (part $PART_NUM/$PART_COUNT)" > "${NEW_NAME%.diff}.info"
      echo "Lines: ~$MAX_LINES" >> "${NEW_NAME%.diff}.info"

      PART_NUM=$((PART_NUM + 1))
    done

    CHUNK_NUM=$((CHUNK_NUM + PART_COUNT))
  fi
done

TOTAL_CHUNKS=$((CHUNK_NUM - 1))
echo ""
echo "================================"
echo "Chunking complete!"
echo "Total chunks created: $TOTAL_CHUNKS"
echo "Chunks saved to: $TEMP_DIR"
echo ""
echo "To view a specific chunk:"
echo "  cat $TEMP_DIR/chunk_N_*.diff"
echo ""
echo "To view chunk info:"
echo "  cat $TEMP_DIR/chunk_N_*.info"
echo ""
echo "To clean up:"
echo "  rm -rf $TEMP_DIR"
