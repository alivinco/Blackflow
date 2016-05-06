## Blackflow app engine

### Application packaging

Application folder structure :

#### AppName_v1 directory:
  
+ AppName.py - App source code , normally an app keeps all logic withing the file .  
+ manifest.json - App interface , used to generate app configurations .  
+ __init\_\_.py  
+ libdir - libraries or source files  


#### manifest.json structure :

+ name - Application name
+ version - Version
+ sub_for - List of topics/variables an app is subscribing for.
     key - subscription name  
     msg_type (optional) - message class .   
     topic    (optional) - topic proposal , may be useful for apps with fixed topic .  
     adapter  (optional) - communication adapter .  
     dev_type (optional) - device type . Is used by configurator as topic generation helper .  
     descr    (optional) - description .  
+ pub_to - List of topic/variables an app is sending messages to  .
     key - publishing topic/variable name  
     msg_type (optional) - message class .  
     topic    (optional) - topic proposal , may be useful for apps with fixed topic .  
     adapter  (optional) - communication adapter .  
     dev_type (optional) - device type . Is used by configurator as topic generation helper .  
     descr    (optional) - description .  
+ configs - List of configurations needs to be set before an app can operate .
+ descr - Short description of the application.

#### App lifecycle :

+ App states :     
     STOPPED - application instance is stopped . Application classes and artifacts are not loaded .    
     LOADED - application classes are loaded .     
     INITIALIZED - application successfully initialize and ready to process messages .   
     RUNNING - application instance is running and processing messages .    
     PAUSED - application instance is loaded and is initialized but not processing messages .     
     STOPPED_WITH_ERROR - application stopped with error .     
     PAUSED_WITH_ERROR - application paused with error .    
      
+ Normal startup flow : STOPPED - > LOADED -> INITIALIZED -> RUNNING
+ Class or artifact loading error flow : STOPPED -> (class loading or artifact loading error) -> STOPPED_WITH_ERROR
+ Initialization failure flow : STOPPED -> LOADED -> (error during initialization) -> STOPPED_WITH_ERROR
+ Non recoverable error during runtime , the same error repeats more then X times in a row : STOPPED ->LOADED -> INITIALIZED -> RUNNING -> (non recoverable error) -> PAUSED_WITH_ERROR
+ User can send START , STOP  , PAUSE commands .
+ Each application instance has auto_startup parameter with can take value START , STOP , PAUSE

#### Supported mehods :

+ self.var_set(variable name,value,persist) - Example self.var_set("alarm_state","armed",True)
+ self.var_get(name)
+ self.publish(topic_name,value) - topic_name is name configured in interface , it isn't address 
+ self.config_get(name)
+ self.get_pubs() - returns dict of all publish interfaces . Normally it is used to iterate over all interfaces .

### Simple app example : 

    from blackflow.core.app import BfApp
    from libs.iot_msg_lib.iot_msg import IotMsg, MsgType
    import logging
    log = logging.getLogger("BfApplicationTemplate")
    
    
    class BfApplicationTemplate(BfApp):
        name = __name__
    
        def on_install(self):
            """
            Invoked once after app installation . Can be used to init application resources
            """
            log.info("%s app was installed ")
    
        def on_uninstall(self):
            """
            Invoked once before app uninstall  . Can be used to clean up application resources
            """
            log.info("%s app was uninstalled ")
    
        def on_start(self):
            """
               The method is invoked once during app startup . Init all variables here
            """
            log.info("%s app was started ")
    
        def on_stop(self):
            """
               The method is invoked during app shutdown . Do all cleanup work here
            """
            log.info("%s app was stopped ")
    
        def on_message(self, topic, iot_msg):
            """
              The method is invoked every time variable from sub_for section is changed (sub_for section in app config)
              :type topic: str
              :param topic: full topic name which includes prefix as "local:" , "mqtt:" , etc .
              :type iot_msg: libs.iot_msg_lib.iot_msg.IotMsg
              :param iot_msg: IotMsg object
             """
            log.info("%s app was triggered by %s" % (self.name, topic))
            situation = iot_msg.get_default_value()
            log.info("Alarm situation %s"%situation)
            # publish is a helper function for var_set.  First argument is publish destination alias and second is a payload
            siren_cmd = IotMsg(self.name,MsgType.CMD,msg_class="binary",msg_subclass="switch")
            self.publish("siren_control", siren_cmd)
            self.var_set("is_alarms_situation", True,persist=True)


