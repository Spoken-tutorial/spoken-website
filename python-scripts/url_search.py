import re
import matplotlib.pyplot as plt

def analyze_log(log_file_path):
    """
    User will be asked to enter the URL substring interactively.
    """

    # Ask the user to enter a URL substring dynamically
    url_keyword = input("Enter the URL substring to search: ").strip()

    pattern = re.compile(
        r'GET\s+(\S+)\s+=>.*?in\s+(\d+)\s+msecs',
        re.IGNORECASE
    )

    times = []

    # Read large log file efficiently
    with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                url = match.group(1)
                time = int(match.group(2))

                if url_keyword in url:
                    times.append(time)

    if not times:
        print(f"\n No matching entries found for: {url_keyword}")
        return

    min_time = min(times)
    max_time = max(times)

    print("\n========== ANALYSIS RESULT ==========")
    print(f"URL Searched        : {url_keyword}")
    print(f"Total Requests      : {len(times)}")
    print(f"Min Response Time   : {min_time} ms")
    print(f"Max Response Time   : {max_time} ms")
    print("======================================\n")

    # Histogram bins: 0–500, 500–1000, ...
    max_bin = ((max_time // 500) + 1) * 500
    bins = list(range(0, max_bin + 500, 500))

    # Improve figure size so x-labels don't overlap
    plt.figure(figsize=(14, 6))

    plt.hist(times, bins=bins, edgecolor='black')
    plt.title(f"Response Time Histogram for '{url_keyword}'")
    plt.xlabel("Response Time (ms)")
    plt.ylabel("Number of Requests")

    # Rotate labels so they are visible
    plt.xticks(bins, rotation=45, ha='right')

    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()  # prevents clipping
    plt.show()



log_path = "./django_spoken.log"
analyze_log(log_path)
