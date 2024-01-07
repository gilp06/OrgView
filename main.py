import json
import dearpygui.dearpygui as dpg
import psycopg
import themes
import util
from database_manager import Database


# Create a program that allows your school’s Career and Technical Education Department to
# collect and store information about local business and community organizations. This program
# should include information on at least 25 different organizations, with details such as, but not
# limited to, type of organization, resources available, and direct contact information for an
# individual. The program should enable users to search and filter the information as needed.

# <editor-fold desc="Data storage">
class LocalData:
    database = None
    organizations = []
    accounts_tab = 0
    organizations_tab = 0
    tab_bar = 0
    wrapped_text = []
    walkthrough_steps = []
    first_edit = 0
    first_delete = 0
    sort_map = {"Organization Name": 1, "Organization Type": 2}
    sort_mode = "Organization Name"


with open("connection_settings.json", "r") as file:
    connection_config_data = json.load(file)

dpg.create_context()

with dpg.font_registry():
    default_font = dpg.add_font("fonts/NotoSansDisplay-Regular.ttf", 20)
    title_font = dpg.add_font("fonts/NotoSansDisplay-Regular.ttf", 32)
    bold_font = dpg.add_font("fonts/NotoSansDisplay-Bold.ttf", 20)


# </editor-fold>

# <editor-fold desc="Login/Initial setup">
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
        with open("connection_settings.json", "w") as writeFile:
            connection_config_data["address"] = dpg.get_value(address)
            connection_config_data["port"] = dpg.get_value(port)
            json.dump(connection_config_data, writeFile)
        dpg.hide_item(login_id)
        draw_organizations_panel()
        draw_accounts_panel()
        draw_help_panel()
        resize_viewport_callback()
        refresh_all_content()

    with dpg.mutex():
        height = 102
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        width = viewport_width // 2
        with dpg.window(no_title_bar=True, modal=True, no_close=True, width=width, height=height, no_move=True,
                        no_resize=True) as login_id:
            username = dpg.add_input_text(width=-1, hint="Username", default_value=connection_config_data["username"])
            password = dpg.add_input_text(width=-1, hint="Password", password=True)
            status = dpg.add_text(parent=login_id, label="Connecting", show=False)
            with dpg.group(show=False) as connection_options_group:
                address = dpg.add_input_text(label="Address", default_value=connection_config_data["address"])
                port = dpg.add_input_text(label="Port", default_value=connection_config_data["port"])
            with dpg.group(horizontal=True):
                login_button = dpg.add_button(label="Sign in", callback=login_to_database)
                dpg.add_button(label="Options", callback=connection_options_callback)
        dpg.set_item_pos(login_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])


# </editor-fold>

# <editor-fold desc="Draw headings of tabs">
def draw_accounts_panel():
    with dpg.tab(label="Accounts", parent=LocalData.tab_bar) as LocalData.accounts_tab:
        dpg.add_input_text(callback=search_users_callback, width=-1, hint="Search Users...", tag="UserSearch")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Refresh", callback=refresh_all_content)
            dpg.add_button(label="+", callback=show_add_user_modal)
        dpg.add_separator()


def sort_callback(sender, app_data):
    LocalData.sort_mode = app_data
    refresh_all_content()


def draw_organizations_panel():
    with dpg.tab(label="Organizations", parent=LocalData.tab_bar) as LocalData.organizations_tab:
        dpg.add_input_text(callback=search_organizations_callback, width=-1, hint="Search Organizations...",
                           tag="OrganizationSearch")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Refresh", callback=refresh_all_content, tag="Refresh")
            dpg.add_button(label="Export", callback=lambda: export_organizations_callback(), tag="Export")
            dpg.add_button(label="+", show=False, callback=lambda: show_modify_modal(), tag="AddButton")
            dpg.add_text("Sort by:")
            dpg.add_combo(items=list(LocalData.sort_map.keys()), width=160, callback=sort_callback,
                          default_value=LocalData.sort_mode)
        dpg.add_separator()


