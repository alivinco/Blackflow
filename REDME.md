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


### Simple app example : 

    import logging
    from libs.msg_template import generate_msg_template
    from core.app import BfApp

    log = logging.getLogger("PullCordSirenApp")

    class PullCordSirenApp(BfApp):
         name = "PullCordSirenApp"
         
         def on_start(self):
         """
           The method is invoked once during app startup . Init all variables here 
         """
             self.var_set("is_alarms_situation", False )
         
         def on_stop():
         """
           The method is invoked during app shutdown . Do all cleanup work here  
         """    
         def on_message(self,triggered_by):
         """
          The method is invoked every time variable from sub_for section is changed (sub_for section in app config) 
         """
             log.info("%s app was triggered by %s"%(self.name,triggered_by))
             situation = self.var_get(triggered_by)["event"]["default"]["value"]
             if situation == "medical" and not self.var_get("is_alarms_situation"):
                 # publish is a helper function for var_set.  First argument is publish destination alias and second is a payload    
                 self.publish("siren_control", self.siren_control("chime"))
                 self.publish("push_cmd_local",{"command":{"properties":{"title":"Emergency","body":"Cord has been pulled or button pressed ","address":""}}})
                 self.var_set("is_alarms_situation",True)
             elif situation == "cancel" or self.var_get("is_alarms_situation"):
                 self.publish("push_cmd_local",{"command":{"properties":{"title":"Emergency cancel","body":"Everything is ok","address":""}}})
                 self.var_set("is_alarms_situation",False)
     
         def siren_control(self,state):
             msg = generate_msg_template(self.name,"command","mode","siren")
             msg["command"]["default"]["value"] = state
             return msg
