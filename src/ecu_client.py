from asyncua import Client
import asyncio
from datetime import datetime

class KathodenmaschinenClient:
    def __init__(self, url="opc.tcp://localhost:4840/freeopcua/server/"):
        self.url = url
        self.client = Client(url=self.url)
        self.daten_node = None
        self.gui = None
        
        # Schwellwerte als Dictionary definieren
        self.schwellwerte = {
            "buds_north": {"min": 0, "max": 500, "beschreibung": "Anzahl Butzen Nord"},
            "buds_south": {"min": 0, "max": 500, "beschreibung": "Anzahl Butzen Süd"},
            "bud_size_ne": {"min": 0, "max": 800, "beschreibung": "Butzengröße Nordost"},
            "bud_size_nw": {"min": 0, "max": 800, "beschreibung": "Butzengröße Nordwest"},
            "bud_size_sw": {"min": 0, "max": 800, "beschreibung": "Butzengröße Südwest"},
            "bud_size_se": {"min": 0, "max": 800, "beschreibung": "Butzengröße Südost"},
            "deflection": {"min": 0, "max": 500, "beschreibung": "Durchbiegung"},
            "weight": {"min": 100, "max": 900, "beschreibung": "Gewicht"}
        }

    async def connect(self):
        await self.client.connect()
        print(f"Verbunden mit Server unter {self.url}")
        
        # Node-ID für die Maschinendaten finden
        uri = "http://kathodenmaschine.simulation"
        idx = await self.client.get_namespace_index(uri)
        
        # Zugriff auf die Daten-Node
        objects = self.client.nodes.objects
        kathodenmaschine = await objects.get_child([f"{idx}:Kathodenmaschine"])
        self.daten_node = await kathodenmaschine.get_child([f"{idx}:Maschinendaten"])
        
        if not self.daten_node:
            raise Exception("Daten-Node nicht gefunden")

    async def update(self):
        if not self.daten_node:
            print("Keine Verbindung zum Server - versuche neu zu verbinden...")
            try:
                await self.connect()
            except Exception as e:
                print(f"Neuverbindung fehlgeschlagen: {e}")
                return

        try:
            daten_string = await self.daten_node.read_value()
            
            if daten_string:
                daten = self.parse_daten(daten_string)
                
                if self.gui:
                    self.gui.add_data("data", daten)
                else:
                    print(f"[{datetime.now()}] Neue Daten empfangen:")
                    for key, value in daten.items():
                        print(f"  {key}: {value}")
                
                warnungen = self.pruefe_schwellwerte(daten)
                if warnungen:
                    if self.gui:
                        self.gui.add_data("warnings", warnungen)
                    else:
                        print("\nSchwellwert-Warnungen:")
                        for warnung in warnungen:
                            print(f"❌ {warnung}")
                            
        except Exception as e:
            print(f"Fehler beim Lesen der Daten: {e}")
            self.daten_node = None

    def parse_daten(self, daten_string):
        werte = daten_string.split("|")
        return {
            "sheet_id": int(werte[0]),
            "section": int(werte[1]),
            "cell": int(werte[2]),
            "period": int(werte[3]),
            "sorting_out_deactivated": bool(int(werte[4])),
            "handling_code": int(werte[5]),
            "recommendation_code": werte[6],
            "intervention_code": werte[7],
            "cathode_counter": int(werte[8]),
            "weight": int(werte[9]),
            "copper_not_released": bool(int(werte[10])),
            "buds_north": int(werte[11]),
            "buds_south": int(werte[12]),
            "stack_number_north": int(werte[13]),
            "stack_number_south": int(werte[14]),
            "stack_quality_north": int(werte[15]),
            "stack_quality_south": int(werte[16]),
            "limit_bud_size": int(werte[17]),
            "bud_size_ne": int(werte[18]),
            "bud_size_nw": int(werte[19]),
            "bud_size_sw": int(werte[20]),
            "bud_size_se": int(werte[21]),
            "deflection": int(werte[22]),
            "limit_deflection": int(werte[23]),
            "suggestion_ecu": int(werte[24])
        }

    def pruefe_schwellwerte(self, daten):
        warnungen = []
        for key, value in daten.items():
            if key in self.schwellwerte:
                schwelle = self.schwellwerte[key]
                if isinstance(value, (int, float)):  # Nur numerische Werte prüfen
                    if value < schwelle["min"]:
                        warnungen.append(
                            f"WARNUNG: {schwelle['beschreibung']} ({key}) ist zu niedrig: "
                            f"{value} < {schwelle['min']}"
                        )
                    elif value > schwelle["max"]:
                        warnungen.append(
                            f"WARNUNG: {schwelle['beschreibung']} ({key}) ist zu hoch: "
                            f"{value} > {schwelle['max']}"
                        )
        return warnungen

async def main():
    client = KathodenmaschinenClient()
    await client.connect()
    print("ECU-Client gestartet...")
    await client.update()

if __name__ == "__main__":
    asyncio.run(main()) 