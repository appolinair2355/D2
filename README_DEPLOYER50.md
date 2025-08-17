# Package Déploiement deployer50 - 17 Août 2025

## Nouvelles Fonctionnalités DEPLOYER50:
• NOUVEAU FORMAT: "🔵910— 3D🔵 statut :⌛" (mot statut fixe)  
• Base de données YAML uniquement (plus de PostgreSQL)
• Système vérification étendu: offsets 0→✅0️⃣, 1→✅1️⃣, 2→✅2️⃣, 3→✅3️⃣, >3→❌❌
• Commande /intervalle (1-60 minutes) - Actuel: 1min
• Configuration persistante YAML complète
• Système déclenchement par As dans premier groupe uniquement
• Édition messages en temps réel avec nouveau format

## Architecture YAML:
- yaml_db/bot_config.yaml - Configuration
- yaml_db/predictions.yaml - Prédictions manuelles  
- yaml_db/auto_predictions.yaml - Prédictions automatiques
- yaml_db/messages_history.yaml - Historique messages

## Variables Render.com:
- Configurez toutes les variables de .env.example
- Port: 10000
- Start Command: python render_main_deployer50.py

## Commandes Disponibles:
/intervalle [minutes] - Configurer délai prédiction
/status - État complet avec intervalle et YAML
/deploy - Générer package deployer50

## Format Messages:
Prédiction: 🔵910— 3D🔵 statut :⌛
Réussite: 🔵910— 3D🔵 statut :✅0️⃣
Échec: 🔵910— 3D🔵 statut :❌❌

Prêt pour déploiement Render.com avec système YAML complet!