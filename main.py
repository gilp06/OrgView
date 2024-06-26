import json
import dearpygui.dearpygui as dpg
import psycopg
from helper import themes, util
from helper.database_manager import Database
from helper.organization import Organization
import os


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
    sort_types = ["Organization Name", "Organization Type"]
    sort_mode = "Organization Name"
    chat_history = []
    chat_history_area = None
    user_input = None
    login_id = None
    logo_id = None
    description_text_id = None


# Load connection settings from JSON file
with open("connection_settings.json", "r") as file:
    connection_config_data = json.load(file)

dpg.create_context()

# Load fonts for the application
with dpg.font_registry():
    default_font = dpg.add_font("fonts/NotoSansDisplay-Regular.ttf", 20)
    title_font = dpg.add_font("fonts/NotoSansDisplay-Regular.ttf", 32)
    bold_font = dpg.add_font("fonts/NotoSansDisplay-Bold.ttf", 20)

# Add custom themes
themes.add_themes()
dpg.bind_theme("DarkTheme")


# </editor-fold>

# <editor-fold desc="Login/Initial setup">
# Function to load texture
def load_texture(image_path):
    width, height, channels, data = dpg.load_image(image_path)
    with dpg.texture_registry(show=False):
        return dpg.add_static_texture(width, height, data)


# Draw the login panel with the logo
# Draw the login panel with the logo
def draw_login_panel():
    def connection_options_callback(sender, unused, user_data):
        toggle = not dpg.is_item_shown(connection_options_group)
        dpg.configure_item(connection_options_group, show=toggle)
        center_login_panel()

    def login_to_database(sender, unused, user_data):
        dpg.disable_item(login_button)
        dpg.set_value(status, "Connecting...")
        dpg.show_item(status)
        try:
            LocalData.database = Database(dpg.get_value(username), dpg.get_value(password), dpg.get_value(address),
                                          dpg.get_value(port))
            print("Login successful")
            if dpg.does_item_exist(LocalData.login_id):
                print("Deleting login panel")
                dpg.delete_item(LocalData.login_id)
            if dpg.does_item_exist("LogoWindow"):
                print("Deleting logo window")
                dpg.delete_item("LogoWindow")
            if dpg.does_item_exist("DescriptionWindow"):
                print("Deleting description window")
                dpg.delete_item("DescriptionWindow")
            dpg.split_frame()  # Ensure the GUI updates
            draw_main_interface()
        except (psycopg.errors.ConnectionTimeout, psycopg.errors.OperationalError) as e:
            dpg.set_value(status, "Connection Failed: " + str(e))
            dpg.enable_item(login_button)

    with dpg.mutex():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        fixed_width = 400  # Set a constant width for the login panel
        with dpg.window(no_title_bar=True, modal=True, no_close=True, width=fixed_width, autosize=True, no_move=True) as login_id:
            LocalData.login_id = login_id  # Store the login_id for future use

            input_width = fixed_width - 20  # Set a constant width for input fields
            username = dpg.add_input_text(width=input_width, hint="Username", default_value=connection_config_data["username"])
            password = dpg.add_input_text(width=input_width, hint="Password", password=True)
            status = dpg.add_text(parent=login_id, label="Connecting", show=False)
            with dpg.group(show=False) as connection_options_group:
                address = dpg.add_input_text(width=input_width, label="Address", default_value=connection_config_data["address"])
                port = dpg.add_input_text(width=input_width, label="Port", default_value=connection_config_data["port"])
            with dpg.group(horizontal=True):
                login_button = dpg.add_button(label="Sign in", callback=login_to_database)
                dpg.add_button(label="Options", callback=connection_options_callback)

    center_login_panel()  # Center the login panel initially



