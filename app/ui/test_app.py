"""
Testscript for Streamlit-applikasjonen

Dette scriptet tester at Streamlit-applikasjonen kan kjøres uten feil.
"""

import os
import sys
import subprocess
import time

def test_streamlit_app():
    """
    Tester at Streamlit-applikasjonen kan kjøres.
    """
    print("Tester Streamlit-applikasjonen...")
    
    # Finn stien til app.py
    app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           "ui", "app.py")
    
    if not os.path.exists(app_path):
        print(f"Feil: Kunne ikke finne app.py på stien: {app_path}")
        return False
    
    try:
        # Start Streamlit-applikasjonen i bakgrunnen
        process = subprocess.Popen(
            ["streamlit", "run", app_path, "--server.headless", "true", "--server.port", "8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Vent litt for å la applikasjonen starte
        time.sleep(5)
        
        # Sjekk om prosessen fortsatt kjører
        if process.poll() is None:
            print("Streamlit-applikasjonen startet vellykket!")
            
            # Vis URL for tilgang
            print("Applikasjonen kjører på: http://localhost:8501")
            
            # Avslutt prosessen
            process.terminate()
            process.wait(timeout=5)
            
            return True
        else:
            # Hent feilmeldinger hvis prosessen avsluttet
            stdout, stderr = process.communicate()
            print(f"Feil ved oppstart av Streamlit-applikasjonen:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
    
    except Exception as e:
        print(f"En feil oppstod under testing av Streamlit-applikasjonen: {str(e)}")
        return False

if __name__ == "__main__":
    test_streamlit_app()
