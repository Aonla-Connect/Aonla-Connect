import streamlit as st
import time
from datetime import datetime
from utils.auth import login_user, register_user, get_current_user
from utils.db import (
    get_main_group_messages, send_main_group_message,
    get_private_messages, send_private_message,
    get_all_users, get_user_groups, create_group,
    get_group_messages, send_group_message,
    upload_file_to_cloudinary, get_group_members,
    add_group_member, is_group_admin
)
from utils.ai import send_to_ai

st.set_page_config(
    page_title="Aonla Connect",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* Reset & Base */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0d1117 !important;
    font-family: 'DM Sans', sans-serif;
    color: #e6edf3;
}

[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #21262d;
    min-width: 320px !important;
    max-width: 320px !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.stDeployButton { display: none; }
div[data-testid="stDecoration"] { display: none; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 2px; }

/* ─── Sidebar Header ─── */
.sidebar-header {
    background: linear-gradient(135deg, #1a7a4a 0%, #0d5c35 100%);
    padding: 20px 16px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid #21262d;
}
.app-logo {
    width: 42px; height: 42px;
    background: rgba(255,255,255,0.15);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    backdrop-filter: blur(10px);
}
.app-title { font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 17px; color: #fff; }
.app-sub { font-size: 11px; color: rgba(255,255,255,0.65); margin-top: 1px; }

/* ─── Search ─── */
.search-box {
    padding: 10px 12px;
    border-bottom: 1px solid #21262d;
}
.search-box input {
    width: 100%;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 20px;
    padding: 8px 14px;
    color: #e6edf3;
    font-size: 13px;
    outline: none;
}

/* ─── Chat Item ─── */
.chat-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px;
    cursor: pointer;
    transition: background 0.15s;
    border-bottom: 1px solid #1c2128;
    position: relative;
}
.chat-item:hover { background: #1c2128; }
.chat-item.active { background: #1f2937; border-left: 3px solid #1a7a4a; }

.avatar {
    width: 46px; height: 46px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 16px;
    flex-shrink: 0;
}
.av-green { background: linear-gradient(135deg, #1a7a4a, #0d5c35); color: #fff; }
.av-blue  { background: linear-gradient(135deg, #1d4ed8, #1e40af); color: #fff; }
.av-purple{ background: linear-gradient(135deg, #7c3aed, #5b21b6); color: #fff; }
.av-orange{ background: linear-gradient(135deg, #ea580c, #c2410c); color: #fff; }
.av-ai    { background: linear-gradient(135deg, #0891b2, #0e7490); color: #fff; }

.chat-info { flex: 1; min-width: 0; }
.chat-name { font-weight: 600; font-size: 14px; color: #e6edf3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chat-preview { font-size: 12px; color: #8b949e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }
.chat-time { font-size: 10px; color: #8b949e; flex-shrink: 0; }
.unread-badge {
    background: #1a7a4a; color: #fff;
    border-radius: 50%; width: 18px; height: 18px;
    font-size: 10px; display: flex; align-items: center; justify-content: center;
    margin-left: 4px;
}

/* Section Label */
.section-label {
    padding: 8px 16px 4px;
    font-size: 10px; font-weight: 700;
    color: #8b949e; letter-spacing: 1.2px; text-transform: uppercase;
}

/* ─── Main Chat Area ─── */
.chat-header {
    background: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 14px 20px;
    display: flex; align-items: center; gap: 14px;
    position: sticky; top: 0; z-index: 100;
}
.chat-header-info { flex: 1; }
.chat-header-name { font-family: 'Nunito', sans-serif; font-weight: 700; font-size: 16px; }
.chat-header-sub { font-size: 11px; color: #8b949e; margin-top: 2px; }
.chat-header-actions { display: flex; gap: 12px; }
.header-btn {
    background: #21262d; border: none; color: #8b949e;
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; font-size: 16px;
    transition: all 0.15s;
}
.header-btn:hover { background: #30363d; color: #e6edf3; }

/* ─── Messages ─── */
.messages-container {
    padding: 16px 20px;
    display: flex; flex-direction: column; gap: 4px;
    min-height: 400px;
}
.msg-row { display: flex; margin-bottom: 2px; }
.msg-row.sent { justify-content: flex-end; }
.msg-row.recv { justify-content: flex-start; }

.msg-bubble {
    max-width: 65%;
    padding: 8px 12px 6px;
    border-radius: 12px;
    font-size: 13.5px;
    line-height: 1.5;
    position: relative;
}
.msg-bubble.sent {
    background: #1a4731;
    border-bottom-right-radius: 4px;
    color: #d2f4e0;
}
.msg-bubble.recv {
    background: #21262d;
    border-bottom-left-radius: 4px;
    color: #e6edf3;
}
.msg-bubble.ai-msg {
    background: linear-gradient(135deg, #0c2940, #0e3a52);
    border: 1px solid #1d4ed8;
    color: #bae6fd;
}
.msg-sender { font-size: 11px; font-weight: 700; color: #1a7a4a; margin-bottom: 3px; }
.msg-time { font-size: 10px; color: #8b949e; text-align: right; margin-top: 3px; }
.msg-media img { max-width: 200px; border-radius: 8px; margin-bottom: 4px; }

/* ─── Input Bar ─── */
.input-area {
    background: #161b22;
    border-top: 1px solid #21262d;
    padding: 12px 16px;
    display: flex; align-items: center; gap: 10px;
    position: sticky; bottom: 0;
}

/* ─── Login Page ─── */
.login-wrap {
    min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #0d1117 0%, #0a2818 100%);
}
.login-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 20px;
    padding: 40px;
    width: 100%; max-width: 400px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.4);
}
.login-logo { text-align: center; margin-bottom: 24px; }
.login-logo-icon {
    width: 72px; height: 72px;
    background: linear-gradient(135deg, #1a7a4a, #0d5c35);
    border-radius: 20px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 36px; margin-bottom: 12px;
}
.login-title { font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 26px; color: #e6edf3; }
.login-sub { font-size: 13px; color: #8b949e; margin-top: 4px; }

/* Streamlit widget overrides */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    color: #e6edf3 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #1a7a4a !important;
    box-shadow: 0 0 0 3px rgba(26,122,74,0.2) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1a7a4a, #0d5c35) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(26,122,74,0.35) !important;
}
.stSelectbox > div > div {
    background: #0d1117 !important;
    border-color: #30363d !important;
    color: #e6edf3 !important;
}
[data-testid="stFileUploader"] {
    background: #0d1117;
    border: 1px dashed #30363d;
    border-radius: 10px;
}
.stTabs [data-baseweb="tab-list"] {
    background: #0d1117;
    border-radius: 10px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #8b949e;
    background: transparent;
    border-radius: 8px;
}
.stTabs [aria-selected="true"] {
    background: #1a7a4a !important;
    color: white !important;
}
.stSuccess { background: #0d2818 !important; border-color: #1a7a4a !important; }
.stError { background: #2d0d0d !important; }
hr { border-color: #21262d !important; }
label { color: #8b949e !important; font-size: 12px !important; }

/* Message input row */
.stChatMessage { background: transparent !important; }
.msg-input-row {
    display: flex; gap: 8px; align-items: flex-end;
    background: #161b22;
    padding: 10px 0 0;
}

/* AI badge */
.ai-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: linear-gradient(90deg, #0891b2, #0e7490);
    color: white; border-radius: 12px;
    padding: 3px 10px; font-size: 11px; font-weight: 600;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ─── SESSION INIT ────────────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "active_chat" not in st.session_state:
    st.session_state.active_chat = {"type": "main_group", "id": None, "name": "Aonla Connect", "is_group": True}
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "show_create_group" not in st.session_state:
    st.session_state.show_create_group = False
if "call_active" not in st.session_state:
    st.session_state.call_active = False

# ─── AUTH PAGE ───────────────────────────────────────────────────────────────
def show_auth():
    st.markdown("""
    <div style="text-align:center; padding: 40px 0 20px;">
        <div style="display:inline-flex; align-items:center; justify-content:center;
                    width:80px; height:80px; background:linear-gradient(135deg,#1a7a4a,#0d5c35);
                    border-radius:24px; font-size:40px; margin-bottom:16px; box-shadow:0 12px 40px rgba(26,122,74,0.35);">
            🌿
        </div>
        <div style="font-family:'Nunito',sans-serif; font-weight:800; font-size:28px; color:#e6edf3;">Aonla Connect</div>
        <div style="font-size:13px; color:#8b949e; margin-top:4px;">Apne logon se judey raho 🤝</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐  Login", "✨  Register"])

    with tab1:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="aapka@email.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
        if st.button("Login karo →", key="login_btn"):
            if email and password:
                user = login_user(email, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Galat email ya password!")
            else:
                st.warning("⚠️ Sab fields bharo")

    with tab2:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        name = st.text_input("Poora Naam", placeholder="Tumhara naam", key="reg_name")
        email2 = st.text_input("Email", placeholder="aapka@email.com", key="reg_email")
        phone = st.text_input("Phone (optional)", placeholder="+91 XXXXX XXXXX", key="reg_phone")
        pass2 = st.text_input("Password", type="password", placeholder="Strong password", key="reg_pass")
        if st.button("Register karo ✨", key="reg_btn"):
            if name and email2 and pass2:
                result = register_user(name, email2, pass2, phone)
                if result:
                    st.success("✅ Account ban gaya! Ab login karo.")
                else:
                    st.error("❌ Email already registered hai ya koi error hua.")
            else:
                st.warning("⚠️ Name, email aur password zaroori hai")

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
def show_sidebar():
    user = st.session_state.user
    ac = st.session_state.active_chat

    st.markdown(f"""
    <div class="sidebar-header">
        <div class="app-logo">🌿</div>
        <div>
            <div class="app-title">Aonla Connect</div>
            <div class="app-sub">👤 {user.get('name','User')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Search
    search = st.text_input("", placeholder="🔍  Search karo...", key="sidebar_search", label_visibility="collapsed")
    st.session_state.search_query = search.lower().strip()

    # ── Main Group ──
    if not search:
        st.markdown('<div class="section-label">📢 Main Group</div>', unsafe_allow_html=True)
        is_active = ac["type"] == "main_group"
        if st.button("🌿  Aonla Connect (Main Group)", key="btn_main_group", use_container_width=True):
            st.session_state.active_chat = {"type": "main_group", "id": None, "name": "Aonla Connect", "is_group": True}
            st.rerun()

        # ── AI Chat ──
        st.markdown('<div class="section-label">🤖 AI Assistant</div>', unsafe_allow_html=True)
        if st.button("🤖  Jitarth AI", key="btn_ai_chat", use_container_width=True):
            st.session_state.active_chat = {"type": "ai_chat", "id": "ai", "name": "Jitarth AI", "is_group": False}
            st.rerun()

    # ── People ──
    all_users = get_all_users()
    filtered_users = [u for u in all_users if u["id"] != user["id"]]
    if search:
        filtered_users = [u for u in filtered_users if search in u.get("name","").lower() or search in u.get("email","").lower()]

    if filtered_users:
        st.markdown('<div class="section-label">👥 Direct Messages</div>', unsafe_allow_html=True)
        for u in filtered_users[:20]:
            uname = u.get("name", "User")
            uid = u["id"]
            is_active = ac["type"] == "dm" and ac["id"] == uid
            icon = uname[0].upper()
            btn_label = f"{'●' if is_active else '○'}  {icon} {uname}"
            if st.button(btn_label, key=f"user_{uid}", use_container_width=True):
                st.session_state.active_chat = {"type": "dm", "id": uid, "name": uname, "is_group": False, "peer": u}
                st.rerun()

    # ── Groups ──
    if not search:
        st.markdown('<div class="section-label">👥 My Groups</div>', unsafe_allow_html=True)
        my_groups = get_user_groups(user["id"])
        for g in my_groups:
            gid = g["id"]
            gname = g.get("name","Group")
            is_active = ac["type"] == "group" and ac["id"] == gid
            if st.button(f"# {gname}", key=f"grp_{gid}", use_container_width=True):
                st.session_state.active_chat = {"type": "group", "id": gid, "name": gname, "is_group": True}
                st.rerun()

        st.markdown("---")
        if st.button("➕ Naya Group banao", use_container_width=True, key="new_grp_btn"):
            st.session_state.show_create_group = True
            st.rerun()

        # Logout
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state.user = None
            st.session_state.active_chat = {"type": "main_group", "id": None, "name": "Aonla Connect", "is_group": True}
            st.rerun()

# ─── CREATE GROUP MODAL ───────────────────────────────────────────────────────
def show_create_group():
    st.markdown("### ➕ Naya Group Banao")
    gname = st.text_input("Group ka naam", key="new_grp_name")
    all_users = get_all_users()
    user = st.session_state.user
    others = [u for u in all_users if u["id"] != user["id"]]
    options = {u["name"]: u["id"] for u in others}
    selected = st.multiselect("Members chunno", list(options.keys()), key="grp_members")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Banao", key="create_grp_confirm"):
            if gname:
                member_ids = [options[n] for n in selected]
                member_ids.append(user["id"])
                result = create_group(gname, user["id"], member_ids)
                if result:
                    st.success(f"Group '{gname}' ban gaya!")
                    st.session_state.show_create_group = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Group nahi bana. Try again.")
    with col2:
        if st.button("❌ Cancel", key="create_grp_cancel"):
            st.session_state.show_create_group = False
            st.rerun()

# ─── RENDER MESSAGES ─────────────────────────────────────────────────────────
def render_messages(messages, current_user_id):
    if not messages:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; color:#8b949e;">
            <div style="font-size:48px; margin-bottom:12px;">💬</div>
            <div style="font-size:15px;">Abhi koi message nahi hai</div>
            <div style="font-size:12px; margin-top:6px;">Pehla message bhejo! 🚀</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for msg in messages:
        is_sent = str(msg.get("user_id", msg.get("sender_id",""))) == str(current_user_id)
        sender_name = msg.get("sender_name", msg.get("name",""))
        content = msg.get("content", msg.get("message",""))
        media_url = msg.get("media_url","")
        msg_time = msg.get("created_at","")
        if msg_time and len(msg_time) > 16:
            msg_time = msg_time[11:16]
        is_ai = msg.get("is_ai", False)

        row_class = "sent" if is_sent else "recv"
        bubble_class = "sent" if is_sent else ("ai-msg" if is_ai else "recv")

        media_html = ""
        if media_url:
            ext = media_url.split(".")[-1].lower()
            if ext in ["jpg","jpeg","png","gif","webp"]:
                media_html = f'<div class="msg-media"><img src="{media_url}" /></div>'
            else:
                media_html = f'<a href="{media_url}" target="_blank" style="color:#1a7a4a;">📎 File download karo</a><br>'

        sender_html = ""
        if not is_sent and sender_name:
            color = "#1a7a4a" if not is_ai else "#0891b2"
            prefix = '<span class="ai-badge">🤖 Jitarth AI</span><br>' if is_ai else ""
            sender_html = f'{prefix}<div class="msg-sender" style="color:{color}">{sender_name}</div>'

        st.markdown(f"""
        <div class="msg-row {row_class}">
            <div class="msg-bubble {bubble_class}">
                {sender_html}
                {media_html}
                <div>{content}</div>
                <div class="msg-time">{msg_time}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── MAIN CHAT ────────────────────────────────────────────────────────────────
def show_main_group():
    user = st.session_state.user
    ac = st.session_state.active_chat

    # Header
    st.markdown("""
    <div class="chat-header">
        <div class="avatar av-green" style="width:40px;height:40px;font-size:18px;">🌿</div>
        <div class="chat-header-info">
            <div class="chat-header-name">Aonla Connect</div>
            <div class="chat-header-sub">📢 Main Group • Sab log yahan hain</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Messages
    msgs = get_main_group_messages()
    msg_container = st.container()
    with msg_container:
        render_messages(msgs, user["id"])

    st.markdown("---")
    # Input
    col1, col2 = st.columns([5, 1])
    with col1:
        msg_text = st.text_input("", placeholder="Message likho...", key="main_group_input", label_visibility="collapsed")
    with col2:
        uploaded = st.file_uploader("", key="main_grp_file", label_visibility="collapsed")

    send_col, ai_col = st.columns([3,2])
    with send_col:
        if st.button("📤 Send", key="main_send", use_container_width=True):
            media_url = None
            if uploaded:
                media_url = upload_file_to_cloudinary(uploaded)
            if msg_text or media_url:
                send_main_group_message(user["id"], user["name"], msg_text or "", media_url)
                st.rerun()
    with ai_col:
        if st.button("🤖 AI ko Pucho", key="main_ai", use_container_width=True):
            if msg_text:
                with st.spinner("AI soch raha hai... 🧠"):
                    ai_reply = send_to_ai(msg_text)
                send_main_group_message(user["id"], user["name"], msg_text or "", None)
                send_main_group_message("ai", "Jitarth AI", ai_reply, None, is_ai=True)
                st.rerun()
            else:
                st.warning("Pehle question likho!")

# ─── DM CHAT ─────────────────────────────────────────────────────────────────
def show_dm():
    user = st.session_state.user
    ac = st.session_state.active_chat
    peer = ac.get("peer", {})
    peer_name = ac.get("name","")
    peer_id = ac.get("id","")
    icon = peer_name[0].upper() if peer_name else "?"

    st.markdown(f"""
    <div class="chat-header">
        <div class="avatar av-blue" style="width:40px;height:40px;font-size:18px;">{icon}</div>
        <div class="chat-header-info">
            <div class="chat-header-name">{peer_name}</div>
            <div class="chat-header-sub">{peer.get('email','')}</div>
        </div>
        <div style="display:flex; gap:8px;">
            <span style="font-size:20px; cursor:pointer;" title="Voice Call">📞</span>
            <span style="font-size:20px; cursor:pointer;" title="Video Call">📹</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Call UI (simple)
    call_col1, call_col2 = st.columns(2)
    with call_col1:
        if st.button("📞 Voice Call", key="voice_call", use_container_width=True):
            st.info(f"📞 {peer_name} ko call ho rahi hai... (WebRTC integration zaroori hai production mein)")
    with call_col2:
        if st.button("📹 Video Call", key="video_call", use_container_width=True):
            st.info(f"📹 {peer_name} ke saath video call... (WebRTC integration zaroori hai production mein)")

    msgs = get_private_messages(user["id"], peer_id)
    render_messages(msgs, user["id"])

    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    with col1:
        msg_text = st.text_input("", placeholder="Message likho...", key="dm_input", label_visibility="collapsed")
    with col2:
        uploaded = st.file_uploader("", key="dm_file", label_visibility="collapsed")

    if st.button("📤 Send", key="dm_send", use_container_width=True):
        media_url = None
        if uploaded:
            media_url = upload_file_to_cloudinary(uploaded)
        if msg_text or media_url:
            send_private_message(user["id"], peer_id, user["name"], msg_text or "", media_url)
            st.rerun()

# ─── GROUP CHAT ───────────────────────────────────────────────────────────────
def show_group_chat():
    user = st.session_state.user
    ac = st.session_state.active_chat
    gid = ac["id"]
    gname = ac["name"]
    is_admin = is_group_admin(gid, user["id"])

    st.markdown(f"""
    <div class="chat-header">
        <div class="avatar av-purple" style="width:40px;height:40px;font-size:18px;">#</div>
        <div class="chat-header-info">
            <div class="chat-header-name">{gname}</div>
            <div class="chat-header-sub">{'👑 Group Admin' if is_admin else '👥 Group Member'}</div>
        </div>
        <div style="display:flex; gap:8px;">
            <span style="font-size:20px; cursor:pointer;" title="Voice Call">📞</span>
            <span style="font-size:20px; cursor:pointer;" title="Video Call">📹</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    call_col1, call_col2 = st.columns(2)
    with call_col1:
        if st.button("📞 Group Voice Call", key="grp_voice", use_container_width=True):
            st.info("📞 Group voice call... (WebRTC zaroori hai)")
    with call_col2:
        if st.button("📹 Group Video Call", key="grp_video", use_container_width=True):
            st.info("📹 Group video call... (WebRTC zaroori hai)")

    if is_admin:
        with st.expander("⚙️ Group Settings (Admin only)"):
            all_users = get_all_users()
            members = get_group_members(gid)
            member_ids = [m["user_id"] for m in members]
            non_members = [u for u in all_users if u["id"] not in member_ids]
            if non_members:
                to_add = st.selectbox("Member add karo", [u["name"] for u in non_members], key="add_member_sel")
                if st.button("➕ Add Member", key="add_mem_btn"):
                    uid_map = {u["name"]: u["id"] for u in non_members}
                    add_group_member(gid, uid_map[to_add])
                    st.success("Member add ho gaya!")
                    st.rerun()

    msgs = get_group_messages(gid)
    render_messages(msgs, user["id"])

    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    with col1:
        msg_text = st.text_input("", placeholder="Message likho...", key="grp_input", label_visibility="collapsed")
    with col2:
        uploaded = st.file_uploader("", key="grp_file", label_visibility="collapsed")

    if st.button("📤 Send", key="grp_send", use_container_width=True):
        media_url = None
        if uploaded:
            media_url = upload_file_to_cloudinary(uploaded)
        if msg_text or media_url:
            send_group_message(gid, user["id"], user["name"], msg_text or "", media_url)
            st.rerun()

# ─── AI CHAT ─────────────────────────────────────────────────────────────────
def show_ai_chat():
    user = st.session_state.user

    st.markdown("""
    <div class="chat-header">
        <div class="avatar av-ai" style="width:40px;height:40px;font-size:18px;">🤖</div>
        <div class="chat-header-info">
            <div class="chat-header-name">Jitarth AI</div>
            <div class="chat-header-sub">🧠 Personal AI Assistant • Sirf tum dekh sakte ho</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    for msg in st.session_state.ai_chat_history:
        is_sent = msg["role"] == "user"
        bubble_class = "sent" if is_sent else "ai-msg recv"
        sender = "Tum" if is_sent else "🤖 Jitarth AI"
        ai_badge = '<span class="ai-badge">🤖 Jitarth AI</span><br>' if not is_sent else ""
        st.markdown(f"""
        <div class="msg-row {'sent' if is_sent else 'recv'}">
            <div class="msg-bubble {bubble_class}">
                {ai_badge}
                <div>{msg['content']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    question = st.text_area("", placeholder="AI se kuch bhi pucho... 🤔", key="ai_input", label_visibility="collapsed", height=80)

    if st.button("🤖 AI ko Bhejo", key="ai_send", use_container_width=True):
        if question.strip():
            st.session_state.ai_chat_history.append({"role": "user", "content": question})
            with st.spinner("🧠 Soch raha hai..."):
                reply = send_to_ai(question)
            st.session_state.ai_chat_history.append({"role": "assistant", "content": reply})
            st.rerun()
        else:
            st.warning("Kuch likho toh!")

    if st.button("🗑️ Chat Clear", key="ai_clear"):
        st.session_state.ai_chat_history = []
        st.rerun()

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.user:
        show_auth()
        return

    if st.session_state.show_create_group:
        show_create_group()
        return

    with st.sidebar:
        show_sidebar()

    ac = st.session_state.active_chat
    chat_type = ac["type"]

    if chat_type == "main_group":
        show_main_group()
    elif chat_type == "dm":
        show_dm()
    elif chat_type == "group":
        show_group_chat()
    elif chat_type == "ai_chat":
        show_ai_chat()
    else:
        st.markdown("<div style='text-align:center;padding:40px;color:#8b949e;'>← Koi chat select karo</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
