# core/auth.py
import streamlit as st

def restore_session():
    """
    Restore session from URL params if Streamlit opens a new connection.
    """
    if not st.session_state.get("authenticated"):

        uid = st.query_params.get("uid", None)
        uname = st.query_params.get("uname", None)

        if uid and uname:
            try:
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = int(uid)
                st.session_state["user_name"] = uname
            except:
                pass

def require_auth():
    """
    Restore first, then verify auth.
    """
    restore_session()

    if not st.session_state.get("authenticated", False):
        st.switch_page("pages/2_Login.py")
        st.stop()

def get_auth_qs():
    """
    Build auth parameters.
    """
    uid = st.session_state.get("user_id")
    uname = st.session_state.get("user_name")

    if uid and uname:
        return f"uid={uid}&uname={uname}"

    return ""

def logout():
    st.session_state.clear()
    st.query_params.clear()
    st.switch_page("app.py")
    st.stop()