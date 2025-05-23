#!/usr/bin/env python3
"""
OCR Processor Module
===================
Modulo per l'estrazione e pulizia del testo da PDF e immagini.
"""

import re
import os
from typing import Optional
from PIL import Image
import pytesseract
import pdf2image


class OCRProcessor:
    """
    Classe per gestire l'estrazione OCR da diversi tipi di file.
    """
    
    def __init__(self, tesseract_config: str = "--oem 3 --psm 6"):
        """
        Inizializza il processore OCR.
        
        Args:
            tesseract_config (str): Configurazione per Tesseract
        """
        self.tesseract_config = tesseract_config
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Verifica che le dipendenze OCR siano disponibili."""
        try:
            # Test Tesseract
            pytesseract.get_tesseract_version()
        except Exception as e:
            raise RuntimeError(
                "Tesseract non trovato. Installa con: "
                "sudo apt-get install tesseract-ocr (Linux) o "
                "brew install tesseract (macOS)"
            )
    
    def extract_text(self, file_path: str) -> str:
        """
        Estrae testo da un file PDF o immagine.
        
        Args:
            file_path (str): Percorso al file
            
        Returns:
            str: Testo estratto
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            return self._extract_from_image(file_path)
        else:
            raise ValueError(f"Formato file non supportato: {file_ext}")
    
    def _extract_from_pdf(self, pdf_path: str) -> str:
        """
        Estrae testo da un file PDF.
        
        Args:
            pdf_path (str): Percorso al PDF
            
        Returns:
            str: Testo estratto da tutte le pagine
        """
        try:
            # Converti PDF in immagini
            pages = pdf2image.convert_from_path(pdf_path, dpi=300)
            
            extracted_text = []
            for i, page in enumerate(pages):
                print(f"  📄 Processando pagina {i+1}/{len(pages)}")
                
                # OCR su ogni pagina
                page_text = pytesseract.image_to_string(
                    page, 
                    lang='ita+eng',  # Supporto italiano e inglese
                    config=self.tesseract_config
                )
                
                if page_text.strip():
                    extracted_text.append(page_text)
            
            return '\n\n'.join(extracted_text)
            
        except Exception as e:
            raise RuntimeError(f"Errore durante l'estrazione dal PDF: {str(e)}")
    
    def _extract_from_image(self, image_path: str) -> str:
        """
        Estrae testo da un file immagine.
        
        Args:
            image_path (str): Percorso all'immagine
            
        Returns:
            str: Testo estratto
        """
        try:
            # Apri l'immagine
            image = Image.open(image_path)
            
            # Converti in RGB se necessario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # OCR
            text = pytesseract.image_to_string(
                image,
                lang='ita+eng',  # Supporto italiano e inglese
                config=self.tesseract_config
            )
            
            return text
            
        except Exception as e:
            raise RuntimeError(f"Errore durante l'estrazione dall'immagine: {str(e)}")
    
    def clean_text(self, raw_text: str) -> str:
        """
        Pulisce il testo estratto dall'OCR rimuovendo artefatti comuni.
        
        Args:
            raw_text (str): Testo grezzo dall'OCR
            
        Returns:
            str: Testo pulito
        """
        if not raw_text:
            return ""
        
        text = raw_text
        
        # Rimuovi caratteri strani e simboli non ASCII comuni dell'OCR
        text = re.sub(r'[^\w\s\.,;:()\-+/=%°<>àèìòùáéíóúâêîôûäëïöüç]', ' ', text)
        
        # Sistema spazi multipli
        text = re.sub(r'\s+', ' ', text)
        
        # Rimuovi righe molto corte (probabilmente artefatti)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Mantieni linee con almeno 3 caratteri o che contengono numeri
            if len(line) >= 3 or re.search(r'\d', line):
                cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        # Normalizza punteggiatura comune
        text = re.sub(r'(\d)\s*[,\.]\s*(\d)', r'\1.\2', text)  # Numeri decimali
        text = re.sub(r'(\d)\s*/\s*(\d)', r'\1/\2', text)      # Frazioni come pressione
        
        # Rimuovi spazi prima della punteggiatura
        text = re.sub(r'\s+([,.;:])', r'\1', text)
        
        # Aggiungi spazio dopo punteggiatura se mancante
        text = re.sub(r'([,.;:])([a-zA-Z])', r'\1 \2', text)
        
        return text.strip()
    
    def preprocess_for_extraction(self, text: str) -> str:
        """
        Preprocessa il testo per migliorare l'estrazione dei parametri.
        
        Args:
            text (str): Testo da preprocessare
            
        Returns:
            str: Testo preprocessato
        """
        # Converti tutto in minuscolo per le regex
        text = text.lower()
        
        # Standardizza unità di misura comuni
        replacements = {
            'mmhg': 'mmHg',
            'bpm': 'bpm',
            'mg/dl': 'mg/dL',
            'mg dl': 'mg/dL',
            'spo2': 'SpO2',
            '°c': '°C',
            ' c°': '°C',
            'gradi': '°C',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Standardizza termini medici comuni
        medical_terms = {
            'pressione arteriosa': 'pressione',
            'press art': 'pressione',
            'pa': 'pressione',
            'frequenza cardiaca': 'frequenza',
            'freq cardiaca': 'frequenza',
            'fc': 'frequenza',
            'battiti': 'bpm',
            'saturazione ossigeno': 'saturazione',
            'sat o2': 'saturazione',
            'ossigenazione': 'saturazione',
            'glicemia': 'glicemia',
            'glucosio': 'glicemia',
            'temperatura corporea': 'temperatura',
            'temp': 'temperatura',
            'febbre': 'temperatura',
        }
        
        for old, new in medical_terms.items():
            text = text.replace(old, new)
        
        return text