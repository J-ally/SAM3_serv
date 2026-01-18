#!/bin/bash

# =========================
# Usage check
# =========================
if [ $# -ne 2 ]; then
    echo "Usage: $0 <path_to_sam3_repo> <max_num_objects>"
    exit 1
fi

SAM3_PATH="$1"
MAX_OBJECTS="$2"
FILE="${SAM3_PATH}/sam3/model/sam3_video_base.py"
LINE_NUMBER=124

# =========================
# Check that the file exists
# =========================
if [ ! -f "$FILE" ]; then
    echo "Error: file $FILE not found."
    exit 1
fi

# =========================
# Replace max_num_objects value
# =========================
sed -i "${LINE_NUMBER}s/max_num_objects = [0-9]\+/max_num_objects = ${MAX_OBJECTS}/" "$FILE"

# =========================
# Check that the modification was applied
# =========================
LINE_CONTENT=$(sed -n "${LINE_NUMBER}p" "$FILE")
echo "Line ${LINE_NUMBER} content after modification: $LINE_CONTENT"

echo "Modification completed successfully."
