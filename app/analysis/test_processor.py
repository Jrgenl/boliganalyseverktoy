"""
Test script for DataProcessor

Dette scriptet tester funksjonaliteten til DataProcessor-klassen.
"""

import sys
import os
import json

# Legg til prosjektmappen i sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.data_processor import DataProcessor, BoligData

def test_data_processor():
    """
    Tester DataProcessor med testdata.
    """
    print("Tester DataProcessor...")
    
    # Last testdata
    test_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "data", "test_bolig_data.json")
    
    if not os.path.exists(test_file):
        print(f"Testfil ikke funnet: {test_file}")
        return
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # Opprett DataProcessor
    processor = DataProcessor()
    
    # Behandle data
    bolig = processor.process_bolig_data(test_data)
    
    # Vis nøkkeldata
    print("\nNøkkeldata fra behandlet boligannonse:")
    print(f"Adresse: {bolig.adresse}")
    print(f"Pris: {bolig.prisantydning} kr")
    print(f"Areal: {bolig.bruksareal} m²")
    print(f"Kvadratmeterpris: {bolig.kvadratmeterpris} kr/m²")
    print(f"Byggeår: {bolig.byggeår} (Alder: {bolig.alder} år)")
    print(f"Boligtype: {bolig.boligtype}")
    print(f"Antall soverom: {bolig.soverom}")
    
    # Lagre behandlede data
    output_file = processor.save_to_json(bolig, "processed_bolig_data.json")
    print(f"\nBehandlede data lagret til: {output_file}")
    
    # Test dataframe-funksjonalitet
    df = processor.create_dataframe([bolig])
    print(f"\nDataFrame opprettet med {len(df)} rader og {len(df.columns)} kolonner")
    
    # Lagre dataframe til CSV
    csv_file = processor.save_dataframe_to_csv(df, "bolig_dataframe.csv")
    print(f"DataFrame lagret til: {csv_file}")
    
    return bolig

if __name__ == "__main__":
    test_data_processor()
