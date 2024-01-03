import dearpygui.dearpygui as dpg
import psycopg
import themes
import util
from database_manager import Database


# Create a program that allows your school’s Career and Technical Education Department to
# collect and store information about local business and community partners. This program
# should include information on at least 25 different partners, with details such as, but not
# limited to, type of organization, resources available, and direct contact information for an
# individual. The program should enable users to search and filter the information as needed.

class LocalData:
    database = None
    workplaces = []
    accounts_tab = 0
    workplaces_tab = 0
    tab_bar = 0


admin = True
dpg.create_context()
# Basically all draw code is written here and must be updated within the dpg.window thingy
themes.add_themes()
with dpg.font_registry():
    default_font = dpg.add_font("fonts/NotoSansDisplay-Regular.ttf", 20)
    title_font = dpg.add_font("fonts/NotoSansDisplay-Regular.ttf", 32)
    bold_font = dpg.add_font("fonts/NotoSansDisplay-Bold.ttf", 20)


def draw_accounts_panel():
    with dpg.tab(label="Accounts", parent=LocalData.tab_bar) as LocalData.accounts_tab:
        dpg.add_input_text(callback=search_users_callback, width=-1, hint="Search Users...", tag="UserSearch")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Refresh", callback=refresh_all_content)
            dpg.add_button(label="+", callback=show_add_user_modal)
        dpg.add_separator()


def draw_login_panel():
    def connection_options_callback(sender, unused, user_data):
        if dpg.is_item_shown(connection_options_group):
            dpg.configure_item(connection_options_group, show=False)
            dpg.configure_item(login_id, height=102)
        else:
            dpg.configure_item(connection_options_group, show=True)
            dpg.configure_item(login_id, height=164)

    def login_to_database(sender, unused, user_data):
        dpg.disable_item(login_button)
        dpg.configure_item(login_id, height=135)
        dpg.set_value(status, "Connecting...")
        dpg.show_item(status)
        try:
            LocalData.database = Database(dpg.get_value(username), dpg.get_value(password), dpg.get_value(address),
                                          dpg.get_value(port))
        except psycopg.errors.ConnectionTimeout:
            dpg.set_value(status, "Connection Timed Out.")
            dpg.enable_item(login_button)
            return
        except psycopg.errors.OperationalError:
            dpg.set_value(status, "Invalid Username or Password.")
            dpg.enable_item(login_button)
            return
        dpg.hide_item(login_id)
        draw_workplaces_panel()
        draw_accounts_panel()
        refresh_all_content()

    with dpg.mutex():
        height = 102
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        width = viewport_width // 2
        with dpg.window(no_title_bar=True, modal=True, no_close=True, width=width, height=height, no_move=True,
                        no_resize=True) as login_id:
            username = dpg.add_input_text(width=-1, hint="Username")
            password = dpg.add_input_text(width=-1, hint="Password", password=True)
            status = dpg.add_text(parent=login_id, label="Connecting", show=False)
            with dpg.group(show=False) as connection_options_group:
                address = dpg.add_input_text(label="Address", default_value="localhost")
                port = dpg.add_input_text(label="Port", default_value="5432")
            with dpg.group(horizontal=True):
                login_button = dpg.add_button(label="Sign in", callback=login_to_database)
                dpg.add_button(label="Options", callback=connection_options_callback)
        dpg.set_item_pos(login_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])


def export_workplaces_callback():
    def file_dialog_callback(sender, appdata):
        LocalData.database.export_data(appdata['file_path_name'])

    with dpg.file_dialog(callback=file_dialog_callback, default_filename="export", file_count=1, modal=True):
        dpg.add_file_extension(".csv")


def draw_workplaces_panel():
    with dpg.tab(label="Workplaces", parent=LocalData.tab_bar) as LocalData.workplaces_tab:
        dpg.add_input_text(callback=search_workplaces_callback, width=-1, hint="Search Workplaces...")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Refresh", callback=refresh_all_content)
            dpg.add_button(label="Export", callback=lambda: export_workplaces_callback())
            dpg.add_button(label="+", show=False, callback=lambda: show_modify_modal(), tag="AddButton")
        dpg.add_separator()


