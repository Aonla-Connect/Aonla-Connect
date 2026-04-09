"""
utils/db.py — Supabase + Cloudinary database operations
"""
import streamlit as st
from supabase import create_client, Client
import cloudinary
import cloudinary.uploader
import cloudinary.api

# ─── Supabase client ─────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# ─── Cloudinary config ───────────────────────────────────────────────────────
def init_cloudinary():
    cloudinary.config(
        cloud_name = st.secrets["CLOUDINARY_CLOUD_NAME"],
        api_key    = st.secrets["CLOUDINARY_API_KEY"],
        api_secret = st.secrets["CLOUDINARY_API_SECRET"],
        secure     = True
    )

# ─── Upload File ─────────────────────────────────────────────────────────────
def upload_file_to_cloudinary(uploaded_file) -> str | None:
    """
    Cloudinary pe file upload karo, URL return karo.
    File ka blob Supabase mein nahi jaata — sirf URL.
    """
    try:
        init_cloudinary()
        result = cloudinary.uploader.upload(
            uploaded_file.read(),
            resource_type="auto",
            folder="aonla_connect"
        )
        return result.get("secure_url")
    except Exception as e:
        st.error(f"File upload failed: {e}")
        return None

# ─── Users ───────────────────────────────────────────────────────────────────
def get_all_users() -> list[dict]:
    try:
        sb = get_supabase()
        resp = sb.table("users").select("id, name, email, phone, avatar_url").execute()
        return resp.data or []
    except Exception as e:
        st.error(f"Users fetch error: {e}")
        return []

def get_user_by_id(user_id: str) -> dict | None:
    try:
        sb = get_supabase()
        resp = sb.table("users").select("*").eq("id", user_id).single().execute()
        return resp.data
    except:
        return None

# ─── Main Group Messages ──────────────────────────────────────────────────────
def get_main_group_messages(limit: int = 50) -> list[dict]:
    try:
        sb = get_supabase()
        resp = (
            sb.table("main_group_messages")
              .select("*, users(name)")
              .order("created_at", desc=False)
              .limit(limit)
              .execute()
        )
        messages = []
        for m in (resp.data or []):
            m["sender_name"] = (m.get("users") or {}).get("name", "Unknown") if not m.get("is_ai") else "Jitarth AI"
            messages.append(m)
        return messages
    except Exception as e:
        st.error(f"Main group messages error: {e}")
        return []

def send_main_group_message(user_id: str, sender_name: str, content: str, media_url: str | None = None, is_ai: bool = False):
    try:
        sb = get_supabase()
        payload = {
            "user_id": user_id,
            "content": content,
            "is_ai": is_ai,
        }
        if media_url:
            payload["media_url"] = media_url
        sb.table("main_group_messages").insert(payload).execute()
    except Exception as e:
        st.error(f"Send message error: {e}")

# ─── Private Messages ─────────────────────────────────────────────────────────
def get_private_messages(user1_id: str, user2_id: str, limit: int = 50) -> list[dict]:
    try:
        sb = get_supabase()
        resp = (
            sb.table("private_messages")
              .select("*, sender:users!private_messages_sender_id_fkey(name)")
              .or_(
                  f"and(sender_id.eq.{user1_id},receiver_id.eq.{user2_id}),"
                  f"and(sender_id.eq.{user2_id},receiver_id.eq.{user1_id})"
              )
              .order("created_at", desc=False)
              .limit(limit)
              .execute()
        )
        messages = []
        for m in (resp.data or []):
            m["sender_name"] = (m.get("sender") or {}).get("name", "Unknown")
            m["user_id"] = m.get("sender_id")
            messages.append(m)
        return messages
    except Exception as e:
        st.error(f"Private messages error: {e}")
        return []

def send_private_message(sender_id: str, receiver_id: str, sender_name: str, content: str, media_url: str | None = None):
    try:
        sb = get_supabase()
        payload = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "content": content,
        }
        if media_url:
            payload["media_url"] = media_url
        sb.table("private_messages").insert(payload).execute()
    except Exception as e:
        st.error(f"Send private message error: {e}")

# ─── Groups ───────────────────────────────────────────────────────────────────
def get_user_groups(user_id: str) -> list[dict]:
    try:
        sb = get_supabase()
        resp = (
            sb.table("group_members")
              .select("group_id, groups(id, name, created_by)")
              .eq("user_id", user_id)
              .execute()
        )
        groups = []
        for row in (resp.data or []):
            g = row.get("groups")
            if g:
                groups.append(g)
        return groups
    except Exception as e:
        st.error(f"Groups fetch error: {e}")
        return []

def create_group(name: str, admin_id: str, member_ids: list[str]) -> dict | None:
    try:
        sb = get_supabase()
        grp = sb.table("groups").insert({"name": name, "created_by": admin_id}).execute()
        gid = grp.data[0]["id"]
        for uid in set(member_ids):
            sb.table("group_members").insert({
                "group_id": gid,
                "user_id": uid,
                "is_admin": uid == admin_id
            }).execute()
        return grp.data[0]
    except Exception as e:
        st.error(f"Create group error: {e}")
        return None

def get_group_members(group_id: str) -> list[dict]:
    try:
        sb = get_supabase()
        resp = (
            sb.table("group_members")
              .select("user_id, is_admin, users(name, email)")
              .eq("group_id", group_id)
              .execute()
        )
        return resp.data or []
    except:
        return []

def add_group_member(group_id: str, user_id: str):
    try:
        sb = get_supabase()
        sb.table("group_members").insert({"group_id": group_id, "user_id": user_id, "is_admin": False}).execute()
    except Exception as e:
        st.error(f"Add member error: {e}")

def is_group_admin(group_id: str, user_id: str) -> bool:
    try:
        sb = get_supabase()
        resp = (
            sb.table("group_members")
              .select("is_admin")
              .eq("group_id", group_id)
              .eq("user_id", user_id)
              .single()
              .execute()
        )
        return (resp.data or {}).get("is_admin", False)
    except:
        return False

# ─── Group Messages ───────────────────────────────────────────────────────────
def get_group_messages(group_id: str, limit: int = 50) -> list[dict]:
    try:
        sb = get_supabase()
        resp = (
            sb.table("group_messages")
              .select("*, users(name)")
              .eq("group_id", group_id)
              .order("created_at", desc=False)
              .limit(limit)
              .execute()
        )
        messages = []
        for m in (resp.data or []):
            m["sender_name"] = (m.get("users") or {}).get("name", "Unknown")
            messages.append(m)
        return messages
    except Exception as e:
        st.error(f"Group messages error: {e}")
        return []

def send_group_message(group_id: str, user_id: str, sender_name: str, content: str, media_url: str | None = None):
    try:
        sb = get_supabase()
        payload = {
            "group_id": group_id,
            "user_id": user_id,
            "content": content,
        }
        if media_url:
            payload["media_url"] = media_url
        sb.table("group_messages").insert(payload).execute()
    except Exception as e:
        st.error(f"Send group message error: {e}")
