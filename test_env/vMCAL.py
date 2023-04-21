
import time
from datetime import datetime

def v_fls_sim_event(func_name):
    """
    A function decorator for applying FLS simulated events specified in DSL:   Delay | Error | Timeout
    When C application calls vFLS callback, first this decorator will be called and then callback function.
    This allows to check if any event is needed to be applied before calling the function callback.
    """
    def decorator_function(func):
        def wrapper_function(*args, **kwargs) -> int:
            events = []
            result = 0
            if func_name in args[0].flash_sim_actions:
                event_list = args[0].flash_sim_actions[func_name]
                get_events(args, events, event_list)
                result = apply_event(args, kwargs, events)
                # if not sim events call function as ussual
                if len(events) == 0:
                    result = func(*args, **kwargs)                    

            return result

        def apply_event(args, kwargs, events):
            result = 0
            for event in events:
                if event['type'] == 'DELAY':
                    time.sleep(event['time']/1000) # in ms
                    result = func(*args, **kwargs)
                elif event['type'] == 'ERROR' :
                        # return error
                    result = 2
                else: #TODO
                    pass

                log_event(args, event)

                return result

        def log_event(args, event):
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # log the event
            log = f"{current_time} - {func_name} -> SIM INTRODUCED {event['type']}"
            args[0].history_data.append(log)

        def get_events(args, events, event_list):
            for event_dict in event_list:
                cycle_num = list(event_dict.keys())[0]
                # check if event needs to be applied immediatelly
                if cycle_num == 0:
                    events.append(event_dict[cycle_num])
                    # get and remove event
                    event_list.remove(event_dict)
                else:
                    # check if event is reached the time in simulation
                    current_time_ms = args[0].time_from_start()
                    if current_time_ms  >= cycle_num:
                        events.append(event_dict[cycle_num])
                        #check proppagation time for ERRORs and TIMEOUTs
                        if event_dict[cycle_num]['type'] != 'DELAY':
                            propagation_time = event_dict[cycle_num]['propagation_time']
                            if propagation_time == 0:
                                # get and remove event
                                event_list.remove(event_dict)
                            else:
                                if current_time_ms > cycle_num + propagation_time:
                                    # get and remove event
                                    event_list.remove(event_dict)
                        else:
                            # get and remove event
                            event_list.remove(event_dict)
                break
        return wrapper_function
    return decorator_function