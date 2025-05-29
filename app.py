import streamlit as st
import pandas as pd

st.title("📂 Upload dan Baca File CSV")

# Widget untuk upload file
uploaded_file = st.file_uploader("Pilih file CSV", type="csv")

# Session states
if 'page' not in st.session_state:
    st.session_state.page = 'upload'
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'users' not in st.session_state:
    st.session_state.users = pd.DataFrame()
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Fungsi Navigasi
def go_to(page):
    st.session_state.page = page

# LOGIN PAGE
def login_page():
    st.title("🔐 Login")

    pay_id = st.text_input("Masukkan PayUserID:")
    login = st.button("Login")
    register = st.button("Register")

    if login:
        if pay_id in st.session_state.users['payUserID'].values:
            st.session_state.user_id = pay_id
            go_to('main_menu')
        else:
            st.error("PayUserID tidak ditemukan. Silakan registrasi.")

    if register:
        go_to('register')

# REGISTER PAGE
def register_page():
    st.title("📝 Register")

    payUserID = st.text_input("PayUserID")

    if not st.session_state.df.empty and 'typeCard' in st.session_state.df.columns:
        typecard_options = sorted(st.session_state.df['typeCard'].dropna().unique())
    else:
        typecard_options = []

    typeCard = st.selectbox("Tipe Kartu", typecard_options if typecard_options else ["Data tidak tersedia"], disabled=not typecard_options)

    userName = st.text_input("UserName")
    userSex = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    userBirthYear = st.number_input("Tahun Lahir", min_value=1900, max_value=2025, value=2000)

    if st.button("Daftar"):
        if payUserID in st.session_state.users['payUserID'].values:
            st.error("PayUserID sudah terdaftar.")
        else:
            new_user = pd.DataFrame([{
                "payUserID": payUserID,
                "typeCard": typeCard,
                "userName": userName,
                "userSex": userSex,
                "userBirthYear": userBirthYear
            }])
            st.session_state.users = pd.concat([st.session_state.users, new_user], ignore_index=True)
            st.success("Registrasi berhasil!")
            go_to('login')

    if st.button("Kembali"):
        go_to('login')

# MAIN MENU
def main_menu(df):
    user_id = st.session_state.user_id
    user = st.session_state.users[st.session_state.users['payUserID'] == user_id].iloc[0]
    st.title(f"👋 Selamat datang, {user['userName']}!")

    if st.button("Cari Koridor"):
        go_to('corridor')
    if st.button("Cek Riwayat"):
        go_to('history')
    if st.button("Logout"):
        st.session_state.user_id = None
        go_to('login')

# CORRIDOR PAGE
def corridor_page(df):
    st.title("🛣️ Cari Koridor")

    if 'routeName' not in df.columns or 'corridorID' not in df.columns:
        st.warning("Data tidak memiliki kolom 'routeName' dan/atau 'corridorID'.")
        return

    route_options = df['routeName'].dropna().unique()
    if len(route_options) == 0:
        st.warning("Tidak ada data routeName yang tersedia.")
        return

    selected_route = st.selectbox("Pilih Halte Awal - Halte Akhir (routeName)", sorted(route_options))

    filtered_df = df[df['routeName'] == selected_route]

    st.write("📌 Nomor Corridor yang Terkait:")
    st.dataframe(filtered_df[['corridorID']].drop_duplicates())

    if not filtered_df.empty:
        most_common_corridor = filtered_df['corridorID'].value_counts().idxmax()
        st.success(f"Corridor yang paling sering muncul untuk rute **'{selected_route}'** adalah: **{most_common_corridor}**")
    else:
        st.warning("Tidak ditemukan corridor untuk rute yang dipilih.")

    if st.button("Kembali"):
        go_to('main_menu')

# HISTORY PAGE
def history_page(df):
    st.title("📜 Riwayat Perjalanan")

    user_id = st.session_state.user_id
    user_data = st.session_state.users[st.session_state.users['payUserID'] == user_id]

    if user_data.empty:
        st.error("User tidak ditemukan.")
        return

    user = user_data.iloc[0]
    st.write(f"**Nama**: {user['userName']}")
    st.write(f"**Tipe Kartu**: {user['typeCard']}")
    st.write(f"**Jenis Kelamin**: {user['userSex']}")
    st.write(f"**Tahun Lahir**: {user['userBirthYear']}")

    if 'payUserID' not in df.columns:
        st.warning("Data tidak memiliki kolom 'payUserID'.")
        return

    history = df[df['payUserID'] == user_id][['transID', 'routeID', 'transDate', 'tapInHour', 'tapOutHour', 'duration', 'direction']]
    if history.empty:
        st.warning("Tidak ada riwayat perjalanan.")
    else:
        st.dataframe(history.reset_index(drop=True))

    if st.button("Kembali"):
        go_to('main_menu')

# ROUTING LOGIC
if st.session_state.page == 'upload':
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Data Preview:")
        st.dataframe(df)

        df['payUserID'] = df['payUserID'].astype(str)
        users_df = df[['payUserID', 'typeCard', 'userName', 'userSex', 'userBirthYear']].drop_duplicates()

        st.session_state.users = users_df.copy()
        st.session_state.df = df.copy()
        go_to('login')
    else:
        st.info("Silakan unggah file CSV terlebih dahulu.")

elif st.session_state.page == 'login':
    login_page()
elif st.session_state.page == 'register':
    register_page()
elif st.session_state.page == 'main_menu':
    main_menu(st.session_state.df)
elif st.session_state.page == 'corridor':
    corridor_page(st.session_state.df)
elif st.session_state.page == 'history':
    history_page(st.session_state.df)app.py
