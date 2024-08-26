import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import massbots

mb = massbots.Api(token=os.environ["TOKEN"])

# Use basic methods
try:
    balance = mb.balance()
    print(f"Balance: {balance}")
except massbots.Error as e:
    print(e)


VIDEO_ID = "R6rhxJjVNCU"

# Use /yt/ group methods
try:
    video = mb.yt.video(VIDEO_ID)
    print(f"Video: {video.title}")

    channel = mb.yt.channel(video.channel_id)
    print(f"Channel: {channel.title}")
except massbots.Error as e:
    print(e)

# Use /dl/ group methods
try:
    # Get available video formats
    video = mb.dl.video(VIDEO_ID)
    cached = video.formats_cached
    uncached = video.formats_uncached

    print(f"Cached formats: {', '.join(cached.keys())}")
    print(f"Uncached formats: {', '.join(uncached.keys())}")

    # Transfer the cached video to your bot instantly
    if len(cached) > 0:
        format = list(cached.keys())[0]
        file_id = mb.dl.video_cached(VIDEO_ID, format)
        print(f"Telegram file_id: {file_id}")

    # Download the video and transfer it to your bot
    if len(uncached) > 0:
        format = list(uncached.keys())[0]
        result = mb.dl.video_download(VIDEO_ID, format)

        print(f"\nStarted downloading {format}...")
        print(f"Status: {result.status}")

        result = result.wait_until_ready(
            callback=lambda r: print(f"Status: {r.status}"),
        )

        if result.status == "ready":
            print(f"Telegram file_id: {result.file_id}")
except massbots.Error as e:
    print(e)
