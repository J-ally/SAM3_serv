for f in static/original/*.mp4; do
    filename=$(basename "$f")  # extract just the filename
    ffmpeg -i "$f" \
        -c:v libx264 -pix_fmt yuv420p -movflags +faststart \
        -c:a aac \
        "static/h264/$filename"
done
