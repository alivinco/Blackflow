### Blackflow app engine

#### Application packaging

Application folder structure :

+ AppName directory
  + AppName.py - App source code , normally an app keeps all logic withing the file .
  + AppName.json - App interface , used to generate app configurations .
  + __init\_\_.py
  + libdir - libraries or source files


AppName.json structure :

+ name - Application name
+ sub_for - List of topics/variables an app is subscribing for.
  + key - subscription name
  + msg_type (optional) - message class .
  + topic    (optional) - topic proposal , may be useful for apps with fixed topic .
  + adapter  (optional) - communication adapter .
  + dev_type (optional) - device type . Is used by configurator as topic generation helper .
  + descr    (optional) - description .
+ pub_to - List of topic/variables an app is sending messages to  .
  + key - publishing topic/variable name
  + msg_type (optional) - message class .
  + topic    (optional) - topic proposal , may be useful for apps with fixed topic .
  + adapter  (optional) - communication adapter .
  + dev_type (optional) - device type . Is used by configurator as topic generation helper .
  + descr    (optional) - description .
+ configs - List of configurations needs to be set before an app can operate .
