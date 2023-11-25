import dearpygui.dearpygui as dpg
import dearpygui.demo
from workplace import Workplace
import ctypes


# Create a program that allows your school’s Career and Technical Education Department to
# collect and store information about local business and community partners. This program
# should include information on at least 25 different partners, with details such as, but not
# limited to, type of organization, resources available, and direct contact information for an
# individual. The program should enable users to search and filter the information as needed.


class LocalData:
    workplaces = [
        Workplace(name="Carbondale Elementary District 95", about="K-8 District in Carbondale", phone="(618) 457-3591",
                  address="1150 E Grand Ave, Carbondale, IL 62901")

    ]


admin = True
dpg.create_context()
# Basically all draw code is written here and must be updated within the dpg.window thingy

with dpg.font_registry():
    default_font = dpg.add_font("fonts/NotoSansDisplay-Regular.ttf", 20)
    title_font = dpg.add_font("fonts/NotoSansDisplay-Regular.ttf", 28)
    bold_font = dpg.add_font("fonts/NotoSansDisplay-Bold.ttf", 20)


def search_callback(sender, filter_string):
    dpg.set_value("filter_id", filter_string)


def delete_callback(sender, unused, user_data):
    LocalData.workplaces.remove(user_data)
    refresh_content()


def show_modify_modal(wp=Workplace("", "", "", ""), edit=False):
    def add_modal_callback(sender, unused, user_data):
        if user_data[1]:
            new_name = dpg.get_value(new_input_name)
            new_about = dpg.get_value(new_input_about)
            new_phone = dpg.get_value(new_input_phone)
            new_address = dpg.get_value(new_input_address)
            if edit:
                wp.name = new_name
                wp.about = new_about
                wp.phone = new_phone
                wp.address = new_address
            else:
                LocalData.workplaces.append(Workplace(name=new_name, phone=new_phone, address=new_address, about=new_about))
            print(LocalData.workplaces)
            refresh_content()
        dpg.set_value(new_input_name, "")
        dpg.set_value(new_input_phone, "")
        dpg.set_value(new_input_address, "")
        dpg.hide_item(add_modal_id)

    with dpg.mutex():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()

        with dpg.window(no_title_bar=True, modal=True, no_close=True, autosize=True, no_move=True) as add_modal_id:
            title = dpg.add_text("Edit Business/Organization") if edit else dpg.add_text("Add Business/Organization")
            dpg.bind_item_font(title, title_font)
            # todo add better text input boxes
            new_input_name = dpg.add_input_text(label="Name", default_value=wp.name)
            new_input_about = dpg.add_input_text(label="About", multiline=True, default_value=wp.about)
            new_input_phone = dpg.add_input_text(label="Phone Number", default_value=wp.phone)
            new_input_address = dpg.add_input_text(label="Address", default_value=wp.address)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Save", user_data=(add_modal_id, True), callback=add_modal_callback)
                dpg.add_button(label="Cancel", user_data=(add_modal_id, False), callback=add_modal_callback)
    dpg.split_frame()
    width = dpg.get_item_width(add_modal_id)
    height = dpg.get_item_height(add_modal_id)
    dpg.set_item_pos(add_modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])


def refresh_content():
    dpg.delete_item("workplace_content")
    with dpg.group(tag="workplace_content", parent="Primary Window"):
        with dpg.filter_set(id="filter_id"):
            for wp in LocalData.workplaces:
                with dpg.group(filter_key=wp.name.lower(), tag=wp.name):
                    title = dpg.add_text(wp.name, wrap=0)
                    dpg.bind_item_font(title, title_font)
                    desc = dpg.add_text("About", wrap=0)
                    dpg.bind_item_font(desc, bold_font)
                    dpg.add_text(wp.about)
                    loc = dpg.add_text("Location", wrap=0)
                    dpg.bind_item_font(loc, bold_font)
                    dpg.add_text(wp.address)
                    contact = dpg.add_text("Contact Information", wrap=0)
                    dpg.add_text(wp.phone)
                    dpg.bind_item_font(contact, bold_font)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Edit", show=admin, user_data=wp, callback=edit_callback)
                        dpg.add_button(label="Delete", show=admin, user_data=wp, callback=delete_callback)
                    dpg.add_separator()


def edit_callback(sender, unused, user_data):
    show_modify_modal(user_data, edit=True)


def draw_workplaces_panel():
    dpg.add_input_text(callback=search_callback, width=-1, hint="Search...")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Refresh")
        dpg.add_button(label="+", show=admin, callback=lambda: show_modify_modal())
    dpg.add_separator()
    refresh_content()


with dpg.window(tag="Primary Window"):
    dpg.bind_font(default_font)
    with dpg.tab_bar():
        with dpg.tab(label="Workplaces"):
            draw_workplaces_panel()

dearpygui.demo.show_demo()

dpg.create_viewport(title="CCHS Coding and Programming", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
