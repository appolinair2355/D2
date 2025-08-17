"""
Version déploiement deployer50 - 17 Août 2025
Bot Telegram avec système YAML complet et nouveau format
"""
import os
import asyncio
import re
import json
import zipfile
import tempfile
import shutil
from datetime import datetime
from telethon import TelegramClient, events
from telethon.events import ChatAction
from dotenv import load_dotenv
from predictor import CardPredictor
from scheduler import PredictionScheduler
from yaml_database import init_yaml_database, yaml_db
from aiohttp import web
import threading

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
try:
    API_ID = int(os.getenv('API_ID') or '0')
    API_HASH = os.getenv('API_HASH') or ''
    BOT_TOKEN = os.getenv('BOT_TOKEN') or ''
    ADMIN_ID = int(os.getenv('ADMIN_ID') or '0')
    PORT = int(os.getenv('PORT') or '10000')
    
    # Validation des variables requises
    if not API_ID or API_ID == 0:
        raise ValueError("API_ID manquant ou invalide")
    if not API_HASH:
        raise ValueError("API_HASH manquant")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN manquant")
        
    print(f"✅ Configuration DEPLOYER50 chargée: API_ID={API_ID}, ADMIN_ID={ADMIN_ID}, PORT={PORT}")
except Exception as e:
    print(f"❌ Erreur configuration: {e}")
    print("Vérifiez vos variables d'environnement")
    exit(1)

# Variables d'état
detected_stat_channel = None
detected_display_channel = None
confirmation_pending = {}
prediction_interval = 5  # Intervalle en minutes avant de chercher "A" (défaut: 5 min)

def load_config():
    """Load configuration from YAML database"""
    global detected_stat_channel, detected_display_channel, prediction_interval
    try:
        if yaml_db:
            detected_stat_channel = yaml_db.get_config('stat_channel')
            detected_display_channel = yaml_db.get_config('display_channel')
            interval_config = yaml_db.get_config('prediction_interval')
            if detected_stat_channel:
                detected_stat_channel = int(detected_stat_channel)
            if detected_display_channel:
                detected_display_channel = int(detected_display_channel)
            if interval_config:
                prediction_interval = int(interval_config)
            print(f"✅ Configuration YAML chargée: Stats={detected_stat_channel}, Display={detected_display_channel}, Intervalle={prediction_interval}min")
        else:
            print("⚠️ Base YAML non disponible")
    except Exception as e:
        print(f"⚠️ Erreur chargement configuration: {e}")

def save_config():
    """Save configuration to YAML database"""
    try:
        if yaml_db:
            # Sauvegarde en base YAML
            yaml_db.set_config('stat_channel', detected_stat_channel)
            yaml_db.set_config('display_channel', detected_display_channel)
            yaml_db.set_config('prediction_interval', prediction_interval)
            print("💾 Configuration sauvegardée en YAML")
    except Exception as e:
        print(f"❌ Erreur sauvegarde configuration: {e}")

# Initialize YAML database
database = init_yaml_database()

# Gestionnaire de prédictions
predictor = CardPredictor()

# Initialize Telegram client
import time
session_name = f'deployer50_session_{int(time.time())}'
client = TelegramClient(session_name, API_ID, API_HASH)

# Serveur web pour monitoring Render.com
async def health_check(request):
    """Health check endpoint"""
    return web.Response(text="deployer50 Bot is running with YAML!", status=200)

async def bot_status(request):
    """Bot status endpoint"""
    status = {
        "version": "deployer50",
        "database": "YAML",
        "format": "🔵{numéro}— 3D🔵 statut :{statut}",
        "bot_online": True,
        "stat_channel": detected_stat_channel,
        "display_channel": detected_display_channel,
        "verification_offsets": "0→✅0️⃣, 1→✅1️⃣, 2→✅2️⃣, 3→✅3️⃣, >3→❌❌"
    }
    return web.json_response(status)

async def create_web_server():
    """Create and start web server for Render.com"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', bot_status)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"✅ Serveur web DEPLOYER50 démarré sur 0.0.0.0:{PORT}")
    return runner

async def start_bot():
    """Start the bot with proper configuration"""
    try:
        await client.start(bot_token=BOT_TOKEN)
        me = await client.get_me()
        print(f"Bot connecté: @{me.username}")
        
        # Load existing configuration
        load_config()
        
        return True
    except Exception as e:
        print(f"Erreur lors du démarrage du bot: {e}")
        return False

async def main():
    """Main function deployer50"""
    print("Démarrage du bot DEPLOYER50...")
    print(f"API_ID: {API_ID}")
    print(f"Bot Token configuré: {'Oui' if BOT_TOKEN else 'Non'}")
    print(f"Port: {PORT}")

    # Validate configuration
    if not API_ID or not API_HASH or not BOT_TOKEN:
        print("❌ Configuration manquante! Vérifiez vos variables d'environnement")
        return

    try:
        # Start web server first
        await create_web_server()
        
        # Start the bot
        if await start_bot():
            print("✅ Bot DEPLOYER50 en ligne avec système YAML!")
            print(f"🆕 Format: 🔵910— 3D🔵 statut :⌛")
            print(f"🌐 Accès web: http://0.0.0.0:{PORT}")
            await client.run_until_disconnected()
        else:
            print("❌ Échec du démarrage du bot")
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du bot demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
    finally:
        try:
            await client.disconnect()
            print("Bot DEPLOYER50 déconnecté proprement")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())