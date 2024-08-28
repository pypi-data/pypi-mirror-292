import streamlit as st
from st_discord_nav import st_discord_nav
# Initialize session state for font size and active page
if 'font_size' not in st.session_state:
    st.session_state.font_size = 24  # Default font size
if 'active_page' not in st.session_state:
    st.session_state.active_page = "Home"  # Default page

# Define your pages and their icons
pages = [
    {"name": "Home", "icon": "FaHome"},
    {"name": "Chat", "icon": "FaComments"},
    {"name": "Friends", "icon": "FaUserFriends"},
    {"name": "Settings", "icon": "FaCog"},
    {"name": "Notifications", "icon": "MdNotifications"},
    {"name": "Profile", "icon": "MdPerson"},
    {"name": "Messages", "icon": "MdEmail"},
    {"name": "Search", "icon": "MdSearch"},
    {"name": "Help", "icon": "MdHelp"},
    {"name": "Logout", "icon": "FaSignOutAlt"},
]

# Use the custom navigation component
current_page = st_discord_nav(
    pages=pages,
    font_size=st.session_state.font_size,  # Pass font size from session state
    key="custom_nav"
)

# Function to update the active page
def update_active_page(new_page):
    st.session_state.active_page = new_page

# Main content area
def main():
    if current_page:
        update_active_page(current_page)  # Update session state with the active page

    if st.session_state.active_page == "Home":
        st.title("Welcome to Custom Nav App")
        st.write("This is the Home page. Click on the icons to navigate to different pages.")
    elif st.session_state.active_page == "Chat":
        st.title("Chat")
        st.write("This is the Chat page.")
    elif st.session_state.active_page == "Friends":
        st.title("Friends")
        st.write("This is the Friends page.")
    elif st.session_state.active_page == "Settings":
        st.title("Settings")
        st.write("This is the Settings page.")
    elif st.session_state.active_page == "Notifications":
        st.title("Notifications")
        st.write("This is the Notifications page.")
    elif st.session_state.active_page == "Profile":
        st.title("Profile")
        st.write("This is the Profile page.")
    elif st.session_state.active_page == "Messages":
        st.title("Messages")
        st.write("This is the Messages page.")
    elif st.session_state.active_page == "Search":
        st.title("Search")
        st.write("This is the Search page.")
    elif st.session_state.active_page == "Help":
        st.title("Help")
        st.write("This is the Help page.")
    elif st.session_state.active_page == "Logout":
        st.title("Logout")
        st.write("You have been logged out.")

if __name__ == "__main__":
    main()
