# Imports - would vary depending on Value classes a dialog system needs
from dataclasses import dataclass, field
from pyrsistent import pvector, v, pmap, m
from datetime import datetime as dt
import datetime

@dataclass
class Value:
    """
    A dataclass used to represent general values, should be used as a parent

    ...

    Attributes
    ----------
    value : str = None
        inherited from the Value dataclass
    confidence : float = 1.0
        inherited from the Value dataclass
    value_confidence : pmap()
        created after the intialization of the dataclass



    Methods
    -------
    post_init()
        Creates "value_confidence"
    """
    value: str = None
    confidence: float = 1.0
    value_confidence: float = field(init=False)

    def __post_init__(self):
        """
        Creates a "value_confidence" pmap after an initialization of the Value class
        """
        self.value_confidence = m(value=self.value, confidence=self.confidence)

@dataclass
class CardsEN(Value):
    """
    A dataclass used to represent poker cards in english

    ...

    Attributes
    ----------
    value : str = None
        inherited from the Value dataclass
    confidence : float = 1.0
        inherited from the Value dataclass
    value_confidence : pmap()
        created after the intialization of the dataclass
    valid: bool = None
        True if an input value is allowed, False otherwise


    Methods
    -------
    post_init()
        Creates "value_confidence" pmap and sets "valid"
    """
    valid: bool = None

    def __post_init__(self):
        """
        Creates "value_confidence" pmap and sets "valid"
        """
        self.value_confidence = m(value=self.value, confidence=self.confidence)
        cards_en = ('ace','king','queen','jack','ten','nine','eight','seven','six','five','four','three','two')
        if self.value in cards_en: 
            self.valid = True
        else:
            self.valid = False


@dataclass
class CardsCZ(Value):
    """
    A dataclass used to represent poker cards in czech

    ...

    Attributes
    ----------
    value : str = None
        inherited from the Value dataclass
    confidence : float = 1.0
        inherited from the Value dataclass
    value_confidence : pmap()
        created after the intialization of the dataclass
    valid: bool = None
        True if an input value is allowed, False otherwise


    Methods
    -------
    post_init()
        Creates "value_confidence" pmap and sets "valid"
    """
    valid: bool = None

    def __post_init__(self):
        """
        Creates "value_confidence" pmap and sets "valid"
        """
        self.value_confidence = m(value=self.value, confidence=self.confidence)
        # cards_en = ('ace','king','queen','jack','ten','nine','eight','seven','six','five','four','three','two')
        # if self.value in cards_en: 
        #     self.valid = True
        # else:
        #     self.valid = False

        cards_cz = ('eso','král', 'královna', 'kluk', 'desítka', 'devítka', 'osmička', 'sedmička', 'šestka', 'pětka', 'čtyřka', 'trojka', 'dvojka')
        if self.value in cards_cz: 
            self.valid = True
        else:
            self.valid = False
@dataclass
class TimeValue(Value):
    """
    A dataclass used to represent Time

    ...

    Attributes
    ----------
    value : str = None
        inherited from the Value dataclass
    confidence : float = 1.0
        inherited from the Value dataclass
    value_confidence : pmap()
        created after the intialization of the dataclass
    valid: bool = None
        True if an input value is allowed, False otherwise


    Methods
    -------
    post_init()
        Creates "value_confidence" pmap and sets "valid"
    """
    valid: bool = None
    
    def __post_init__(self):
        """
        Creates "value_confidence" pmap and sets "valid"
        """
        self.value_confidence = m(value=self.value, confidence=self.confidence)
        hours, minutes, *seconds = self.value.split(":")
        print(hours, minutes, seconds)
        if seconds:
            seconds = seconds[0]
        else:
            seconds = "00"
        self.valid = True
        print(hours, minutes, seconds)
        try:
            datetime.time(hour=int(hours), minute=int(minutes), second=int(seconds))
        except ValueError:
            self.valid = False