# </editor-fold>

# <editor-fold desc="Search bars">
def search_organizations_callback(sender, filter_string):
    dpg.set_value("organization_filter_id", filter_string)


def search_users_callback(sender, filter_string):
    refresh_accounts_content(filter_string)


# </editor-fold>

# <editor-fold desc="Refresh accounts menu for admins">
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


# </editor-fold>

# <editor-fold desc="Reset password menu">
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


# </editor-fold>

# <editor-fold desc="Add new user menu">
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


# </editor-fold>

# <editor-fold desc="Refresh organizations">
def refresh_organization_content(editor):
    LocalData.first_edit = 0
    LocalData.first_delete = 0

    def collapse_item_callback(sender, unused, userdata):
        if userdata[0]:
            dpg.set_item_user_data(sender, (False, userdata[1]))
            dpg.set_item_label(sender, "Show more")
            dpg.hide_item(userdata[1])
        else:
            dpg.set_item_user_data(sender, (True, userdata[1]))
            dpg.set_item_label(sender, "Show less")
            dpg.show_item(userdata[1])

    dpg.delete_item("organization_content")
    LocalData.organizations = LocalData.database.get_organization_content()
    sorted_list = sorted(list(LocalData.organizations), key=lambda x: x[LocalData.sort_map[LocalData.sort_mode]])
    with dpg.group(tag="organization_content", parent=LocalData.organizations_tab):
        with dpg.filter_set(id="organization_filter_id"):
            for wp in sorted_list:
                with dpg.group(filter_key=wp[1].lower(), tag=wp[0]):
                    title = dpg.add_text(wp[1], wrap=0)
                    dpg.bind_item_font(title, title_font)
                    t = dpg.add_text(wp[2], wrap=0)
                    with dpg.group(show=False) as collapse:

                        if wp[3] != "":
                            loc = dpg.add_text("Location", wrap=0)
                            dpg.bind_item_font(loc, bold_font)
                            util.hyperlink(wp[3], util.generate_google_maps_url(wp[3]), str(wp[0]) + "hyperlink")

                        if wp[8] != "":
                            wh = dpg.add_text("Website", wrap=0)
                            dpg.bind_item_font(wh, bold_font)
                            util.hyperlink(wp[8], wp[8], str(wp[0]) + "website")

                        resources = dpg.add_text("Resources Available")
                        dpg.bind_item_font(resources, bold_font)
                        LocalData.wrapped_text.append(dpg.add_text(wp[4]))

                        contact = dpg.add_text("Contact Information", wrap=0)
                        dpg.bind_item_font(contact, bold_font)

                        if wp[5] != "":
                            dpg.add_text(wp[5])
                        if wp[6] != "":
                            dpg.add_text(wp[6])
                        if wp[7] != "":
                            dpg.add_text(wp[7])

                        description = dpg.add_text("Description")
                        dpg.bind_item_font(description, bold_font)
                        LocalData.wrapped_text.append(dpg.add_text(wp[9]))

                    with dpg.group(horizontal=True):
                        b = dpg.add_button(label="Show more", user_data=(False, collapse),
                                           callback=collapse_item_callback)
                        dpg.bind_item_theme(b, "ClickableText")

                        b = dpg.add_button(label="Edit", show=editor, user_data=wp, callback=edit_callback)
                        dpg.bind_item_theme(b, "ClickableText")
                        if LocalData.first_edit == 0:
                            LocalData.first_edit = b

                        b = dpg.add_button(label="Delete", show=editor, user_data=wp, callback=delete_modal_callback)
                        dpg.bind_item_theme(b, "ClickableText")
                        if LocalData.first_delete == 0:
                            LocalData.first_delete = b
                    dpg.add_separator()


# </editor-fold>

