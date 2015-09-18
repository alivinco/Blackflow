from Queue import Queue, Empty
import logging
import thread
import time

__author__ = 'alivinco'

log = logging.getLogger("state_machine")

class State:
    def __init__(self,current_state,new_state,transition_value,action_func,timeout,timeout_event):
        """
        State definition
        :param current_state: value which represents current state
        :param new_state: value which  represents next or new state .
        :param transition_value: transition event which moves state machine forwards to next state if transition_value match new evetn
        :param action_func: Action which is performed just before state change.
        :param timeout: Timeout defines how long the system can be in the current_stat .
               If the system stays in the current state more then timeout value then timeout_event is generated.
        :param timeout_event:timeout event defines state machine transition if timeout ocures .
        """
        self.current_state = current_state
        self.new_state = new_state
        self.transition_value = transition_value
        self.action_func = action_func
        self.timeout = timeout
        self.timeout_event = timeout_event


class StateMachine:
    def __init__(self,state_definitions):
        """

        :param state_definitions: rules loaded into production memory.
        """
        # Production memory (rules)
        self.state_definitions = state_definitions
        # Working memory (facts)
        self.incoming_event_queue = Queue()
        self.current_state = 0
        self.end_state = 0
        self.is_end_state = True

    def start(self,start_state,end_state):
        """!
        Starts state flow execution in separate thread .
        @param start_state:
        @param end_state:
        """
        self.incoming_event_queue.empty()
        if  self.is_end_state :
            self.current_state = start_state
            self.end_state = end_state
            self.current_states_obj = filter(lambda item : item.current_state == start_state,self.state_definitions)
            thread.start_new_thread(self.__run,())
        else :
            log.error("State machine can't be started since another instance is already running")


    def enqueue_event(self,event):
        """!
        Method is used to enqueue message into state machine queue
        @param event: event has to be in format {"event":event_code,"data":data_in_some_format} .
                     The entire event object will be passed into action function .
        """
        log.debug("Enqueueing event = %s"%event)
        self.incoming_event_queue.put(event)

    def set_state_definitions(self,state_definitions):
        self.state_definitions = state_definitions

    def is_running(self):
        return not(self.is_end_state)

    def __run(self):

        """
        Main loop which runs Pattern Matcher which is using rules from Production memory and facts from Working memory (queue)

        """
        self.is_end_state = False

        while not self.is_end_state :
            try:
                log.debug("Current state = %s"%self.current_state)
                # getting transition event
                try:
                    msg = self.incoming_event_queue.get(timeout=self.current_states_obj[0].timeout)
                    event = msg["event"]
                    log.debug("Event is = %s"%event)
                except Empty :
                    log.error("State timeout . The system has spent too much time in the state . ")
                    self.enqueue_event({"event":self.current_states_obj[0].timeout_event,"data":None})
                    continue
                except:
                    log.exception("getting message:")
                    log.error("Msg object doesn't comply to expected event format.The even is discarded")
                    continue

                # searching for current state among several states witch matching transition state
                try:
                    current_state = filter(lambda state:state.transition_value==event,self.current_states_obj)[0]
                except:
                    log.error("The event is not in transition event list therefore will be discarded.")
                    continue
                if current_state.action_func : current_state.action_func(msg)

                if current_state.new_state == self.end_state:
                   self.is_end_state = True
                   self.current_state = self.end_state
                   self.current_states_obj = filter(lambda item : item.current_state == self.end_state,self.state_definitions)
                else :
                   try:
                        self.current_states_obj = filter(lambda item : item.current_state == current_state.new_state,self.state_definitions)
                        self.current_state = self.current_states_obj[0].current_state
                   except:
                        log.error("Transition to new state failed . The system can't find definition for new state")
                        break

            except Exception as ex:
                log.exception(ex)
                break

        log.debug("State machine reached it's finite state")











