import csv
import os


def export(file_path, data, labels):
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([col[0] for col in labels])
        writer.writerows(data)
