from asyncua import Server, ua
import asyncio
import random
from datetime import datetime

class KathodenmaschinenSimulator:
    def __init__(self):
        self.server = Server()
        self.sheet_counter = 1000000  # 7-stellige Sheet ID
        
    async def init(self):
        await self.server.init()
        
        # Server-Einstellungen
        self.server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")
        self.server.set_server_name("Kathodenmaschinen-Simulator")
        
        # Session-Einstellungen
        self.server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        self.server._session_timeout = 60000  # 60 Sekunden Session-Timeout
        
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
            try:
                await self.server.stop()
                print(f"[{datetime.now()}] Server gestoppt")
            except Exception as e:
                print(f"Fehler beim Stoppen des Servers: {e}")

    def generiere_datensatz(self):
        daten = {
            "sheet_id": self.sheet_counter,
            "section": random.randint(100, 999),
            "cell": random.randint(100, 999),
            "period": random.randint(1, 3),
            "sorting_out_deactivated": random.choice([0, 1]),
            "handling_code": random.randint(0, 4),
            "recommendation_code": f"{random.randint(10, 99)}|{random.randint(10, 99)}",
            "intervention_code": f"{random.randint(10, 99)}",
            "cathode_counter": random.randint(1, 63),
            "weight": random.randint(100, 999),
            "copper_not_released": random.choice([0, 1]),
            "buds_north": random.randint(0, 999),
            "buds_south": random.randint(0, 999),
            "stack_number_north": random.randint(0, 4),
            "stack_number_south": random.randint(0, 4),
            "stack_quality_north": random.randint(0, 4),
            "stack_quality_south": random.randint(0, 4),
            "limit_bud_size": random.randint(100, 999),
            "bud_size_ne": random.randint(0, 999),
            "bud_size_nw": random.randint(0, 999),
            "bud_size_sw": random.randint(0, 999),
            "bud_size_se": random.randint(0, 999),
            "deflection": random.randint(0, 999),
            "limit_deflection": random.randint(100, 999),
            "suggestion_ecu": random.randint(0, 9)
        }
        
        self.sheet_counter += 1
        return "|".join(str(value) for value in daten.values())

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
    try:
        await simulator.run()
    except KeyboardInterrupt:
        print("\nSimulator wird beendet...")
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
    finally:
        await simulator.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulator wird beendet...")