"""
Gestionnaire de base de données YAML pour le bot Telegram
Remplace complètement le système PostgreSQL
"""
import yaml
import os
from datetime import datetime, date, time
from typing import Dict, Any, Optional, List
from pathlib import Path

class YAMLDatabase:
    """Gestionnaire de base de données YAML pour le bot"""
    
    def __init__(self, db_dir: str = "yaml_db"):
        """
        Initialise la base de données YAML
        
        Args:
            db_dir: Répertoire pour stocker les fichiers YAML
        """
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(exist_ok=True)
        
        # Fichiers de données
        self.config_file = self.db_dir / "bot_config.yaml"
        self.predictions_file = self.db_dir / "predictions.yaml"
        self.auto_predictions_file = self.db_dir / "auto_predictions.yaml"
        self.messages_file = self.db_dir / "messages_history.yaml"
        
        self._init_files()
        print("✅ Base de données YAML initialisée")
    
    def _init_files(self):
        """Initialise les fichiers YAML s'ils n'existent pas"""
        default_files = {
            self.config_file: {},
            self.predictions_file: {"predictions": []},
            self.auto_predictions_file: {"auto_predictions": []},
            self.messages_file: {"messages": []}
        }
        
        for file_path, default_content in default_files.items():
            if not file_path.exists():
                self._save_yaml(file_path, default_content)
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Charge un fichier YAML"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            print(f"Erreur chargement {file_path}: {e}")
            return {}
    
    def _save_yaml(self, file_path: Path, data: Dict[str, Any]):
        """Sauvegarde un fichier YAML"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
        except Exception as e:
            print(f"Erreur sauvegarde {file_path}: {e}")
    
    # === CONFIGURATION ===
    def get_config(self, key: str) -> Optional[str]:
        """Récupère une valeur de configuration"""
        try:
            config = self._load_yaml(self.config_file)
            return config.get(key)
        except Exception as e:
            print(f"Erreur get_config({key}): {e}")
            return None
    
    def set_config(self, key: str, value: Any):
        """Définit une valeur de configuration"""
        try:
            config = self._load_yaml(self.config_file)
            config[key] = str(value) if value is not None else None
            config['updated_at'] = datetime.now().isoformat()
            self._save_yaml(self.config_file, config)
            print(f"✅ Configuration mise à jour: {key} = {value}")
        except Exception as e:
            print(f"Erreur set_config({key}, {value}): {e}")
    
    def get_all_config(self) -> Dict[str, Any]:
        """Récupère toute la configuration"""
        return self._load_yaml(self.config_file)
    
    # === PRÉDICTIONS MANUELLES ===
    def add_prediction(self, game_number: int, suit_combination: str = None, 
                      message_id: int = None, chat_id: int = None) -> bool:
        """Ajoute une nouvelle prédiction manuelle"""
        try:
            predictions_data = self._load_yaml(self.predictions_file)
            if "predictions" not in predictions_data:
                predictions_data["predictions"] = []
            
            prediction = {
                "id": len(predictions_data["predictions"]) + 1,
                "game_number": game_number,
                "suit_combination": suit_combination,
                "status": "⌛",
                "message_id": message_id,
                "chat_id": chat_id,
                "created_at": datetime.now().isoformat(),
                "verified_at": None,
                "prediction_type": "manual"
            }
            
            predictions_data["predictions"].append(prediction)
            self._save_yaml(self.predictions_file, predictions_data)
            print(f"✅ Prédiction ajoutée: #{game_number}")
            return True
        except Exception as e:
            print(f"Erreur add_prediction: {e}")
            return False
    
    def update_prediction_status(self, game_number: int, status: str) -> bool:
        """Met à jour le statut d'une prédiction"""
        try:
            predictions_data = self._load_yaml(self.predictions_file)
            if "predictions" not in predictions_data:
                return False
            
            for prediction in predictions_data["predictions"]:
                if prediction["game_number"] == game_number:
                    prediction["status"] = status
                    prediction["verified_at"] = datetime.now().isoformat()
                    self._save_yaml(self.predictions_file, predictions_data)
                    print(f"✅ Statut prédiction #{game_number} mis à jour: {status}")
                    return True
            
            return False
        except Exception as e:
            print(f"Erreur update_prediction_status: {e}")
            return False
    
    def get_prediction(self, game_number: int) -> Optional[Dict[str, Any]]:
        """Récupère une prédiction par numéro de jeu"""
        try:
            predictions_data = self._load_yaml(self.predictions_file)
            if "predictions" not in predictions_data:
                return None
            
            for prediction in predictions_data["predictions"]:
                if prediction["game_number"] == game_number:
                    return prediction
            return None
        except Exception as e:
            print(f"Erreur get_prediction: {e}")
            return None
    
    def get_pending_predictions(self) -> List[Dict[str, Any]]:
        """Récupère toutes les prédictions en attente"""
        try:
            predictions_data = self._load_yaml(self.predictions_file)
            if "predictions" not in predictions_data:
                return []
            
            return [p for p in predictions_data["predictions"] if p["status"] == "⌛"]
        except Exception as e:
            print(f"Erreur get_pending_predictions: {e}")
            return []
    
    def get_all_predictions(self) -> List[Dict[str, Any]]:
        """Récupère toutes les prédictions"""
        try:
            predictions_data = self._load_yaml(self.predictions_file)
            return predictions_data.get("predictions", [])
        except Exception as e:
            print(f"Erreur get_all_predictions: {e}")
            return []
    
    # === PRÉDICTIONS AUTOMATIQUES (SCHEDULER) ===
    def add_auto_prediction(self, numero: str, lanceur: str, heure_lancement: str,
                           heure_prediction: str, **kwargs) -> bool:
        """Ajoute une prédiction automatique"""
        try:
            auto_data = self._load_yaml(self.auto_predictions_file)
            if "auto_predictions" not in auto_data:
                auto_data["auto_predictions"] = []
            
            prediction = {
                "id": len(auto_data["auto_predictions"]) + 1,
                "numero": numero,
                "lanceur": lanceur,
                "heure_lancement": heure_lancement,
                "heure_prediction": heure_prediction,
                "statut": "⌛",
                "message_id": kwargs.get("message_id"),
                "chat_id": kwargs.get("chat_id"),
                "launched": kwargs.get("launched", False),
                "verified": kwargs.get("verified", False),
                "prediction_format": kwargs.get("prediction_format", "3D"),
                "created_at": date.today().isoformat()
            }
            
            auto_data["auto_predictions"].append(prediction)
            self._save_yaml(self.auto_predictions_file, auto_data)
            print(f"✅ Prédiction automatique ajoutée: {numero}")
            return True
        except Exception as e:
            print(f"Erreur add_auto_prediction: {e}")
            return False
    
    def update_auto_prediction(self, numero: str, **kwargs) -> bool:
        """Met à jour une prédiction automatique"""
        try:
            auto_data = self._load_yaml(self.auto_predictions_file)
            if "auto_predictions" not in auto_data:
                return False
            
            for prediction in auto_data["auto_predictions"]:
                if prediction["numero"] == numero:
                    for key, value in kwargs.items():
                        if key in prediction:
                            prediction[key] = value
                    self._save_yaml(self.auto_predictions_file, auto_data)
                    print(f"✅ Prédiction automatique {numero} mise à jour")
                    return True
            
            return False
        except Exception as e:
            print(f"Erreur update_auto_prediction: {e}")
            return False
    
    def get_auto_prediction(self, numero: str) -> Optional[Dict[str, Any]]:
        """Récupère une prédiction automatique par numéro"""
        try:
            auto_data = self._load_yaml(self.auto_predictions_file)
            if "auto_predictions" not in auto_data:
                return None
            
            for prediction in auto_data["auto_predictions"]:
                if prediction["numero"] == numero:
                    return prediction
            return None
        except Exception as e:
            print(f"Erreur get_auto_prediction: {e}")
            return None
    
    def get_pending_auto_predictions(self) -> List[Dict[str, Any]]:
        """Récupère toutes les prédictions automatiques en attente"""
        try:
            auto_data = self._load_yaml(self.auto_predictions_file)
            if "auto_predictions" not in auto_data:
                return []
            
            return [p for p in auto_data["auto_predictions"] 
                   if p["launched"] and not p["verified"]]
        except Exception as e:
            print(f"Erreur get_pending_auto_predictions: {e}")
            return []
    
    # === HISTORIQUE DES MESSAGES ===
    def add_message_history(self, chat_id: int, message_id: int, content: str, 
                           message_type: str = "normal"):
        """Ajoute un message à l'historique"""
        try:
            messages_data = self._load_yaml(self.messages_file)
            if "messages" not in messages_data:
                messages_data["messages"] = []
            
            message = {
                "id": len(messages_data["messages"]) + 1,
                "chat_id": chat_id,
                "message_id": message_id,
                "content": content[:500],  # Limiter la taille
                "message_type": message_type,
                "created_at": datetime.now().isoformat()
            }
            
            messages_data["messages"].append(message)
            
            # Garder seulement les 1000 derniers messages
            if len(messages_data["messages"]) > 1000:
                messages_data["messages"] = messages_data["messages"][-1000:]
            
            self._save_yaml(self.messages_file, messages_data)
        except Exception as e:
            print(f"Erreur add_message_history: {e}")
    
    # === STATISTIQUES ===
    def get_prediction_statistics(self) -> Dict[str, Any]:
        """Calcule les statistiques des prédictions"""
        try:
            predictions = self.get_all_predictions()
            auto_predictions = self._load_yaml(self.auto_predictions_file).get("auto_predictions", [])
            
            # Statistiques prédictions manuelles
            manual_total = len(predictions)
            manual_wins = len([p for p in predictions if '✅' in p.get("status", "")])
            manual_losses = len([p for p in predictions if '❌' in p.get("status", "")])
            manual_pending = len([p for p in predictions if p.get("status") == "⌛"])
            
            # Statistiques prédictions automatiques
            auto_total = len(auto_predictions)
            auto_wins = len([p for p in auto_predictions if '✅' in p.get("statut", "")])
            auto_losses = len([p for p in auto_predictions if '❌' in p.get("statut", "")])
            auto_pending = len([p for p in auto_predictions if p.get("statut") == "⌛"])
            
            total_predictions = manual_total + auto_total
            total_wins = manual_wins + auto_wins
            total_losses = manual_losses + auto_losses
            total_pending = manual_pending + auto_pending
            
            win_rate = (total_wins / total_predictions * 100) if total_predictions > 0 else 0.0
            
            return {
                "total": total_predictions,
                "wins": total_wins,
                "losses": total_losses,
                "pending": total_pending,
                "win_rate": win_rate,
                "manual": {
                    "total": manual_total,
                    "wins": manual_wins,
                    "losses": manual_losses,
                    "pending": manual_pending
                },
                "auto": {
                    "total": auto_total,
                    "wins": auto_wins,
                    "losses": auto_losses,
                    "pending": auto_pending
                }
            }
        except Exception as e:
            print(f"Erreur get_prediction_statistics: {e}")
            return {"total": 0, "wins": 0, "losses": 0, "pending": 0, "win_rate": 0.0}

# Instance globale
yaml_db = None

def init_yaml_database():
    """Initialise la base de données YAML"""
    global yaml_db
    try:
        yaml_db = YAMLDatabase()
        return yaml_db
    except Exception as e:
        print(f"❌ Erreur initialisation base YAML: {e}")
        return None