from libs.dialog import SpeechCloudWS, Dialog
from datetime import datetime as dt
import datetime
import random
import asyncio
import logging
from train_creator import create_trains, find_train
from StateRepresentation import State, Value, Slot, Station, TraintypeEnum, TimeValue

class Dialog(Dialog):

    async def main(self):
        
        self.trains = create_trains()
        self.state = State()
        self.state.new_slots(to_station=Station, from_station=Station, time=TimeValue, train_type=TraintypeEnum)
        self.state.expect(self.state.complete_empty, self.state.to_station, self.state.from_station, self.state.time, self.state.train_type)
        
        await self.welcome()

        await self.slu()

        await self.synthesize_and_wait(text="Konec dialogu. Nashledanou.")

    async def welcome(self):
        
        await self.synthesize_and_wait("Dobrý den. Vyhledám pro vás vlakové spojení.")

    async def slu(self):
        now = dt.now()
        current_time = now.strftime("%H:%M:%S")
        self.state.push(time=current_time)

        grammars = self.grammar_from_dict("command", 
                {"end": {"konec","skonči","ukončit"}, "continue": {"pokračuj", "pokračovat"},
                 "help": "nápověda"}) 

        
        from_stations = {"Praha": {"z Prahy, z prahy"}, "Brno": {"z Brna", "z brna"}, "České Budějovice": {"z Čekých Budějovic", "z čekých budějovic", "z Budějovic", "z budějovic"}, "Hradec Králové": {"z Hradce Králové", "z hradce králové", "z Hradce", "z hradce"},
        "Jihlava": {"z Jihlavy", "z jihlavy"}, "Karlovy Vary": {"z Karlových Varů", "z karlových varů", "z Varů", "z varů"}, "Liberec": {"z Liberce", "z liberce"}, "Olomouc": {"z Olomouce", "z olomouce"}, "Ostrava": {"z Ostravy", "z ostravy"}, "Pardubice": {"z Pardubic", "z pardubic"},
        "Plzeň": {"z Plzně", "z plzně"}, "Ústí nad Labem": {"z Ústí nad Labem", "z ústí nad labem", "z ústí", "z Ústí"}, "Zlín": {"ze Zlína", "z Zlína", "ze zlína", "z zlína"}}
        
        to_stations = {"Praha": {"do Prahy, do prahy"}, "Brno": {"do Brna", "do brna"}, "České Budějovice": {"do Čekých Budějovic", "do čekých budějovic", "do Budějovic", "do budějovic"}, "Hradec Králové": {"do Hradce Králové", "do hradce králové", "do Hradce", "do hradce"},
        "Jihlava": {"do Jihlavy", "do jihlavy"}, "Karlovy Vary": {"do Karlových Varů", "do karlových varů", "do Varů", "do varů"}, "Liberec": {"do Liberce", "do liberce"}, "Olomouc": {"do Olomouce", "do olomouce"}, "Ostrava": {"do Ostravy", "do ostravy"}, "Pardubice": {"do Pardubic", "do pardubic"},
        "Plzeň": {"do Plzně", "do plzně"}, "Ústí nad Labem": {"do Ústí nad Labem", "do ústí nad labem", "do ústí", "do Ústí"}, "Zlín": {"do Zlína", "do Zlína", "do zlína", "do zlína"}}
        
        train_types = {"O": "osobák", "R": "rychlík", "ANY": "vlak"}
        
        grammars += self.grammar_from_dict("from_station",{"Praha": {"z Prahy, z prahy"}, "Brno": {"z Brna", "z brna"}, "České Budějovice": {"z Čekých Budějovic", "z čekých budějovic", "z Budějovic", "z budějovic"}, "Hradec Králové": {"z Hradce Králové", "z hradce králové", "z Hradce", "z hradce"},
        "Jihlava": {"z Jihlavy", "z jihlavy"}, "Karlovy Vary": {"z Karlových Varů", "z karlových varů", "z Varů", "z varů"}, "Liberec": {"z Liberce", "z liberce"}, "Olomouc": {"z Olomouce", "z olomouce"}, "Ostrava": {"z Ostravy", "z ostravy"}, "Pardubice": {"z Pardubic", "z pardubic"},
        "Plzeň": {"z Plzně", "z plzně"}, "Ústí nad Labem": {"z Ústí nad Labem", "z ústí nad labem", "z ústí", "z Ústí"}, "Zlín": {"ze Zlína", "z Zlína", "ze zlína", "z zlína"}})
        
        grammars += self.grammar_from_dict("to_station", {"Praha": {"do Prahy, do prahy"}, "Brno": {"do Brna", "do brna"}, "České Budějovice": {"do Čekých Budějovic", "do čekých budějovic", "do Budějovic", "do budějovic"}, "Hradec Králové": {"do Hradce Králové", "do hradce králové", "do Hradce", "do hradce"},
        "Jihlava": {"do Jihlavy", "do jihlavy"}, "Karlovy Vary": {"do Karlových Varů", "do karlových varů", "do Varů", "do varů"}, "Liberec": {"do Liberce", "do liberce"}, "Olomouc": {"do Olomouce", "do olomouce"}, "Ostrava": {"do Ostravy", "do ostravy"}, "Pardubice": {"do Pardubic", "do pardubic"},
        "Plzeň": {"do Plzně", "do plzně"}, "Ústí nad Labem": {"do Ústí nad Labem", "do ústí nad labem", "do ústí", "do Ústí"}, "Zlín": {"do Zlína", "do Zlína", "do zlína", "do zlína"}})
        
        grammars += self.grammar_from_dict("train_type", {"R":{"rychlík", "rychlíkem"}, "O":{"osobák", "osobákem", "osobní vlak", "osobním vlakem"}, "ANY": {"jakýmkoliv vlakem"}})

        grammars += self.grammar_from_dict("confirm", {"confirm":{"potvrzuji", "potvrzuju", "potvrzuje", "ano"}})
        grammars += self.grammar_from_dict("not_confirm", {"not_confirm":{"nepotvrzuji", "nepotvrzuju", "nepotvrzuje", "ne"}})
        grammars += self.grammar_from_dict("show_state_repres", {"show_state_repres":{"ukaž mi karty", "ukaž mi obě karty"}})
        grammars += self.grammar_from_dict("delete_state_repres", {"delete_state_repres":{"smaž karty", "smaž obě karty"}})
        grammars += self.grammar_from_dict("choose", {"choose":{"vybírám"}})
        grammars += self.grammar_from_dict("change", {"change":{"změnit", "změnil"}})

        await self.define_slu_grammars(grammars)
        end = False
        while not end:
            
            result_1 = await self.synthesize_and_wait_for_slu_result(text="Řeknětě prosím odkuď a kam chcete jet, případně jakým typem vlaku.", timeout=4.)
            
            if result_1.command.first:
                command = result_1.command.first

                if command == "end":
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz konec. Ukončuji dialog.")
                    end = True
                    self.state.push()
                    self.state.expect(self.state.emptying_slots, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                    self.state.push(self.state.empty_slots_fcn, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                    break
                elif command == "help":
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz pomoct. Vyhledám pro vás vlakové spojení. Řeknětě z jakého města a do jakého města chcete jet, případnětě i řeknětě, jakým typem vlaku chcete jet.")
                    continue
                elif command == "continue":
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz pokračovat. Pokračuji v dialogu.")
                    continue

            if (result_1.from_station.first and result_1.to_station.first):
                # bylo receno z a kam 
                from_station = result_1.from_station.first
                to_station = result_1.to_station.first

                self.state.push(from_station=from_station, to_station=to_station)
                if result_1.train_type.first:
                    # kontrola, jestli byl recen typ vlaku, pokud ne -> je to uzivateli jedno
                    train_type = result_1.train_type.first
                else:
                    train_type = "ANY"
                self.state.push(train_type=train_type)
                while True:
                    if train_type == "ANY":       
                        result = await self.synthesize_and_wait_for_slu_result(text=f"Chcete jet z města {self.state.from_station.first_value} do města {self.state.to_station.first_value}. Chcete potvrdit tyto údaje?", timeout=4.)
                    else:
                        result = await self.synthesize_and_wait_for_slu_result(text=f"Chcete jet z města {self.state.from_station.first_value} do města {self.state.to_station.first_value} vlakem typu {train_types[self.state.train_type.first_value]}. Chcete potvrdit tyto údaje?", timeout=4.)
                    if result.confirm.first:
                        self.state.expect(self.state.confirm_unconfirmed, self.state.from_station, self.state.to_station, self.state.train_type, self.state.time)
                        self.state.push(self.state.from_station, self.state.to_station, self.state.train_type, self.state.time)
                        # byly potvrzeno
                        self.state.expect(self.state.present, self.state.from_station, self.state.to_station, self.state.train_type, self.state.time)
                        found_train = find_train(self.state.from_station.first_value, self.state.to_station.first_value, self.state.time.first_value, self.state.train_type.first_value, self.trains)
                        if found_train:
                            await self.synthesize_and_wait(text=f"Z města {self.state.from_station.first_value} do města {self.state.to_station.first_value} jede {train_types[self.state.train_type.first_value]} v {found_train[0]}:00.")
                        else:
                            await self.synthesize_and_wait(text=f"Z města {self.state.from_station.first_value} do města {self.state.to_station.first_value} už dnes {train_types[self.state.train_type.first_value]} nejede.")
                        self.state.push()
                        self.state.expect(self.state.emptying_slots, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        self.state.push(self.state.empty_slots_fcn, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        
                        break
                    if result.not_confirm.first:
                        # nepotvrzeny
                        await self.synthesize_and_wait(text=f"Nechcete potvrdit odjezd z města {self.state.from_station.first_value} do města {self.state.to_station.first_value}. Údaje budou smazány.")
                        self.state.expect(self.state.emptying_slots, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        self.state.push(self.state.empty_slots_fcn, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        break
                    if result.from_station.first and not result.to_station.first:
                        # znova recena odkud
                        from_station = result.from_station.first
                        self.state.push(from_station=from_station)
                        self.state.expect(self.state.disambig, self.state.from_station)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro výchozí stanici jste již řekl {self.state.from_station.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.from_station.first):
                                # vyresena inkonzistence
                                from_station = result.from_station.first
                                self.state.push(to_station=from_station)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má výchozí stanice mít.")
                                continue

                    if not result.from_station.first and result.to_station.first:
                        # znova receno kam
                        to_station = result.to_station.first
                        self.state.push(to_station=to_station)
                        self.state.expect(self.state.disambig, self.state.to_station)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro cílovou stanici jste již řekl {self.state.to_station.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.to_station.first):
                                # vyresena inkonzistence
                                to_station = result.to_station.first
                                self.state.push(to_station=to_station)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má cílová stanice stanice mít.")
                                continue

                    if result.from_station.first and result.to_station.first:
                        # znova z a kam
                        to_station = result.to_station.first
                        from_station = result.from_station.first
                        self.state.push(from_station=from_station, to_station=to_station)
                        self.state.expect(self.state.disambig, self.state.from_station, self.state.to_station)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro výchozí stanici jste již řekl {self.state.from_station.all_values} a pro cílovou stanici jste již řekl {self.state.to_station.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.from_station.first and result.to_station.first):
                                # vyresena inkonzistence
                                to_station = result.to_station.first
                                from_station = result.from_station.first
                                self.state.push(from_station=from_station, to_station=to_station)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu mají stanice mít.")
                                continue
                                                    
                    if result.command.first:
                        # rozpoznan prikaz
                        command = result.command.first

                        if command == "end":
                            # ukonceni dialogu
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz konec. Ukončuji dialog.")
                            end = True
                            self.state.push()
                            self.state.expect(self.state.emptying_slots, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                            self.state.push(self.state.empty_slots_fcn, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                            break
                        elif command == "help":
                            # command help
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz pomoct. Musíte potvrdit stanice a já vám řeknu, kdy vám pojede vlak.")
                            continue
                        elif command == "continue":
                            # command continue
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz pokračovat. Pokračuji v dialogu.")
                            continue
            
            if result_1.from_station.first and not result_1.to_station.first:
                # receno pouze z
                from_station = result_1.from_station.first
                self.state.push(from_station=from_station)
                if result_1.train_type.first:
                    # kontrola, jestli byl recen typ vlaku, pokud ne -> je to uzivateli jedno

                    train_type = result_1.train_type.first
                else:
                    train_type = "ANY"
                self.state.push(train_type=train_type)

                while True:
                    if train_type == "ANY":       
                        result = await self.synthesize_and_wait_for_slu_result(text=f"Chcete jet z města {self.state.from_station.first_value}. Do jakého města chcete jet?", timeout=4.)
                    else:
                        result = await self.synthesize_and_wait_for_slu_result(text=f"Chcete jet z města {self.state.from_station.first_value} vlakem typu {train_types[self.state.train_type.first_value]}. Do jakého města chcete jet?", timeout=4.)
                    if result.from_station.first:
                        # znovu receno z
                        from_station = result.from_station.first
                        self.state.push(from_station=from_station)
                        self.state.expect(self.state.disambig, self.state.from_station)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro výchozí stanici jste již řekl {self.state.from_station.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if result.from_station.first:
                                # vyresena inkonzistence
                                from_station = result.from_station.first
                                self.state.push(from_station=from_station)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnota má výchozí stanicem mít.")
                                continue

                    if result.to_station.first:
                        # receno kam
                        to_station = result.to_station.first
                        self.state.push(to_station=to_station)
                        break
                while True:       
                    result = await self.synthesize_and_wait_for_slu_result(text=f"Chcete jet z města {self.state.from_station.first_value} do města {self.state.to_station.first_value} vlakem typu {train_types[self.state.train_type.first_value]}. Chcete potvrdit tyto údaje?", timeout=4.)
                    if result.confirm.first:
                        self.state.expect(self.state.confirm_unconfirmed, self.state.from_station, self.state.to_station, self.state.train_type, self.state.time)
                        self.state.push(self.state.from_station, self.state.to_station, self.state.train_type, self.state.time)
                        # byly potvrzeno
                        self.state.expect(self.state.present, self.state.from_station, self.state.to_station, self.state.train_type, self.state.time)
                        found_train = find_train(self.state.from_station.first_value, self.state.to_station.first_value, self.state.time.first_value, self.state.train_type.first_value, self.trains)
                        if found_train:
                            await self.synthesize_and_wait(text=f"Z města {self.state.from_station.first_value} do města {self.state.to_station.first_value} jede vlak type {train_types[self.state.train_type.first_value]} v {found_train[0]}:00.")
                        else:
                            await self.synthesize_and_wait(text=f"Z města {self.state.from_station.first_value} do města {self.state.to_station.first_value} už dnes {train_types[self.state.train_type.first_value]} nejede.")
                        self.state.push()
                        self.state.expect(self.state.emptying_slots, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        self.state.push(self.state.empty_slots_fcn, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        
                        break
                    if result.not_confirm.first:
                        # nepotvrzeny
                        await self.synthesize_and_wait(text=f"Nechcete potvrdit odjezd z města {self.state.from_station.first_value} do města {self.state.to_station.first_value}. Údaje budou smazány.")
                        self.state.push()
                        self.state.expect(self.state.emptying_slots, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        self.state.push(self.state.empty_slots_fcn, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        break
                    if result.from_station.first and not result.to_station.first:
                        # znova receno odkud
                        from_station = result.from_station.first
                        self.state.push(from_station=from_station)
                        self.state.expect(self.state.disambig, self.state.from_station)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro cílovou stanici jste již řekl {self.state.to_station.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.to_station.first):
                                # vyresena inkonzistence
                                to_station = result.to_station.first
                                self.state.push(to_station=to_station)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má cílová stanice mít.")
                                continue

                    if not result.from_station.first and result.to_station.first:
                        # znova receno kam
                        to_station = result.to_station.first
                        self.state.push(to_station=to_station)
                        self.state.expect(self.state.disambig, self.state.to_station)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro cílovou stanici jste již řekl {self.state.to_station.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.to_station.first):
                                # vyresena inkonzistence
                                to_station = result.to_station.first
                                self.state.push(to_station=to_station)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má cílová stanice mít.")
                                continue

                    if result.from_station.first and result.to_station.first:
                        # znova receno z a kam
                        to_station = result.to_station.first
                        from_station = result.from_station.first
                        self.state.push(from_station=from_station, to_station=to_station)
                        self.state.expect(self.state.disambig, self.state.from_station, self.state.to_station)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro výchozí stanici jste již řekl {self.state.from_station.all_values} a pro cílovou stanici jste již řekl {self.state.to_station.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.from_station.first and result.to_station.first):
                                # vyresena inkonzistence
                                to_station = result.to_station.first
                                from_station = result.from_station.first
                                self.state.push(from_station=from_station, to_station=to_station)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu mají stanice mít.")
                                continue

                    if result.command.first:
                        # rozpoznan prikaz
                        command = result.command.first

                        if command == "end":
                            # ukonceni dialogu
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz konec. Ukončuji dialog.")
                            end = True
                            self.state.push()
                            self.state.expect(self.state.emptying_slots, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                            self.state.push(self.state.empty_slots_fcn, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                            break
                        elif command == "help":
                            # command help
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz pomoct. Musíte potvrdit stanice a já vám řeknu, kdy vám pojede vlak.")
                            continue
                        elif command == "continue":
                            # command continue
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz pokračovat. Pokračuji v dialogu.")
                            continue
                                
            if not result_1.from_station.first and result_1.to_station.first:
                # receno pouze kam
                to_station = result_1.to_station.first
                self.state.push(to_station=to_station)
                if result_1.train_type.first:
                    # kontrola, jestli byl recen typ vlaku, pokud ne -> je to uzivateli jedno
                    train_type = result_1.train_type.first
                else:
                    train_type = "ANY"
                self.state.push(train_type=train_type)

                while True:
                    if train_type == "ANY":       
                        result = await self.synthesize_and_wait_for_slu_result(text=f"Chcete jet do města {self.state.to_station.first_value}. Z jakého města chcete jet?", timeout=4.)
                    else:
                        result = await self.synthesize_and_wait_for_slu_result(text=f"Chcete jet do města {self.state.to_station.first_value} vlakem typu {train_types[self.state.train_type.first_value]}. Z jakého města chcete jet?", timeout=4.)
                    if result.to_station.first:
                        # znovu receno kam
                        to_station = result.to_station.first
                        self.state.push(to_station=to_station)
                        self.state.expect(self.state.disambig, self.state.to_station)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro výchozí stanici jste již řekl {self.state.to_station.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if result.to_station.first:
                                # vyresena inkonzistence
                                to_station = result.to_station.first
                                self.state.push(to_station=to_station)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má vychozí stanice mít.")
                                continue
                    if result.from_station.first:
                        # receno z
                        from_station = result.from_station.first
                        self.state.push(from_station=from_station)
                        break
                while True:       
                    result = await self.synthesize_and_wait_for_slu_result(text=f"Chcete jet z města {self.state.from_station.first_value} do města {self.state.to_station.first_value} vlakem typu {train_types[self.state.train_type.first_value]}. Chcete potvrdit tyto údaje?", timeout=4.)
                    if result.confirm.first:
                        self.state.expect(self.state.confirm_unconfirmed, self.state.from_station, self.state.to_station, self.state.train_type, self.state.time)
                        self.state.push(self.state.from_station, self.state.to_station, self.state.train_type, self.state.time)
                        # byly potvrzeny
                        self.state.expect(self.state.present, self.state.from_station, self.state.to_station, self.state.train_type, self.state.time)
                        found_train = find_train(self.state.from_station.first_value, self.state.to_station.first_value, self.state.time.first_value, self.state.train_type.first_value, self.trains)
                        if found_train:
                            await self.synthesize_and_wait(text=f"Z města {self.state.from_station.first_value} do města {self.state.to_station.first_value} jede vlak type {self.state.train_type.first_value} v {found_train[0]}:00.")
                        else:
                            await self.synthesize_and_wait(text=f"Z města {self.state.from_station.first_value} do města {self.state.to_station.first_value} dnes už {train_types[self.state.train_type.first_value]} nejede.")
                        self.state.push()
                        self.state.expect(self.state.emptying_slots, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        self.state.push(self.state.empty_slots_fcn, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        
                        break
                    if result.not_confirm.first:
                        # nepotvrzeny
                        await self.synthesize_and_wait(text=f"Nechcete potvrdit odjezd z města {self.state.from_station.first_value} do města {self.state.to_station.first_value} vlakem typu {train_types[self.state.train_type.first_value]}. Údaje budou smazány.")
                        self.state.push()
                        self.state.expect(self.state.emptying_slots, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        self.state.push(self.state.empty_slots_fcn, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                        break
                    if result.from_station.first and not result.to_station.first:
                        # znova receno odkud
                        from_station = result.from_station.first
                        self.state.push(from_station=from_station)
                        self.state.expect(self.state.disambig, self.state.from_station)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro cílovou stanici jste již řekl {self.state.to_station.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.to_station.first):
                                # vyresena inkonzistence
                                to_station = result.to_station.first
                                self.state.push(to_station=to_station)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má cílová stanice mít.")
                                continue

                    if not result.from_station.first and result.to_station.first:
                        # znova receno kam
                        to_station = result.to_station.first
                        self.state.push(to_station=to_station)
                        self.state.expect(self.state.disambig, self.state.to_station)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro cílovou stanici jste již řekl {self.state.to_station.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.to_station.first):
                                # vyresena inkonzistence
                                to_station = result.to_station.first
                                self.state.push(to_station=to_station)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má cílová stanice mít.")
                                continue

                    if result.from_station.first and result.to_station.first:
                        # znova receno z a kam
                        to_station = result.to_station.first
                        from_station = result.from_station.first
                        self.state.push(from_station=from_station, to_station=to_station)
                        self.state.expect(self.state.disambig, self.state.from_station, self.state.to_station)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro výchozí stanici jste již řekl {self.state.from_station.all_values} a pro cílovou stanici jste již řekl {self.state.to_station.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.from_station.first and result.to_station.first):
                                # vyresena inkonzistence
                                to_station = result.to_station.first
                                from_station = result.from_station.first
                                self.state.push(from_station=from_station, to_station=to_station)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu mají stanice mít.")
                                continue

                    if result.command.first:
                        # rozpoznan prikaz
                        command = result.command.first

                        if command == "end":
                            # ukonceni dialogu
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz konec. Ukončuji dialog.")
                            end = True
                            self.state.push()
                            self.state.expect(self.state.emptying_slots, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                            self.state.push(self.state.empty_slots_fcn, self.state.from_station, self.state.to_station, self.state.time, self.state.train_type)
                            break
                        elif command == "help":
                            # command help
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz pomoct. Musíte potvrdit stanice a já vám řeknu, kdy vám pojede vlak.")
                            continue
                        elif command == "continue":
                            # command continue
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz pokračovat. Pokračuji v dialogu.")
                            continue

            if not result_1.from_station.first and not result_1.to_station.first:
                # nebylo rozpoznano nic
                await self.synthesize_and_wait(text=f"Neřekl jste odkuď a kam chcete jet.")
                continue
        print(self.state.History)            
           


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-10s %(message)s', level=logging.DEBUG)

    SpeechCloudWS.run(Dialog, address="0.0.0.0", port=8888)


    