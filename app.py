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
    page_title="Phantasma - Medical Portal",
    page_icon="👁️",
    layout="centered"
)

# Clean CSS bez zaobljenih linija
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
        border-radius: 0px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        width: 450px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .logo-container {
        margin-bottom: 2rem;
    }
    .logo-img {
        max-width: 400px;
        height: auto;
        margin: 0 auto;
        display: block;
    }
    .company-tagline {
        color: #5c6bc0;
        font-size: 1rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    .stTextInput>div>div>input, .stTextInput>div>div>input:focus {
        border: 1px solid #ccc;
        border-radius: 0px;
        padding: 0.75rem;
        font-size: 1rem;
    }
    .stButton>button {
        width: 100%;
        background: #1a237e;
        color: white;
        border: none;
        padding: 0.85rem;
        border-radius: 0px;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 1rem;
        border: 1px solid #1a237e;
    }
    .stButton>button:hover {
        background: #3949ab;
        border-color: #3949ab;
    }
    .footer {
        margin-top: 2rem;
        color: #7986cb;
        font-size: 0.8rem;
    }
    .app-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        transition: all 0.2s ease;
    }
    .app-card:hover {
        border-color: #1a237e;
        background: #fff;
    }
    .app-icon {
        width: 50px;
        height: 50px;
        object-fit: contain;
        margin-bottom: 0.5rem;
    }
    /* Remove rounded corners from all elements */
    .stSelectbox>div>div, .stNumberInput>div>div>input, .stTextInput>div>div>input {
        border-radius: 0px !important;
    }
    /* Remove extra padding from streamlit elements */
    .stImage {
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stImage"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Hide streamlit form border */
    .stForm {
        border: none !important;
    }
    form {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

class UserManager:
    def __init__(self):
        # Inicijaliziraj session state ako ne postoji
        if 'users' not in st.session_state:
            st.session_state.users = {
                'admin': {
                    'password_hash': self._hash_password('PhantasmaAdmin2024!'),
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
    
    def get_user_role(self, username):
        """Sigurno dobiva role iz session state"""
        if username in st.session_state.users:
            return st.session_state.users[username].get('role', 'user')
        return 'user'

def load_image_from_url(url, size=200):
    """Učitava sliku s URL-a i resize-a je"""
    try:
        response = requests.get(url)
        image = Image.open(io.BytesIO(response.content))
        
        # Create white background
        background = Image.new('RGBA', (size, size), (255, 255, 255, 255))
        
        # Calculate position to center the image
        img_ratio = image.width / image.height
        if img_ratio > 1:
            # Wide image
            new_width = size
            new_height = int(size / img_ratio)
        else:
            # Tall image
            new_height = size
            new_width = int(size * img_ratio)
            
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calculate position to center
        x = (size - new_width) // 2
        y = (size - new_height) // 2
        
        # Paste image on background
        background.paste(image, (x, y), image if image.mode == 'RGBA' else None)
        
        return background
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def login_screen():
    # Koristimo jedan veliki HTML blok za cijeli login screen
    st.markdown("""
    <div class="login-container">
        <div class="logo-container">
            <img src="https://i.postimg.cc/PfKTSZBT/Phantasmed-logo.png" class="logo-img" alt="Phantasma Logo">
            <div class="company-tagline">Medical Vision Applications</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Streamlit forma - sada će se prikazati unutar login containera
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("**Username**", placeholder="Unesite svoj username", key="username_input")
        password = st.text_input("**Password**", type="password", placeholder="Unesite svoj password", key="password_input")
        submit = st.form_submit_button("**PRIJAVA U PORTAL**")
        
        if submit:
            if not username or not password:
                st.error("Molimo unesite username i password")
            else:
                user_manager = UserManager()
                success, message = user_manager.verify_login(username, password)
                
                if success:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.session_state.user_role = user_manager.get_user_role(username)
                    st.success("Uspješna prijava!")
                    st.rerun()
                else:
                    st.error(f"{message}")
    
    # Footer i zatvaranje login containera
    st.markdown("""
        <div class="footer">
            Siguran pristup medicinskim aplikacijama
        </div>
    </div>
    """, unsafe_allow_html=True)

def admin_dashboard():
    user_manager = UserManager()
    
    st.title("Admin Dashboard")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Kreiraj Korisnike", "Aktivni Korisnici", "Medicinske Aplikacije"])
    
    with tab1:
        st.subheader("Kreiraj Novi Korisnički Račun")
        
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Naziv kliničkog centra", placeholder="npr. Klinika za očne bolesti")
            role = st.selectbox("Uloga", ["user", "doctor", "admin"])
        with col2:
            days_valid = st.number_input("Dana važenja", min_value=1, max_value=365, value=90)
        
        if st.button("Generiraj Korisničke Podatke"):
            if client_name:
                username, password = user_manager.generate_username_password(client_name, role, days_valid)
            else:
                username, password = user_manager.generate_username_password(role=role, days_valid=days_valid)
            
            st.success("Korisnički račun uspješno kreiran!")
            
            st.markdown("---")
            st.markdown("### Korisnički Podaci")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Username:**\n`{username}`")
                st.info(f"**Uloga:**\n{role}")
            with col2:
                st.warning(f"**Password:**\n`{password}`")
                st.info(f"**Važi do:**\n{(datetime.now() + timedelta(days=days_valid)).strftime('%d.%m.%Y.')}")
            
            credentials_text = f"""PHANTASMA - Medical Vision Applications

Korisnički podaci:

Username: {username}
Password: {password}
Uloga: {role}
Važi do: {(datetime.now() + timedelta(days=days_valid)).strftime('%d.%m.%Y.')}

Portal: https://your-portal-url.streamlit.app

────────────────────────────
Medicinske aplikacije za dijagnostiku vida
Za podršku: support@phantasma.hr"""

            st.download_button(
                label="Preuzmi Login Podatke (TXT)",
                data=credentials_text,
                file_name=f"phantasma_medical_login_{username}.txt",
                mime="text/plain"
            )
    
    with tab2:
        st.subheader("Aktivni Korisnici")
        
        users_data = []
        for username, data in st.session_state.users.items():
            users_data.append({
                'Username': username,
                'Klinika': data.get('client_name', 'N/A'),
                'Uloga': data.get('role', 'user'),
                'Kreiran': data.get('created', datetime.now()).strftime('%d.%m.%Y.'),
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
            st.info("Nema kreiranih korisnika")
    
    with tab3:
        st.subheader("Medicinske Aplikacije")
        
        # Definiraj aplikacije s custom ikonama
        apps = {
            "Tear Film Analyzer": {
                "url": "https://tear-film-analyzer.streamlit.app/",
                "icon": "https://i.postimg.cc/hjQgv32j/Screenshot-2025-11-05-125227-removebg-preview.png",
                "description": "Analiza suhoće oka i kvalitete suznog filma"
            },
            "Vision Quest": {
                "url": "https://visionquest.streamlit.app/",
                "icon": "https://i.postimg.cc/4xHKCBgK/Screenshot-2025-11-05-125214-removebg-preview.png",
                "description": "Kompletna dijagnostika vida"
            },
            "Maritime Vision Test": {
                "url": "https://maritime-vision-test.streamlit.app/",
                "icon": "https://i.postimg.cc/DyjrHD01/Screenshot-2025-11-05-125128-removebg-preview.png",
                "description": "Specjalizirani testovi za pomorce"
            },
            "Near Vision Examiner": {
                "url": "https://nearvisionexaminer.streamlit.app/",
                "icon": "https://i.postimg.cc/hPdgcwfY/Screenshot-2025-11-05-125200-removebg-preview.png",
                "description": "Dijagnostika bliskog vida"
            }
        }
        
        # Preloadaj sve ikone odjednom
        with st.spinner("Učitavanje aplikacija..."):
            app_icons = {}
            for app_name, app_data in apps.items():
                app_icons[app_name] = load_image_from_url(app_data["icon"], 80)
        
        # Koristimo 2 kolone za prikaz 4 aplikacija (2x2)
        cols = st.columns(2)
        for idx, (app_name, app_data) in enumerate(apps.items()):
            with cols[idx % 2]:
                app_icon = app_icons[app_name]
                st.markdown(f"""
                <div class="app-card">
                    <div style="text-align: center; padding: 1rem;">
                """, unsafe_allow_html=True)
                
                if app_icon:
                    st.image(app_icon, width=80)
                else:
                    st.markdown("""
                        <div style="width: 80px; height: 80px; background: #e8eaf6; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.5rem auto; border: 1px solid #c5cae9;">
                            👁️
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                        <h4 style='margin: 0.5rem 0 0.5rem 0; color: #1a237e; font-size: 1.1rem;'>{app_name}</h4>
                        <p style='margin: 0 0 1rem 0; color: #666; font-size: 0.85rem;'>{app_data["description"]}</p>
                        <a href='{app_data["url"]}' target='_blank' style='background: #1a237e; color: white; padding: 0.6rem 1.2rem; text-decoration: none; border: 1px solid #1a237e; font-weight: 500; display: inline-block; width: 100%; text-align: center;'>Otvori Aplikaciju</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def user_dashboard():
    user_manager = UserManager()
    current_user = st.session_state.get('current_user', '')
    user_data = st.session_state.users.get(current_user, {})
    client_name = user_data.get('client_name', '')
    
    if client_name:
        st.title(f"Dobrodošli, {client_name}!")
    else:
        st.title(f"Dobrodošli, {current_user}!")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Medicinske Aplikacije")
        st.markdown("Odaberite aplikaciju za dijagnostiku:")
    with col2:
        expiry = user_data.get('expires')
        if expiry:
            days_left = (expiry - datetime.now()).days
            if days_left > 7:
                st.success(f"Preostalo dana: {days_left}")
            else:
                st.warning(f"Preostalo dana: {days_left}")
    
    # Definiraj aplikacije s custom ikonama
    apps = {
        "Tear Film Analyzer": {
            "url": "https://tear-film-analyzer.streamlit.app/",
            "icon": "https://i.postimg.cc/hjQgv32j/Screenshot-2025-11-05-125227-removebg-preview.png",
            "description": "Analiza suhoće oka i kvalitete suznog filma"
        },
        "Vision Quest": {
            "url": "https://visionquest.streamlit.app/",
            "icon": "https://i.postimg.cc/4xHKCBgK/Screenshot-2025-11-05-125214-removebg-preview.png",
            "description": "Kompletna dijagnostika vida"
        },
        "Maritime Vision Test": {
            "url": "https://maritime-vision-test.streamlit.app/",
            "icon": "https://i.postimg.cc/DyjrHD01/Screenshot-2025-11-05-125128-removebg-preview.png",
            "description": "Specjalizirani testovi za pomorce"
        },
        "Near Vision Examiner": {
            "url": "https://nearvisionexaminer.streamlit.app/",
            "icon": "https://i.postimg.cc/hPdgcwfY/Screenshot-2025-11-05-125200-removebg-preview.png",
            "description": "Dijagnostika bliskog vida"
        }
    }
    
    # Preloadaj sve ikone odjednom
    with st.spinner("Učitavanje aplikacija..."):
        app_icons = {}
        for app_name, app_data in apps.items():
            app_icons[app_name] = load_image_from_url(app_data["icon"], 80)
    
    # Koristimo 2 kolone za prikaz 4 aplikacija (2x2)
    cols = st.columns(2)
    for idx, (app_name, app_data) in enumerate(apps.items()):
        with cols[idx % 2]:
            app_icon = app_icons[app_name]
            st.markdown(f"""
            <div class="app-card">
                <div style="text-align: center; padding: 1rem;">
            """, unsafe_allow_html=True)
            
            if app_icon:
                st.image(app_icon, width=80)
            else:
                st.markdown("""
                    <div style="width: 80px; height: 80px; background: #e8eaf6; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.5rem auto; border: 1px solid #c5cae9;">
                        👁️
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
                    <h4 style='margin: 0.5rem 0 0.5rem 0; color: #1a237e; font-size: 1.1rem;'>{app_name}</h4>
                    <p style='margin: 0 0 1rem 0; color: #666; font-size: 0.85rem;'>{app_data["description"]}</p>
                    <a href='{app_data["url"]}' target='_blank' style='background: #1a237e; color: white; padding: 0.6rem 1.2rem; text-decoration: none; border: 1px solid #1a237e; font-weight: 500; display: inline-block; width: 100%; text-align: center;'>Pokreni Aplikaciju</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

def main():
    # Inicijaliziraj sve session state varijable
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = ''
    if 'user_role' not in st.session_state:
        st.session_state.user_role = 'user'
    
    # Inicijaliziraj UserManager (to će inicijalizirati users ako ne postoji)
    user_manager = UserManager()
    
    if not st.session_state.logged_in:
        login_screen()
    else:
        with st.sidebar:
            st.markdown("### PHANTASMA Medical")
            st.markdown("---")
            st.write(f"**Korisnik:** {st.session_state.current_user}")
            st.write(f"**Uloga:** {st.session_state.user_role}")
            
            if st.session_state.user_role == 'admin':
                st.success("Admin Mode")
            else:
                st.info("User Mode")
            
            st.markdown("---")
            if st.button("**Logout**", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_user = ''
                st.session_state.user_role = 'user'
                st.rerun()
        
        if st.session_state.user_role == 'admin':
            admin_dashboard()
        else:
            user_dashboard()

if __name__ == "__main__":

    main()

