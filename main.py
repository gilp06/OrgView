import dearpygui.dearpygui as dpg
import ctypes

# Create a program that allows your school’s Career and Technical Education Department to
# collect and store information about local business and community partners. This program
# should include information on at least 25 different partners, with details such as, but not
# limited to, type of organization, resources available, and direct contact information for an
# individual. The program should enable users to search and filter the information as needed.

admin = True
workplaces = [
    {'Name': "CES95", 'Phone Number': "(618) 457-3591", 'Address': "1150 E Grand Ave, Carbondale, IL 62901"},
    {'Name': "Workplace 2", 'Phone Number': "(618) 457-3591", 'Address': "1150 E Grand Ave, Carbondale, IL 62901"},
    {'Name': "Workplace 3", 'Phone Number': "(618) 457-3591", 'Address': "1150 E Grand Ave, Carbondale, IL 62901"},
    ]




dpg.create_context()
# Basically all draw code is written here and must be updated within the dpg.window thingy

with dpg.font_registry():
    default_font = dpg.add_font("fonts/NotoSansDisplay-Regular.ttf", 20)
    title_font = dpg.add_font("fonts/NotoSansDisplay-Regular.ttf", 28)
    bold_font = dpg.add_font("fonts/NotoSansDisplay-Bold.ttf", 20)

def search_callback(sender, filter_string):
    dpg.set_value("filter_id", filter_string)

def draw_workplaces_panel():
    dpg.add_input_text(callback=search_callback, width=-1, hint="Search...")
    with dpg.group(horizontal=True):
        dpg.add_button(label="+")
        dpg.add_button(label="Refresh")
    dpg.add_separator()
    with dpg.filter_set(id="filter_id"):
        for wp in workplaces:
            with dpg.group(filter_key=wp["Name"].lower()):
                title = dpg.add_text(wp['Name'])
                dpg.bind_item_font(title, title_font)

                desc = dpg.add_text("About")
                dpg.bind_item_font(desc, bold_font)

                loc = dpg.add_text("Location")
                dpg.bind_item_font(loc, bold_font)

                contact = dpg.add_text("Contact Information")
                dpg.bind_item_font(contact, bold_font)

                dpg.add_separator()
    pass

with dpg.window(tag="Primary Window"):
    dpg.bind_font(default_font)
    with dpg.tab_bar():
        with dpg.tab(label="Workplaces"):
            draw_workplaces_panel()

dpg.create_viewport(title="CCHS Coding and Programming", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