def draw_description():
    if not dpg.does_item_exist("DescriptionWindow"):
        with dpg.child_window(width=400, height=200, no_scrollbar=True, tag="DescriptionWindow", parent="Primary Window"):
            dpg.add_text("OrgView is a user-friendly database tool designed to help manage information for local businesses and organizations. "
                         "It allows multiple users to browse and edit information on each business, and securely stores that information in a remote database. "
                         "OrgView is always up-to-date with the latest changes made by you and other contributors. "
                         "Data entry is easy, and data exporting is supported, allowing exports to .csv for use in other programs.", wrap=380, tag="DescriptionText")


def center_login_panel():
    if dpg.does_item_exist(LocalData.login_id):
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        login_width = dpg.get_item_width(LocalData.login_id)
        login_height = dpg.get_item_height(LocalData.login_id)

        login_x = (viewport_width - login_width) // 2
        login_y = (viewport_height - login_height) // 2
        dpg.set_item_pos(LocalData.login_id, [login_x, login_y])

        if dpg.does_item_exist("LogoWindow"):
            logo_width = dpg.get_item_width("LogoWindow")
            logo_height = dpg.get_item_height("LogoWindow")
            logo_x = (viewport_width - logo_width) // 2
            logo_y = login_y - logo_height - 20
            dpg.set_item_pos("LogoWindow", [logo_x, logo_y])

        if dpg.does_item_exist("DescriptionWindow"):
            desc_width = dpg.get_item_width("DescriptionWindow")
            desc_height = dpg.get_item_height("DescriptionWindow")
            desc_x = login_x + login_width + 20
            desc_y = (viewport_height - desc_height) // 2
            dpg.set_item_pos("DescriptionWindow", [desc_x, desc_y])

def draw_logo():
    if LocalData.logo_id:
        if not dpg.does_item_exist("LogoWindow"):
            with dpg.child_window(width=200, height=200, no_scrollbar=True, tag="LogoWindow", parent="Primary Window"):
                dpg.add_image(LocalData.logo_id, width=200, height=200, tag="LogoImage")


logo_path = "Images/Logo.png"
LocalData.logo_id = load_texture(logo_path)


def visible_call(sender, app_data):
    """
    Callback triggered when the primary window becomes visible.
    - sender: The widget (window) that triggered this callback.
    - app_data: Additional data associated with the visibility event.
    """
    draw_login_panel()
    draw_logo()
    draw_description()
    center_login_panel()


# Adjust the font size for the login screen
with dpg.font_registry():
    large_font = dpg.add_font("fonts/NotoSansDisplay-Regular.ttf", 28)
    large_bold_font = dpg.add_font("fonts/NotoSansDisplay-Bold.ttf", 28)

# Bind the larger font to the login elements
dpg.bind_font(large_font)

# </editor-fold>


image_path = "Images/chat_icon.png"
image_id = load_texture(image_path)


def draw_chatbox_button():
    """Draws the chatbox button in the bottom right corner of the main window."""
    viewport_width = dpg.get_viewport_client_width()
    viewport_height = dpg.get_viewport_client_height()

    if dpg.does_item_exist("ChatboxButton"):
        dpg.delete_item("ChatboxButton")

    dpg.add_image_button(texture_tag=image_id, width=60, height=60, callback=toggle_chatbox, tag="ChatboxButton",
                         frame_padding=0, background_color=(0, 0, 0, 0), parent="Primary Window")

    dpg.set_item_pos("ChatboxButton", [viewport_width - 80, viewport_height - 100])


def draw_chatbox():
    """Draws the chatbox window in the bottom right corner of the main window."""
    viewport_width = dpg.get_viewport_client_width()
    viewport_height = dpg.get_viewport_client_height()
    with dpg.window(label="Chatbox", pos=[viewport_width - 410, viewport_height - 310], width=400, height=300,
                    show=False, tag="ChatboxWindow"):
        with dpg.group(horizontal=True):
            dpg.add_text("Chatbox")
            dpg.add_button(label="X", callback=toggle_chatbox)
        dpg.add_separator()
        LocalData.chat_history_area = dpg.add_text("", wrap=400)
        LocalData.user_input = dpg.add_input_text(label="", multiline=True, width=-1, height=100, on_enter=True,
                                                  callback=send_message)


