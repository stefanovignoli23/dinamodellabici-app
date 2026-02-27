import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection
import requests
from icalendar import Calendar
import datetime
import pytz

st.set_page_config(page_title="Dinamo Della Bici", page_icon="⚽")
st.title('Dinamo Della Bici Official App',text_alignment='center')
st.logo('media/dinamodellabici_logo.png', size='large')
st.image('media/dinamodellabici_logo.png')

@st.cache_data
def load_data():
    conn = st.connection("gsheets",type = GSheetsConnection)
    df = conn.read(spreadsheet=st.secrets['spreadsheet'])
    return df

if st.sidebar.button("🔄 Aggiorna i risultati"):
    st.cache_data.clear()
    st.rerun()

df = load_data()

for col in [c for c in df if 'gol' not in c]:
    df[col] = df[col].str.upper()

st.divider()
last_match = df.iloc[-1,]
st.subheader("Il risultato dell'ultima partita")

st.write(
         "**Campo** 📍:", last_match.campo,'\n\n',
         "**Risultato** ⚽:", last_match.squadra_casa," ",last_match.gol_squadra_casa,' - ',last_match.gol_squadra_ospite," ",last_match.squadra_ospite,'\n\n',
         "**Marcatori** :blue_heart::",last_match.marcatori_dinamo,'\n\n',
         "**Assist** 🫂:",last_match.assist
       )
st.link_button(label="Clicca per vedere la classifica su LiveScore",
            url="https://livescore.csibologna.it/league_details.php?project_id=792")

st.divider()

st.subheader("Le statistiche della stagione")
def _add_medal_emoji(val): 
  if val == 1: 
    return f"🥇 {val}" 
  elif val == 2: 
    return f"🥈 {val}" 
  elif val == 3: 
    return f"🥉 {val}" 
  else: return val 

lista_marcatori = df.marcatori_dinamo.str.split(',').explode().tolist()
df_marcatori = pd.DataFrame(lista_marcatori)
df_marcatori = pd.DataFrame(df_marcatori.value_counts().reset_index()).rename(columns={0:'Giocatori','count':'Gol'})
df_marcatori = df_marcatori[(df_marcatori.Giocatori.notna())&(df_marcatori.Giocatori != '')].reset_index().rename(columns={'index':'Classifica'})
df_marcatori['Classifica'] = df_marcatori['Classifica']+1
df_marcatori = (
  df_marcatori.copy().style 
  .format(_add_medal_emoji, subset=['Classifica']) 
)

lista_assist = df.assist.str.split(',').explode().tolist()
df_assist = pd.DataFrame(lista_assist)
df_assist = pd.DataFrame(df_assist.value_counts().reset_index()).rename(columns={0:'Giocatori','count':'Assist'}).reset_index().rename(columns={'index':'Classifica'})
df_assist = df_assist[(df_assist.Giocatori.notna())&(df_assist.Giocatori != '')]
df_assist['Classifica'] = df_assist['Classifica']+1
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

st.subheader("Il calendario")

def load_calendar(ical_url: str):
    response = requests.get(ical_url)
    response.raise_for_status()
    return Calendar.from_ical(response.content)

ITALY_TZ = pytz.timezone("Europe/Rome")

def get_events(cal, days_ahead=30):
    events = []
    now = datetime.datetime.now(datetime.timezone.utc)
    limit = now + datetime.timedelta(days=days_ahead)

    for component in cal.walk():
        if component.name == "VEVENT":
            start = component.get('dtstart').dt
            end = component.get('dtend').dt

            # Normalizza a datetime con timezone
            if isinstance(start, datetime.date) and not isinstance(start, datetime.datetime):
                start = datetime.datetime(start.year, start.month, start.day, tzinfo=datetime.timezone.utc)
                end = datetime.datetime(end.year, end.month, end.day, tzinfo=datetime.timezone.utc)

            # Se il datetime non ha timezone, assumiamo UTC
            if start.tzinfo is None:
                start = pytz.utc.localize(start)
                end = pytz.utc.localize(end)

            # Converti in ora italiana 🇮🇹
            start = start.astimezone(ITALY_TZ)
            end = end.astimezone(ITALY_TZ)

            if now <= start.astimezone(datetime.timezone.utc) <= limit:
                events.append({
                    "titolo": str(component.get('summary', 'Senza titolo')),
                    "inizio": start,
                    "fine": end,
                    "descrizione": str(component.get('description', '')),
                    "luogo": str(component.get('location', '')),
                })

    return sorted(events, key=lambda x: x['inizio'])

