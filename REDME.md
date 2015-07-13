## Blackflow app engine

### Application packaging

Application folder structure :

#### AppName directory:
  
+ AppName.py - App source code , normally an app keeps all logic withing the file .  
+ AppName.json - App interface , used to generate app configurations .  
+ __init\_\_.py  
+ libdir - libraries or source files  


#### AppName.json structure :

+ name - Application name
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


### Simple app example : 

    import logging
    from libs.msg_template import generate_msg_template
    from core.app import BfApp

    log = logging.getLogger("PullCordSirenApp")

    class PullCordSirenApp(BfApp):
         name = "PullCordSirenApp"
         
         def init_app(self):
         """
           The method is invoked once during app startup . Init all variables here 
         """
             self.var_set("is_alarms_situation", False )
             
         def run(self,triggered_by):
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
