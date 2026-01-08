import csv
import statistics

filename = "evaluation_results.csv"

try:
    times = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract time string like "2.50s" -> float 2.50
            time_str = row["Time"].replace("s", "")
            times.append(float(time_str))

    if not times:
        print("No data found in evaluation_results.csv")
    else:
        min_lat = min(times)
        max_lat = max(times)
        mean_lat = statistics.mean(times)
        median_lat = statistics.median(times)

        print(f"Minimum latency: {min_lat:.2f}s")
        print(f"Maximum latency: {max_lat:.2f}s")
        print(f"Mean latency: {mean_lat:.2f}s")
        print(f"Median latency: {median_lat:.2f}s")

except FileNotFoundError:
    print(f"File {filename} not found.")