# <editor-fold desc="Delete organization menu">
def show_delete_prompt(organization):
    def delete_callback(sender, unused, user_data):
        if user_data:
            LocalData.database.delete_id(organization[0])
            refresh_all_content()
        dpg.hide_item(delete_id)

    with dpg.mutex():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        with dpg.window(no_title_bar=True, modal=True, no_close=True, autosize=True, no_move=True) as delete_id:
            dpg.add_text("Do you really want to delete this organization?", wrap=-1)
            dpg.add_text()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Yes", width=150, user_data=True, callback=delete_callback)
                dpg.add_button(label="No", width=150, user_data=False, callback=delete_callback)
    dpg.split_frame()
    width = dpg.get_item_width(delete_id)
    height = dpg.get_item_height(delete_id)
    dpg.set_item_pos(delete_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])


# </editor-fold>

# <editor-fold desc="Add/Edit organizations menu">
def show_modify_modal(wp=("", "", "", "", "", "", "", "", "", ""), edit=False):
    def add_modal_callback(sender, unused, user_data):
        dpg.disable_item(sender)
        new_data = (
            dpg.get_value(new_input_organization_name),
            dpg.get_value(new_input_type_of_organization)
            if dpg.get_value(new_input_type_of_organization) != "Organization Type" else "Business",
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
        dpg.enable_item(sender)
        dpg.hide_item(add_modal_id)

    with dpg.mutex():
        viewport_width = dpg.get_item_width("Primary Window")
        viewport_height = dpg.get_item_height("Primary Window")
        width = viewport_width / 1.5
        height = viewport_height / 1.5
        with dpg.window(no_title_bar=True, modal=True, no_close=True, width=width, height=height, no_move=True,
                        no_resize=True) as add_modal_id:
            title = dpg.add_text("Edit Business/Organization") if edit else dpg.add_text("Add Business/Organization")
            dpg.bind_item_font(title, title_font)
            # todo add better text input boxes
            with dpg.group(width=-1):
                new_input_organization_name = dpg.add_input_text(hint="Organization Name", default_value=wp[1])
                enum_options = [
                    "Business", "Nonprofit", "Not-for-profit", "Government", "Other"
                ]
                new_input_type_of_organization = dpg.add_combo(items=enum_options,
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


# </editor-fold>

# <editor-fold desc="Export menu">
def export_organizations_callback():
    def file_dialog_callback(sender, appdata):
        LocalData.database.export_data(appdata['file_path_name'])

    with dpg.file_dialog(callback=file_dialog_callback, default_filename="export", file_count=1, modal=True):
        dpg.add_file_extension(".csv")


# </editor-fold>

# <editor-fold desc="Main refresh function">
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
    LocalData.wrapped_text.clear()
    LocalData.wrapped_text.append("Overview")
    refresh_organization_content(editor)
    refresh_accounts_content(dpg.get_value("UserSearch"))
    resize_viewport_callback()


# </editor-fold>

# <editor-fold desc="Help Panel">
def draw_help_panel():
    with dpg.tab(label="Help", parent=LocalData.tab_bar):
        with dpg.group(horizontal=True):
            dpg.add_text("Press this button to take a tour through CTEdb: ")
            dpg.add_button(label="Walkthrough", callback=walkthrough_callback)
        subtitle = dpg.add_text("Overview")
        dpg.bind_item_font(subtitle, bold_font)
        dpg.add_text("CTEdb is a simple and user-friendly database tool designed to help manage information for local "
                     "businesses and organizations. It allows multiple users to browse and edit information on each "
                     "business, and securely stores that information in a remote database. It always up-to-date with "
                     "the latest changes you and other contributors make. CTEdb makes data entry easy and data "
                     "exporting as well, allowing exports to .csv for use in other programs.", tag="Overview")
        subtitle = dpg.add_text("Roles")
        dpg.bind_item_font(subtitle, bold_font)
        dpg.add_text("CTEdb contains three roles with different permission levels which can be changed by "
                     "administrators.")
        dpg.add_text("Viewers: Can view entries in the database.", bullet=True)
        dpg.add_text("Editors: Can add, edit and delete entries in the database.", bullet=True)
        dpg.add_text("Admins: Can add, edit and delete entries in the database and manage other accounts.", bullet=True)
        subtitle = dpg.add_text("Forgot password?")
        dpg.bind_item_font(subtitle, bold_font)
        dpg.add_text("Ask your administrators for a password reset and they can set a new password or change your "
                     "roles.")
        subtitle = dpg.add_text("Credits")
        dpg.bind_item_font(subtitle, bold_font)
        dpg.add_text("Created by Gil Powers and Bill Xu using DearPyGui and PostgreSQL.")


# </editor-fold>

# <editor-fold desc="Walkthrough">
def walkthrough_callback(sender, unused, user_data):
    LocalData.walkthrough_steps.clear()
    LocalData.walkthrough_steps.append(("Refresh", "Refreshes all content.", 4))
    LocalData.walkthrough_steps.append(("OrganizationSearch", "Search and filter content.", 6))
    if "editor" in LocalData.database.roles or "admin" in LocalData.database.roles:
        LocalData.walkthrough_steps.append(("Export", "Opens a menu to export to a .csv file.", 4))
        LocalData.walkthrough_steps.append(("AddButton", "Add new organization to database.", 4))
        if LocalData.first_edit != 0:
            LocalData.walkthrough_steps.append((LocalData.first_edit, "Edit organization in database.", 6))
            LocalData.walkthrough_steps.append((LocalData.first_delete, "Remove organization from database.", 6))
    dpg.set_value(LocalData.tab_bar, LocalData.organizations_tab)
    pos = dpg.get_item_pos(LocalData.walkthrough_steps[0][0])
    pos[1] += dpg.get_item_rect_size(LocalData.walkthrough_steps[0][0])[1] + LocalData.walkthrough_steps[0][2]
    with dpg.window(label="Walkthrough", no_resize=True, autosize=True,
                    pos=pos, modal=True, tag="WalkthroughWindow", no_title_bar=True, no_move=True):
        dpg.add_text(LocalData.walkthrough_steps[0][1], tag="WalkthroughText")
        dpg.bind_item_theme(LocalData.walkthrough_steps[0][0], "HelpHighlight")
        dpg.add_button(label="Next", callback=next_item_in_walkthrough)


def next_item_in_walkthrough(sender, unused, user_data):
    if LocalData.walkthrough_steps[0][0] is LocalData.first_edit \
            or LocalData.walkthrough_steps[0][0] is LocalData.first_delete:
        dpg.bind_item_theme(LocalData.walkthrough_steps[0][0], "ClickableText")
    else:
        dpg.bind_item_theme(LocalData.walkthrough_steps[0][0], "")
    LocalData.walkthrough_steps.pop(0)
    if len(LocalData.walkthrough_steps) == 0:
        dpg.delete_item("WalkthroughWindow")
        return
    print(dpg.get_item_pos(LocalData.walkthrough_steps[0][0]))
    pos = dpg.get_item_pos(LocalData.walkthrough_steps[0][0])
    pos[1] += dpg.get_item_rect_size(LocalData.walkthrough_steps[0][0])[1] + LocalData.walkthrough_steps[0][2]
    dpg.set_item_pos("WalkthroughWindow", pos)
    dpg.bind_item_theme(LocalData.walkthrough_steps[0][0], "HelpHighlight")
    dpg.set_value("WalkthroughText", LocalData.walkthrough_steps[0][1])


# </editor-fold>

# <editor-fold desc="Window Callbacks">
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


def resize_viewport_callback():
    for i in LocalData.wrapped_text:
        dpg.configure_item(i, wrap=(dpg.get_viewport_client_width() - 20))


# </editor-fold>

with dpg.window(tag="Primary Window"):
    themes.add_themes()
    dpg.bind_font(default_font)
    LocalData.tab_bar = dpg.add_tab_bar()

dpg.bind_item_handler_registry("Primary Window", "primary_handler")

dpg.set_viewport_resize_callback(resize_viewport_callback)

dpg.create_viewport(title="CTEdb", width=800, height=600)
dpg.toggle_viewport_fullscreen()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
