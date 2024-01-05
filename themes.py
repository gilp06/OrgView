import dearpygui.dearpygui as dpg


def add_themes():
    with dpg.theme(tag="hyperlinkTheme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [29, 151, 236, 25])
            dpg.add_theme_color(dpg.mvThemeCol_Text, [29, 151, 236])
    with dpg.theme(tag="ClickableText"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [29, 151, 236, 25])
            dpg.add_theme_color(dpg.mvThemeCol_Text, [29, 151, 236])
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0.2)
    with dpg.theme(tag="HelpHighlight"):
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 2)
            dpg.add_theme_color(dpg.mvThemeCol_Border, value=[255, 255, 119])
            dpg.add_theme_color(dpg.mvThemeCol_Text, value=[255, 255, 119])
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 2)
            dpg.add_theme_color(dpg.mvThemeCol_Border, value=[255,255,119])
            dpg.add_theme_color(dpg.mvThemeCol_Text, value=[255, 255, 119])