def toggle_chatbox(sender, app_data, user_data):
    """Toggles the visibility of the chatbox window."""
    is_visible = dpg.get_item_configuration("ChatboxWindow")["show"]
    dpg.configure_item("ChatboxWindow", show=not is_visible)
    dpg.configure_item("ChatboxButton", show=not is_visible)


def send_message(sender, app_data, user_data):
    """Handles sending the user's message and displaying it in the chat history.

    Parameters:
    - sender: The widget (input text) that triggered this callback.
    - app_data: The value of the input text when the callback was triggered.
    - user_data: Optional data that can be passed to the callback.
    """
    # Get the user input from the input text widget
    message = dpg.get_value(LocalData.user_input)

    # Append the message to the chat history
    chat_history = dpg.get_value(LocalData.chat_history_area)
    updated_chat_history = f"{chat_history}\nUser: {message}"
    dpg.set_value(LocalData.chat_history_area, updated_chat_history)

    # Clear the input text widget for the next message
    dpg.set_value(LocalData.user_input, "")


def resize_viewport_callback():
    """
    Handles viewport resizing events, such as adjusting text wrapping, centering the login panel,
    and repositioning the chatbox button.
    """
    for i in LocalData.wrapped_text:
        dpg.configure_item(i, wrap=(dpg.get_viewport_client_width() - 20))
    center_login_panel()  # Center the login panel when the viewport is resized

    if dpg.does_item_exist("ChatboxButton"):
        dpg.set_item_pos("ChatboxButton",
                         [dpg.get_viewport_client_width() - 80, dpg.get_viewport_client_height() - 100])


def send_chat_message(sender, app_data, user_data):
    """
    Placeholder function to handle sending chat messages.
    """
    message = dpg.get_value("ChatboxInput")
    print("Message sent:", message)
    dpg.set_value("ChatboxInput", "")


# <editor-fold desc="Draw headings of tabs">
def draw_accounts_panel():
    """
    Draws the accounts tab panel which allows for user management (searching, adding, and refreshing users).
    """
    with dpg.tab(label="Accounts", parent=LocalData.tab_bar) as LocalData.accounts_tab:
        dpg.add_input_text(callback=search_users_callback, width=-1, hint="Search Users...", tag="UserSearch")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Refresh", callback=refresh_all_content)
            dpg.add_button(label="+", callback=show_add_user_modal)
        dpg.add_separator()


def draw_main_interface():
    """Draws the main interface of the application."""
    draw_organizations_panel()
    draw_accounts_panel()
    draw_help_panel()
    draw_chatbox_button()
    draw_chatbox()
    resize_viewport_callback()
    refresh_all_content()

    # Ensure chatbox window is initially hidden
    dpg.configure_item("ChatboxWindow", show=False)


def sort_callback(sender, app_data):
    """
    Callback for sorting organizations based on selected criteria.
    - sender: The widget (combo box) that triggered this callback.
    - app_data: The selected sort option.
    """
    LocalData.sort_mode = app_data
    refresh_all_content()


def draw_organizations_panel():
    """
    Draws the organizations tab panel which allows for managing and viewing organizations (searching, adding, exporting, and sorting).
    """
    with dpg.tab(label="Organizations", parent=LocalData.tab_bar) as LocalData.organizations_tab:
        dpg.add_input_text(callback=search_organizations_callback, width=-1, hint="Search Organizations...",
                           tag="OrganizationSearch")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Refresh", callback=refresh_all_content, tag="Refresh")
            dpg.add_button(label="Export", callback=lambda: export_organizations_callback(), tag="Export")
            dpg.add_button(label="+", show=False, callback=lambda: show_modify_modal(), tag="AddButton")
            dpg.add_text("Sort by:")
            dpg.add_combo(items=list(LocalData.sort_types), width=160, callback=sort_callback,
                          default_value=LocalData.sort_mode)
            dpg.add_button(label="?", callback=walkthrough_callback)
        dpg.add_separator()


# </editor-fold>

