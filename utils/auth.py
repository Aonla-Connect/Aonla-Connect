"""
utils/auth.py — Authentication via Supabase
"""
import streamlit as st
from supabase import create_client, Client
import hashlib

@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name: str, email: str, password: str, phone: str = "") -> dict | None:
    """
    Naya user register karo. Password hashed store hoga.
    """
    try:
        sb = get_supabase()
        # Check if email already exists
        existing = sb.table("users").select("id").eq("email", email).execute()
        if existing.data:
            return None  # Already registered

        payload = {
            "name": name,
            "email": email,
            "password_hash": hash_password(password),
            "phone": phone or None,
        }
        resp = sb.table("users").insert(payload).execute()
        return resp.data[0] if resp.data else None
    except Exception as e:
        st.error(f"Register error: {e}")
        return None


def login_user(email: str, password: str) -> dict | None:
    """
    Email + password se login karo.
    Returns user dict (without password_hash) or None.
    """
    try:
        sb = get_supabase()
        resp = (
            sb.table("users")
              .select("id, name, email, phone, avatar_url, password_hash")
              .eq("email", email)
              .single()
              .execute()
        )
        user = resp.data
        if not user:
            return None
        if user.get("password_hash") != hash_password(password):
            return None
        # Return without password_hash
        return {k: v for k, v in user.items() if k != "password_hash"}
    except Exception as e:
        return None


def get_current_user() -> dict | None:
    return st.session_state.get("user")
