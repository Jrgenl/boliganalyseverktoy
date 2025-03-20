"""
Integrasjonstest for boliganalyseverktøyet

Dette scriptet tester hele systemet fra ende til ende, inkludert:
- Scraping av finn.no
- Databehandling
- Analyse
- Brukergrensesnitt
"""

import os
import sys
import unittest
import json
import time
from unittest.mock import patch, MagicMock

# Legg til prosjektmappen i sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer prosjektmoduler
from scraper.finn_scraper import FinnScraper
from analysis.data_processor import DataProcessor, BoligData
from analysis.bolig_analyzer import BoligAnalyzer

class TestBoligAnalyseSystem(unittest.TestCase):
    """
    Testklasse for å teste hele boliganalysesystemet.
    """
    
    def setUp(self):
        """
        Setter opp testmiljøet.
        """
        self.test_url = "https://www.finn.no/realestate/homes/ad.html?finnkode=398290726"
        self.scraper = FinnScraper()
        self.processor = DataProcessor()
        self.analyzer = BoligAnalyzer()
        
        # Opprett testmapper hvis de ikke eksisterer
        os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data'), exist_ok=True)
    
    def test_scraper_extracts_finnkode(self):
        """
        Tester at scraperen kan ekstrahere finnkode fra URL.
        """
        finnkode = self.scraper.extract_finn_code(self.test_url)
        self.assertIsNotNone(finnkode, "Kunne ikke ekstrahere finnkode fra URL")
        self.assertEqual(finnkode, "398290726", "Feil finnkode ekstrahert")
        print("✅ Scraper kan ekstrahere finnkode fra URL")
    
    def test_scraper_validates_url(self):
        """
        Tester at scraperen validerer URL-er korrekt.
        """
        valid_url = "https://www.finn.no/realestate/homes/ad.html?finnkode=123456789"
        invalid_url = "https://www.example.com/not-finn"
        
        # Implementer en enkel validering basert på extract_finn_code
        self.assertIsNotNone(self.scraper.extract_finn_code(valid_url), "Gyldig URL ble ikke validert")
        self.assertIsNone(self.scraper.extract_finn_code(invalid_url), "Ugyldig URL ble validert")
        print("✅ Scraper validerer URL-er korrekt")
    
    @patch('scraper.finn_scraper.FinnScraper.get_bolig_data')
    def test_end_to_end_with_mock_data(self, mock_scrape):
        """
        Tester hele systemet fra ende til ende med mock-data.
        """
        # Last testdata
        test_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                'data', 'processed_bolig_data.json')
        
        if not os.path.exists(test_file):
            self.skipTest(f"Testfil ikke funnet: {test_file}")
        
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        # Mock scraper-respons
        mock_scrape.return_value = test_data
        
        # Test hele prosessen
        try:
            # 1. Hent data (mocket)
            raw_data = self.scraper.get_bolig_data(self.test_url)
            self.assertIsNotNone(raw_data, "Ingen data returnert fra scraper")
            
            # 2. Behandle data
            bolig_data = self.processor.process_bolig_data(raw_data)
            self.assertIsNotNone(bolig_data, "Ingen data returnert fra processor")
            self.assertEqual(bolig_data.finnkode, test_data.get('finnkode', ''), "Feil finnkode i behandlet data")
            
            # 3. Analyser data
            analyzed_data = self.analyzer.analyze_bolig(bolig_data)
            self.assertIsNotNone(analyzed_data, "Ingen data returnert fra analyzer")
            self.assertTrue(hasattr(analyzed_data, 'risikoer'), "Analysert data mangler risikoer")
            self.assertTrue(hasattr(analyzed_data, 'høydepunkter'), "Analysert data mangler høydepunkter")
            
            # 4. Utfør prisanalyse
            price_analysis = self.analyzer.utfør_prisanalyse(analyzed_data)
            self.assertIsNotNone(price_analysis, "Ingen data returnert fra prisanalyse")
            self.assertIn('estimert_markedsverdi', price_analysis, "Prisanalyse mangler estimert markedsverdi")
            
            print("✅ Ende-til-ende test med mock-data fullført vellykket")
            
        except Exception as e:
            self.fail(f"Ende-til-ende test feilet: {str(e)}")
    
    def test_data_processor_creates_valid_bolig_data(self):
        """
        Tester at DataProcessor oppretter gyldige BoligData-objekter.
        """
        # Opprett minimalt datasett
        minimal_data = {
            'finnkode': '123456789',
            'tittel': 'Testbolig',
            'adresse': 'Testveien 1',
            'boligtype': 'Leilighet',
            'bruksareal': 50,
            'byggeår': 2010,
            'prisantydning': 2000000
        }
        
        # Behandle data
        bolig_data = self.processor.process_bolig_data(minimal_data)
        
        # Sjekk at objektet er gyldig
        self.assertIsInstance(bolig_data, BoligData, "Returnert objekt er ikke en BoligData-instans")
        self.assertEqual(bolig_data.finnkode, minimal_data['finnkode'], "Feil finnkode")
        self.assertEqual(bolig_data.tittel, minimal_data['tittel'], "Feil tittel")
        self.assertEqual(bolig_data.adresse, minimal_data['adresse'], "Feil adresse")
        self.assertEqual(bolig_data.boligtype, minimal_data['boligtype'], "Feil boligtype")
        self.assertEqual(bolig_data.bruksareal, minimal_data['bruksareal'], "Feil bruksareal")
        self.assertEqual(bolig_data.byggeår, minimal_data['byggeår'], "Feil byggeår")
        self.assertEqual(bolig_data.prisantydning, minimal_data['prisantydning'], "Feil prisantydning")
        
        # Sjekk at beregnede verdier er korrekte
        self.assertEqual(bolig_data.alder, 2025 - minimal_data['byggeår'], "Feil alder")
        self.assertEqual(bolig_data.kvadratmeterpris, minimal_data['prisantydning'] // minimal_data['bruksareal'], "Feil kvadratmeterpris")
        
        print("✅ DataProcessor oppretter gyldige BoligData-objekter")
    
    def test_analyzer_identifies_risks_and_highlights(self):
        """
        Tester at BoligAnalyzer identifiserer risikoer og høydepunkter.
        """
        # Opprett testdata med kjente nøkkelord
        test_data = BoligData({
            'finnkode': '123456789',
            'tittel': 'Flott leilighet med nytt kjøkken',
            'adresse': 'Testveien 1',
            'boligtype': 'Leilighet',
            'bruksareal': 50,
            'byggeår': 1970,
            'prisantydning': 2000000,
            'beskrivelse': 'Leiligheten har et nytt kjøkken og flott bad, men det er noe fuktproblemer i kjeller. Leiligheten ligger i første etasje.',
            'etasje': '1'
        })
        
        # Analyser data
        analyzed_data = self.analyzer.analyze_bolig(test_data)
        
        # Sjekk at risikoer er identifisert
        self.assertTrue(len(analyzed_data.risikoer) > 0, "Ingen risikoer identifisert")
        
        # Sjekk at høydepunkter er identifisert
        self.assertTrue(len(analyzed_data.høydepunkter) > 0, "Ingen høydepunkter identifisert")
        
        # Sjekk spesifikke risikoer og høydepunkter
        risk_categories = [risk['kategori'] for risk in analyzed_data.risikoer]
        highlight_categories = [highlight['kategori'] for highlight in analyzed_data.høydepunkter]
        
        # Forventede kategorier basert på testdata
        self.assertIn('fukt', risk_categories, "Fuktproblemer ikke identifisert som risiko")
        self.assertIn('beliggenhet', risk_categories, "Første etasje ikke identifisert som risiko")
        self.assertIn('kjøkken', highlight_categories, "Nytt kjøkken ikke identifisert som høydepunkt")
        self.assertIn('bad', highlight_categories, "Flott bad ikke identifisert som høydepunkt")
        
        print("✅ BoligAnalyzer identifiserer risikoer og høydepunkter korrekt")
    
    def test_price_analysis_handles_missing_data(self):
        """
        Tester at prisanalysen håndterer manglende data.
        """
        # Opprett testdata med manglende prisinformasjon
        test_data = BoligData({
            'finnkode': '123456789',
            'tittel': 'Testbolig',
            'adresse': 'Testveien 1',
            'boligtype': 'Leilighet',
            'bruksareal': 50,
            'byggeår': 2010,
            'prisantydning': 0,  # Manglende prisantydning
            'totalpris': 0       # Manglende totalpris
        })
        
        # Utfør prisanalyse
        price_analysis = self.analyzer.utfør_prisanalyse(test_data)
        
        # Sjekk at analysen ikke feiler og returnerer et resultat
        self.assertIsNotNone(price_analysis, "Prisanalyse returnerte None")
        self.assertIsInstance(price_analysis, dict, "Prisanalyse returnerte ikke en dictionary")
        
        # Sjekk at estimert markedsverdi er beregnet selv med manglende data
        self.assertIn('estimert_markedsverdi', price_analysis, "Estimert markedsverdi mangler")
        self.assertGreater(price_analysis['estimert_markedsverdi'], 0, "Estimert markedsverdi er 0 eller negativ")
        
        print("✅ Prisanalyse håndterer manglende data korrekt")
    
    def test_data_processor_save_and_load(self):
        """
        Tester at DataProcessor kan lagre og laste BoligData.
        """
        # Opprett testdata
        test_data = BoligData({
            'finnkode': '123456789',
            'tittel': 'Testbolig for lagring',
            'adresse': 'Testveien 1',
            'boligtype': 'Leilighet',
            'bruksareal': 50,
            'byggeår': 2010,
            'prisantydning': 2000000
        })
        
        # Lagre data
        filename = "test_save_load.json"
        saved_path = self.processor.save_to_json(test_data, filename)
        
        self.assertTrue(os.path.exists(saved_path), f"Fil ikke opprettet: {saved_path}")
        
        # Last data
        loaded_data = self.processor.load_from_json(saved_path)
        
        self.assertIsNotNone(loaded_data, "Ingen data lastet")
        self.assertIsInstance(loaded_data, BoligData, "Lastet data er ikke en BoligData-instans")
        self.assertEqual(loaded_data.finnkode, test_data.finnkode, "Feil finnkode i lastet data")
        self.assertEqual(loaded_data.tittel, test_data.tittel, "Feil tittel i lastet data")
        
        # Rydd opp
        if os.path.exists(saved_path):
            os.remove(saved_path)
        
        print("✅ DataProcessor kan lagre og laste BoligData korrekt")

def run_tests():
    """
    Kjører alle tester.
    """
    print("Kjører integrasjonstester for boliganalyseverktøyet...")
    print("-" * 70)
    
    # Opprett test suite
    suite = unittest.TestSuite()
    suite.addTest(TestBoligAnalyseSystem('test_scraper_extracts_finnkode'))
    suite.addTest(TestBoligAnalyseSystem('test_scraper_validates_url'))
    suite.addTest(TestBoligAnalyseSystem('test_data_processor_creates_valid_bolig_data'))
    suite.addTest(TestBoligAnalyseSystem('test_analyzer_identifies_risks_and_highlights'))
    suite.addTest(TestBoligAnalyseSystem('test_price_analysis_handles_missing_data'))
    suite.addTest(TestBoligAnalyseSystem('test_data_processor_save_and_load'))
    suite.addTest(TestBoligAnalyseSystem('test_end_to_end_with_mock_data'))
    
    # Kjør tester
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("-" * 70)
    print(f"Kjørte {result.testsRun} tester")
    print(f"Suksess: {result.testsRun - len(result.errors) - len(result.failures)}")
    print(f"Feil: {len(result.errors)}")
    print(f"Feilede: {len(result.failures)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
