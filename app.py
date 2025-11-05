import streamlit as st
import hashlib
import secrets
import string
import pandas as pd
from datetime import datetime, timedelta
import requests
from PIL import Image
import io

# Page config
st.set_page_config(
    page_title="Phant - Medical Portal",
    page_icon="👁️",
    layout="centered"
)

# Custom CSS za Phant branding
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .login-container {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        width: 420px;
        text-align: center;
    }
    .logo-container {
        margin-bottom: 1.5rem;
    }
    .company-name {
        color: #1a237e;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0.5rem 0 0.2rem 0;
        font-family: 'Arial', sans-serif;
    }
    .company-tagline {
        color: #5c6bc0;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    .stTextInput>div>div>input, .stTextInput>div>div>input:focus {
        border: 2px solid #e8eaf6;
        border-radius: 10px;
        padding: 0.75rem;
        font-size: 1rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%);
        color: white;
        border: none;
        padding: 0.85rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #3949ab 0%, #1a237e 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(57, 73, 171, 0.4);
    }
    .footer {
        margin-top: 2rem;
        color: #7986cb;
        font-size: 0.8rem;
    }
    .app-card {
        background: linear-gradient(135deg, #f5f7ff 0%, #e8eaf6 100%);
        border: 2px solid #e8eaf6;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        transition: all 0.3s ease;
    }
    .app-card:hover {
        border-color: #3949ab;
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(57, 73, 171, 0.15);
    }
</style>
""", unsafe_allow_html=True)

class UserManager:
    def __init__(self):
        if 'users' not in st.session_state:
            st.session_state.users = {
                'admin': {
                    'password_hash': self._hash_password('PhantAdmin2024!'),
                    'created': datetime.now(),
                    'role': 'admin'
                }
            }

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_username_password(self, client_name='', role='user', days_valid=90):
        while True:
            if client_name:
                base_username = client_name.lower().replace(' ', '_')
                username = f"{base_username}_{secrets.token_hex(2)}"
            else:
                username = f"user_{secrets.token_hex(3)}"
            
            if username not in st.session_state.users:
                break
        
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        password = ''.join(secrets.choice(alphabet) for _ in range(10))
        
        st.session_state.users[username] = {
            'password_hash': self._hash_password(password),
            'created': datetime.now(),
            'expires': datetime.now() + timedelta(days=days_valid),
            'role': role,
            'client_name': client_name
        }
        
        return username, password

    def verify_login(self, username, password):
        if username in st.session_state.users:
            user_data = st.session_state.users[username]
            if 'expires' in user_data and datetime.now() > user_data['expires']:
                return False, "Korisnički račun je istekao"
            
            if user_data['password_hash'] == self._hash_password(password):
                return True, "Uspješna prijava"
        return False, "Pogrešan username ili password"

def load_logo():
    try:
        logo_url = "https://i.postimg.cc/L8cW5X4H/phant-logo.png"
        response = requests.get(logo_url)
        image = Image.open(io.BytesIO(response.content))
        return image
    except:
        return None

def login_screen():
    st.markdown("""
    <div class="login-container">
        <div class="logo-container">
    """, unsafe_allow_html=True)
    
    logo = load_logo()
    if logo:
        st.image(logo, width=120)
    else:
        st.markdown("""
        <div style='color: #1a237e; font-size: 2rem; margin-bottom: 1rem;'>🔮</div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
            <div class="company-name">PHANT</div>
            <div class="company-tagline">Medical Vision Applications</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("👤 **Username**", placeholder="Unesite svoj username")
        password = st.text_input("🔒 **Password**", type="password", placeholder="Unesite svoj password")
        submit = st.form_submit_button("🚀 **PRIJAVA U PORTAL**")
        
        if submit:
            if not username or not password:
                st.error("📝 Molimo unesite username i password")
            else:
                user_manager = UserManager()
                success, message = user_manager.verify_login(username, password)
                
                if success:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.session_state.user_role = user_manager.users[username]['role']
                    st.success("✅ Uspješna prijava!")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    st.markdown("""
        <div class="footer">
            🔒 Siguran pristup medicinskim aplikacijama
        </div>
    </div>
    """, unsafe_allow_html=True)

def admin_dashboard():
    user_manager = UserManager()
    
    st.title("👨‍💼 Admin Dashboard")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["🎯 Kreiraj Korisnike", "👥 Aktivni Korisnici", "🔗 Medicinske Aplikacije"])
    
    with tab1:
        st.subheader("Kreiraj Novi Korisnički Račun")
        
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Naziv kliničkog centra", placeholder="npr. Klinika za očne bolesti")
            role = st.selectbox("Uloga", ["user", "doctor", "admin"])
        with col2:
            days_valid = st.number_input("Dana važenja", min_value=1, max_value=365, value=90)
        
        if st.button("🎁 Generiraj Korisničke Podatke", type="primary"):
            if client_name:
                username, password = user_manager.generate_username_password(client_name, role, days_valid)
            else:
                username, password = user_manager.generate_username_password(role=role, days_valid=days_valid)
            
            st.success("✅ Korisnički račun uspješno kreiran!")
            
            st.markdown("---")
            st.markdown("### 📋 Korisnički Podaci")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**👤 Username:**\n`{username}`")
                st.info(f"**👥 Uloga:**\n{role}")
            with col2:
                st.warning(f"**🔒 Password:**\n`{password}`")
                st.info(f"**📅 Važi do:**\n{(datetime.now() + timedelta(days=days_valid)).strftime('%d.%m.%Y.')}")
            
            credentials_text = f"""PHANT - Medical Vision Applications

Korisnički podaci:

👤 Username: {username}
🔒 Password: {password}
👥 Uloga: {role}
📅 Važi do: {(datetime.now() + timedelta(days=days_valid)).strftime('%d.%m.%Y.')}

🌐 Portal: https://your-portal-url.streamlit.app

────────────────────────────
🔒 Medicinske aplikacije za dijagnostiku vida
📧 Za podršku: support@phant.com"""

            st.download_button(
                label="📥 Preuzmi Login Podatke (TXT)",
                data=credentials_text,
                file_name=f"phant_medical_login_{username}.txt",
                mime="text/plain",
                type="primary"
            )
    
    with tab2:
        st.subheader("📊 Aktivni Korisnici")
        
        users_data = []
        for username, data in user_manager.users.items():
            users_data.append({
                'Username': username,
                'Klinika': data.get('client_name', 'N/A'),
                'Uloga': data['role'],
                'Kreiran': data['created'].strftime('%d.%m.%Y.'),
                'Istječe': data.get('expires', 'Nikad').strftime('%d.%m.%Y.') if isinstance(data.get('expires'), datetime) else 'Nikad',
                'Status': 'Aktivan' if not data.get('expires') or datetime.now() <= data.get('expires', datetime.now()) else 'Istekao'
            })
        
        if users_data:
            df = pd.DataFrame(users_data)
            st.dataframe(df, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ukupno Korisnika", len(users_data))
            with col2:
                active_users = len([u for u in users_data if u['Status'] == 'Aktivan'])
                st.metric("Aktivni", active_users)
            with col3:
                expired_users = len([u for u in users_data if u['Status'] == 'Istekao'])
                st.metric("Istekli", expired_users)
        else:
            st.info("📝 Nema kreiranih korisnika")
    
    with tab3:
        st.subheader("👁️ Medicinske Aplikacije")
        st.markdown("Dostupne Phant aplikacije za dijagnostiku vida:")
        
        apps = {
            "👁️ Tear Film Analyzer": "https://tear-film-analyzer.streamlit.app/",
            "🔍 Vision Quest": "https://visionquest.streamlit.app/", 
            "⚓ Maritime Vision Test": "https://maritime-vision-test.streamlit.app/",
            "📖 Near Vision Examiner": "https://nearvisionexaminer.streamlit.app/"
        }
        
        for app_name, app_url in apps.items():
            st.markdown(f"""
            <div class="app-card">
                <h4 style='margin: 0 0 0.5rem 0; color: #1a237e;'>{app_name}</h4>
                <p style='margin: 0 0 1rem 0; color: #666; font-size: 0.9rem;'>Napredna medicinska aplikacija</p>
                <a href='{app_url}' target='_blank' style='background: #1a237e; color: white; padding: 0.5rem 1.5rem; text-decoration: none; border-radius: 8px; font-weight: 500; display: inline-block;'>Otvori Aplikaciju →</a>
            </div>
            """, unsafe_allow_html=True)

def user_dashboard():
    user_manager = UserManager()
    user_data = user_manager.users.get(st.session_state.current_user, {})
    client_name = user_data.get('client_name', '')
    
    if client_name:
        st.title(f"👋 Dobrodošli, {client_name}!")
    else:
        st.title(f"👋 Dobrodošli, {st.session_state.current_user}!")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("👁️ Medicinske Aplikacije")
        st.markdown("Odaberite aplikaciju za dijagnostiku:")
    with col2:
        expiry = user_data.get('expires')
        if expiry:
            days_left = (expiry - datetime.now()).days
            if days_left > 7:
                st.success(f"📅 Preostalo dana: {days_left}")
            else:
                st.warning(f"⚠️ Preostalo dana: {days_left}")
    
    apps = {
        "👁️ Tear Film Analyzer": "https://tear-film-analyzer.streamlit.app/",
        "🔍 Vision Quest": "https://visionquest.streamlit.app/", 
        "⚓ Maritime Vision Test": "https://maritime-vision-test.streamlit.app/",
        "📖 Near Vision Examiner": "https://nearvisionexaminer.streamlit.app/"
    }
    
    cols = st.columns(2)
    for idx, (app_name, app_url) in enumerate(apps.items()):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="app-card">
                <h4 style='margin: 0 0 1rem 0; color: #1a237e;'>{app_name}</h4>
                <a href='{app_url}' target='_blank' style='background: #1a237e; color: white; padding: 0.6rem 1.2rem; text-decoration: none; border-radius: 8px; font-weight: 500; display: inline-block; width: 100%; text-align: center;'>Pokreni Aplikaciju</a>
            </div>
            """, unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_screen()
    else:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🔮 PHANT Medical")
            st.markdown("---")
            st.write(f"**👤 Korisnik:** {st.session_state.current_user}")
            st.write(f"**🎯 Uloga:** {st.session_state.user_role}")
            
            if st.session_state.user_role == 'admin':
                st.success("🛡️ Admin Mode")
            else:
                st.info("👥 User Mode")
            
            st.markdown("---")
            if st.button("🚪 **Logout**", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
        
        if st.session_state.user_role == 'admin':
            admin_dashboard()
        else:
            user_dashboard()

if __name__ == "__main__":
    main()