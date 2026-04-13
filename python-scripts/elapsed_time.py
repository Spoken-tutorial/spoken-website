import requests
import csv
from datetime import datetime
import time

INPUT_FILE = "foss-lang.csv"
OUTPUT_FILE = "request_results.csv"

# Limit number of output rows (you can change this!)
counter = 50

# Spoken Tutorial search URL
BASE_URL = "https://beta.spoken-tutorial.org/tutorial-search/"


def make_request(url, params):
    timestamp = datetime.now().isoformat()
    try:
        res = requests.get(url, params=params, timeout=10)
        elapsed = res.elapsed.total_seconds()
        status = res.status_code
        return elapsed, status, timestamp
    except:
        return None, None, timestamp


def main():
    with open(INPUT_FILE, "r") as infile, open(OUTPUT_FILE, "w", newline="") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)

        # CSV header
        writer.writerow([
            "foss",
            "language",
            "url",
            "elapsed1",
            "elapsed2",
            "status_code",
            "timestamp"
        ])

        count = 0

        for row in reader:

            if count >= counter:
                break

            foss = row["foss"].strip()
            language = row["language"].strip()

            # Replace spaces with "+" for URL
            foss_url = foss.replace(" ", "+")

            # Build URL correctly
            final_url = (
                f"{BASE_URL}?search_foss={foss_url}"
                f"&search_language={language}"
            )

            params = {
                "search_foss": foss,
                "search_language": language
            }

            # 1st request
            elapsed1, status1, ts1 = make_request(BASE_URL, params)

            time.sleep(1)

            # 2nd request
            elapsed2, status2, ts2 = make_request(BASE_URL, params)

            final_status = status2 if status2 is not None else status1
            final_timestamp = ts2

            writer.writerow([
                foss,
                language,
                final_url,
                elapsed1,
                elapsed2,
                final_status,
                final_timestamp
            ])

            print(f"Done → {foss}-{language}: {elapsed1}s, {elapsed2}s")
            count += 1

    print("\nCSV created:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
