import board
import digitalio
import storage

print("setting filesystem to writable!")
storage.remount("/", readonly=True)
