import dearpygui.dearpygui as dpg
import urllib.parse
import webbrowser
import csv
import os


def hyperlink(display, address, tag):
    b = dpg.add_button(label=display, callback=lambda: webbrowser.open(address), tag=tag)
    dpg.bind_item_theme(item=tag, theme="hyperlinkTheme")


def export(file_path, data, labels):
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([col[0] for col in labels])
        writer.writerows(data)


def generate_google_maps_url(location_string):
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(location_string)
