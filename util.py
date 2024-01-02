import dearpygui.dearpygui as dpg
import webbrowser


def hyperlink(address):
    b = dpg.add_button(label=address, callback=lambda: webbrowser.open(address))
    dpg.bind_item_theme(b, "hyperlinkTheme")
