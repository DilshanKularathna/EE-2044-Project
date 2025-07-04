import sys, struct, platform

# 1. Python version
print("Python version:", sys.version)

# 2. Interpreter bitness (True=64‑bit, False=32‑bit)
print("Is 64‑bit Python?", sys.maxsize > 2**32)

# 3. Pointer size in bits (bitness)
print("Pointer size:", struct.calcsize("P") * 8, "bits")

# 4. platform.architecture (may show '64bit' or '32bit')
print("platform.architecture:", platform.architecture()[0])
