#!/usr/bin/env python3
"""
Test Script per Medical Report Parameter Extractor
==================================================
Script per testare l'estrazione di parametri da testo di esempio.
"""

import json
from parameter_extractor import ParameterExtractor
from json_output import JSONOutputGenerator


def test_parameter_extraction():
    """Testa l'estrazione di parametri da testo di esempio."""
    
    # Testo di test realistico
    test_texts = [
        """
        Paziente maschio, 45 anni.
        Pressione arteriosa 135/85 mmHg, FC 76 bpm.
        Saturazione ossigeno 96%, glicemia 102 mg/dL.
        Peso 74 kg, altezza 179 cm.
        Temperatura 36.7°C.
        """,
        
        """
        ESAME OBIETTIVO:
        PA: 120/80 mmHg
        Frequenza cardiaca: 68 bpm
        SpO2: 98%
        Temp: 37.1°C
        Peso corporeo: 65.5 kg
        Statura: 165 cm
        Glicemia: 95 mg/dL
        """,
        
        """
        Controllo di routine.
        Pressione 110/70, polso 62 battiti al minuto.
        Saturazione 99%, febbre assente (36.4°C).
        Il paziente pesa 80 kg ed è alto 180 cm.
        Glucosio nel sangue: 88 mg/dL.
        """,
        
        """
        Paziente anziana, 78 anni.
        Press. art.: 150/95 mmHg (ipertensione)
        FC: 88 bpm, sat O2: 94%
        Temperatura corporea: 36.8°C
        Peso: 58 kg, altezza: 155 cm
        BG: 180 mg/dL (diabete)
        """
    ]
    
    extractor = ParameterExtractor()
    json_generator = JSONOutputGenerator()
    
    print("🧪 TEST ESTRAZIONE PARAMETRI VITALI")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📋 TEST CASE {i}:")
        print(f"Testo: {text.strip()[:100]}...")
        
        # Estrai parametri
        parameters = extractor.extract_all_parameters(text)
        
        # Calcola BMI
        bmi = extractor.calculate_bmi(
            parameters.get('weight'), 
            parameters.get('height')
        )
        if bmi:
            parameters['bmi'] = bmi
        
        # Statistiche
        stats = extractor.get_extraction_stats(parameters)
        
        print(f"\n✅ PARAMETRI ESTRATTI:")
        for param, value in parameters.items():
            status = "✅" if value else "❌"
            print(f"  {status} {param.replace('_', ' ').title()}: {value or 'Non trovato'}")
        
        print(f"\n📊 STATISTICHE:")
        print(f"  • Parametri totali: {stats['total_parameters']}")
        print(f"  • Parametri estratti: {stats['extracted_parameters']}")
        print(f"  • Tasso di successo: {stats['extraction_rate']}%")
        
        # Test classificazioni
        print(f"\n🏥 CLASSIFICAZIONI CLINICHE:")
        bp_status = json_generator._classify_blood_pressure(parameters.get('blood_pressure'))
        hr_status = json_generator._classify_heart_rate(parameters.get('heart_rate'))
        glucose_status = json_generator._classify_glucose(parameters.get('glucose'))
        
        print(f"  • Pressione: {bp_status}")
        print(f"  • Frequenza cardiaca: {hr_status}")
        print(f"  • Glicemia: {glucose_status}")
        
        # Assessment rischio
        risk = json_generator._assess_risk(parameters)
        print(f"  • Livello di rischio: {risk['overall_risk_level']}")
        if risk['risk_factors']:
            print(f"  • Fattori di rischio: {', '.join(risk['risk_factors'])}")
        
        print("-" * 50)


def test_json_generation():
    """Testa la generazione di output JSON completo."""
    
    print("\n🔧 TEST GENERAZIONE JSON")
    print("=" * 50)
    
    # Parametri di esempio
    sample_parameters = {
        'blood_pressure': '135/85 mmHg',
        'heart_rate': '76 bpm',
        'glucose': '102 mg/dL',
        'saturation': '96%',
        'temperature': '36.7°C',
        'weight': '74 kg',
        'height': '179 cm',
        'bmi': '23.1'
    }
    
    json_generator = JSONOutputGenerator()
    
    # Genera output JSON completo
    output = json_generator.generate_output(
        file_path="test_report.pdf",
        raw_text="Testo grezzo di esempio...",
        cleaned_text="testo pulito di esempio...",
        parameters=sample_parameters
    )
    
    print("✅ JSON generato con successo!")
    print("\n📄 STRUTTURA OUTPUT:")
    
    # Mostra struttura
    for key in output.keys():
        print(f"  • {key}")
        if isinstance(output[key], dict):
            for subkey in output[key].keys():
                print(f"    - {subkey}")
    
    # Mostra esempi di valori
    print(f"\n📊 ESEMPI DI VALORI:")
    print(f"  • Tasso estrazione: {output['extraction_info']['extraction_rate_percent']}%")
    print(f"  • Livello di rischio: {output['risk_assessment']['overall_risk_level']}")
    print(f"  • Fattori di rischio: {len(output['risk_assessment']['risk_factors'])}")
    
    # Salva JSON di esempio
    with open('test_output.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("💾 JSON salvato in 'test_output.json'")


def run_regex_tests():
    """Testa i pattern regex individualmente."""
    
    print("\n🔍 TEST PATTERN REGEX")
    print("=" * 50)
    
    extractor = ParameterExtractor()
    
    # Test cases per ogni parametro
    test_cases = {
        'Pressione Arteriosa': [
            "Pressione arteriosa 120/80 mmHg",
            "PA: 135/85 mmHg",
            "Press. 110/70",
            "Sistolica 140, diastolica 90"
        ],
        'Frequenza Cardiaca': [
            "Frequenza cardiaca 75 bpm",
            "FC: 68 bpm",
            "Polso 82 battiti",
            "Battiti cardiaci: 90"
        ],
        'Glicemia': [
            "Glicemia 95 mg/dL",
            "Glucosio 110 mg/dL",
            "BG: 88",
            "Glucose: 102 mg/dl"
        ],
        'Saturazione': [
            "Saturazione ossigeno 98%",
            "SpO2: 96%",
            "Sat O2 94%",
            "Ossigenazione 99%"
        ]
    }
    
    for param_name, texts in test_cases.items():
        print(f"\n🎯 {param_name}:")
        
        for text in texts:
            if 'pressione' in param_name.lower():
                result = extractor.extract_blood_pressure(text)
            elif 'frequenza' in param_name.lower():
                result = extractor.extract_heart_rate(text)
            elif 'glicemia' in param_name.lower():
                result = extractor.extract_glucose(text)
            elif 'saturazione' in param_name.lower():
                result = extractor.extract_saturation(text)
            
            status = "✅" if result else "❌"
            print(f"  {status} '{text}' -> {result}")


if __name__ == "__main__":
    print("🚀 AVVIO TEST SUITE")
    print("=" * 60)
    
    try:
        # Esegui tutti i test
        test_parameter_extraction()
        test_json_generation()
        run_regex_tests()
        
        print("\n🎉 TUTTI I TEST COMPLETATI CON SUCCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRORE DURANTE I TEST: {str(e)}")
        import traceback
        traceback.print_exc()