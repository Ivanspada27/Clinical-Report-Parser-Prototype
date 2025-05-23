#!/usr/bin/env python3
"""
JSON Output Generator Module
===========================
Modulo per generare output JSON strutturato dai parametri estratti.
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, Any
from parameter_extractor import ParameterExtractor


class JSONOutputGenerator:
    """
    Classe per generare output JSON strutturato dai parametri vitali estratti.
    """
    
    def __init__(self):
        """Inizializza il generatore JSON."""
        self.parameter_extractor = ParameterExtractor()
    
    def generate_output(
        self, 
        file_path: str, 
        raw_text: str, 
        cleaned_text: str, 
        parameters: Dict[str, Optional[str]]
    ) -> Dict[str, Any]:
        """
        Genera l'output JSON strutturato completo.
        
        Args:
            file_path (str): Percorso del file processato
            raw_text (str): Testo grezzo dall'OCR
            cleaned_text (str): Testo pulito
            parameters (Dict): Parametri estratti
            
        Returns:
            Dict: Output JSON strutturato
        """
        # Calcola BMI se possibile
        bmi = self.parameter_extractor.calculate_bmi(
            parameters.get('weight'), 
            parameters.get('height')
        )
        if bmi:
            parameters['bmi'] = bmi
        
        # Genera metadati file
        file_info = self._get_file_info(file_path)
        
        # Genera statistiche estrazione
        extraction_stats = self.parameter_extractor.get_extraction_stats(parameters)
        
        # Genera classificazione rischio (bonus)
        risk_assessment = self._assess_risk(parameters)
        
        # Struttura output principale
        output = {
            "metadata": {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size_bytes": file_info["size"],
                "file_extension": file_info["extension"],
                "processing_timestamp": datetime.now().isoformat(),
                "processor_version": "1.0"
            },
            "extraction_info": {
                "total_parameters": extraction_stats["total_parameters"],
                "extracted_parameters": extraction_stats["extracted_parameters"],
                "extraction_rate_percent": extraction_stats["extraction_rate"],
                "text_length_raw": len(raw_text),
                "text_length_cleaned": len(cleaned_text),
                "processing_status": "success"
            },
            "vital_parameters": {
                "blood_pressure": {
                    "value": parameters.get('blood_pressure'),
                    "unit": "mmHg",
                    "normal_range": "90-120/60-80 mmHg",
                    "status": self._classify_blood_pressure(parameters.get('blood_pressure'))
                },
                "heart_rate": {
                    "value": parameters.get('heart_rate'),
                    "unit": "bpm",
                    "normal_range": "60-100 bpm",
                    "status": self._classify_heart_rate(parameters.get('heart_rate'))
                },
                "glucose": {
                    "value": parameters.get('glucose'),
                    "unit": "mg/dL",
                    "normal_range": "70-100 mg/dL (fasting)",
                    "status": self._classify_glucose(parameters.get('glucose'))
                },
                "oxygen_saturation": {
                    "value": parameters.get('saturation'),
                    "unit": "%",
                    "normal_range": "95-100%",
                    "status": self._classify_saturation(parameters.get('saturation'))
                },
                "body_temperature": {
                    "value": parameters.get('temperature'),
                    "unit": "°C",
                    "normal_range": "36.1-37.2°C",
                    "status": self._classify_temperature(parameters.get('temperature'))
                },
                "weight": {
                    "value": parameters.get('weight'),
                    "unit": "kg",
                    "normal_range": "varies by height/age",
                    "status": "unknown"
                },
                "height": {
                    "value": parameters.get('height'),
                    "unit": "cm",
                    "normal_range": "varies by age/gender",
                    "status": "unknown"
                },
                "bmi": {
                    "value": parameters.get('bmi'),
                    "unit": "kg/m²",
                    "normal_range": "18.5-24.9",
                    "status": self._classify_bmi(parameters.get('bmi'))
                }
            },
            "risk_assessment": risk_assessment,
            "raw_text_sample": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
            "cleaned_text_sample": cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text
        }
        
        return output
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Ottiene informazioni sul file."""
        try:
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "extension": os.path.splitext(file_path)[1].lower(),
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        except OSError:
            return {
                "size": 0,
                "extension": "unknown",
                "last_modified": None
            }
    
    def _classify_blood_pressure(self, bp: Optional[str]) -> str:
        """Classifica la pressione arteriosa."""
        if not bp:
            return "unknown"
        
        try:
            systolic, diastolic = map(int, bp.split('/')[0:2])
            
            if systolic < 90 or diastolic < 60:
                return "low"
            elif systolic <= 120 and diastolic <= 80:
                return "normal"
            elif systolic <= 129 and diastolic <= 80:
                return "elevated"
            elif systolic <= 139 or diastolic <= 89:
                return "high_stage1"
            else:
                return "high_stage2"
        except (ValueError, IndexError):
            return "invalid"
    
    def _classify_heart_rate(self, hr: Optional[str]) -> str:
        """Classifica la frequenza cardiaca."""
        if not hr:
            return "unknown"
        
        try:
            rate = int(hr.split()[0])
            
            if rate < 60:
                return "low"
            elif 60 <= rate <= 100:
                return "normal"
            else:
                return "high"
        except (ValueError, IndexError):
            return "invalid"
    
    def _classify_glucose(self, glucose: Optional[str]) -> str:
        """Classifica la glicemia."""
        if not glucose:
            return "unknown"
        
        try:
            value = int(glucose.split()[0])
            
            if value < 70:
                return "low"
            elif 70 <= value <= 100:
                return "normal"
            elif 101 <= value <= 125:
                return "prediabetes"
            else:
                return "diabetes"
        except (ValueError, IndexError):
            return "invalid"
    
    def _classify_saturation(self, sat: Optional[str]) -> str:
        """Classifica la saturazione di ossigeno."""
        if not sat:
            return "unknown"
        
        try:
            value = int(sat.replace('%', ''))
            
            if value < 90:
                return "critical"
            elif 90 <= value < 95:
                return "low"
            else:
                return "normal"
        except (ValueError, IndexError):
            return "invalid"
    
    def _classify_temperature(self, temp: Optional[str]) -> str:
        """Classifica la temperatura corporea."""
        if not temp:
            return "unknown"
        
        try:
            value = float(temp.replace('°C', ''))
            
            if value < 36.1:
                return "low"
            elif 36.1 <= value <= 37.2:
                return "normal"
            elif 37.3 <= value <= 38.0:
                return "mild_fever"
            else:
                return "high_fever"
        except (ValueError, IndexError):
            return "invalid"
    
    def _classify_bmi(self, bmi: Optional[str]) -> str:
        """Classifica il BMI."""
        if not bmi:
            return "unknown"
        
        try:
            value = float(bmi)
            
            if value < 18.5:
                return "underweight"
            elif 18.5 <= value <= 24.9:
                return "normal"
            elif 25.0 <= value <= 29.9:
                return "overweight"
            else:
                return "obese"
        except (ValueError, IndexError):
            return "invalid"
    
    def _assess_risk(self, parameters: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """
        Valuta il rischio generale basato sui parametri vitali.
        
        Args:
            parameters (Dict): Parametri vitali estratti
            
        Returns:
            Dict: Valutazione del rischio
        """
        risk_factors = []
        risk_level = "unknown"
        
        # Controlla ogni parametro
        bp_status = self._classify_blood_pressure(parameters.get('blood_pressure'))
        if bp_status in ['high_stage1', 'high_stage2']:
            risk_factors.append("Ipertensione")
        
        hr_status = self._classify_heart_rate(parameters.get('heart_rate'))
        if hr_status in ['low', 'high']:
            risk_factors.append("Frequenza cardiaca anomala")
        
        glucose_status = self._classify_glucose(parameters.get('glucose'))
        if glucose_status in ['prediabetes', 'diabetes']:
            risk_factors.append("Glicemia elevata")
        
        sat_status = self._classify_saturation(parameters.get('saturation'))
        if sat_status in ['low', 'critical']:
            risk_factors.append("Saturazione ossigeno bassa")
        
        temp_status = self._classify_temperature(parameters.get('temperature'))
        if temp_status in ['mild_fever', 'high_fever']:
            risk_factors.append("Febbre")
        
        bmi_status = self._classify_bmi(parameters.get('bmi'))
        if bmi_status in ['underweight', 'obese']:
            risk_factors.append("BMI anomalo")
        
        # Determina livello di rischio
        if len(risk_factors) == 0:
            risk_level = "low"
        elif len(risk_factors) <= 2:
            risk_level = "moderate"
        else:
            risk_level = "high"
        
        return {
            "overall_risk_level": risk_level,
            "risk_factors": risk_factors,
            "risk_factor_count": len(risk_factors),
            "recommendations": self._get_recommendations(risk_factors),
            "requires_medical_attention": len(risk_factors) > 2 or sat_status == 'critical'
        }
    
    def _get_recommendations(self, risk_factors: list) -> list:
        """Genera raccomandazioni basate sui fattori di rischio."""
        recommendations = []
        
        if "Ipertensione" in risk_factors:
            recommendations.append("Consultare un medico per la pressione alta")
            recommendations.append("Ridurre il consumo di sale")
        
        if "Glicemia elevata" in risk_factors:
            recommendations.append("Controllo diabetologico")
            recommendations.append("Monitoraggio glicemia regolare")
        
        if "Saturazione ossigeno bassa" in risk_factors:
            recommendations.append("Consulenza medica urgente")
        
        if "Febbre" in risk_factors:
            recommendations.append("Monitoraggio temperatura")
            recommendations.append("Idratazione adeguata")
        
        if "BMI anomalo" in risk_factors:
            recommendations.append("Consulenza nutrizionale")
        
        if not recommendations:
            recommendations.append("Continuare controlli regolari")
        
        return recommendations
    
    def save_to_file(self, data: Dict[str, Any], output_path: str) -> bool:
        """
        Salva i dati JSON su file.
        
        Args:
            data (Dict): Dati da salvare
            output_path (str): Percorso file output
            
        Returns:
            bool: True se salvato con successo
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Errore salvando JSON: {str(e)}")
            return False