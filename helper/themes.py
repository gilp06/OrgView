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
            dpg.add_theme_color(dpg.mvThemeCol_Border, value=[255, 255, 119])
            dpg.add_theme_color(dpg.mvThemeCol_Text, value=[255, 255, 119])

    # Dark Theme resembling the original palette
    with dpg.theme(tag="DarkTheme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [30, 30, 30, 255])
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, [35, 35, 35, 255])
            dpg.add_theme_color(dpg.mvThemeCol_Border, [60, 60, 60, 255])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, [50, 50, 50, 255])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, [60, 60, 60, 255])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, [70, 70, 70, 255])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, [25, 25, 25, 255])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, [35, 35, 35, 255])
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, [40, 40, 40, 255])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, [20, 20, 20, 255])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, [60, 60, 60, 255])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, [70, 70, 70, 255])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, [80, 80, 80, 255])
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, [110, 110, 255, 255])
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, [110, 110, 255, 255])
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, [150, 150, 255, 255])
            dpg.add_theme_color(dpg.mvThemeCol_Button, [80, 80, 80, 255])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [100, 100, 100, 255])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [120, 120, 120, 255])
            dpg.add_theme_color(dpg.mvThemeCol_Header, [70, 70, 70, 255])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, [90, 90, 90, 255])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, [110, 110, 110, 255])
            dpg.add_theme_color(dpg.mvThemeCol_Separator, [60, 60, 60, 255])
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, [80, 80, 80, 255])
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, [100, 100, 100, 255])
            dpg.add_theme_color(dpg.mvThemeCol_Text, [220, 220, 220, 255])
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, [128, 128, 128, 255])
            dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg, [110, 110, 255, 255])
    with dpg.theme(tag="ChatButtonTheme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [100, 149, 237, 255])  # Light blue color
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [65, 105, 225, 255])  # Royal blue color
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 128, 255])  # Navy color
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 25)  # Make it circular
