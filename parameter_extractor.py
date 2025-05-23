#!/usr/bin/env python3
"""
Parameter Extractor Module
=========================
Modulo per l'estrazione di parametri vitali tramite regex.
"""

import re
from typing import Dict, Optional, List, Tuple


class ParameterExtractor:
    """
    Classe per estrarre parametri vitali dal testo medico usando regex.
    """
    
    def __init__(self):
        """Inizializza l'estrattore con i pattern regex."""
        self._init_regex_patterns()
    
    def _init_regex_patterns(self):
        """Inizializza tutti i pattern regex per i parametri vitali."""
        
        # Pattern per pressione arteriosa (120/80 mmHg)
        self.blood_pressure_patterns = [
            r'(?:pressione|pa|press)\s*[:\s]*(\d{2,3})\s*/\s*(\d{2,3})\s*mmhg',
            r'(\d{2,3})\s*/\s*(\d{2,3})\s*mmhg',
            r'(?:pressione|pa)\s*[:\s]*(\d{2,3})\s*/\s*(\d{2,3})',
            r'(?:sistolica|sist)\s*[:\s]*(\d{2,3}).*?(?:diastolica|diast)\s*[:\s]*(\d{2,3})',
        ]
        
        # Pattern per frequenza cardiaca (bpm)
        self.heart_rate_patterns = [
            r'(?:frequenza|fc|freq)\s*[:\s]*(\d{2,3})\s*bpm',
            r'(\d{2,3})\s*bpm',
            r'(?:frequenza|fc|battiti)\s*[:\s]*(\d{2,3})',
            r'(?:polso|pulse)\s*[:\s]*(\d{2,3})',
        ]
        
        # Pattern per glicemia (mg/dL)
        self.glucose_patterns = [
            r'(?:glicemia|glucosio|gluc)\s*[:\s]*(\d{2,3})\s*mg/dl',
            r'(?:glicemia|glucosio)\s*[:\s]*(\d{2,3})',
            r'glucose?\s*:?\s*(\d{2,3})\s*mg/dl',
            r'bg\s*:?\s*(\d{2,3})',
        ]
        
        # Pattern per saturazione (SpO2 %)
        self.saturation_patterns = [
            r'(?:saturazione|sat|spo2)\s*[:\s]*(\d{2,3})\s*%',
            r'spo2\s*[:\s]*(\d{2,3})',
            r'(?:saturazione|ossigenazione)\s*[:\s]*(\d{2,3})',
            r'o2\s*[:\s]*(\d{2,3})\s*%',
        ]
        
        # Pattern per temperatura (°C)
        self.temperature_patterns = [
            r'(?:temperatura|temp|febbre)\s*[:\s]*(\d{2,3}\.?\d?)\s*°c',
            r'(?:temperatura|temp)\s*[:\s]*(\d{2,3}\.?\d?)',
            r'(\d{2,3}\.\d)\s*°c',
            r'(?:febbre|fever)\s*[:\s]*(\d{2,3}\.?\d?)',
        ]
        
        # Pattern per peso (kg)
        self.weight_patterns = [
            r'(?:peso|weight|wt)\s*[:\s]*(\d{2,3}\.?\d?)\s*kg',
            r'(?:peso|weight)\s*[:\s]*(\d{2,3}\.?\d?)',
            r'(\d{2,3}\.?\d?)\s*kg(?:\s|$)',
            r'body\s*weight\s*[:\s]*(\d{2,3}\.?\d?)',
        ]
        
        # Pattern per altezza (cm)
        self.height_patterns = [
            r'(?:altezza|height|ht)\s*[:\s]*(\d{3})\s*cm',
            r'(?:altezza|height)\s*[:\s]*(\d{3})',
            r'(\d{3})\s*cm(?:\s|$)',
            r'(?:statura|tall)\s*[:\s]*(\d{3})',
            r'(\d)\.\d{2}\s*m',  # formato metri (es. 1.75 m)
        ]
    
    def extract_all_parameters(self, text: str) -> Dict[str, Optional[str]]:
        """
        Estrae tutti i parametri vitali dal testo.
        
        Args:
            text (str): Testo da cui estrarre i parametri
            
        Returns:
            Dict: Dizionario con tutti i parametri estratti
        """
        # Preprocessa il testo
        processed_text = self._preprocess_text(text)
        
        return {
            'blood_pressure': self.extract_blood_pressure(processed_text),
            'heart_rate': self.extract_heart_rate(processed_text),
            'glucose': self.extract_glucose(processed_text),
            'saturation': self.extract_saturation(processed_text),
            'temperature': self.extract_temperature(processed_text),
            'weight': self.extract_weight(processed_text),
            'height': self.extract_height(processed_text),
            'bmi': None  # Calcolato automaticamente se peso e altezza sono presenti
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocessa il testo per migliorare l'estrazione."""
        # Converti in minuscolo
        text = text.lower()
        
        # Normalizza spazi e punteggiatura
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[,;]\s*', ' ', text)
        
        return text
    
    def extract_blood_pressure(self, text: str) -> Optional[str]:
        """Estrae la pressione arteriosa."""
        for pattern in self.blood_pressure_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    systolic, diastolic = match.groups()
                    # Validazione: valori realistici
                    if 70 <= int(systolic) <= 250 and 40 <= int(diastolic) <= 150:
                        return f"{systolic}/{diastolic} mmHg"
        return None
    
    def extract_heart_rate(self, text: str) -> Optional[str]:
        """Estrae la frequenza cardiaca."""
        for pattern in self.heart_rate_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rate = match.group(1)
                # Validazione: valori realistici
                if 40 <= int(rate) <= 200:
                    return f"{rate} bpm"
        return None
    
    def extract_glucose(self, text: str) -> Optional[str]:
        """Estrae la glicemia."""
        for pattern in self.glucose_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                glucose = match.group(1)
                # Validazione: valori realistici
                if 50 <= int(glucose) <= 500:
                    return f"{glucose} mg/dL"
        return None
    
    def extract_saturation(self, text: str) -> Optional[str]:
        """Estrae la saturazione di ossigeno."""
        for pattern in self.saturation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                saturation = match.group(1)
                # Validazione: valori realistici
                if 70 <= int(saturation) <= 100:
                    return f"{saturation}%"
        return None
    
    def extract_temperature(self, text: str) -> Optional[str]:
        """Estrae la temperatura corporea."""
        for pattern in self.temperature_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                temp = match.group(1)
                temp_float = float(temp)
                # Validazione: valori realistici (35-42°C)
                if 35.0 <= temp_float <= 42.0:
                    return f"{temp}°C"
        return None
    
    def extract_weight(self, text: str) -> Optional[str]:
        """Estrae il peso."""
        for pattern in self.weight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                weight = match.group(1)
                weight_float = float(weight)
                # Validazione: valori realistici (20-300 kg)
                if 20.0 <= weight_float <= 300.0:
                    return f"{weight} kg"
        return None
    
    def extract_height(self, text: str) -> Optional[str]:
        """Estrae l'altezza in cm o m."""
        for pattern in self.height_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                raw = match.group(0)
                digits_only = re.findall(r'\d+(?:\.\d+)?', raw)
                if not digits_only:
                    continue
                val = digits_only[0]
                try:
                    if 'm' in raw and float(val) < 3:  # Se < 3 metri, assumi metri
                        cm = int(float(val) * 100)
                        if 100 <= cm <= 250:
                            return f"{cm} cm"
                    else:  # Assumi centimetri
                        cm = int(float(val))
                        if 100 <= cm <= 250:
                            return f"{cm} cm"
                except ValueError:
                    continue
        return None


    
    def calculate_bmi(self, weight: Optional[str], height: Optional[str]) -> Optional[str]:
        """
        Calcola il BMI se peso e altezza sono disponibili.
        
        Args:
            weight (str): Peso in formato "XX kg"
            height (str): Altezza in formato "XXX cm"
            
        Returns:
            str: BMI calcolato o None
        """
        if not weight or not height:
            return None
        
        try:
            # Estrai valori numerici
            weight_kg = float(re.search(r'([\d.]+)', weight).group(1))
            height_cm = float(re.search(r'(\d+)', height).group(1))
            
            # Converti altezza in metri
            height_m = height_cm / 100
            
            # Calcola BMI
            bmi = weight_kg / (height_m ** 2)
            
            return f"{bmi:.1f}"
            
        except (ValueError, AttributeError):
            return None
    
    def get_extraction_stats(self, parameters: Dict[str, Optional[str]]) -> Dict[str, int]:
        """
        Restituisce statistiche sui parametri estratti.
        
        Args:
            parameters (Dict): Parametri estratti
            
        Returns:
            Dict: Statistiche di estrazione
        """
        total_params = len(parameters)
        extracted_params = sum(1 for v in parameters.values() if v is not None)
        
        return {
            'total_parameters': total_params,
            'extracted_parameters': extracted_params,
            'extraction_rate': round((extracted_params / total_params) * 100, 1)
        }