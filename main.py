import dearpygui.dearpygui as dpg
import ctypes

dpg.create_context()
dpg.create_viewport(title="CCHS Coding and Programming", width=800, height=600)

# Basically all draw code is written here and must be updated within the dpg.window thingy

with dpg.window(label="Main Window"):
    dpg.add_text("Hello world!")

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