def show_delete_prompt(workplace):
    def delete_callback(sender, unused, user_data):
        if user_data:
            LocalData.database.delete_id(workplace[0])
            refresh_all_content()
        dpg.hide_item(delete_id)

    with dpg.mutex():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        with dpg.window(no_title_bar=True, modal=True, no_close=True, autosize=True, no_move=True) as delete_id:
            dpg.add_text("Do you really want to delete this workplace?", wrap=-1)
            dpg.add_text()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Yes", width=150, user_data=True, callback=delete_callback)
                dpg.add_button(label="No", width=150, user_data=False, callback=delete_callback)
    dpg.split_frame()
    width = dpg.get_item_width(delete_id)
    height = dpg.get_item_height(delete_id)
    dpg.set_item_pos(delete_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])


def search_workplaces_callback(sender, filter_string):
    dpg.set_value("workplace_filter_id", filter_string)


def search_users_callback(sender, filter_string):
    refresh_accounts_content(filter_string)


def show_modify_modal(wp=("", "", "", "", "", "", "", "", "", ""), edit=False):
    def add_modal_callback(sender, unused, user_data):
        new_data = (
            dpg.get_value(new_input_organization_name),
            dpg.get_value(new_input_type_of_organization),
            dpg.get_value(new_input_location),
            dpg.get_value(new_input_resources_available),
            dpg.get_value(new_input_contact_person),
            dpg.get_value(new_input_contact_email),
            dpg.get_value(new_input_contact_phone),
            dpg.get_value(new_input_website),
            dpg.get_value(new_input_description)
        )
        if user_data[1]:
            if edit:
                LocalData.database.edit_id(new_data, wp[0])
            else:
                LocalData.database.add_content(new_data)
            refresh_all_content()
        dpg.set_value(new_input_organization_name, "")
        dpg.set_value(new_input_type_of_organization, "")
        dpg.set_value(new_input_location, "")
        dpg.set_value(new_input_website, "")
        dpg.set_value(new_input_resources_available, "")
        dpg.set_value(new_input_contact_person, "")
        dpg.set_value(new_input_contact_email, "")
        dpg.set_value(new_input_contact_phone, "")
        dpg.set_value(new_input_description, "")
        dpg.hide_item(add_modal_id)

    with dpg.mutex():
        viewport_width = dpg.get_item_width("Primary Window")
        viewport_height = dpg.get_item_height("Primary Window")
        width = viewport_width // 1.5
        height = viewport_height // 1.5
        with dpg.window(no_title_bar=True, modal=True, no_close=True, width=width, height=height, no_move=True,
                        no_resize=True) as add_modal_id:
            title = dpg.add_text("Edit Business/Organization") if edit else dpg.add_text("Add Business/Organization")
            dpg.bind_item_font(title, title_font)
            # todo add better text input boxes
            with dpg.group(width=-1):
                new_input_organization_name = dpg.add_input_text(hint="Organization Name", default_value=wp[1])
                new_input_type_of_organization = dpg.add_combo(items=LocalData.database.get_enum_options(),
                                                               default_value=(
                                                                   "Organization Type" if wp[2] == "" else wp[2]))
                new_input_location = dpg.add_input_text(hint="Location", default_value=wp[3])
                new_input_website = dpg.add_input_text(hint="Website", default_value=wp[8])
                dpg.add_text("Resources Available")
                new_input_resources_available = dpg.add_input_text(multiline=True, default_value=wp[4])
                dpg.add_text("Contact Information")
                new_input_contact_person = dpg.add_input_text(hint="Name", width=-1, default_value=wp[5])
                new_input_contact_email = dpg.add_input_text(hint="Email", no_spaces=True, width=-1,
                                                             default_value=wp[6])
                new_input_contact_phone = dpg.add_input_text(hint="Phone", decimal=True, no_spaces=True,
                                                             default_value=wp[7])
                dpg.add_text("Description")
                new_input_description = dpg.add_input_text(multiline=True, default_value=wp[9])
            with dpg.group(horizontal=True):
                dpg.add_button(label="Save", user_data=(add_modal_id, True), callback=add_modal_callback)
                dpg.add_button(label="Cancel", user_data=(add_modal_id, False), callback=add_modal_callback)
    dpg.split_frame()
    dpg.set_item_pos(add_modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])