@dataclass
class Station(Value):
    """
    A dataclass used to represent e.g. train or bus stations

    ...

    Attributes
    ----------
    value : str = None
        inherited from the Value dataclass
    confidence : float = 1.0
        inherited from the Value dataclass
    value_confidence : pmap()
        created after the intialization of the dataclass
    valid: bool = None
        True if an input value is allowed, False otherwise


    Methods
    -------
    post_init()
        Creates "value_confidence" pmap and sets "valid"
    """
    valid: bool = None

    def __post_init__(self):
        """
        Creates "value_confidence" pmap and sets "valid"
        """
        self.value_confidence = m(value=self.value, confidence=self.confidence)
        stations = ('Praha','Brno','České Budějovice','Hradec Králové','Jihlava','Karlovy Vary', 'Liberec', 'Olomouc', 'Ostrava', 'Pardubice', 'Plzeň', 'Ústí nad Labem', 'Zlín')
        if self.value in stations: 
            self.valid = True
        else:
            self.valid = False

@dataclass
class TraintypeEnum(Value):
    """
    A dataclass used to represent train types ("O" - osobní, "R" - rychlík, "ANY" - uživatel nespecifikoval)

    ...

    Attributes
    ----------
    value : str = None
        inherited from the Value dataclass
    confidence : float = 1.0
        inherited from the Value dataclass
    value_confidence : pmap()
        created after the intialization of the dataclass
    valid: bool = None
        True if an input value is allowed, False otherwise


    Methods
    -------
    post_init()
        Creates "value_confidence" pmap and sets "valid"
    """
    valid: bool = None

    def __post_init__(self):
        """
        Creates "value_confidence" pmap and sets "valid"
        """
        self.value_confidence = m(value=self.value, confidence=self.confidence)
        train_types = ('R','O','ANY')
        if self.value in train_types: 
            self.valid = True
        else:
            self.valid = False

class Slot:
    """
    A class used to represent a Slot

    ...

    Attributes
    ----------
    __value = None
        list of dataclass Value instances, sorted by confidence in a descending order
    __state = None
        string used to represent a state of the Slot according to a Dialog Manager -> None (empty) / "unconfirmed" / "inconsistent" / "confirmed"


    Methods
    -------
    value()
        __value getter

    value(input_value)
        ___value setter

    all_values()
        getter of all values in the Slot

    value_at_index(idx)
        getter of value at an index idx (idx+1 position)

    state()
        __state getter

    state(state_value)
        __state setter    
    """
    def __init__(self):
        """
        Initialization of the Slot instance

        Attributes
        ----------
        __value = None
        __state = None
        """
        self.__value = None
        self.__state = None
        self.__first_value = None
        self.__last_value = None

    @property
    def first_value(self):
        """Returns __first_value

        """

        return self.__first_value

    @property
    def last_value(self):
        """Returns __last_value

        """

        return self.__last_value

    @property
    def value(self):
        """Returns __value

        """

        return self.__value

    @value.setter
    def value(self, input_value):
        """
        The input_value is added to previous values depending on its confidence (descending order).
        If __value is empty (None), the new input_value is put in a list so that the new values can be easily appended and sorted.
        If there is exactly one value in __value, the state of the slot in "unconfirmed", if there are more it is "inconsistent"
        The input_value is also checked if it is valid

        Parameters
        ----------
        input_value : Value()
            The instance of Value() (or classes inherited from Value()) to be added to the Slot

        """
        if input_value.valid:
            if self.__value is None:
                self.__value = [input_value]
                self.__state = 'unconfirmed'
            else:
                self.__value.append(input_value)
                self.__value.sort(key=lambda x: x.value_confidence['confidence'], reverse=True)
                self.__state = 'inconsistent'
            self.__first_value = self.__value[0].value_confidence['value']
            self.__last_value = self.__value[-1].value_confidence['value']
        else:
            print("Value not valid!")

    @property
    def all_values(self):
        """
        Returns all values of the Slot as a list.
        Returns None if there is no __value.

        """
        all_values = list()
        if self.__value is not None:
            for i in range(len(self.__value)):
                all_values.append(self.__value[i].value_confidence['value'])
        else:
            return self.__value
        return all_values


    def value_at_index(self, index):
        """
        Returns a value at an index (index+1 position).
        Returns None and prints "index not in the slot" if the index is larger then length of the value list of the slot.

        Parameters
        ----------
        index : int
            index
        """
        all_values = self.all_values
        try:
            value_at_index = all_values[index]
            return value_at_index
        except IndexError:
            print(f"Index {index} is larger then the length of the value list of the slot")
            return None 

    @property
    def state(self):
        """
        Returns string __state
        """
        return self.__state

    @state.setter
    def state(self, state_value):
        """
        Sets string __state

        Parameters
        ----------
        state_value : str
            state of the Slot
        """
        self.__state = state_value

    