# <editor-fold desc="Search bars">
def search_organizations_callback(sender, filter_string):
    """
    Filters the organization content based on the provided search string.
    - sender: The widget (input text) that triggered this callback.
    - filter_string: The string to filter organizations by.
    """
    dpg.set_value("organization_filter_id", filter_string)


def search_users_callback(sender, filter_string):
    """
    Filters the user accounts based on the provided search string.
    - sender: The widget (input text) that triggered this callback.
    - filter_string: The string to filter user accounts by.
    """
    refresh_accounts_content(filter_string)


# </editor-fold>

# <editor-fold desc="Refresh accounts menu for admins">
def refresh_accounts_content(filter_string):
    """
    Refreshes the user accounts content based on the search string and current roles.
    - filter_string: The string to filter user accounts by.
    """

    def change_role_callback(sender, unused, user_data):
        """
        Changes the role of a user (promotes/demotes between viewer and editor).
        - sender: The widget (button) that triggered this callback.
        - unused: Unused in this callback, reserved for potential future use.
        - user_data: Tuple containing current role status and username.
        """
        if user_data[0]:
            LocalData.database.set_role_for_user(user_data[1], 'viewer')
            LocalData.database.remove_role_for_user(user_data[1], 'editor')
        else:
            LocalData.database.set_role_for_user(user_data[1], 'editor')
            LocalData.database.remove_role_for_user(user_data[1], 'viewer')
        refresh_accounts_content(filter_string)

    def delete_user_callback(sender, unused, user_data):
        """
        Deletes a user account from the database.
        - sender: The widget (button) that triggered this callback.
        - unused: Unused in this callback, reserved for potential future use.
        - user_data: The username of the user to be deleted.
        """
        LocalData.database.delete_user(user_data)
        refresh_all_content()

    user_list = list(LocalData.database.get_users())
    user_list.sort()  # Sort the user list
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
    """
    Shows the reset password dialog for a user.
    - sender: The widget (button) that triggered this callback.
    - unused: Unused in this callback, reserved for potential future use.
    - user: The username of the user to reset the password for.
    """

    def reset_password_callback(s, u, accepted):
        """
        Resets the password if the user confirms the action.
        - s: The widget (button) that triggered this callback.
        - u: Unused in this callback, reserved for potential future use.
        - accepted: Boolean indicating whether the action was confirmed.
        """
        if accepted[0]:
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
    """
    Shows the add user modal for creating a new user account.
    """

    def add_modal_callback(sender, unused, user_data):
        """
        Adds a new user to the database if the action is confirmed.
        - sender: The widget (button) that triggered this callback.
        - unused: Unused in this callback, reserved for potential future use.
        - user_data: Tuple containing modal ID and confirmation status.
        """
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
def get_sort_key(org):
    """
    Returns the sorting key based on the current sort mode.
    - org: The organization object to be sorted.
    """
    return org.organization_name if LocalData.sort_mode == "Organization Name" else org.type_of_organization


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
    LocalData.organizations = [Organization(*org) for org in LocalData.database.get_organization_content()]
    sorted_list = sorted(LocalData.organizations, key=lambda org: get_sort_key(org))

    with dpg.group(tag="organization_content", parent=LocalData.organizations_tab):
        with dpg.filter_set(id="organization_filter_id"):
            for wp in sorted_list:
                with dpg.group(horizontal=False):
                    title = dpg.add_text(wp.organization_name, wrap=0)
                    dpg.bind_item_font(title, title_font)
                    t = dpg.add_text(wp.type_of_organization, wrap=0)

                    with dpg.group(show=False) as collapse:
                        if wp.location != "":
                            loc = dpg.add_text("Location", wrap=0)
                            dpg.bind_item_font(loc, bold_font)
                            util.hyperlink(wp.location, util.generate_google_maps_url(wp.location),
                                           str(wp.organization_id) + "hyperlink")

                        if wp.website != "":
                            wh = dpg.add_text("Website", wrap=0)
                            dpg.bind_item_font(wh, bold_font)
                            util.hyperlink(wp.website, wp.website, str(wp.organization_id) + "website")

                        resources = dpg.add_text("Resources Available")
                        dpg.bind_item_font(resources, bold_font)
                        LocalData.wrapped_text.append(dpg.add_text(wp.resources_available))

                        contact = dpg.add_text("Contact Information", wrap=0)
                        dpg.bind_item_font(contact, bold_font)
                        if wp.contact_person != "":
                            dpg.add_text(wp.contact_person)
                        if wp.contact_email != "":
                            dpg.add_text(wp.contact_email)
                        if wp.contact_phone != "":
                            dpg.add_text(wp.contact_phone)

                        description = dpg.add_text("Description")
                        dpg.bind_item_font(description, bold_font)
                        LocalData.wrapped_text.append(dpg.add_text(wp.description))

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
    """
    Shows a confirmation prompt to delete an organization.
    - organization: The organization object to be deleted.
    """

    def delete_callback(sender, unused, user_data):
        """
        Deletes the organization if the action is confirmed.
        - sender: The widget (button) that triggered this callback.
        - unused: Unused in this callback, reserved for potential future use.
        - user_data: Boolean indicating whether the action was confirmed.
        """
        if user_data:
            LocalData.database.delete_id(organization.organization_id)
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
def show_modify_modal(current_org=Organization(), edit=False):
    """
    Shows the modal for adding or editing an organization.
    - current_org: The current organization object to be edited, defaults to a new Organization.
    - edit: Boolean indicating whether the modal is for editing or adding an organization.
    """

    def add_modal_callback(sender, unused, user_data):
        """
        Adds or edits an organization in the database based on user input.
        - sender: The widget (button) that triggered this callback.
        - unused: Unused in this callback, reserved for potential future use.
        - user_data: Boolean indicating whether the action was confirmed.
        """
        dpg.disable_item(sender)  # Disable the save button to prevent multiple submissions
        new_data = Organization(
            current_org.organization_id,
            dpg.get_value(new_input_organization_name),
            dpg.get_value(new_input_type_of_organization),
            dpg.get_value(new_input_location),
            dpg.get_value(new_input_resources_available),
            dpg.get_value(new_input_contact_person),
            dpg.get_value(new_input_contact_email),
            dpg.get_value(new_input_contact_phone),
            dpg.get_value(new_input_website),
            dpg.get_value(new_input_description),
        )
        if user_data:
            dpg.delete_item(dpg.delete_item("validation_issues"))
            validation_issues = util.get_validation_issues(new_data)
            if len(validation_issues) > 0:
                issues_group = dpg.add_group(parent=add_modal_id, before=save_options_buttons)
                dpg.add_alias("validation_issues", issues_group)
                for item in validation_issues:
                    dpg.add_text(item, parent=issues_group)
                dpg.enable_item(sender)
                return
            if edit:
                LocalData.database.edit_id(new_data.get_values_as_tuple())
            else:
                LocalData.database.add_content(new_data.get_values_as_tuple()[:9])
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
            with dpg.group(width=-1):
                new_input_organization_name = dpg.add_input_text(hint="Organization Name",
                                                                 default_value=current_org.organization_name)
                enum_options = ["Business", "Nonprofit", "Not-for-profit", "Government", "Other"]
                new_input_type_of_organization = dpg.add_combo(items=enum_options, default_value=(
                    "Organization Type" if current_org.type_of_organization == "" else current_org.type_of_organization))
                new_input_location = dpg.add_input_text(hint="Location", default_value=current_org.location)
                new_input_website = dpg.add_input_text(hint="Website", default_value=current_org.website)
                dpg.add_text("Resources Available")
                new_input_resources_available = dpg.add_input_text(multiline=True,
                                                                   default_value=current_org.resources_available)
                dpg.add_text("Contact Information")
                new_input_contact_person = dpg.add_input_text(hint="Name", width=-1,
                                                              default_value=current_org.contact_person)
                new_input_contact_email = dpg.add_input_text(hint="Email", no_spaces=True, width=-1,
                                                             default_value=current_org.contact_email)
                new_input_contact_phone = dpg.add_input_text(hint="Phone", decimal=True, no_spaces=True,
                                                             default_value=current_org.contact_phone)
                dpg.add_text("Description")
                new_input_description = dpg.add_input_text(multiline=True, default_value=current_org.description)
            with dpg.group(horizontal=True) as save_options_buttons:
                dpg.add_button(label="Save", user_data=True, callback=add_modal_callback)
                dpg.add_button(label="Cancel", user_data=False, callback=add_modal_callback)
    dpg.split_frame()
    dpg.set_item_pos(add_modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])