def refresh_workplace_content(editor):
    def collapse_item_callback(sender, unused, userdata):
        if userdata[0]:
            dpg.set_item_user_data(sender, (False, userdata[1]))
            dpg.set_item_label(sender, "Show more")
            dpg.hide_item(userdata[1])
        else:
            dpg.set_item_user_data(sender, (True, userdata[1]))
            dpg.set_item_label(sender, "Show less")
            dpg.show_item(userdata[1])

    dpg.delete_item("workplace_content")
    LocalData.workplaces = LocalData.database.get_workplace_content()
    with dpg.group(tag="workplace_content", parent=LocalData.workplaces_tab):
        with dpg.filter_set(id="workplace_filter_id"):
            for wp in LocalData.workplaces:
                with dpg.group(filter_key=wp[1].lower(), tag=wp[0]):
                    title = dpg.add_text(wp[1], wrap=0)
                    dpg.bind_item_font(title, title_font)
                    t = dpg.add_text(wp[2], wrap=0)
                    with dpg.group(show=False) as collapse:
                        loc = dpg.add_text("Location", wrap=0)
                        dpg.bind_item_font(loc, bold_font)
                        util.hyperlink(wp[3], util.generate_google_maps_url(wp[3]))

                        wh = dpg.add_text("Website", wrap=0)
                        dpg.bind_item_font(wh, bold_font)
                        util.hyperlink(wp[8], wp[8])

                        resources = dpg.add_text("Resources Available")
                        dpg.bind_item_font(resources, bold_font)
                        dpg.add_text(wp[4])

                        contact = dpg.add_text("Contact Information", wrap=0)
                        dpg.bind_item_font(contact, bold_font)
                        dpg.add_text(wp[5])
                        dpg.add_text(wp[6])
                        dpg.add_text(wp[7])

                        description = dpg.add_text("Description")
                        dpg.bind_item_font(description, bold_font)
                        dpg.add_text(wp[9])

                    with dpg.group(horizontal=True):
                        b = dpg.add_button(label="Show more", user_data=(False, collapse),
                                           callback=collapse_item_callback)
                        dpg.bind_item_theme(b, "ClickableText")
                        b = dpg.add_button(label="Edit", show=editor, user_data=wp, callback=edit_callback)
                        dpg.bind_item_theme(b, "ClickableText")
                        b = dpg.add_button(label="Delete", show=editor, user_data=wp, callback=delete_modal_callback)
                        dpg.bind_item_theme(b, "ClickableText")
                    dpg.add_separator()


def show_reset_password(sender, unused, user):
    def reset_password_callback(s, u, accepted):
        if accepted[0]:
            print("Change password")
            LocalData.database.change_password(user, dpg.get_value(pw))
            refresh_all_content()
        dpg.hide_item(reset_id)

    with dpg.mutex():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        with dpg.window(no_title_bar=True, modal=True, no_close=True, autosize=True, no_move=True) as reset_id:
            dpg.add_text("Please enter a new password:")
            pw = dpg.add_input_text(password=True)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Confirm", width=150, user_data=(True, pw), callback=reset_password_callback)
                dpg.add_button(label="Cancel", width=150, user_data=(False, ""), callback=reset_password_callback)
    dpg.split_frame()
    width = dpg.get_item_width(reset_id)
    height = dpg.get_item_height(reset_id)
    dpg.set_item_pos(reset_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])


