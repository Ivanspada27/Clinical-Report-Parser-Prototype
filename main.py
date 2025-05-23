#!/usr/bin/env python3
"""
Medical Report Parameter Extractor
==================================
Sistema per l'estrazione di parametri vitali da referti medici scannerizzati.
Utilizza OCR e regex per identificare ed estrarre valori clinici.

Author: AI Assistant
Version: 1.0
"""

import json
import os
import sys
from typing import Dict, Optional, List
import argparse
from datetime import datetime

from ocr_processor import OCRProcessor
from parameter_extractor import ParameterExtractor
from json_output import JSONOutputGenerator


class MedicalReportProcessor:
    """
    Classe principale per processare referti medici e estrarre parametri vitali.
    """
    
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.parameter_extractor = ParameterExtractor()
        self.json_generator = JSONOutputGenerator()
    
    def process_file(self, file_path: str) -> Dict:
        """
        Processa un singolo file (PDF o immagine) ed estrae i parametri vitali.
        
        Args:
            file_path (str): Percorso al file da processare
            
        Returns:
            Dict: Dizionario con i parametri estratti
        """
        print(f"📄 Processando file: {file_path}")
        
        # Verifica esistenza file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File non trovato: {file_path}")
        
        # Step 1: OCR
        print("🔍 Eseguendo OCR...")
        raw_text = self.ocr_processor.extract_text(file_path)
        
        if not raw_text.strip():
            print("⚠️  Warning: Nessun testo estratto dal file")
            return self._empty_result(file_path)
        
        # Step 2: Pulizia testo
        print("🧹 Pulendo il testo...")
        cleaned_text = self.ocr_processor.clean_text(raw_text)
        
        # Step 3: Estrazione parametri
        print("🎯 Estraendo parametri vitali...")
        parameters = self.parameter_extractor.extract_all_parameters(cleaned_text)
        
        # Step 4: Generazione output strutturato
        result = self.json_generator.generate_output(
            file_path=file_path,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            parameters=parameters
        )
        
        print("✅ Processamento completato!")
        return result
    
    def process_directory(self, directory_path: str) -> List[Dict]:
        """
        Processa tutti i file compatibili in una directory.
        
        Args:
            directory_path (str): Percorso alla directory
            
        Returns:
            List[Dict]: Lista dei risultati per ogni file
        """
        results = []
        supported_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory non trovata: {directory_path}")
        
        files = [f for f in os.listdir(directory_path) 
                if os.path.splitext(f)[1].lower() in supported_extensions]
        
        if not files:
            print("⚠️  Nessun file compatibile trovato nella directory")
            return results
        
        print(f"📂 Trovati {len(files)} file da processare")
        
        for filename in files:
            file_path = os.path.join(directory_path, filename)
            try:
                result = self.process_file(file_path)
                results.append(result)
            except Exception as e:
                print(f"❌ Errore processando {filename}: {str(e)}")
                results.append(self._error_result(file_path, str(e)))
        
        return results
    
    def _empty_result(self, file_path: str) -> Dict:
        """Genera un risultato vuoto per file senza testo."""
        return self.json_generator.generate_output(
            file_path=file_path,
            raw_text="",
            cleaned_text="",
            parameters={}
        )
    
    def _error_result(self, file_path: str, error_message: str) -> Dict:
        """Genera un risultato di errore."""
        return {
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": error_message,
            "parameters": {}
        }


def main():
    """Funzione principale del programma."""
    parser = argparse.ArgumentParser(
        description="Estrattore di parametri vitali da referti medici"
    )
    parser.add_argument(
        "input_path",
        help="File o directory da processare"
    )
    parser.add_argument(
        "-o", "--output",
        default="output.json",
        help="File di output JSON (default: output.json)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Output verboso"
    )
    
    args = parser.parse_args()
    
    try:
        processor = MedicalReportProcessor()
        
        # Processa file singolo o directory
        if os.path.isfile(args.input_path):
            results = [processor.process_file(args.input_path)]
        elif os.path.isdir(args.input_path):
            results = processor.process_directory(args.input_path)
        else:
            print(f"❌ Errore: {args.input_path} non è un file o directory valido")
            sys.exit(1)
        
        # Salva risultati
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Risultati salvati in: {args.output}")
        
        # Statistiche finali
        total_files = len(results)
        successful = sum(1 for r in results if r.get('status') != 'error')
        print(f"📊 Processati: {successful}/{total_files} file con successo")
        
        # Output verboso
        if args.verbose:
            for result in results:
                print(f"\n📄 {result.get('file_path', 'Unknown')}")
                if result.get('status') == 'error':
                    print(f"❌ Errore: {result.get('error')}")
                else:
                    params = result.get('parameters', {})
                    found_params = sum(1 for v in params.values() if v is not None)
                    print(f"✅ Parametri estratti: {found_params}/8")
    
    except KeyboardInterrupt:
        print("\n⏹️  Operazione interrotta dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore critico: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()