# </editor-fold>

# <editor-fold desc="Export menu">
def export_organizations_callback():
    """
    Opens a file dialog to export the organizations data to a CSV file.
    """

    def file_dialog_callback(sender, appdata):
        """
        Exports the organization data to the specified file path.
        - sender: The widget (file dialog) that triggered this callback.
        - appdata: The data from the file dialog, including the selected file path.
        """
        LocalData.database.export_data(appdata['file_path_name'])

    with dpg.file_dialog(callback=file_dialog_callback, default_filename="export", file_count=1, modal=True):
        dpg.add_file_extension(".csv")


# </editor-fold>

# <editor-fold desc="Main refresh function">
def refresh_all_content():
    """
    Refreshes all content in the application based on the user's roles.
    """
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
    """
    Draws the help panel with detailed instructions, an interactive walkthrough, FAQ, and support information.
    """
    with dpg.tab(label="About", parent=LocalData.tab_bar):
        # Overview Section
        with dpg.group(horizontal=True):
            dpg.add_text("Press the \"?\" button in the Organizations tab to go through an interactive tutorial.")
        subtitle = dpg.add_text("Overview")
        dpg.bind_item_font(subtitle, bold_font)
        dpg.add_text(
            "OrgView is a user-friendly database tool designed to help manage information for local businesses and organizations. "
            "It allows multiple users to browse and edit information on each business, and securely stores that information in a remote database. "
            "OrgView is always up-to-date with the latest changes made by you and other contributors. "
            "Data entry is easy, and data exporting is supported, allowing exports to .csv for use in other programs.",
            tag="Overview")

        # Roles Section
        subtitle = dpg.add_text("Roles")
        dpg.bind_item_font(subtitle, bold_font)
        dpg.add_text("OrgView contains three roles with different permission levels:")
        dpg.add_text("Viewers: Can view entries in the database.", bullet=True)
        dpg.add_text("Editors: Can add, edit, and delete entries in the database.", bullet=True)
        dpg.add_text("Admins: Can add, edit, and delete entries in the database and manage other accounts.",
                     bullet=True)

        # Forgot Password Section
        subtitle = dpg.add_text("Forgot password?")
        dpg.bind_item_font(subtitle, bold_font)
        dpg.add_text("Ask your administrators for a password reset. They can set a new password or change your roles.")

        # Credits Section
        subtitle = dpg.add_text("Credits")
        dpg.bind_item_font(subtitle, bold_font)
        dpg.add_text("Created by Gil Powers and Bill Xu using DearPyGui and PostgreSQL.")

        # FAQ Section
        subtitle = dpg.add_text("FAQ")
        dpg.bind_item_font(subtitle, bold_font)
        dpg.add_text("Q: How do I add a new organization?")
        dpg.add_text("A: Click the '+' button in the Organizations tab and fill in the details.")
        dpg.add_text("Q: How do I export data?")
        dpg.add_text("A: Click the 'Export' button in the Organizations tab to export data to a .csv file.")
        dpg.add_text("Q: How do I change my password?")
        dpg.add_text("A: Ask an administrator to reset your password.")


