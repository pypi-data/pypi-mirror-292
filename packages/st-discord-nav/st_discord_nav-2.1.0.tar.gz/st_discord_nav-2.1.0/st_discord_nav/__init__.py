import os
import streamlit.components.v1 as components

# Set the _RELEASE flag to False while developing the component, and True for production
_RELEASE = True

# Declare the Streamlit component
if not _RELEASE:
    _component_func = components.declare_component(
        "custom_nav",
        url="http://localhost:3001",  # URL for the dev server when developing the component
    )
else:
    # Path to the build directory in production
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_discord_nav", path=build_dir)

# Create a wrapper function for the component
def st_discord_nav(pages=None, font_size=30, icon_size=48, icon_color=None, active_icon_color=None, 
               hover_icon_color=None, background_color=None, active_background_color=None, 
               hover_background_color=None, border_radius=None, active_border_radius=None, 
               hover_border_radius=None, nav_width=80, nav_gap=32, key=None):
    """Create a custom navigation component.

    Parameters
    ----------
    pages: list of dicts
        A list of pages with names and icons for the navigation bar.
    font_size: int
        Font size for the icons.
    icon_size: int
        Size of the icons.
    icon_color: str
        Color of the icons.
    active_icon_color: str
        Color of the active icon.
    hover_icon_color: str
        Color of the icon on hover.
    background_color: str
        Background color of the navigation bar.
    active_background_color: str
        Background color of the active icon.
    hover_background_color: str
        Background color of the icon on hover.
    border_radius: str
        Border radius of the icons.
    active_border_radius: str
        Border radius of the active icon.
    hover_border_radius: str
        Border radius of the icon on hover.
    nav_width: int
        Width of the navigation bar.
    nav_gap: int
        Gap between icons in the navigation bar.
    key: str or None
        An optional key that uniquely identifies this component.

    Returns
    -------
    str
        The name of the active page.
    """
    # Call the component function and return its value
    component_value = _component_func(
        pages=pages, 
        fontSize=font_size, 
        iconSize=icon_size, 
        iconColor=icon_color, 
        activeIconColor=active_icon_color, 
        hoverIconColor=hover_icon_color, 
        backgroundColor=background_color, 
        activeBackgroundColor=active_background_color, 
        hoverBackgroundColor=hover_background_color, 
        borderRadius=border_radius, 
        activeBorderRadius=active_border_radius, 
        hoverBorderRadius=hover_border_radius, 
        navWidth=nav_width, 
        navGap=nav_gap, 
        key=key, 
        default=None
    )
    return component_value
