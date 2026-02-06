import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Dinamo Della Bici", page_icon="⚽")
st.title('Dinamo Della Bici Official App',text_alignment='center')
st.logo('media/dinamodellabici_logo.png', size='large')
st.image('media/dinamodellabici_logo.png')

@st.cache_data
def load_data():
    conn = st.connection("gsheets",type = GSheetsConnection)
    df = conn.read(spreadsheet=st.secrets['spreadsheet'])
    return df
df = load_data()

for col in [c for c in df if 'gol' not in c]:
    df[col] = df[col].str.upper()

st.divider()
last_match = df.iloc[-1,]
st.subheader("Il risultato dell'ultima partita")
st.write(
         "**Campo** 📍:", last_match.campo,'\n\n',
         "**Risultato** ⚽:", last_match.squadra_casa," ",last_match.gol_squadra_casa,' - ',last_match.gol_squadra_ospite," ",last_match.squadra_ospite,'\n\n',
         "**Marcatori** :blue_heart::",last_match.marcatori_dinamo 
       )

st.divider()

st.subheader("Le statistiche della stagione")
def _add_medal_emoji(val): 
  if val == 0: 
    return f"🥇" 
  elif val == 1: 
    return f"🥈" 
  elif val == 2: 
    return f"🥉" 
  else: return val 

lista_marcatori = df.marcatori_dinamo.str.split(',').explode().tolist()
df_marcatori = pd.DataFrame(lista_marcatori)
df_marcatori = pd.DataFrame(df_marcatori.value_counts().reset_index()).rename(columns={0:'Giocatori','count':'Gol'})
df_marcatori = df_marcatori[(df_marcatori.Giocatori.notna())&(df_marcatori.Giocatori != '')].reset_index().rename(columns={'index':'Classifica'})
df_marcatori = (
  df_marcatori.copy().style 
  .format(_add_medal_emoji, subset=['Classifica']) 
)

lista_assist = df.assist.str.split(',').explode().tolist()
df_assist = pd.DataFrame(lista_assist)
df_assist = pd.DataFrame(df_assist.value_counts().reset_index()).rename(columns={0:'Giocatori','count':'Assist'}).reset_index().rename(columns={'index':'Classifica'})
df_assist = df_assist[(df_assist.Giocatori.notna())&(df_assist.Giocatori != '')]
df_assist = (
  df_assist.copy().style 
  .format(_add_medal_emoji, subset=['Classifica']) 
)

lista_campi = df.campo.str.split(',').explode().tolist()
df_campi = pd.DataFrame(lista_campi)
df_campi = pd.DataFrame(df_campi.value_counts().reset_index()).rename(columns={0:'Campo','count':'Partite giocate'})
df_campi = df_campi[(df_campi.Campo.notna())&(df_campi.Campo != '')]

tab1, tab2, tab3 = st.tabs(["**Gol**", "**Assist**", "**Campi**"])
tab1.dataframe(df_marcatori, hide_index = True, use_container_width=True)
tab2.dataframe(df_assist, hide_index = True, use_container_width=True)
tab3.dataframe(df_campi, hide_index = True, use_container_width=True)

st.divider()

st.subheader("L'inno")
st.markdown("Non dimenticare di darti la carica per la prossima partita! 🎧🎸", text_alignment='center')
st.audio("media/dinamodellabici.mpeg", format="audio/mpeg", loop=False)

st.divider()

st.subheader("I campi")
dict_campi_url = {
   'Cavina':"https://www.google.it/maps/place/44%C2%B031'22.1%22N+11%C2%B016'08.5%22E/@44.5228217,11.2664574,775m/data=!3m2!1e3!4b1!4m4!3m3!8m2!3d44.5228179!4d11.2690323?entry=ttu&g_ep=EgoyMDI2MDEyMC4wIKXMDSoKLDEwMDc5MjA3M0gBUAM%3D",
   'Castel Maggiore':"https://www.google.it/maps/place/44%C2%B034'29.8%22N+11%C2%B021'27.3%22E/@44.5749437,11.3550045,774m/data=!3m2!1e3!4b1!4m4!3m3!8m2!3d44.5749399!4d11.3575794?entry=ttu&g_ep=EgoyMDI2MDEyMC4wIKXMDSoKLDEwMDc5MjA3M0gBUAM%3D",
   'Pallavicini':"https://www.google.it/maps/place/44%C2%B031'00.2%22N+11%C2%B015'01.3%22E/@44.5167183,11.2477889,775m/data=!3m2!1e3!4b1!4m4!3m3!8m2!3d44.5167145!4d11.2503638?entry=ttu&g_ep=EgoyMDI2MDExMy4wIKXMDSoKLDEwMDc5MjA3M0gBUAM%3D",
   'Savena':"https://www.google.it/maps/place/44%C2%B030'02.1%22N+11%C2%B022'00.1%22E/@44.5005726,11.3641227,775m/data=!3m2!1e3!4b1!4m4!3m3!8m2!3d44.5005688!4d11.3666976?entry=ttu&g_ep=EgoyMDI2MDExMy4wIKXMDSoKLDEwMDc5MjA3M0gBUAM%3D",
   'Siro':"https://www.google.it/maps/place/44%C2%B029'32.2%22N+11%C2%B023'53.8%22E/@44.4922694,11.3957142,775m/data=!3m2!1e3!4b1!4m4!3m3!8m2!3d44.4922656!4d11.3982891?entry=ttu&g_ep=EgoyMDI2MDEyMC4wIKXMDSoKLDEwMDc5MjA3M0gBUAM%3D"
}
dict_campi ={
    'Pallavicini':[44.516714549247105, 11.250363781254205,'#2986cc'],
    'Savena':[44.500568844009685, 11.366697557669758,'#69ca3f'],
    'Castel Maggiore':[44.57493989465883, 11.357579377283864,'#f44336'],
    'Cavina':[44.52281793271603, 11.269032290985205,'#f18732'],
    'Siro':[44.49226558188355, 11.398289084660481,'#d3da6d']
}

option = st.selectbox(
    "In quale campo vuoi andare?",
    ("Cavina", "Castel Maggiore", "Pallavicini", "Savena", "Siro"),
)
colore_campo = dict_campi.get(option)
st.markdown("Hai selezionato "+f"<span style='color:{colore_campo[2]}'>{option}</span>", unsafe_allow_html=True)
st.link_button(label="Clicca qui quando vuoi partire 🚗",
            url=dict_campi_url[option])

campo = pd.DataFrame(dict_campi).T.reset_index()
campo = campo.rename(columns = {'index':'Campo',0:'lat',1:'lon',2:'colore'})
st.map(campo,
    latitude = 'lat',
    longitude ='lon',
    size = 200,
    color = 'colore',
    zoom = 10.2,
    height = 250
    )