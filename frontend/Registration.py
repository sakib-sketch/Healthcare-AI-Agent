import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Force reload of database package to clear out old SQLite caching from active Streamlit memory
if 'database' in sys.modules:
    import importlib
    if 'database.db' in sys.modules:
        import database.db
        importlib.reload(database.db)
    import database
    importlib.reload(database)

import streamlit as st

from database import create_users_table
from auth import register_user, login_user, reset_password, logout_user

# =========================
# INITIALIZE DATABASE
# =========================
create_users_table()

def render_auth_page():
    # =========================
    # SESSION STATE
    # =========================
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "user" not in st.session_state:
        st.session_state.user = None

    st.title("🏥 Healthcare AI Authentication")

    # =========================
    # LOGOUT
    # =========================
    if st.session_state.authenticated:

        st.success(f"Welcome {st.session_state.user[1]}")

        st.subheader("✅ You are logged in")

        if st.button("Logout"):
            if st.session_state.user:
                logout_user(st.session_state.user[0])
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

    else:

        menu = st.sidebar.selectbox(
            "Choose Option",
            ["Login", "Register", "Forgot Password"]
        )

        # =========================
        # REGISTER
        # =========================
        if menu == "Register":

            st.subheader("📝 Create Account")

            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Register"):

                if not name or not email or not password:
                    st.warning("All fields required")

                else:
                    success, message = register_user(
                        name,
                        email,
                        password
                    )

                    if success:
                        st.success(message)

                    else:
                        st.error(message)

        # =========================
        # LOGIN
        # =========================
        elif menu == "Login":

            st.subheader("🔐 Login")

            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Login"):

                success, result = login_user(email, password)

                if success:

                    st.session_state.authenticated = True
                    st.session_state.user = result

                    st.success("Login successful")

                    st.rerun()

                else:
                    st.error(result)

        # =========================
        # FORGOT PASSWORD
        # =========================
        elif menu == "Forgot Password":

            st.subheader("🔑 Reset Password")

            email = st.text_input("Registered Email")
            new_password = st.text_input(
                "New Password",
                type="password"
            )

            if st.button("Reset Password"):

                success, message = reset_password(
                    email,
                    new_password
                )

                if success:
                    st.success(message)

                else:
                    st.error(message)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Healthcare AI Login",
        layout="centered"
    )
    render_auth_page()