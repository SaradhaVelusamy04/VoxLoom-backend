import base64

audio_path = "demo/hi-413164.mp3"

with open(audio_path, "rb") as f:
    audio_bytes = f.read()

audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

# Save the base64 string to a file for convenience
with open("demo/audio_base64.txt", "w") as f:
    f.write(audio_b64)

print("Base64 conversion done! Check demo/audio_base64.txt")
