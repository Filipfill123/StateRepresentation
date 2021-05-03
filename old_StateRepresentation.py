from pyrsistent import v, pvector
from pyrsistent import m, pmap

class StateRepresentation:
    
    def __init__(self, user_state):
        """
        Initialization of STATE REPRESENTATION
        TaskSlot for task's state
        UserSlot for user's state
        AgentSlots for agent's slots
        """
        self.TaskSlot = TaskSlot()
        self.UserSlot = UserSlot(user_state)
        self.AgentSlots = m()
        self.StateRepresentation = v(self.UserSlot, self.AgentSlots, self.TaskSlot)
        self.Memory = list()
        

    def update_state_representation(self):
        """
        Updates StateRepresentation for Memory
        """
        self.StateRepresentation = v(self.UserSlot, self.AgentSlots, self.TaskSlot)
    """
    Agent functions
    """
    def update_agent_slot(self, name, slot_value, slot_confidence, slot_state="not_confirmed"):
        """
        Saves Memory of StateRepresentation and inserts a slot in Agent, then updates StateRepresentation
        Args: name of the slot, slot value, confidence score for the value, state of the slot is generally set as "not_confirmed"
        """
        self.Memory.append(self.StateRepresentation)
        self.AgentSlots = self.AgentSlots.set(name, AgentSlot(name, slot_state, slot_value, slot_confidence))
        self.update_state_representation()


    def remove_agent_slot(self, which_slot):
        """
        Saves Memory of StateRepresentation and removes a desired slot, then updates StateRepresentation
        Args: idx of slot to remove
        """
        self.Memory.append(self.StateRepresentation)
        self.AgentSlots = self.AgentSlots.remove(which_slot)
        self.update_state_representation()

    def print_agent_names(self):
        """
        Primarely for debugging, prints names of all agent's slots
        """
        names = []
        for key in self.AgentSlots.iteritems():
            names.append(key)
        return names


    def get_state_representation(self):
        """
        Returns whole StateRepresentation
        """
        return self.StateRepresentation

    def get_slot_value(self, which_slot, index=0):
        """
        For getting value of a specific slot
        Args: number of slot to get
        
        Returns: value of a specific slot
        """
        slot_value = self.AgentSlots[which_slot].get_slot_value_slot(index)
        return slot_value
    
    def get_all_slot_values(self, which_slot):
        """
        For getting all values of a single slot
        Args: idx of slot
        """
        slot_values = list()
        for i in range(len(self.AgentSlots[which_slot].slot_value_confidence)):
            slot_values.append(self.AgentSlots[which_slot].get_slot_value_slot(i))
        return slot_values

    def get_all_slots_value(self): 
        """
        For getting value of all slots
        
        Returns: array of values for all slots ([ace, king,...]) for slot_1 and slot_2,...
        """
        slots_value = list()
        for i in range(len(self.AgentSlots)):
            slots_value.append(self.AgentSlots[i].get_slot_value_confidence_slot())
        return slots_value


    def get_all_not_confirmed_slots(self):
        """
        For getting all uncofirmed slots
        Returns: array of arrays [[1, "ace"], [4, "two"],...] = [[which_slot_is_not_confirmed, slot_value],...] 
        """
        uncofirmed_slots = list()
        for i in range(len(self.AgentSlots)):
            if self.AgentSlots[i].get_slot_state_slot() == "not_confirmed":
                uncofirmed_slots.append([i+1, self.AgentSlots[i].get_slot_value_confidence_slot()])
        return uncofirmed_slots

    def get_all_confirmed_slots(self):
        """
        For getting all cofirmed slots
        Returns: array of arrays [[1, "ace"], [4, "two"],...] = [[which_slot_is_confirmed, slot_value],...] 
        """
        cofirmed_slots = list()
        for i in range(len(self.AgentSlots)):
            if self.AgentSlots[i].get_slot_state_slot() == "confirmed":
                cofirmed_slots.append([i+1, self.AgentSlots[i].get_slot_value_cofidence_slot()])
        return cofirmed_slots

    def get_all_inconsistent_slots(self):
        """
        For getting all inconsistent slots
        Returns: array of arrays [[1, ["ace",0.9]], [4, ["two",0.87]],...] = [[which_slot_is_inconsistent, [[slot_value_1, confidence_score_1], [slot_value_2, confidence_score_2]]],...] 
        """
        inconsistent_slots = list()
        for i in range(len(self.AgentSlots)):
            if self.AgentSlots[i].get_slot_state_slot() == "inconsistent":
                inconsistent_slots.append([i+1, self.AgentSlots[i].get_slot_value_confidence_slot()])
        return inconsistent_slots


    def get_all_empty_slots(self):
        """
        For getting all empty slots
        Returns: array of number of empty slots [1, 4, 7,...]
        """
        empty_slots = list()
        for i in range(len(self.AgentSlots)):
            if (self.AgentSlots[i].get_slot_state_slot() is None or self.AgentSlots[i].get_slot_state_slot() == "empty"):
                empty_slots.append(i+1)
        return empty_slots


    def set_slot_value_confidence(self, which_slot, slot_value, slot_confidence):
        """
        For setting an unconfirmed value to a slot
        Args: value to set, number of slot
        
        """
        self.Memory.append(self.StateRepresentation)
        self.AgentSlots[which_slot].set_slot_value_confidence_slot(slot_value, slot_confidence)
        self.update_state_representation()

    def set_slot_not_cofirmed(self, which_slot):
        """
        For setting a slot to an unconfirmed state
        Args: which slot to confirm
        """
        self.Memory.append(self.StateRepresentation)
        self.AgentSlots[which_slot].set_slot_state_slot("not_confirmed")
        self.update_state_representation()

    def set_slot_confirmed(self, which_slot):
        """
        For setting a slot to a confirmed state
        Args: which slot to confirm
        """
        self.Memory.append(self.StateRepresentation)
        self.AgentSlots[which_slot].set_slot_state_slot("confirmed")
        self.update_state_representation()

    def set_slot_inconsistent(self, which_slot):
        """
        For setting a slot to an inconsistent state
        Args: which slot to inconsist
        """
        self.Memory.append(self.StateRepresentation)
        self.AgentSlots[which_slot].set_slot_state_slot("inconsistent")
        self.update_state_representation()
    
            
    """
    General functions
    """

    def get_task_state(self):
        """
        For getting state of task
        Returns: (str) state of task
        """
        task_state = self.TaskSlot.get_task_state_slot()

        return task_state


    def get_user_state(self):
        """
        For getting state of user
        Returns: (str) state of user
        """
        user_state = self.UserSlot.get_user_state_slot()
        
        return user_state


    def set_task_state(self, task_state):
        """
        For setting a task state
        Args: the task state to be set
        """
        self.TaskSlot.set_task_state_slot(task_state)


    def set_user_state(self, user_state):
        """
        For setting a user state
        Args: the user state to be set
        """
        self.UserSlot.set_user_state_slot(user_state)

    
    def delete_state_representation(self):
        """
        Deletes the whole state representation - primarely for debugging purposes
        """
        self.UserSlot.set_user_state_slot(None)
        self.TaskSlot.set_task_state_slot(None)
        self.AgentSlots = m()
            


