import asyncio
import tkinter as tk
from ecu_client import KathodenmaschinenClient
from ecu_gui import KathodenmaschinenGUI
import sys
import traceback

class Application:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("Kathodenmaschinen Monitor")
            
            # Event Loop für async Operationen erstellen
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Client mit Fehlerbehandlung initialisieren
            try:
                self.client = KathodenmaschinenClient()
                print("Client erfolgreich initialisiert")
            except Exception as e:
                print(f"Fehler beim Initialisieren des Clients: {e}")
                traceback.print_exc()
                sys.exit(1)
            
            # GUI mit Fehlerbehandlung initialisieren
            try:
                self.gui = KathodenmaschinenGUI(self.client, self.root)
                self.client.gui = self.gui
                print("GUI erfolgreich initialisiert")
            except Exception as e:
                print(f"Fehler beim Initialisieren der GUI: {e}")
                traceback.print_exc()
                sys.exit(1)
            
            # Periodisch die Client-Updates ausführen
            self.root.after(100, self.update_client)
            
        except Exception as e:
            print(f"Fehler in der Application-Initialisierung: {e}")
            traceback.print_exc()
            sys.exit(1)
    
    def connect_client(self):
        try:
            self.loop.run_until_complete(self.client.connect())
            print("ECU-Client gestartet...")
        except Exception as e:
            print(f"Verbindungsfehler: {e}")
            traceback.print_exc()
            # Nach 5 Sekunden erneut versuchen
            self.root.after(5000, self.connect_client)
    
    def update_client(self):
        try:
            # Client-Update im bestehenden Event Loop ausführen
            self.loop.run_until_complete(self.client.update())
        except Exception as e:
            print(f"Update-Fehler: {e}")
            traceback.print_exc()
        finally:
            # Nächstes Update planen
            self.root.after(6000, self.update_client)
    
    def run(self):
        try:
            # Initial Connection versuchen
            self.connect_client()
            # GUI-Loop starten
            self.root.mainloop()
        except Exception as e:
            print(f"Fehler beim Ausführen der Anwendung: {e}")
            traceback.print_exc()
    
    def cleanup(self):
        try:
            if hasattr(self.client, 'db_handler'):
                self.client.db_handler.close()
            self.loop.close()
        except Exception as e:
            print(f"Fehler beim Cleanup: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    try:
        app = Application()
        app.run()
    except Exception as e:
        print(f"Kritischer Fehler: {e}")
        traceback.print_exc()
    finally:
        try:
            app.cleanup()
        except Exception as e:
            print(f"Fehler beim finalen Cleanup: {e}")
            traceback.print_exc() 