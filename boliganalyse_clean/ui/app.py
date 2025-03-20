"""
Streamlit brukergrensesnitt for boliganalyseverktøyet

Dette scriptet implementerer et brukergrensesnitt for boliganalyseverktøyet
ved hjelp av Streamlit.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import requests
from io import BytesIO
import time
import re

# Legg til prosjektmappen i sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer prosjektmoduler
from scraper.finn_scraper import FinnScraper
from analysis.data_processor import DataProcessor, BoligData
from analysis.bolig_analyzer import BoligAnalyzer

# Konfigurer Streamlit-siden
st.set_page_config(
    page_title="Boliganalyseverktøy",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definer farger og stiler
COLORS = {
    'primary': '#1E88E5',
    'secondary': '#26A69A',
    'warning': '#FFA726',
    'danger': '#EF5350',
    'light': '#F5F5F5',
    'dark': '#212121',
    'background': '#FFFFFF',
    'text': '#212121'
}

# Funksjon for å laste inn CSS
def load_css():
    st.markdown("""
    <style>
    .main {
        background-color: #FFFFFF;
        padding: 20px;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #1E88E5;
    }
    .highlight {
        background-color: #E3F2FD;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .risk-high {
        background-color: #FFEBEE;
        border-left: 5px solid #EF5350;
        padding: 10px;
        margin-bottom: 5px;
    }
    .risk-medium {
        background-color: #FFF8E1;
        border-left: 5px solid #FFA726;
        padding: 10px;
        margin-bottom: 5px;
    }
    .risk-low {
        background-color: #F1F8E9;
        border-left: 5px solid #AED581;
        padding: 10px;
        margin-bottom: 5px;
    }
    .highlight-item {
        background-color: #E0F7FA;
        border-left: 5px solid #26A69A;
        padding: 10px;
        margin-bottom: 5px;
    }
    .info-box {
        background-color: #E8EAF6;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
        border: 1px solid #BDBDBD;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Funksjon for å vise velkomstmelding
def show_welcome():
    st.title("Boliganalyseverktøy")
    st.markdown("""
    <div class="info-box">
    <h3>Velkommen til Boliganalyseverktøyet!</h3>
    <p>Dette verktøyet hjelper deg med å analysere boligannonser fra Finn.no. 
    Lim inn URL-en til en boligannonse fra Finn.no, og få en detaljert analyse av boligen.</p>
    <p>Analysen inkluderer:</p>
    <ul>
        <li>Identifisering av potensielle risikoer</li>
        <li>Fremheving av positive aspekter</li>
        <li>Prisanalyse og estimert markedsverdi</li>
        <li>Beregning av månedlige kostnader</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Funksjon for å validere Finn.no URL
def validate_finn_url(url):
    """
    Validerer at URL-en er en gyldig Finn.no boligannonse.
    """
    if not url:
        return False
    
    # Sjekk om URL-en er fra Finn.no
    if not ('finn.no' in url and 'realestate' in url):
        return False
    
    # Sjekk om URL-en inneholder finnkode
    if not ('finnkode=' in url or '/ad.html?' in url):
        return False
    
    return True

# Funksjon for å hente og analysere boligdata
@st.cache_data(ttl=3600)  # Cache resultater i 1 time
def analyze_property(url):
    """
    Henter og analyserer boligdata fra en Finn.no URL.
    """
    try:
        # Opprett scraper
        scraper = FinnScraper()
        
        # Hent boligdata
        with st.spinner('Henter boligdata fra Finn.no...'):
            raw_data = scraper.scrape_bolig_from_url(url)
        
        if not raw_data:
            st.error("Kunne ikke hente data fra den angitte URL-en. Sjekk at URL-en er korrekt.")
            return None
        
        # Behandle data
        with st.spinner('Behandler boligdata...'):
            processor = DataProcessor()
            bolig_data = processor.process_bolig_data(raw_data)
        
        # Analyser data
        with st.spinner('Analyserer boligdata...'):
            analyzer = BoligAnalyzer()
            analyzed_data = analyzer.analyze_bolig(bolig_data)
            price_analysis = analyzer.utfør_prisanalyse(analyzed_data)
        
        # Lagre analyserte data
        processor.save_to_json(analyzed_data, "siste_analyserte_bolig.json")
        
        return {
            'bolig_data': analyzed_data,
            'price_analysis': price_analysis
        }
    
    except Exception as e:
        st.error(f"En feil oppstod under analysen: {str(e)}")
        return None

# Funksjon for å vise boliginformasjon
def display_property_info(bolig_data):
    """
    Viser grunnleggende boliginformasjon.
    """
    st.header("Boliginformasjon")
    
    # Vis bilde hvis tilgjengelig
    if bolig_data.bilder and len(bolig_data.bilder) > 0:
        try:
            response = requests.get(bolig_data.bilder[0])
            img = Image.open(BytesIO(response.content))
            st.image(img, use_column_width=True)
        except:
            st.info("Kunne ikke laste bilde")
    
    # Vis tittel og adresse
    st.markdown(f"<h2>{bolig_data.tittel}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3>{bolig_data.adresse}</h3>", unsafe_allow_html=True)
    
    # Vis nøkkelinformasjon i kolonner
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<h4>Pris</h4>", unsafe_allow_html=True)
        if bolig_data.prisantydning > 0:
            st.markdown(f"<p><b>Prisantydning:</b> {bolig_data.prisantydning:,} kr</p>".replace(',', ' '), unsafe_allow_html=True)
        if bolig_data.totalpris > 0:
            st.markdown(f"<p><b>Totalpris:</b> {bolig_data.totalpris:,} kr</p>".replace(',', ' '), unsafe_allow_html=True)
        if bolig_data.fellesutgifter > 0:
            st.markdown(f"<p><b>Fellesutgifter:</b> {bolig_data.fellesutgifter:,} kr/mnd</p>".replace(',', ' '), unsafe_allow_html=True)
        if bolig_data.kvadratmeterpris > 0:
            st.markdown(f"<p><b>Kvadratmeterpris:</b> {bolig_data.kvadratmeterpris:,} kr/m²</p>".replace(',', ' '), unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h4>Boliginfo</h4>", unsafe_allow_html=True)
        st.markdown(f"<p><b>Boligtype:</b> {bolig_data.boligtype}</p>", unsafe_allow_html=True)
        st.markdown(f"<p><b>Eierform:</b> {bolig_data.eierform}</p>", unsafe_allow_html=True)
        if bolig_data.bruksareal > 0:
            st.markdown(f"<p><b>Bruksareal:</b> {bolig_data.bruksareal} m²</p>", unsafe_allow_html=True)
        if bolig_data.primærrom > 0:
            st.markdown(f"<p><b>Primærrom:</b> {bolig_data.primærrom} m²</p>", unsafe_allow_html=True)
        if bolig_data.soverom > 0:
            st.markdown(f"<p><b>Soverom:</b> {bolig_data.soverom}</p>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<h4>Bygningsinfo</h4>", unsafe_allow_html=True)
        if bolig_data.byggeår > 0:
            st.markdown(f"<p><b>Byggeår:</b> {bolig_data.byggeår}</p>", unsafe_allow_html=True)
        if bolig_data.alder > 0:
            st.markdown(f"<p><b>Alder:</b> {bolig_data.alder} år</p>", unsafe_allow_html=True)
        if bolig_data.etasje:
            st.markdown(f"<p><b>Etasje:</b> {bolig_data.etasje}</p>", unsafe_allow_html=True)
        if bolig_data.tomteareal > 0:
            st.markdown(f"<p><b>Tomteareal:</b> {bolig_data.tomteareal} m²</p>", unsafe_allow_html=True)
    
    # Vis fasiliteter
    if bolig_data.fasiliteter and len(bolig_data.fasiliteter) > 0:
        st.markdown("<h4>Fasiliteter</h4>", unsafe_allow_html=True)
        fasiliteter_str = ", ".join(bolig_data.fasiliteter)
        st.markdown(f"<p>{fasiliteter_str}</p>", unsafe_allow_html=True)
    
    # Vis beskrivelse
    if bolig_data.beskrivelse:
        with st.expander("Vis boligbeskrivelse"):
            st.markdown(bolig_data.beskrivelse)

# Funksjon for å vise risikoer
def display_risks(bolig_data):
    """
    Viser identifiserte risikoer ved boligen.
    """
    st.header("Identifiserte risikoer")
    
    if not bolig_data.risikoer or len(bolig_data.risikoer) == 0:
        st.info("Ingen spesifikke risikoer identifisert.")
        return
    
    # Sorter risikoer etter alvorlighetsgrad
    sorted_risks = sorted(
        bolig_data.risikoer, 
        key=lambda x: {'høy': 0, 'medium': 1, 'lav': 2}.get(x.get('alvorlighetsgrad', 'lav'), 3)
    )
    
    for risk in sorted_risks:
        severity = risk.get('alvorlighetsgrad', 'lav')
        category = risk.get('kategori', '')
        keyword = risk.get('nøkkelord', '')
        context = risk.get('kontekst', '')
        
        if severity == 'høy':
            st.markdown(f"""
            <div class="risk-high">
                <h4>⚠️ {category.capitalize()}</h4>
                <p><b>Nøkkelord:</b> {keyword}</p>
                <p><b>Kontekst:</b> {context}</p>
                <p><b>Alvorlighetsgrad:</b> Høy</p>
            </div>
            """, unsafe_allow_html=True)
        elif severity == 'medium':
            st.markdown(f"""
            <div class="risk-medium">
                <h4>⚠️ {category.capitalize()}</h4>
                <p><b>Nøkkelord:</b> {keyword}</p>
                <p><b>Kontekst:</b> {context}</p>
                <p><b>Alvorlighetsgrad:</b> Medium</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="risk-low">
                <h4>ℹ️ {category.capitalize()}</h4>
                <p><b>Nøkkelord:</b> {keyword}</p>
                <p><b>Kontekst:</b> {context}</p>
                <p><b>Alvorlighetsgrad:</b> Lav</p>
            </div>
            """, unsafe_allow_html=True)

# Funksjon for å vise høydepunkter
def display_highlights(bolig_data):
    """
    Viser identifiserte høydepunkter ved boligen.
    """
    st.header("Høydepunkter")
    
    if not bolig_data.høydepunkter or len(bolig_data.høydepunkter) == 0:
        st.info("Ingen spesifikke høydepunkter identifisert.")
        return
    
    # Grupper høydepunkter etter kategori
    highlights_by_category = {}
    for highlight in bolig_data.høydepunkter:
        category = highlight.get('kategori', 'annet')
        if category not in highlights_by_category:
            highlights_by_category[category] = []
        highlights_by_category[category].append(highlight)
    
    # Vis høydepunkter gruppert etter kategori
    for category, highlights in highlights_by_category.items():
        with st.expander(f"{category.capitalize()} ({len(highlights)})"):
            for highlight in highlights:
                keyword = highlight.get('nøkkelord', '')
                context = highlight.get('kontekst', '')
                
                st.markdown(f"""
                <div class="highlight-item">
                    <h4>✅ {keyword.capitalize()}</h4>
                    <p>{context}</p>
                </div>
                """, unsafe_allow_html=True)

# Funksjon for å vise prisanalyse
def display_price_analysis(price_analysis, bolig_data):
    """
    Viser prisanalyse for boligen.
    """
    st.header("Prisanalyse")
    
    if "error" in price_analysis:
        st.error(f"Kunne ikke utføre prisanalyse: {price_analysis['error']}")
        return
    
    # Vis prisantydning og estimert markedsverdi
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Prisantydning", 
            value=f"{price_analysis.get('prisantydning', 0):,} kr".replace(',', ' ')
        )
        
        if bolig_data.kvadratmeterpris > 0:
            st.metric(
                label="Kvadratmeterpris", 
                value=f"{bolig_data.kvadratmeterpris:,} kr/m²".replace(',', ' ')
            )
    
    with col2:
        avvik_prosent = price_analysis.get('verdi_avvik_prosent', 0)
        avvik_tekst = f"{avvik_prosent:+.1f}%" if avvik_prosent != 0 else "0%"
        
        st.metric(
            label="Estimert markedsverdi", 
            value=f"{price_analysis.get('estimert_markedsverdi', 0):,} kr".replace(',', ' '),
            delta=avvik_tekst
        )
    
    # Vis månedlige kostnader
    st.subheader("Månedlige kostnader")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Lånekostnad", 
            value=f"{price_analysis.get('månedlig_lånekostnad', 0):,} kr/mnd".replace(',', ' ')
        )
    
    with col2:
        st.metric(
            label="Fellesutgifter", 
            value=f"{bolig_data.fellesutgifter:,} kr/mnd".replace(',', ' ')
        )
    
    with col3:
        st.metric(
            label="Totale månedlige kostnader", 
            value=f"{price_analysis.get('månedlig_totalkostnad', 0):,} kr/mnd".replace(',', ' ')
        )
    
    # Vis prissammenligning med graf
    st.subheader("Prissammenligning")
    
    # Opprett data for graf
    labels = ['Prisantydning', 'Estimert markedsverdi']
    values = [price_analysis.get('prisantydning', 0), price_analysis.get('estimert_markedsverdi', 0)]
    
    if all(v > 0 for v in values):
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(labels, values, color=[COLORS['primary'], COLORS['secondary']])
        
        # Legg til verdier over stolpene
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height):,} kr'.replace(',', ' '),
                    ha='center', va='bottom', rotation=0)
        
        ax.set_ylabel('Pris (kr)')
        ax.set_title('Sammenligning av prisantydning og estimert markedsverdi')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        st.pyplot(fig)
    else:
        st.info("Ikke nok prisdata for å vise sammenligning.")

# Hovedfunksjon
def main():
    # Last inn CSS
    load_css()
    
    # Vis sidebar
    st.sidebar.title("Boliganalyseverktøy")
    st.sidebar.markdown("---")
    
    # Inputfelt for Finn.no URL
    st.sidebar.subheader("Analyser bolig")
    finn_url = st.sidebar.text_input("Lim inn Finn.no boligannonse URL:")
    
    analyze_button = st.sidebar.button("Analyser bolig")
    
    # Vis informasjon om verktøyet
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Om verktøyet**
    
    Dette verktøyet analyserer boligannonser fra Finn.no og gir deg innsikt i:
    - Potensielle risikoer
    - Positive aspekter
    - Prisanalyse
    - Månedlige kostnader
    
    Lim inn URL-en til en boligannonse fra Finn.no og klikk på "Analyser bolig".
    """)
    
    # Hovedinnhold
    if not finn_url and not analyze_button:
        show_welcome()
    elif analyze_button:
        if not validate_finn_url(finn_url):
            st.error("Ugyldig Finn.no URL. Vennligst oppgi en gyldig URL til en boligannonse på Finn.no.")
        else:
            # Analyser boligen
            results = analyze_property(finn_url)
            
            if results:
                bolig_data = results['bolig_data']
                price_analysis = results['price_analysis']
                
                # Vis resultater
                display_property_info(bolig_data)
                
                # Vis risikoer og høydepunkter i kolonner
                col1, col2 = st.columns(2)
                
                with col1:
                    display_risks(bolig_data)
                
                with col2:
                    display_highlights(bolig_data)
                
                # Vis prisanalyse
                display_price_analysis(price_analysis, bolig_data)

if __name__ == "__main__":
    main()
