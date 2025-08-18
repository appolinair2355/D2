import re
import random
from typing import Tuple, Optional, List

class CardPredictor:
    """Card game prediction engine with pattern matching and result verification"""
    
    def __init__(self):
        self.last_predictions = []  # Liste [(numéro, combinaison)]
        self.prediction_status = {}  # Statut des prédictions par numéro
        self.processed_messages = set()  # Pour éviter les doublons
        self.status_log = []  # Historique des statuts
        self.prediction_messages = {}  # Stockage des IDs de messages de prédiction
        # Système As uniquement (plus de numéros déclencheurs)
        
    def reset(self):
        """Reset all prediction data"""
        self.last_predictions.clear()
        self.prediction_status.clear()
        self.processed_messages.clear()
        self.status_log.clear()
        self.prediction_messages.clear()
        print("Données de prédiction réinitialisées")

    def extract_game_number(self, message: str) -> Optional[int]:
        """Extract game number from message using pattern #N followed by digits"""
        try:
            # Look for patterns like "#N 123" or "#N123"
            match = re.search(r"#N\s*(\d+)", message, re.IGNORECASE)
            if match:
                return int(match.group(1))
            
            # Alternative pattern matching
            match = re.search(r"jeu\s*#?\s*(\d+)", message, re.IGNORECASE)
            if match:
                return int(match.group(1))
                
            return None
        except (ValueError, AttributeError):
            return None

    def extract_symbols_from_parentheses(self, message: str) -> List[str]:
        """Extract content from parentheses in the message"""
        try:
            return re.findall(r"\(([^)]*)\)", message)
        except Exception:
            return []

    def count_total_cards(self, symbols_str: str) -> int:
        """Count total card symbols in a string"""
        card_symbols = ['♠️', '♥️', '♦️', '♣️', '♠', '♥', '♦', '♣']
        count = 0
        for symbol in card_symbols:
            count += symbols_str.count(symbol)
        return count

    def normalize_suits(self, suits_str: str) -> str:
        """Normalize and sort card suits"""
        # Map emoji versions to simple versions
        suit_map = {
            '♠️': '♠', '♥️': '♥', '♦️': '♦', '♣️': '♣'
        }
        
        normalized = suits_str
        for emoji, simple in suit_map.items():
            normalized = normalized.replace(emoji, simple)
        
        # Extract only card symbols and sort them
        suits = [c for c in normalized if c in '♠♥♦♣']
        return ''.join(sorted(set(suits)))

    def should_predict(self, message: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """Determine if a prediction should be made based on the message - LOGIQUE As"""
        try:
            # Extract game number
            game_number = self.extract_game_number(message)
            if game_number is None:
                return False, None, None

            # Extract symbols from parentheses first to check for Ace trigger
            matches = self.extract_symbols_from_parentheses(message)
            if len(matches) < 2:
                print(f"❌ Pas assez de groupes de parenthèses (besoin de 2): {matches}")
                return False, None, None

            first_group = matches[0]
            second_group = matches[1]
            
            # NOUVELLE LOGIQUE: Vérifier la présence d'As (A) dans les groupes
            ace_count_first = first_group.count('A')
            ace_count_second = second_group.count('A')
            
            print(f"🎯 Analyse As: Premier groupe='{first_group}' (As: {ace_count_first}), Deuxième groupe='{second_group}' (As: {ace_count_second})")
            
            # RÈGLES DE DÉCLENCHEMENT STRICTES:
            # 1. Prédire SEULEMENT si EXACTEMENT 1 As dans le PREMIER groupe
            # 2. NE PAS prédire si As dans le DEUXIÈME groupe  
            # 3. NE PAS prédire si 2 ou plus As dans le PREMIER groupe
            if ace_count_first != 1:
                if ace_count_first == 0:
                    print(f"❌ Pas d'As dans le premier groupe, pas de prédiction")
                else:
                    print(f"❌ {ace_count_first} As détectés dans le premier groupe (il faut exactement 1), pas de prédiction")
                return False, None, None
                
            if ace_count_second > 0:
                print(f"❌ {ace_count_second} As détecté(s) dans le deuxième groupe, prédiction bloquée")
                return False, None, None
            
            print(f"✅ Condition As validée: EXACTEMENT 1 As dans premier groupe uniquement")

            # Calculate predicted game number (jeu suivant)
            predicted_game = game_number + 1
            
            # ANTI-DOUBLON: Check if predicted game already has a prediction (any status)
            if predicted_game in self.prediction_status:
                print(f"❌ Prédiction déjà existante pour le jeu #{predicted_game} (statut: {self.prediction_status[predicted_game]}), ignoré")
                return False, None, None
            
            # Check if current game already processed
            if game_number in self.processed_messages:
                print(f"Jeu #{game_number} déjà traité, ignoré")
                return False, None, None

            # Get suits from first group
            suits = self.normalize_suits(first_group)
            
            if not suits:
                return False, None, None

            # Mark current game as processed
            self.processed_messages.add(game_number)
            
            # Create prediction for target game
            self.prediction_status[predicted_game] = '⌛'
            self.last_predictions.append((predicted_game, suits))
            
            print(f"✅ Prédiction créée: Jeu #{predicted_game} -> {suits} (déclenchée par #{game_number} avec As dans premier groupe)")
            print(f"📊 Prédictions actives: {[k for k, v in self.prediction_status.items() if v == '⌛']}")
            return True, predicted_game, suits

        except Exception as e:
            print(f"Erreur dans should_predict: {e}")
            return False, None, None
    
    def store_prediction_message(self, game_number: int, message_id: int, chat_id: int):
        """Store prediction message ID for later editing"""
        self.prediction_messages[game_number] = {'message_id': message_id, 'chat_id': chat_id}
        
    def get_prediction_message(self, game_number: int):
        """Get stored prediction message details"""
        return self.prediction_messages.get(game_number)

    def verify_prediction(self, message: str) -> Tuple[Optional[bool], Optional[int]]:
        """Verify prediction results based on verification message"""
        try:
            # Check for verification tags
            if not any(tag in message for tag in ["✅", "🔰", "❌", "⭕"]):
                return None, None

            # Extract game number
            game_number = self.extract_game_number(message)
            if game_number is None:
                return None, None

            # Extract symbol groups
            groups = self.extract_symbols_from_parentheses(message)
            if len(groups) < 2:
                return None, None

            first_group = groups[0]
            second_group = groups[1]

            def is_valid_result():
                """Check if the result has valid card distribution (2+2)"""
                return (self.count_total_cards(first_group) == 2 and 
                        self.count_total_cards(second_group) == 2)

            # Check for pending predictions within offset range (0, 1, 2, 3)
            for offset in range(4):  # Check 0, 1, 2, 3 games back
                target_number = game_number - offset
                
                if (target_number in self.prediction_status and 
                    self.prediction_status[target_number] == '⌛'):
                    
                    if is_valid_result():
                        # Success with offset indicator
                        if offset == 0:
                            statut = '✅0️⃣'  # Perfect timing
                        elif offset == 1:
                            statut = '✅1️⃣'  # 1 game late
                        elif offset == 2:
                            statut = '✅2️⃣'  # 2 games late
                        else:
                            statut = '✅3️⃣'  # 3 games late
                            
                        self.prediction_status[target_number] = statut
                        self.status_log.append((target_number, statut))
                        print(f"Prédiction réussie: Jeu #{target_number} avec offset {offset}")
                        return True, target_number
            
            # No matching predictions found
            return None, None

        except Exception as e:
            print(f"Erreur dans verify_prediction: {e}")
            return None, None
    
    def check_expired_predictions(self, current_game_number: int) -> List[int]:
        """Check for expired predictions (offset > 3) and mark them as failed"""
        expired_predictions = []
        
        for pred_num, status in list(self.prediction_status.items()):
            if status == '⌛' and current_game_number > pred_num + 3:  # Changé de 2 à 3
                # Marquer comme échouée
                self.prediction_status[pred_num] = '❌❌'
                self.status_log.append((pred_num, '❌❌'))
                expired_predictions.append(pred_num)
                print(f"❌ Prédiction expirée: #{pred_num} marquée comme échouée (jeu actuel: #{current_game_number})")
        
        return expired_predictions

    def is_pending_edit_message(self, message: str) -> Tuple[bool, Optional[int]]:
        """Check if message is pending edit (contains ⏰ or 🕐)"""
        game_number = self.extract_game_number(message)
        if game_number and ("⏰" in message or "🕐" in message):
            print(f"🔄 Message #{game_number} en cours d'édition détecté: ⏰ ou 🕐")
            return True, game_number
        return False, None
                        return True, target_number
                    else:
                        # Failed prediction
                        statut = '❌❌'
                        self.prediction_status[target_number] = statut
                        self.status_log.append((target_number, statut))
                        print(f"Prédiction échouée: Jeu #{target_number}")
                        return False, target_number

            return None, None

        except Exception as e:
            print(f"Erreur dans verify_prediction: {e}")
            return None, None

    def get_statistics(self) -> dict:
        """Get prediction statistics"""
        try:
            total_predictions = len(self.status_log)
            if total_predictions == 0:
                return {
                    'total': 0,
                    'wins': 0,
                    'losses': 0,
                    'pending': len([s for s in self.prediction_status.values() if s == '⏳']),
                    'win_rate': 0.0
                }

            wins = sum(1 for _, status in self.status_log if '✅' in status)
            losses = sum(1 for _, status in self.status_log if '❌' in status or '⭕' in status)
            pending = len([s for s in self.prediction_status.values() if s == '⌛'])
            win_rate = (wins / total_predictions * 100) if total_predictions > 0 else 0.0

            return {
                'total': total_predictions,
                'wins': wins,
                'losses': losses,
                'pending': pending,
                'win_rate': win_rate
            }
        except Exception as e:
            print(f"Erreur dans get_statistics: {e}")
            return {'total': 0, 'wins': 0, 'losses': 0, 'pending': 0, 'win_rate': 0.0}

    def get_recent_predictions(self, count: int = 10) -> List[Tuple[int, str]]:
        """Get recent predictions with their status"""
        try:
            recent = []
            for game_num, suits in self.last_predictions[-count:]:
                status = self.prediction_status.get(game_num, '⌛')
                recent.append((game_num, suits, status))
            return recent
        except Exception as e:
            print(f"Erreur dans get_recent_predictions: {e}")
            return []