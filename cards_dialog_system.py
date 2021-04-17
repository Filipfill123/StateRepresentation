from libs.dialog import SpeechCloudWS, Dialog
import datetime as dt
import random
import asyncio
import logging
from StateRepresentation import State, Value, CardsCZ, Slot

class Dialog(Dialog):

    async def main(self):
        self.state = State()
        self.state.new_slots(first_card=Cards, second_card=Cards)
        self.state.expect(self.state.complete_empty, self.state.first_card, self.state.second_card)

        await self.welcome()

        await self.slu()

        await self.synthesize_and_wait(text="Konec dialogu. Nashledanou.")

    async def welcome(self):
        # pro "zrychlení" samotné otázky ohledně kornaviru
        await self.synthesize_and_wait("Dobrý den. Můžete mi předložit dvě karty a já vám řeknu, jestli dohromady tvoří pár, nebo ne.")

    async def slu(self):
        
        grammars = self.grammar_from_dict("command", 
                {"end": {"konec","skonči","ukončit"}, "continue": {"pokračuj", "pokračovat", "ano"},
                 "help": "nápověda"}) 

        
        grammars += self.grammar_from_dict("karta", {"eso": {"eso"}, "král": {"král"}, "královna": {"dáma", "královna"}, "kluk": {"kluk", "princ"}, "desítka":{"desítka"},"devítka":{"devítka"}, "osmička":{"osmička"}, "sedmička":{"sedmička"}, "šestka":{"šestka"}, "pětka":{"pětka"}, "čtyřka":{"čtyřka", "čtyrka"}, "trojka":{"trojka"}, "dvojka":{"dvojka"}, "test": {"test_karta"}})
        grammars += self.grammar_from_dict("first_card", {"first_card":{"první karta", "první kartu"}})
        grammars += self.grammar_from_dict("second_card", {"second_card":{"druhá karta", "druhou kartu"}})
        grammars += self.grammar_from_dict("confirm", {"confirm":{"potvrzuji", "potvrzuju", "potvrzuje", "ano"}})
        grammars += self.grammar_from_dict("not_confirm", {"not_confirm":{"nepotvrzuji", "nepotvrzuju", "nepotvrzuje", "ne"}})
        grammars += self.grammar_from_dict("show_state_repres", {"show_state_repres":{"ukaž mi karty", "ukaž mi obě karty"}})
        grammars += self.grammar_from_dict("delete_state_repres", {"delete_state_repres":{"smaž karty", "smaž obě karty"}})
        grammars += self.grammar_from_dict("choose", {"choose":{"vybírám"}})

        await self.define_slu_grammars(grammars)
        end = False
        while not end:
            # první dotaz
            
            result_1 = await self.synthesize_and_wait_for_slu_result(text="Jaké karty vás zajímají?", timeout=4.)
            
            if result_1.command.first:
                command = result_1.command.first

                if command == "end":
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz konec. Ukončuji dialog.")
                    end = True
                    break
                elif command == "help":
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz pomoct. Můžete mi předložit dvě karty a já vám řeknu, jestli dohromady tvoří pár nebo ne.")
                    continue
                elif command == "continue":
                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz pokračovat. Pokračuji v dialogu.")
                    continue

            if (result_1.first_card.first and result_1.second_card.first and result_1.karta.first and result_1.karta.last):
                # byly receny obe karty
                first = result_1.karta.first
                second = result_1.karta.last
                self.state.push(first_card=first, second_card=second)
                
                while True:       
                    result = await self.synthesize_and_wait_for_slu_result(text=f"První karta je {self.state.first_card.first_value} a druhá karta je {self.state.second_card.first_value}. Chcete potvrdit tyto karty?", timeout=4.)
                    if result.confirm.first:
                        self.state.expect(self.state.confirm_unconfirmed, self.state.first_card, self.state.second_card)
                        self.state.push(self.state.first_card, self.state.second_card)
                        # byly obe potvrzeny
                        if self.state.first_card.first_value == self.state.second_card.first_value:
                            # par
                            self.state.expect(self.state.present, self.state.first_card, self.state.second_card)
                            await self.synthesize_and_wait(text=f"{self.state.first_card.first_value} a {self.state.second_card.first_value} je pár.")
                            self.state.push()
                            self.state.expect(self.state.emptying_slots, self.state.first_card, self.state.second_card)
                            self.state.push(self.state.empty_slots_fcn, self.state.first_card, self.state.second_card)
                            break
                        else:
                            # nepar
                            self.state.expect(self.state.present, self.state.first_card, self.state.second_card)
                            await self.synthesize_and_wait(text=f"{self.state.first_card.first_value} a {self.state.second_card.first_value} není pár.")
                            self.state.push()
                            self.state.delete_state_representation()
                            break
                    if result.not_confirm.first:
                        # nepotvrzeny
                        await self.synthesize_and_wait(text=f"Nechcete potvrdit první kartu {self.state.first_card.first_value} a druhou kartu {self.state.second_card.first_value}. Budou smazány.")
                        self.state.push()
                        self.state.expect(self.state.emptying_slots, self.state.first_card, self.state.second_card)
                        self.state.push(self.state.empty_slots_fcn, self.state.first_card, self.state.second_card)
                        break
                    if result.first_card.first and not result.second_card.first:
                        # znova recena prvni karta
                        first = result.karta.first
                        self.state.push(first_card=first)
                        self.state.expect(self.state.disambig, self.state.first_card)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro první kartu jste již řekl {self.state.first_card.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.first_card.first and result.karta.first):
                                # vyresena inkonzistence
                                first = result.karta.first
                                self.state.push(first_card=first)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má mít první karta.")
                                continue
                        
                    if not result.first_card.first and result.second_card.first:
                        # znova recena druha karta
                        second = result.karta.first
                        self.state.push(second_card=second)
                        self.state.expect(self.state.disambig, self.state.second_card)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro druhou kartu jste již řekl {self.state.second_card.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.second_card.first and result.karta.last):
                                # vyresena inkonzistence
                                second = result.karta.first
                                self.state.push(second_card=second)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má mít druhá karta.")
                                continue
                        
                    if result.first_card.first and result.second_card.first:
                        # znova receny obe karty
                        first = result.karta.first
                        second = result.karta.last
                        self.state.push(first_card= first, second_card=second)
                        self.state.expect(self.state.disambig, self.state.first_card, self.state.second_card)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro první kartu jste již řekl {self.state.first_card.all_values} a pro druhou kartu {self.state.second_card.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if (result.first_card.first and result.karta.first and result.second_card.first and result.karta.last):
                                # vyresena inkonzistence
                                first = result.karta.first
                                second = result.karta.last
                                self.state.push(first_card=first, second_card=second)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu mají mít obě karty.")
                                continue

                    if result.command.first:
                        # rozpoznan prikaz
                        command = result.command.first

                        if command == "end":
                            # ukonceni dialogu
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz konec. Ukončuji dialog.")
                            end = True
                            self.state.push()
                            break
                        elif command == "help":
                            # command help
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz pomoct. Musíte potvrdit jednu nebo obě karty a já vám řeknu, jestli dohromady tvoří pár a nebo ne.")
                            continue
                        elif command == "continue":
                            # command continue
                            await self.synthesize_and_wait(text=f"Rozpoznán příkaz pokračovat. Pokračuji v dialogu.")
                            continue
            
            if result_1.first_card.first and not result_1.second_card.first:
                # recena pouze prvni karta
                first = result_1.karta.first
                self.state.push(first_card=first)
                while True:
                    result = await self.synthesize_and_wait_for_slu_result(text=f"První karta je {self.state.first_card.first_value}. Jaká je druhá karta?", timeout=4.)
                    if result.first_card.first and result.karta.first:
                        # znovu recena prvni karta
                        first = result.karta.first
                        self.state.push(first_card=first)
                        self.state.expect(self.state.disambig, self.state.first_card)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro první kartu jste již řekl {self.state.first_card.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if result.karta.first:
                                # vyresena inkonzistence
                                first = result.karta.first
                                self.state.push(first_card=first)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má mít první karta.")
                                continue
                    if (result.second_card.first and result.karta.first):
                        # recena hodnota pro druhou kartu
                        second = result.karta.first
                        self.state.push(second_card=second)
                        break
                while True:       
                            result = await self.synthesize_and_wait_for_slu_result(text=f"První karta je {self.state.first_card.first_value} a druhá karta je {self.state.second_card.first_value}. Chcete potvrdit tyto karty?", timeout=4.)
                            if result.confirm.first:
                                self.state.expect(self.state.confirm_unconfirmed, self.state.first_card, self.state.second_card)
                                self.state.push(self.state.first_card, self.state.second_card)
                                # byly obe potvrzeny
                                if self.state.first_card.first_value == self.state.second_card.first_value:
                                    # par
                                    self.state.expect(self.state.present, self.state.first_card, self.state.second_card)
                                    await self.synthesize_and_wait(text=f"{self.state.first_card.first_value} a {self.state.second_card.first_value} je pár.")
                                    self.state.push()
                                    self.state.expect(self.state.emptying_slots, self.state.first_card, self.state.second_card)
                                    self.state.push(self.state.empty_slots_fcn, self.state.first_card, self.state.second_card)
                                    break
                                else:
                                    # nepar
                                    self.state.expect(self.state.present, self.state.first_card, self.state.second_card)
                                    await self.synthesize_and_wait(text=f"{self.state.first_card.first_value} a {self.state.second_card.first_value} není pár.")
                                    self.state.push()
                                    self.state.expect(self.state.emptying_slots, self.state.first_card, self.state.second_card)
                                    self.state.push(self.state.empty_slots_fcn, self.state.first_card, self.state.second_card)
                                    break
                            if result.not_confirm.first:
                                # nepotvrzeny
                                await self.synthesize_and_wait(text=f"Nechcete potvrdit první kartu {self.state.first_card.first_value} a druhou kartu {self.state.second_card.first_value}. Budou smazány.")
                                self.state.delete_state_representation()
                                self.state.push()
                                break
                            if result.first_card.first and not result.second_card.first:
                                # znova recena prvni karta
                                first = result.karta.first
                                self.state.push(first_card=first)
                                self.state.expect(self.state.disambig, self.state.first_card)
                                while True:
                                    result = await self.synthesize_and_wait_for_slu_result(text=f"Pro první kartu jste již řekl {self.state.first_card.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                                    if (result.first_card.first and result.karta.first):
                                        # vyresena inkonzistence
                                        first = result.karta.first
                                        self.state.push(first_card=first)
                                        break
                                    else:
                                        # nebylo nic rozpoznano
                                        await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má mít první karta.")
                                        continue

                            if not result.first_card.first and result.second_card.first:
                                # znova recena druha karta
                                second = result.karta.first
                                self.state.push(second_card=second)
                                self.state.expect(self.state.disambig, self.state.second_card)
                                while True:
                                    result = await self.synthesize_and_wait_for_slu_result(text=f"Pro druhou kartu jste již řekl {self.state.second_card.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                                    if (result.second_card.first and result.karta.first):
                                        # vyresena inkonzistence
                                        second = result.karta.first
                                        self.state.push(second_card=second)
                                        break
                                    else:
                                        # nebylo nic rozpoznano
                                        await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má mít druhá karta.")
                                        continue

                            if result.first_card.first and result.second_card.first:
                                # znova receny obe karty
                                first = result.karta.first
                                second = result.karta.last
                                self.state.push(first_card= first, second_card=second)
                                self.state.expect(self.state.disambig, self.state.first_card, self.state.second_card)
                                while True:
                                    result = await self.synthesize_and_wait_for_slu_result(text=f"Pro první kartu jste již řekl {self.state.first_card.all_values} a pro druhou kartu {self.state.second_card.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                                    if (result.first_card.first and result.karta.first and result.second_card.first and result.karta.last):
                                        # vyresena inkonzistence
                                        first = result.karta.first
                                        second = result.karta.last
                                        self.state.push(first_card=first, second_card=second)
                                        break
                                    else:
                                        # nebylo nic rozpoznano
                                        await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu mají mít obě karty.")
                                        continue

                            if result.command.first:
                                # rozpoznan prikaz
                                command = result.command.first

                                if command == "end":
                                    # ukonceni dialogu
                                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz konec. Ukončuji dialog.")
                                    end = True
                                    self.state.push()
                                    break
                                elif command == "help":
                                    # command help
                                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz pomoct. Musíte potvrdit jednu nebo obě karty a já vám řeknu, jestli dohromady tvoří pár a nebo ne.")
                                    continue
                                elif command == "continue":
                                    # command continue
                                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz pokračovat. Pokračuji v dialogu.")
                                    continue
                                
            if not result_1.first_card.first and result_1.second_card.first:
                # recena pouze druha karta
                second = result_1.karta.first
                self.state.push(second_card=second)

                while True:
                    result = await self.synthesize_and_wait_for_slu_result(text=f"Druhá karta je {self.state.second_card.first_value}. Jaká je první karta?", timeout=4.)
                    if result.second_card.first and result.karta.first:
                        # znovu recena druha karta
                        second = result.karta.first
                        self.state.push(second_card=second)
                        self.state.expect(self.state.disambig, self.state.second_card)
                        while True:
                            result = await self.synthesize_and_wait_for_slu_result(text=f"Pro druhou kartu jste již řekl {self.state.second_card.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                            if result.karta.first:
                                # vyresena inkonzistence
                                second = result.karta.first
                                self.state.push(second_card=second)
                                break
                            else:
                                # nebylo nic rozpoznano
                                await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má mít druhá karta.")
                                continue
                    if (result.first_card.first and result.karta.first):
                        # recena hodnota pro prvni kartu
                        first = result.karta.first
                        self.state.push(first_card=first)
                        break
                while True:       
                            result = await self.synthesize_and_wait_for_slu_result(text=f"První karta je {self.state.first_card.first_value} a druhá karta je {self.state.second_card.first_value}. Chcete potvrdit tyto karty?", timeout=4.)
                            if result.confirm.first:
                                self.state.expect(self.state.confirm_unconfirmed, self.state.first_card, self.state.second_card)
                                self.state.push(self.state.first_card, self.state.second_card)
                                # byly obe potvrzeny
                                if self.state.first_card.first_value == self.state.second_card.first_value:
                                    # par
                                    self.state.expect(self.state.present, self.state.first_card, self.state.second_card)
                                    await self.synthesize_and_wait(text=f"{self.state.first_card.first_value} a {self.state.second_card.first_value} je pár.")
                                    self.state.push()
                                    self.state.expect(self.state.emptying_slots, self.state.first_card, self.state.second_card)
                                    self.state.push(self.state.empty_slots_fcn, self.state.first_card, self.state.second_card)
                                    break
                                else:
                                    # nepar
                                    self.state.expect(self.state.present, self.state.first_card, self.state.second_card)
                                    await self.synthesize_and_wait(text=f"{self.state.first_card.first_value} a {self.state.second_card.first_value} není pár.")
                                    self.state.push()
                                    self.state.expect(self.state.emptying_slots, self.state.first_card, self.state.second_card)
                                    self.state.push(self.state.empty_slots_fcn, self.state.first_card, self.state.second_card)
                                    break
                            if result.not_confirm.first:
                                # nepotvrzeny
                                await self.synthesize_and_wait(text=f"Nechcete potvrdit první kartu {self.state.first_card.first_value} a druhou kartu {self.state.second_card.first_value}. Budou smazány.")
                                self.state.delete_state_representation()
                                self.state.push()
                                break
                            if result.first_card.first and not result.second_card.first:
                                # znova recena prvni karta
                                first = result.karta.first
                                self.state.push(first_card=first)
                                self.state.expect(self.state.disambig, self.state.first_card)
                                while True:
                                    result = await self.synthesize_and_wait_for_slu_result(text=f"Pro první kartu jste již řekl {self.state.first_card.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                                    if (result.first_card.first and result.karta.first):
                                        # vyresena inkonzistence
                                        first = result.karta.first
                                        self.state.push(first_card=first)
                                        break
                                    else:
                                        # nebylo nic rozpoznano
                                        await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má mít první karta.")
                                        continue

                            if not result.first_card.first and result.second_card.first:
                                # znova recena druha karta
                                second = result.karta.first
                                self.state.push(second_card=second)
                                self.state.expect(self.state.disambig, self.state.second_card)
                                while True:
                                    result = await self.synthesize_and_wait_for_slu_result(text=f"Pro druhou kartu jste již řekl {self.state.second_card.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                                    if (result.second_card.first and result.karta.first):
                                        # vyresena inkonzistence
                                        second = result.karta.first
                                        self.state.push(second_card=second)
                                        break
                                    else:
                                        # nebylo nic rozpoznano
                                        await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu má mít druhá karta.")
                                        continue

                            if result.first_card.first and result.second_card.first:
                                # znova receny obe karty
                                first = result.karta.first
                                second = result.karta.last
                                self.state.push(first_card= first, second_card=second)
                                self.state.expect(self.state.disambig, self.state.first_card, self.state.second_card)
                                while True:
                                    result = await self.synthesize_and_wait_for_slu_result(text=f"Pro první kartu jste již řekl {self.state.first_card.all_values} a pro druhou kartu {self.state.second_card.all_values}. Musíte z nich vybrat jednu. Jaká je vaše odpověď?", timeout=4.)
                                    if (result.first_card.first and result.karta.first and result.second_card.first and result.karta.last):
                                        # vyresena inkonzistence
                                        first = result.karta.first
                                        second = result.karta.last
                                        self.state.push(first_card=first, second_card=second)
                                        break
                                    else:
                                        # nebylo nic rozpoznano
                                        await self.synthesize_and_wait(text=f"Neřekl jste, jakou hodnotu mají mít obě karty.")
                                        continue

                            if result.command.first:
                                # rozpoznan prikaz
                                command = result.command.first

                                if command == "end":
                                    # ukonceni dialogu
                                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz konec. Ukončuji dialog.")
                                    end = True
                                    self.state.push()
                                    break
                                elif command == "help":
                                    # command help
                                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz pomoct. Musíte potvrdit jednu nebo obě karty a já vám řeknu, jestli dohromady tvoří pár a nebo ne.")
                                    continue
                                elif command == "continue":
                                    # command continue
                                    await self.synthesize_and_wait(text=f"Rozpoznán příkaz pokračovat. Pokračuji v dialogu.")
                                    continue

            if not result_1.first_card.first and not result_1.second_card.first:
                # nebyly rozpoznany zadne karty
                await self.synthesize_and_wait(text=f"Neřekl jste žádnou kartu.")
                continue
        print(self.state.History)            
           


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-10s %(message)s', level=logging.DEBUG)

    SpeechCloudWS.run(Dialog, address="0.0.0.0", port=8888)


    