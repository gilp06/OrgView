import dearpygui.dearpygui as dpg
import urllib.parse
import webbrowser
import csv
import re
import os


def hyperlink(display, address, tag):
    b = dpg.add_button(label=display, callback=lambda: webbrowser.open(address), tag=tag)
    dpg.bind_item_theme(item=tag, theme="hyperlinkTheme")


def export(file_path, data, labels):
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([col[0] for col in labels])
        writer.writerows(data)


def get_validation_issues(organization):
    strings = []
    print(organization.get_values_as_tuple())
    if organization.organization_name == "":
        strings.append("Please enter a organization name.")
    if organization.type_of_organization == "Organization Type":
        strings.append("Please select an organization type.")
    phone_regex = re.search(r'1[\s./-]?\(?[\d]+\)?[\s./-]?[\d]+[-/.]?[\d]+\s?[\d]+', organization.contact_phone)
    if not bool(phone_regex) and organization.contact_phone != "":
        strings.append("Please enter a valid phone number.")
    email_regex = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', organization.contact_email)
    if not bool(email_regex) and organization.contact_email:
        strings.append("Please enter a valid email address.")

    return strings


def generate_google_maps_url(location_string):
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(location_string)