def walkthrough_callback(sender, unused, user_data):
    """
    Starts the interactive walkthrough, guiding the user through the main features of the application.
    """
    LocalData.walkthrough_steps.clear()
    LocalData.walkthrough_steps.append(("Refresh", "Refreshes all content.", 4))
    LocalData.walkthrough_steps.append(("OrganizationSearch", "Search and filter content.", 6))
    if "editor" in LocalData.database.roles or "admin" in LocalData.database.roles:
        LocalData.walkthrough_steps.append(("Export", "Opens a menu to export to a .csv file.", 4))
        LocalData.walkthrough_steps.append(("AddButton", "Add a new organization to the database.", 4))
        if LocalData.first_edit != 0:
            LocalData.walkthrough_steps.append((LocalData.first_edit, "Edit an organization in the database.", 6))
            LocalData.walkthrough_steps.append((LocalData.first_delete, "Remove an organization from the database.", 6))
    pos = dpg.get_item_pos(LocalData.walkthrough_steps[0][0])
    pos[1] += dpg.get_item_rect_size(LocalData.walkthrough_steps[0][0])[1] + LocalData.walkthrough_steps[0][2]
    with dpg.window(label="Walkthrough", no_resize=True, autosize=True,
                    pos=pos, modal=True, tag="WalkthroughWindow", no_title_bar=True, no_move=True):
        dpg.add_text(LocalData.walkthrough_steps[0][1], tag="WalkthroughText")
        dpg.bind_item_theme(LocalData.walkthrough_steps[0][0], "HelpHighlight")
        dpg.add_button(label="Next", callback=next_item_in_walkthrough)