def show_add_user_modal():
    def add_modal_callback(sender, unused, user_data):
        if user_data[1]:
            new_name = dpg.get_value(new_input_name)
            new_password = dpg.get_value(new_input_password)
            LocalData.database.add_user(new_name, new_password)
            refresh_all_content()
        dpg.set_value(new_input_name, "")
        dpg.set_value(new_input_password, "")
        dpg.hide_item(add_user_modal_id)

    with dpg.mutex():
        viewport_width = dpg.get_item_width("Primary Window")
        viewport_height = dpg.get_item_height("Primary Window")

        with dpg.window(no_title_bar=True, modal=True, no_close=True, autosize=True, no_move=True) as add_user_modal_id:
            title = dpg.add_text("Add User")
            dpg.bind_item_font(title, title_font)
            # todo add better text input boxes
            new_input_name = dpg.add_input_text(label="Username")
            new_input_password = dpg.add_input_text(label="Password")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Save", user_data=(add_user_modal_id, True), callback=add_modal_callback)
                dpg.add_button(label="Cancel", user_data=(add_user_modal_id, False), callback=add_modal_callback)
    dpg.split_frame()
    width = dpg.get_item_width(add_user_modal_id)
    height = dpg.get_item_height(add_user_modal_id)
    dpg.set_item_pos(add_user_modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])


def refresh_accounts_content(filter_string):
    def change_role_callback(sender, unused, user_data):
        print(user_data)
        if user_data[0]:
            LocalData.database.set_role_for_user(user_data[1], 'viewer')
            LocalData.database.remove_role_for_user(user_data[1], 'editor')
        else:
            LocalData.database.set_role_for_user(user_data[1], 'editor')
            LocalData.database.remove_role_for_user(user_data[1], 'viewer')
        refresh_accounts_content(filter_string)

    def delete_user_callback(sender, unused, user_data):
        LocalData.database.delete_user(user_data)
        refresh_all_content()

    user_list = list(LocalData.database.get_users())
    user_list.sort()
    dpg.delete_item("accounts_content")
    if 'admin' not in LocalData.database.roles:
        return
    with dpg.group(tag="accounts_content", parent=LocalData.accounts_tab):
        with dpg.table(header_row=True):
            dpg.add_table_column(label="Username")
            dpg.add_table_column(label="Permissions")
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()
            for i in user_list:
                if filter_string not in i[0]:
                    continue
                with dpg.table_row():
                    role = LocalData.database.get_roles_for_user(i[0])[0]
                    dpg.add_text(i[0])
                    dpg.add_text(str.title(role))
                    if role != 'admin':
                        text = "Enable Editing" if role == 'viewer' else "Disable Editing"
                        dpg.add_button(label=text, user_data=(role == 'editor', i[0]), callback=change_role_callback)
                        dpg.add_button(label="Reset Password", user_data=i[0], callback=show_reset_password)
                        dpg.add_button(label="Delete User", user_data=i[0], callback=delete_user_callback)


def refresh_all_content():
    LocalData.database.update_roles()
    dpg.hide_item(LocalData.accounts_tab)
    editor = False
    if 'admin' in LocalData.database.roles:
        dpg.show_item(LocalData.accounts_tab)
        editor = True
        dpg.show_item("AddButton")
    if 'editor' in LocalData.database.roles:
        dpg.hide_item(LocalData.accounts_tab)
        editor = True
        dpg.show_item("AddButton")
    if 'viewer' in LocalData.database.roles:
        dpg.hide_item(LocalData.accounts_tab)
        dpg.hide_item("AddButton")
    refresh_workplace_content(editor)
    refresh_accounts_content(dpg.get_value("UserSearch"))


def delete_modal_callback(sender, unused, user_data):
    show_delete_prompt(user_data)


def edit_callback(sender, unused, user_data):
    show_modify_modal(user_data, edit=True)


def visible_call(sender, app_data):
    print("visible")
    draw_login_panel()
    dpg.bind_item_handler_registry("Primary Window", 0)


with dpg.item_handler_registry(tag="primary_handler") as handler:
    dpg.add_item_visible_handler(callback=visible_call)

with dpg.window(tag="Primary Window"):
    dpg.bind_font(default_font)
    LocalData.tab_bar = dpg.add_tab_bar()

dpg.bind_item_handler_registry("Primary Window", "primary_handler")

dpg.create_viewport(title="CTEdb", width=800, height=600)
dpg.toggle_viewport_fullscreen()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