class TaskSlot:
    """
    Class for TaskSlot (similar to UserSlot class, different classes used for clarity)
    """
    def __init__(self):
        """
        Initialization, TODO if task_state should be input
        """
        self.task_state = None

    def set_task_state_slot(self, task_state):
        """
        For setting the task state
        Args: task state (should be from a set of approved keywords)
        """
        self.task_state = task_state

    def get_task_state_slot(self):
        """
        Returns task state
        """
        return self.task_state

class UserSlot:
    """
    Class for UserSlot (similar to TaskSlot class, different classes used for clarity)
    """
    def __init__(self, user_state):
        """
        Initialization, TODO if user_state should be input
        """
        self.user_state = user_state
    
    def set_user_state_slot(self, user_state):
        """
        For setting the user state
        Args: user state (should be from a set of approved keywords)
        """
        self.user_state = user_state

    def get_user_state_slot(self):
        """
        Returns user state
        """
        return self.user_state

class AgentSlot:
    """
    Class for AgentSlot
    """
    def __init__(self, name, slot_state, slot_value, slot_confidence):
        """
        Initialization
        Args: name of the slot, state of the slot, value for the slot, confidence score for the value
        """
        self.name = name
        self.slot_state = slot_state
        self.slot_value_confidence = [{"value": slot_value, "confidence_score": slot_confidence}]  # slot value and confidence are linked and are in a list,
                                                                                                   # so that we can have more than one pair of value and confidence


    def set_slot_value_confidence_slot(self, slot_value, slot_confidence):
        """
        Sets or inserts a new value-confidence_score pair in the slot. If it is the first pair to be set, state of the slot is "not_confirmed", else it is "inconsistent"
        Args: slot value, confidence score for the value
        """
        if not self.get_slot_value_confidence_slot():
            self.slot_value_confidence = [{"value": slot_value, "confidence_score": slot_confidence}]
            self.slot_state = "not_confirmed"
        else:
            self.slot_value_confidence.append({"value": slot_value, "confidence_score": slot_confidence})
            self.slot_value_confidence.sort(key=lambda x: x["confidence_score"], reverse=True)
            self.slot_state = "inconsistent"

    def set_slot_state_slot(self, slot_state):
        """
        For setting a slot state
        Args: slot state ("not_confirmed", "inconcistent", "confirmed", "empty"/None)
        """
        self.slot_state = slot_state

    def get_all_slot_values_slot(self):
        """
        Returns a dict() with slot_name, slot_value_confidence pair and slot_state
        """
        return {"slot_name": self.name, "slot_value_confidence": self.slot_value_confidence, "slot_state": self.slot_state}

    def get_slot_name_slot(self):
        """
        Returns slot name
        """
        return self.name

    def get_slot_value_slot(self, index):
        """
        Returns slot value
        Args: idx of value-confidence pair of the slot
        """
        return self.slot_value_confidence[index]["value"]

    def get_slot_confidence_slot(self, index):
        """
        Returns confidence score for the value
        Args: idx of value-confidence pair of the slot
        """
        return self.slot_value_confidence[index]["confidence_score"]

    def get_slot_value_confidence_slot(self):
        """
        Returns all value-confidence pairs of the slot
        """
        return self.slot_value_confidence

    def get_slot_state_slot(self):
        """
        Returns a state of the slot
        """
        return self.slot_state