def next_item_in_walkthrough(sender, unused, user_data):
    """
    Moves to the next step in the interactive walkthrough.
    """
    if LocalData.walkthrough_steps[0][0] is LocalData.first_edit \
            or LocalData.walkthrough_steps[0][0] is LocalData.first_delete:
        dpg.bind_item_theme(LocalData.walkthrough_steps[0][0], "ClickableText")
    else:
        dpg.bind_item_theme(LocalData.walkthrough_steps[0][0], "")
    LocalData.walkthrough_steps.pop(0)
    if len(LocalData.walkthrough_steps) == 0:
        dpg.delete_item("WalkthroughWindow")
        return
    pos = dpg.get_item_pos(LocalData.walkthrough_steps[0][0])
    pos[1] += dpg.get_item_rect_size(LocalData.walkthrough_steps[0][0])[1] + LocalData.walkthrough_steps[0][2]
    dpg.set_item_pos("WalkthroughWindow", pos)
    dpg.bind_item_theme(LocalData.walkthrough_steps[0][0], "HelpHighlight")
    dpg.set_value("WalkthroughText", LocalData.walkthrough_steps[0][1])


# </editor-fold>

# <editor-fold desc="Window Callbacks">
def delete_modal_callback(sender, unused, user_data):
    """
    Shows the delete confirmation prompt for an organization.
    - sender: The widget (button) that triggered this callback.
    - unused: Unused in this callback, reserved for potential future use.
    - user_data: The organization object to be deleted.
    """
    show_delete_prompt(user_data)


def edit_callback(sender, unused, user_data):
    """
    Shows the edit modal for an organization.
    - sender: The widget (button) that triggered this callback.
    - unused: Unused in this callback, reserved for potential future use.
    - user_data: The organization object to be edited.
    """
    show_modify_modal(user_data, edit=True)


# </editor-fold>

# Bind the function to handle when the primary window becomes visible
with dpg.item_handler_registry(tag="primary_handler") as handler:
    dpg.add_item_visible_handler(callback=visible_call)

# Create the primary window
with dpg.window(tag="Primary Window"):
    dpg.bind_font(default_font)
    LocalData.tab_bar = dpg.add_tab_bar()

dpg.bind_item_handler_registry("Primary Window", "primary_handler")

dpg.create_viewport(title="OrgView", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.maximize_viewport()

# Bind resize callback
dpg.set_viewport_resize_callback(resize_viewport_callback)

# Set primary window
dpg.set_primary_window("Primary Window", True)

# Start DearPyGUI
dpg.start_dearpygui()

# Safe disconnect
if LocalData.database:
    LocalData.database.disconnect()
dpg.destroy_context()