class State:
    """
    A class used to represent a State

    ...

    Attributes
    ----------
    expectations = pvector
        immutable list expectations from the last Turn of the Dialog, for solving callbacks and storing the history of the dialog
    slot_names = pvector
        immutable list of slots being added by the new_slots() method
    History = pvector
        immutable list for storing the history of the dialog
    value_classes = pmap
        immutable dictionary used for the correct usage of instances of the dataclass Value


    Methods
    -------
    push(*args, **kwargs)
        handles callbacks and expectations, adds new values if there any, confirms slots if there any
    extend(**kwargs)
        function used for adding ("extending") values to a slot
    assign(**kwargs)
        function used for assigning values to a slot - used if there inconsistencies in a slot
    confirm_slots(*args)
        function used for confirming slots
    empty_slots_fcn(*args)
        function used for emptying slots
    expect(*args)
        fills expectations with callbacks and considered slots
    complete_empty(**kwargs)
        callback function - for completing/filling empty slots
    confirm_unconfirmed(**kwargs)
        callback function - for confirming unconfirmed slots
    disambig(**kwargs)
        callback function - for solving inconsistencies
    present(**kwargs)
        callback function - for presenting slots and their values (usually used at the end of the dialog)
    emptying_slots(**kwargs)
        callback function - for emptying slots
    empty_slots()
        returns empty slots (slots with __state = None) as dict slot_name:value-> {'slot_1': <instance of Value()>, 'slot_2': <instance of Value()>,...}
    confirmed_slots()
        returns confirmed slots slots (slots with __state = "confirmed") as dict slot_name:value-> {'slot_1': <instance of Value()>, 'slot_2': <instance of Value()>,...}
    unconfirmed_slots()
        returns unconfirmed slots slots (slots with __state = "unconfirmed") as dict slot_name:value-> {'slot_1': <instance of Value()>, 'slot_2': <instance of Value()>,...}
    inconsistent_slots()
        returns inconsistent slots slots (slots with __state = "inconsistent") as dict slot_name:value-> {'slot_1': <instance of Value()>, 'slot_2': <instance of Value()>,...}
    new_slots(**kwargs)
        used for creating new slots in the State and specifying which Value class to use for which slot
    delete_state_representation()
        empties slots 
    delete_slot(slot_name)
        empties a specific slot
    convert_value(slot_name, input_value)
        used for converting/standardization of an input value in assign() and extend()
    """
    def __init__(self):
        """
        Initialization of the Slot instance

        Attributes
        ----------
        expectations = pvector
        slot_names = pvector
        History = pvector
        value_classes = pmap
        """
        self.expectations = v()  
        self.slot_names = v()
        self.History = v()
        self.value_classes = m()

    def push(self, *args, **kwargs):
        """
        Function used in connection with a expect(). expect() fills self.expectations and push checks if they are handled.
        If needed, push calls extend() for adding new values to a slot or confirm_slot()/empty_slots_fcn() depending on a previous turn in dialog.
        expectations are appended to State's history.

        Parameters
        ----------
        args
            list of slot names for confirming or emptying slots
        kwargs
            dict of slot_name:Value() pairs for extending slots

        """
        expectations, self.expectations = self.expectations, v()
        if len(expectations) != 0: # condition so as not to have an empty spaces in history
            self.History = self.History.append(expectations)
        for cb, slot_names in expectations:
            
            cbkwargs = {key: kwargs.get(key) for key in slot_names}

            # Call the expectation callback and pass myself as first argument
            handled = cb(self, **cbkwargs)
            if handled:
                # The arguments were handled by the callback
                for key in slot_names:
                    del kwargs[key]

        if kwargs:
            # Only change state if there is something to push
            self.extend(**kwargs)

        if args and cb.__name__ == "confirm_unconfirmed":
            self.confirm_slots(*args)
        if args and cb.__name__ == "emptying_slots":
            self.empty_slots_fcn(*args)

    def extend(self, **kwargs):
        """
        Function used in connection with a push(). push() calls extend if there any new values to be added to a slot.
        User can input a value in a number o ways (string, list of string, Value(), list of Value()..) so a value converted to an instance of Value() is used.
        extend() just checks if the value is just Value() or list of Value()

        Parameters
        ----------
        kwargs
            dict of slot_name:Value() pairs for extending slots

        """
        for key, value in kwargs.items():

            slot_name = key
            converted_value = self.convert_value(slot_name, value)
            if isinstance(converted_value, list):
                for value_in in converted_value:
                    self.__dict__[slot_name].value = value_in
                    print("Extended values:", slot_name, '=',value_in.value)

            else:
                self.__dict__[slot_name].value = converted_value
                print("Extended values:", slot_name, '=',converted_value.value)


    def assign(self, **kwargs):
        """
        Function used in connection with a state.push(state.disambig). Assigns a specific value to a slot.
        User can input a value in a number o ways (string, list of string, Value(), list of Value()..) so a value converted to an instance of Value() is used.

        Parameters
        ----------
        kwargs
            dict of slot_name:Value() pairs for extending slots

        """
        for key, value in kwargs.items():
            for i in range(len(self.__dict__[key].value)):
                self.__dict__[key].value.pop()
            
            converted_value = self.convert_value(key, value)
            self.__dict__[key].value = converted_value

            print("Assigned values:", key, '=', converted_value.value)

    def confirm_slots(self, *args):
        """
        Function used in connection with a state.push(state.confirm_unconfirmed). Confirms specified slots.
        
        Parameters
        ----------
        args
            list of slot_names
        """
        for slot_name in self.slot_names:  # iterate over slots
            for slot in args:
                if getattr(self, slot_name) is slot:
                    self.__dict__[slot_name].state = 'confirmed'
                    print(f"Slot {slot_name} is confirmed")

    def empty_slots_fcn(self, *args):
        """
        Function used in connection with a state.push(state.emptying_slots). Empties specified slots.
        
        Parameters
        ----------
        args
            list of slot_names
        """
        for slot_name in self.slot_names:  # iterate over slots
            for slot in args:
                if getattr(self, slot_name) is slot:
                    self.__dict__[slot_name] = Slot()
                    print(f"Slot {slot_name} is emptied")

    def expect(self, cb, *args):
        """
        Function used in connection to fill self.expectations as what should happen in the next dialog turn.
        Appends callback function and slot names to self.expectations.
        
        Parameters
        ----------
        cb
            callback function
        args
            list of slot_names
        """

        slot_names = v()
        for slot_name in self.slot_names:  # iterate over slots
            for slot in args:
                if getattr(self, slot_name) is slot:
                    slot_names = slot_names.append(slot_name)
        self.expectations = self.expectations.append((cb, slot_names))

    @staticmethod
    def emptying_slots(self, **kwargs):
        """
        Callback function used for emptying slots.
        
        Parameters
        ----------
        kwargs
            dict of slot names: None
        """
        for slot_name in kwargs:
            print(f'Slot {slot_name} will be emptied')

    @staticmethod
    def complete_empty(self, **kwargs):
        """
        Callback function used for completing empty slots.
        
        Parameters
        ----------
        kwargs
            dict of slot names: None
        """
        for slot_name in kwargs:
            print(f'Slot {slot_name} must be filled')
            

    @staticmethod
    def confirm_unconfirmed(self, **kwargs):
        """
        Callback function used for confirming unconfirmed slots.
        
        Parameters
        ----------
        kwargs
            dict of slot names: None
        """
        for slot_name in kwargs:
            print(f'Slot {slot_name} must be confirmed')
            

    @staticmethod
    def disambig(self, **kwargs):
        """
        Callback function used for solving inconsistencies in a slot.
        Input value is not accepted if it is not already present in slot's __value.
        
        Parameters
        ----------
        kwargs
            dict of slot names:value
        """
        for key, value in kwargs.items():
            if isinstance(value, (list, tuple)):
                value = value[0]
            if value not in self.__dict__[key].all_values:
                print(f'Value {value} was not accepted, it was not in proposed values {self.__dict__[key].all_values} of slot {key}')
                return False # the values were not assigned -> the slots were not handled
            else:
                print(f'Value {value} was accepted in slot {key}')
                self.assign(**kwargs)
                return True  # the slots were handled

    @staticmethod
    def present(self, **kwargs):
        """
        Callback function used for presenting slots and their values.
        
        Parameters
        ----------
        kwargs
            dict of slot names:value
        """
        for slot_name in kwargs:
            print("Value was presented", getattr(self, slot_name).first_value, "for slot ", slot_name)

    def empty_slots(self):
        """
        Returns all empty slots as a dict() -> {'slot_1': Value(), 'slot_2': Value()...}
        
        """
        empty_slots = dict()
        for attribute, value in self.__dict__.items():
            if isinstance(value, Slot):
                if self.__dict__[attribute].state is None:
                    empty_slots[attribute] = value
        return empty_slots

    def confirmed_slots(self):
        """
        Returns all confirmed slots as a dict() -> {'slot_1': Value(), 'slot_2': Value()...}
        
        """
        confirmed_slots = dict()
        for attribute, value in self.__dict__.items():
            if isinstance(value, Slot):
                if self.__dict__[attribute].state == 'confirmed':
                    confirmed_slots[attribute] = value
        return confirmed_slots

    def unconfirmed_slots(self):
        """
        Returns all unconfirmed slots as a dict() -> {'slot_1': Value(), 'slot_2': Value()...}
        
        """
        unconfirmed_slots = dict()
        for attribute, value in self.__dict__.items():
            if isinstance(value, Slot):
                if self.__dict__[attribute].state == 'unconfirmed':
                    unconfirmed_slots[attribute] = value
        return unconfirmed_slots

    def inconsistent_slots(self):
        """
        Returns all inconsistent slots as a dict() -> {'slot_1': Value(), 'slot_2': Value()...}
        
        """
        inconsistent_slots = dict()
        for attribute, value in self.__dict__.items():
            if isinstance(value, Slot):
                if self.__dict__[attribute].state == 'inconsistent':
                    inconsistent_slots[attribute] = value
        return inconsistent_slots
    
    def new_slots(self, **kwargs):
        """
        Function creates prepares instances of Slot() with input names. Also used for specifying which instance of Value() should be used for a given slot.
        Names of created slots are appended to the state's history.
        Parameters
        ----------
        kwargs
            dict of slot names:which Value() to use (state.new_slots(card=Cards, to_station=Station,...))
        
        """
        for slot_name, value_class in kwargs.items():
            self.value_classes = self.value_classes.set(slot_name, value_class)
            self.__dict__[slot_name] = Slot()
            self.slot_names = self.slot_names.append(slot_name)
            print("New slot added: ", slot_name)
        self.History = self.History.append(self.slot_names)

    def delete_state_representation(self):
        """
        Empties all slots (overwrites them with an empty Slot()). Usually used at the end of the dialog or for debugging purposes.
        """

        for slot_name in self.slot_names:
            self.__dict__[slot_name] = Slot()

    def delete_slot(slot_name):
        """
        Empties a specific slot (overwrites it with an empty Slot()). Usually used at when the user wants to change a value of the slot or for debugging purposes.
        """
        self.__dict__[slot_name] = Slot()

    def convert_value(self, slot_name, value_in):
        """
        Converts the input value which can be e.g. string, list of string, Value(), list of Value()... to the desired instance of Value()
        """
        value_out = None
        if isinstance(value_in, (list, tuple)):
            if len(value_in) > 1:
                value_out = list()
                for value_in_in in value_in:
                    if isinstance(value_in_in, Value):
                        values_list.append(value_in_in)
                    else:
                        values_list.append(self.value_classes[slot_name](value_in_in))
            else:
                if isinstance(value_in[0], Value):
                    value_out = value_in[0]
                else:
                    value_out = self.value_classes[slot_name](value_in[0])
            return value_out
        else:
            value_out = None
            if isinstance(value_in, Value):
                value_out = value_in
            else:
                value_out = self.value_classes[slot_name](value_in)
            return value_out