ICAL_URL = st.secrets.get("ICAL_URL", "")

GIORNI = {
    "Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì",
    "Thursday": "Giovedì", "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"
}

def date_format(dt):
    giorno = GIORNI[dt.strftime("%A")]
    return f"{giorno} {dt.strftime('%d/%m %H:%M')}"

try:
  cal = load_calendar(ICAL_URL)
  events = get_events(cal)
  st.success(f"{len(events)} eventi trovati")
  for e in events:
      st.write(f"📌 {date_format(e['inizio'])} - {e['titolo']}")
except Exception as ex:
    st.error(f"Errore nel caricamento: {ex}")
st.divider()

st.subheader("I campi")
dict_campi_url = {
   'Cavina':"https://maps.app.goo.gl/3ZAfML1tQ3hmHS1c9",
   'Castel Maggiore':"https://maps.app.goo.gl/ahYyaGg7sDBCfVgJ7",
   'Dlf':"https://maps.app.goo.gl/Cb3Qobkm96NrCvPL7",
   'Pallavicini':"https://maps.app.goo.gl/6yo8mdw7fTfngjNM9",
   'Savena':"https://maps.app.goo.gl/4aqjM17ocfqVj19BA",
   'Siro':"https://maps.app.goo.gl/vvHhdUASkUiuT1U96"
}
dict_campi ={
    'Pallavicini':[44.516714549247105, 11.250363781254205,'#2986cc'],
    'Savena':[44.500568844009685, 11.366697557669758,'#69ca3f'],
    'Castel Maggiore':[44.57493989465883, 11.357579377283864,'#f44336'],
    'Cavina':[44.52281793271603, 11.269032290985205,'#F18732'],
    'Siro':[44.49226558188355, 11.398289084660481,'#d3da6d'],
    'Dlf':[44.506830187552815, 11.354371407376616,"#673dda"]
}

option = st.selectbox(
    "In quale campo vuoi andare?",
    ("Cavina", "Castel Maggiore", "Dlf", "Pallavicini", "Savena", "Siro"),
    placeholder='Seleziona il campo...'
)
#colore_campo = dict_campi.get(option)
#st.markdown("Hai selezionato "+f"<span style='color:{colore_campo[2]}'>{option}</span>", unsafe_allow_html=True)

@st.dialog("⚠️ Confermi?")
def confirm_exit(url,option):
    st.warning("Campo "+option+"! Confermi di voler partire?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("✅ Continua", url, use_container_width=True)
    with col2:
        if st.button("❌ Annulla", use_container_width=True):
            st.rerun()

if st.button("Clicca qui quando vuoi partire 🚗"):
    confirm_exit(dict_campi_url[option],option)

st.markdown("""
<style>
.legend-item {
    display: flex;
    align-items: center;
    flex: 1;
    min-width: 0;
}
.legend-item span {
    width: 20px;
    text-align: center;
    flex-shrink: 0;
}
</style>

<div style="display: flex; gap: 20px; margin-bottom: 10px;font-size: 12px;">
    <div class="legend-item"><span style="color: #F18732;">●</span> Cavina</div>
    <div class="legend-item"><span style="color: #f44336;">●</span> Castel Maggiore</div>
    <div class="legend-item"><span style="color: #673dda;">●</span> Dlf</div>      
</div>
<div style="display: flex; gap: 20px; margin-bottom: 10px;font-size: 12px;">
    <div class="legend-item"><span style="color: #2986cc;">●</span> Pallavicini</div>
    <div class="legend-item"><span style="color: #69ca3f;">●</span> Savena</div>
    <div class="legend-item"><span style="color: #d3da6d;">●</span> Siro</div>        
</div>
""", unsafe_allow_html=True)

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