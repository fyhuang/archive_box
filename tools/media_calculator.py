import sys

def main():
    bitrate_kbits = float(sys.argv[1])

    durations_mins = [5, 15, 30, 60, 90, 120]
    for mins in durations_mins:
        seconds = mins * 60
        bytes_per_second = (bitrate_kbits / 8.0) * 1024
        total_bytes = bytes_per_second * seconds
        total_mb = total_bytes / 1024 / 1024
        print("{} mins = {:.2f} MB".format(mins, total_mb))

if __name__ == "__main__":
    main()
