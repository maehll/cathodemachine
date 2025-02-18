from asyncua import Server, ua
import asyncio
import random
from datetime import datetime

class KathodenmaschinenSimulator:
    def __init__(self):
        self.server = Server()
        self.sheet_counter = 1000000
        
    def generiere_datensatz(self):
        self.sheet_counter += 1
        return f"{self.sheet_counter}|" + \
               f"{random.randint(100,999)}|" + \
               f"{random.randint(100,999)}|" + \
               f"{random.randint(1,3)}|" + \
               f"{random.randint(0,1)}|" + \
               f"{random.randint(0,4)}|" + \
               f"{random.randint(10,99)}|" + \
               f"{random.randint(10,99)}|" + \
               f"{random.randint(1,63)}|" + \
               f"{random.randint(100,900)}|" + \
               f"{random.randint(0,1)}|" + \
               f"{random.randint(0,500)}|" + \
               f"{random.randint(0,500)}|" + \
               f"{random.randint(0,4)}|" + \
               f"{random.randint(0,4)}|" + \
               f"{random.randint(0,4)}|" + \
               f"{random.randint(0,4)}|" + \
               f"{random.randint(100,999)}|" + \
               f"{random.randint(0,800)}|" + \
               f"{random.randint(0,800)}|" + \
               f"{random.randint(0,800)}|" + \
               f"{random.randint(0,800)}|" + \
               f"{random.randint(0,500)}|" + \
               f"{random.randint(100,999)}|" + \
               f"{random.randint(0,1)}"

    async def init(self):
        await self.server.init()
        
        # Server-Einstellungen
        self.server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")
        self.server.set_server_name("Kathodenmaschinen-Simulator")
        
        # Namespace erstellen
        uri = "http://kathodenmaschine.simulation"
        idx = await self.server.register_namespace(uri)
        
        # Objekte erstellen
        objects = self.server.nodes.objects
        self.kathodenmaschine = await objects.add_object(idx, "Kathodenmaschine")
        self.daten_node = await self.kathodenmaschine.add_variable(
            idx, 
            "Maschinendaten",
            "",
            ua.VariantType.String
        )
        
        # Variable schreibbar machen
        await self.daten_node.set_writable(True)
        
        print(f"[{datetime.now()}] Server initialisiert auf opc.tcp://localhost:4840")
        await self.server.start()
        print(f"[{datetime.now()}] Server gestartet und bereit für Verbindungen")

    async def cleanup(self):
        if hasattr(self, 'server'):
            await self.server.stop()
            print(f"[{datetime.now()}] Server gestoppt")

    async def run(self):
        try:
            await self.init()
            
            while True:
                try:
                    daten_string = self.generiere_datensatz()
                    await self.daten_node.write_value(daten_string)
                    print(f"[{datetime.now()}] Neue Daten geschrieben: {daten_string}")
                    await asyncio.sleep(6)
                except Exception as e:
                    print(f"Fehler beim Schreiben der Daten: {e}")
                    await asyncio.sleep(1)  # Kurze Pause bei Fehler
                    
        except Exception as e:
            print(f"Fehler im Simulator: {e}")
        finally:
            await self.cleanup()

async def main():
    simulator = KathodenmaschinenSimulator()
    await simulator.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulator wird beendet...")