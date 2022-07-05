Search.setIndex({docnames:["explanations/glossary","explanations/how-component-updates-are-ordered","how-to/accomplish-a-task","index","reference/api","reference/contributing","tutorials/creating-a-device","tutorials/creating-a-simulation","tutorials/creating-an-adapter","tutorials/installation","tutorials/running-a-simulation"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.viewcode":1,sphinx:56},filenames:["explanations/glossary.rst","explanations/how-component-updates-are-ordered.rst","how-to/accomplish-a-task.rst","index.rst","reference/api.rst","reference/contributing.rst","tutorials/creating-a-device.rst","tutorials/creating-a-simulation.rst","tutorials/creating-an-adapter.rst","tutorials/installation.rst","tutorials/running-a-simulation.rst"],objects:{"":[[4,0,0,"-","examples"],[4,0,0,"-","tickit"]],"examples.devices":[[4,0,0,"-","remote_controlled"],[4,0,0,"-","shutter"],[4,0,0,"-","trampoline"]],"examples.devices.remote_controlled":[[4,1,1,"","RemoteControlled"],[4,1,1,"","RemoteControlledAdapter"],[4,1,1,"","RemoteControlledDevice"]],"examples.devices.remote_controlled.RemoteControlledAdapter":[[4,2,1,"","get_hidden"],[4,2,1,"","get_observed_bytes"],[4,2,1,"","get_observed_str"],[4,2,1,"","get_unobserved_bytes"],[4,2,1,"","get_unobserved_str"],[4,2,1,"","misc"],[4,2,1,"","on_connect"],[4,2,1,"","set_hidden"],[4,2,1,"","set_observed_bytes"],[4,2,1,"","set_observed_str"],[4,2,1,"","set_unobserved_bytes"],[4,2,1,"","set_unobserved_str"],[4,2,1,"","yield_observed"]],"examples.devices.remote_controlled.RemoteControlledDevice":[[4,1,1,"","Inputs"],[4,1,1,"","Outputs"],[4,2,1,"","update"]],"examples.devices.shutter":[[4,1,1,"","Shutter"],[4,1,1,"","ShutterAdapter"],[4,1,1,"","ShutterDevice"]],"examples.devices.shutter.ShutterAdapter":[[4,2,1,"","get_position"],[4,2,1,"","get_target"],[4,2,1,"","set_target"]],"examples.devices.shutter.ShutterDevice":[[4,1,1,"","Inputs"],[4,1,1,"","Outputs"],[4,2,1,"","move"],[4,2,1,"","update"]],"examples.devices.trampoline":[[4,1,1,"","RandomTrampoline"],[4,1,1,"","RandomTrampolineDevice"],[4,1,1,"","TrampolineDevice"]],"examples.devices.trampoline.RandomTrampolineDevice":[[4,2,1,"","update"]],"examples.devices.trampoline.TrampolineDevice":[[4,1,1,"","Inputs"],[4,1,1,"","Outputs"],[4,2,1,"","update"]],"tickit.adapters":[[4,0,0,"-","composed"],[4,0,0,"-","epicsadapter"],[4,0,0,"-","interpreters"],[4,0,0,"-","servers"]],"tickit.adapters.composed":[[4,1,1,"","ComposedAdapter"],[4,3,1,"","T"]],"tickit.adapters.composed.ComposedAdapter":[[4,2,1,"","handle_message"],[4,2,1,"","on_connect"],[4,2,1,"","run_forever"]],"tickit.adapters.epicsadapter":[[4,1,1,"","EpicsAdapter"],[4,1,1,"","InputRecord"],[4,1,1,"","OutputRecord"]],"tickit.adapters.epicsadapter.EpicsAdapter":[[4,2,1,"","after_update"],[4,2,1,"","build_ioc"],[4,2,1,"","link_input_on_interrupt"],[4,2,1,"","load_records_without_DTYP_fields"],[4,2,1,"","on_db_load"],[4,2,1,"","run_forever"]],"tickit.adapters.interpreters":[[4,0,0,"-","command"]],"tickit.adapters.interpreters.command":[[4,0,0,"-","command_interpreter"],[4,0,0,"-","regex_command"]],"tickit.adapters.interpreters.command.command_interpreter":[[4,1,1,"","Command"],[4,1,1,"","CommandInterpreter"]],"tickit.adapters.interpreters.command.command_interpreter.Command":[[4,4,1,"","interrupt"],[4,2,1,"","parse"]],"tickit.adapters.interpreters.command.command_interpreter.CommandInterpreter":[[4,2,1,"","handle"],[4,2,1,"","unknown_command"]],"tickit.adapters.interpreters.command.regex_command":[[4,1,1,"","RegexCommand"]],"tickit.adapters.interpreters.command.regex_command.RegexCommand":[[4,2,1,"","parse"]],"tickit.adapters.servers":[[4,0,0,"-","tcp"]],"tickit.adapters.servers.tcp":[[4,1,1,"","TcpServer"]],"tickit.adapters.servers.tcp.TcpServer":[[4,2,1,"","run_forever"]],"tickit.core":[[4,0,0,"-","adapter"],[4,0,0,"-","components"],[4,0,0,"-","device"],[4,0,0,"-","management"],[4,0,0,"-","runner"],[4,0,0,"-","state_interfaces"],[4,0,0,"-","typedefs"]],"tickit.core.adapter":[[4,1,1,"","Adapter"],[4,1,1,"","Interpreter"],[4,1,1,"","RaiseInterrupt"],[4,1,1,"","Server"],[4,3,1,"","T"]],"tickit.core.adapter.Adapter":[[4,2,1,"","after_update"],[4,2,1,"","run_forever"]],"tickit.core.adapter.Interpreter":[[4,2,1,"","handle"]],"tickit.core.adapter.Server":[[4,2,1,"","run_forever"]],"tickit.core.components":[[4,0,0,"-","component"],[4,0,0,"-","device_simulation"],[4,0,0,"-","system_simulation"]],"tickit.core.components.component":[[4,1,1,"","BaseComponent"],[4,1,1,"","Component"],[4,1,1,"","ComponentConfig"]],"tickit.core.components.component.BaseComponent":[[4,2,1,"","handle_input"],[4,2,1,"","on_tick"],[4,2,1,"","output"],[4,2,1,"","raise_interrupt"],[4,2,1,"","run_forever"]],"tickit.core.components.component.Component":[[4,2,1,"","on_tick"],[4,2,1,"","run_forever"]],"tickit.core.components.device_simulation":[[4,1,1,"","DeviceSimulation"]],"tickit.core.components.device_simulation.DeviceSimulation":[[4,2,1,"","on_tick"],[4,2,1,"","run_forever"]],"tickit.core.components.system_simulation":[[4,1,1,"","SystemSimulation"],[4,1,1,"","SystemSimulationComponent"]],"tickit.core.components.system_simulation.SystemSimulationComponent":[[4,4,1,"","components"],[4,4,1,"","expose"],[4,2,1,"","on_tick"],[4,2,1,"","run_forever"]],"tickit.core.device":[[4,1,1,"","Device"],[4,1,1,"","DeviceUpdate"],[4,3,1,"","InMap"],[4,3,1,"","OutMap"]],"tickit.core.device.Device":[[4,2,1,"","update"]],"tickit.core.management":[[4,0,0,"-","event_router"],[4,0,0,"-","schedulers"],[4,0,0,"-","ticker"]],"tickit.core.management.event_router":[[4,3,1,"","Default_InverseWiring_Struct"],[4,3,1,"","Default_Wiring_Struct"],[4,1,1,"","EventRouter"],[4,1,1,"","InverseWiring"],[4,3,1,"","Inverse_Wiring_Struct"],[4,1,1,"","Wiring"],[4,3,1,"","Wiring_Struct"]],"tickit.core.management.event_router.EventRouter":[[4,5,1,"","component_tree"],[4,5,1,"","components"],[4,2,1,"","dependants"],[4,5,1,"","input_components"],[4,5,1,"","inverse_component_tree"],[4,5,1,"","output_components"],[4,2,1,"","route"],[4,5,1,"","wiring"]],"tickit.core.management.event_router.InverseWiring":[[4,2,1,"","from_component_configs"],[4,2,1,"","from_wiring"]],"tickit.core.management.event_router.Wiring":[[4,2,1,"","from_inverse_wiring"]],"tickit.core.management.schedulers":[[4,0,0,"-","base"],[4,0,0,"-","master"],[4,0,0,"-","slave"]],"tickit.core.management.schedulers.base":[[4,1,1,"","BaseScheduler"]],"tickit.core.management.schedulers.base.BaseScheduler":[[4,2,1,"","add_wakeup"],[4,2,1,"","get_first_wakeups"],[4,2,1,"","handle_message"],[4,2,1,"","schedule_interrupt"],[4,2,1,"","setup"],[4,2,1,"","update_component"]],"tickit.core.management.schedulers.master":[[4,1,1,"","MasterScheduler"]],"tickit.core.management.schedulers.master.MasterScheduler":[[4,2,1,"","add_wakeup"],[4,2,1,"","run_forever"],[4,2,1,"","schedule_interrupt"],[4,2,1,"","setup"],[4,2,1,"","sleep_time"]],"tickit.core.management.schedulers.slave":[[4,1,1,"","SlaveScheduler"]],"tickit.core.management.schedulers.slave.SlaveScheduler":[[4,2,1,"","add_exposing_wiring"],[4,2,1,"","on_tick"],[4,2,1,"","run_forever"],[4,2,1,"","schedule_interrupt"],[4,2,1,"","update_component"]],"tickit.core.management.ticker":[[4,1,1,"","Ticker"]],"tickit.core.management.ticker.Ticker":[[4,5,1,"","components"],[4,2,1,"","propagate"],[4,2,1,"","schedule_possible_updates"]],"tickit.core.runner":[[4,6,1,"","run_all"],[4,6,1,"","run_all_forever"]],"tickit.core.state_interfaces":[[4,0,0,"-","internal"],[4,0,0,"-","kafka"],[4,0,0,"-","state_interface"]],"tickit.core.state_interfaces.internal":[[4,3,1,"","C"],[4,1,1,"","InternalStateConsumer"],[4,1,1,"","InternalStateProducer"],[4,1,1,"","InternalStateServer"],[4,1,1,"","Message"],[4,3,1,"","Messages"],[4,3,1,"","P"]],"tickit.core.state_interfaces.internal.InternalStateConsumer":[[4,2,1,"","add_message"],[4,2,1,"","subscribe"]],"tickit.core.state_interfaces.internal.InternalStateProducer":[[4,2,1,"","produce"]],"tickit.core.state_interfaces.internal.InternalStateServer":[[4,2,1,"","create_topic"],[4,2,1,"","push"],[4,2,1,"","remove_topic"],[4,2,1,"","subscribe"],[4,5,1,"","topics"]],"tickit.core.state_interfaces.internal.Message":[[4,5,1,"","value"]],"tickit.core.state_interfaces.kafka":[[4,3,1,"","C"],[4,1,1,"","KafkaStateConsumer"],[4,1,1,"","KafkaStateProducer"],[4,3,1,"","P"]],"tickit.core.state_interfaces.kafka.KafkaStateConsumer":[[4,2,1,"","subscribe"]],"tickit.core.state_interfaces.kafka.KafkaStateProducer":[[4,2,1,"","produce"]],"tickit.core.state_interfaces.state_interface":[[4,3,1,"","C"],[4,3,1,"","P"],[4,1,1,"","StateConsumer"],[4,3,1,"","StateInterface"],[4,1,1,"","StateProducer"],[4,6,1,"","add"],[4,6,1,"","get_interface"],[4,6,1,"","interfaces"],[4,6,1,"","satisfy_externality"]],"tickit.core.state_interfaces.state_interface.StateConsumer":[[4,2,1,"","subscribe"]],"tickit.core.state_interfaces.state_interface.StateProducer":[[4,2,1,"","produce"]],"tickit.core.typedefs":[[4,3,1,"","Changes"],[4,3,1,"","ComponentID"],[4,1,1,"","ComponentPort"],[4,1,1,"","Input"],[4,1,1,"","Interrupt"],[4,1,1,"","Output"],[4,3,1,"","PortID"],[4,3,1,"","SimTime"],[4,3,1,"","State"]],"tickit.core.typedefs.ComponentPort":[[4,2,1,"","deserialize"],[4,2,1,"","serialize"]],"tickit.devices":[[4,0,0,"-","cryostream"],[4,0,0,"-","femto"],[4,0,0,"-","pneumatic"],[4,0,0,"-","sink"],[4,0,0,"-","source"]],"tickit.devices.cryostream":[[4,0,0,"-","base"],[4,0,0,"-","cryostream"],[4,0,0,"-","states"],[4,0,0,"-","status"]],"tickit.devices.cryostream.base":[[4,1,1,"","CryostreamBase"]],"tickit.devices.cryostream.base.CryostreamBase":[[4,2,1,"","cool"],[4,2,1,"","end"],[4,2,1,"","get_status"],[4,2,1,"","hold"],[4,2,1,"","pause"],[4,2,1,"","plat"],[4,2,1,"","purge"],[4,2,1,"","ramp"],[4,2,1,"","restart"],[4,2,1,"","resume"],[4,2,1,"","set_status_format"],[4,2,1,"","stop"],[4,2,1,"","turbo"],[4,2,1,"","update_temperature"]],"tickit.devices.cryostream.cryostream":[[4,1,1,"","CryostreamAdapter"],[4,1,1,"","CryostreamDevice"]],"tickit.devices.cryostream.cryostream.CryostreamAdapter":[[4,2,1,"","cool"],[4,2,1,"","end"],[4,2,1,"","hold"],[4,2,1,"","on_connect"],[4,2,1,"","pause"],[4,2,1,"","plat"],[4,2,1,"","purge"],[4,2,1,"","ramp"],[4,2,1,"","restart"],[4,2,1,"","resume"],[4,2,1,"","set_status_format"],[4,2,1,"","stop"],[4,2,1,"","turbo"]],"tickit.devices.cryostream.cryostream.CryostreamDevice":[[4,1,1,"","Inputs"],[4,1,1,"","Outputs"],[4,2,1,"","update"]],"tickit.devices.cryostream.states":[[4,1,1,"","AlarmCodes"],[4,1,1,"","HardwareType"],[4,1,1,"","PhaseIds"],[4,1,1,"","RunModes"]],"tickit.devices.cryostream.status":[[4,1,1,"","ExtendedStatus"],[4,1,1,"","Status"]],"tickit.devices.cryostream.status.ExtendedStatus":[[4,2,1,"","from_packed"],[4,2,1,"","pack"]],"tickit.devices.cryostream.status.Status":[[4,2,1,"","from_packed"],[4,2,1,"","pack"]],"tickit.devices.femto":[[4,0,0,"-","femto"]],"tickit.devices.femto.femto":[[4,1,1,"","FemtoAdapter"],[4,1,1,"","FemtoDevice"]],"tickit.devices.femto.femto.FemtoAdapter":[[4,2,1,"","callback"],[4,2,1,"","on_db_load"]],"tickit.devices.femto.femto.FemtoDevice":[[4,1,1,"","Inputs"],[4,1,1,"","Outputs"],[4,2,1,"","get_current"],[4,2,1,"","get_gain"],[4,2,1,"","set_current"],[4,2,1,"","set_gain"],[4,2,1,"","update"]],"tickit.devices.pneumatic":[[4,0,0,"-","pneumatic"]],"tickit.devices.pneumatic.pneumatic":[[4,1,1,"","PneumaticAdapter"],[4,1,1,"","PneumaticDevice"]],"tickit.devices.pneumatic.pneumatic.PneumaticAdapter":[[4,2,1,"","callback"],[4,2,1,"","on_db_load"]],"tickit.devices.pneumatic.pneumatic.PneumaticDevice":[[4,1,1,"","Outputs"],[4,2,1,"","get_speed"],[4,2,1,"","get_state"],[4,2,1,"","set_speed"],[4,2,1,"","set_state"],[4,2,1,"","update"]],"tickit.devices.sink":[[4,1,1,"","Sink"],[4,1,1,"","SinkDevice"]],"tickit.devices.sink.SinkDevice":[[4,1,1,"","Inputs"],[4,1,1,"","Outputs"],[4,2,1,"","update"]],"tickit.devices.source":[[4,1,1,"","Source"],[4,1,1,"","SourceDevice"]],"tickit.devices.source.SourceDevice":[[4,1,1,"","Inputs"],[4,1,1,"","Outputs"],[4,2,1,"","update"]],"tickit.tickit":[[4,3,1,"","__version__"]],"tickit.utils":[[4,0,0,"-","byte_format"],[4,0,0,"-","configuration"],[4,0,0,"-","singleton"],[4,0,0,"-","topic_naming"]],"tickit.utils.byte_format":[[4,1,1,"","ByteFormat"]],"tickit.utils.byte_format.ByteFormat":[[4,2,1,"","deserialize"],[4,2,1,"","serialize"]],"tickit.utils.configuration":[[4,0,0,"-","configurable"],[4,0,0,"-","loading"]],"tickit.utils.configuration.configurable":[[4,3,1,"","Cls"],[4,6,1,"","as_tagged_union"],[4,3,1,"","is_tagged_union"],[4,6,1,"","rec_subclasses"]],"tickit.utils.configuration.loading":[[4,6,1,"","importing_conversion"],[4,6,1,"","read_configs"]],"tickit.utils.singleton":[[4,1,1,"","Singleton"]],"tickit.utils.singleton.Singleton":[[4,2,1,"","__call__"]],"tickit.utils.topic_naming":[[4,6,1,"","input_topic"],[4,6,1,"","output_topic"],[4,6,1,"","valid_component_id"]],examples:[[4,0,0,"-","devices"]],tickit:[[4,0,0,"-","adapters"],[4,0,0,"-","core"],[4,0,0,"-","devices"],[4,0,0,"-","utils"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","data","Python data"],"4":["py","attribute","Python attribute"],"5":["py","property","Python property"],"6":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:data","4":"py:attribute","5":"py:property","6":"py:function"},terms:{"0":[3,4,6,7,8,10],"08":6,"1":[4,5,8,10],"10":[4,6,7],"100":5,"100000000":[6,8],"1000000000":[4,7,10],"100m":4,"139":[7,10],"14":4,"16":8,"162":10,"1e8":6,"1e9":[3,4],"1s":7,"2":[4,5,6,8,10],"200000000":6,"2000000000":[7,10],"209786950024":8,"209886950024":8,"209986950024":8,"210086950024":8,"225":[7,10],"24":6,"255":3,"25565":[4,8],"2e":6,"3":[4,5,9],"300":4,"300000000":6,"300k":4,"310":4,"33096":8,"4":[6,8],"42":[4,6],"5":4,"5600000000000005":8,"6":8,"7":[8,9],"72":8,"7200000000000015":8,"8":[4,6,8],"9":6,"9n":7,"abstract":4,"break":8,"byte":[4,8],"case":4,"class":[0,3,4],"default":[4,6,8,10],"do":[2,5,6,7,8,10],"final":[6,7,8,10],"float":[4,6,8],"function":4,"import":[4,5,6,8],"int":[3,4,6,8],"new":[3,4,5,6,7,8],"return":[0,3,4,6,8],"static":[4,5],"super":8,"true":[4,8],"try":8,"while":5,A:[0,1,4],And:8,As:[1,6,7,8,10],At:7,For:[4,9],If:[1,4,5,9],In:[4,6,7,8,10],It:[2,9],On:4,Or:4,The:[3,4,5,6,8,9],These:5,To:5,With:[8,10],__call__:[3,4,6,8],__init__:[3,6,8],__subclasses__:4,__version__:4,_asyncio:4,_devic:8,_map:4,abl:4,abov:4,absenc:6,access:3,accompani:8,accord:[4,10],accoridng:4,accumul:4,achiev:4,across:[4,6,8],act:[0,4,6,8],action:5,activ:9,ad:4,adapt:[0,3,6,7],add:[4,5,7,8],add_exposing_wir:4,add_messag:4,add_wakeup:4,addition:[0,3,8],address:4,adjust:4,afford:3,after:[0,4,10],after_upd:4,again:[3,4],against:4,aim:1,aiokafka:4,akin:[6,7,8,10],alarm:4,alarm_cod:4,alarmcod:4,alia:4,alias:4,all:[0,1,4,5,6,7,8,10],allow:[0,4,6,7,8],alon:4,alongsid:1,alreadi:1,also:[5,8,9],alter:[4,8],although:9,amount:4,amplifi:4,an:[0,2,3,4,6,7,10],ani:[1,4,5,6,7,8,9,10],anystr:4,apach:10,api:[3,5],apischema:4,append:[4,8],ar:[0,4,5,7,8,9],arbitrari:4,arg:4,argument:[4,6,8],as_tagged_union:4,ask:3,assert:1,assign:4,associ:7,asyhcnron:4,async:[4,8],asynchron:4,asyncio:4,asynciter:4,asyncron:4,attach:4,attempt:4,auto:10,automat:[4,5,6,8],avail:[4,10],avg_gas_heat:4,avg_suct_heat:4,await:[1,4,8],awoken:4,b:[1,3,4,8],back:[4,8],bar:3,base:[3,8],basecompon:4,baseschedul:4,bbhhhbbhhhhhbbbbbbhhbb:4,bbhhhbbhhhhhbbbbbbhhbbbbbbbbhh:4,becaus:1,been:[1,4,9],befor:[4,5],begin:[1,4,6,7,8],behaviour:4,being:[4,10],below:[1,8],between:[0,3,4],big:[4,5],bin:9,black:5,blob:3,block:4,bo:[3,4,7,10],bool:4,both:[1,4,10],bound:4,bring:4,broke:10,broker:10,brought:1,bug:5,build:[4,5],build_ioc:4,byteformat:[4,8],c:[1,4],cach:4,calcul:4,call:[3,4,8],call_at:[4,6],call_in:[4,6,7,8,10],callabl:[4,8],callback:[0,4],callback_period:[3,4,7],can:[1,4,5,6,8,9],cannot:4,captur:[0,1,8],categori:3,caught:5,cd:5,chang:[0,4,5,6,7,8,10],changelog:[3,5],charact:[4,8],check:[1,4,5],checklist:5,choos:5,cl:4,classmethod:4,client:[0,4,8],clone:5,close:4,code:[3,4],cold:4,collat:4,collect:[0,1],com:[3,4,5,9],come:4,command:[3,6,7,10],command_interpret:8,commandinterpret:[4,8],commandlin:[3,9],common:4,commun:8,complet:[1,4],complex:3,compliant:5,compnent:4,compon:[0,3,6,7,8,10],component_tre:4,componentconfig:[3,4,7,8],componentid:4,componentport:4,componet:4,compos:[1,8],composedadapt:4,compris:[7,8],comput:[1,4],config:[4,6,7,8,10],config_path:[4,10],configur:[3,10],confiur:6,conform:5,connect:[4,8],consid:1,consist:[6,7],constant:6,construct:4,constructor:4,consum:4,contain:[4,5],contin:4,contini:4,continu:[4,10],contr_sink:3,contravari:4,contribut:3,control:[3,4,5,6,7,8,9],controller_numb:4,convent:5,convers:4,cool:4,core:[6,8],coroutin:4,correspond:[0,1,4],cost:1,covari:4,coverag:5,creat:[4,10],create_top:4,cryostreamadapt:4,cryostreambas:4,cryostreamdevic:4,current:[4,6,8,9],custom:4,customis:4,d102:3,d:[1,8],data:4,dataclass:[3,4,6,7,8],date:1,db_file:4,de:4,debug:[3,4,8],decim:8,decod:[4,8],decor:[4,8],decreas:4,def:[3,6,8],default_inversewiring_struct:4,default_posit:[4,6,8],default_wiring_struct:4,defaultdict:4,defer:4,defin:[0,3,4,6,7,8,10],delai:4,deleg:4,delta:[3,7,10],denot:[4,7,8,10],depend:[1,4],deriv:4,deseri:4,desir:4,detail:5,determin:[4,6,8],dev:5,devic:[0,3,8,10],device_simul:6,devicesimul:[3,4,6,8],deviceupd:[3,4,6],dict:4,differ:4,directori:5,disabl:4,discov:1,distribut:[4,10],distriubt:4,dl:[3,4,5,9],dls_control:5,doc:5,docstr:5,document:9,doe:[4,5],doesn:2,don:5,downscal:4,dtyp:4,due:4,durat:4,dure:[0,4,10],e:0,each:[4,7,10],eagerli:4,easi:[6,8],easili:5,echo:4,editor:[6,7,8],either:[1,4],electron:4,elif:6,els:6,emit:[3,10],empti:[1,4],enabl:4,encod:[4,8],end:4,endian:4,enough:2,ensur:[0,1],enumer:4,epic:4,equal:4,error:[4,5],escap:8,establish:1,evap_adjust:4,evap_heat:4,evap_temp:4,event:[3,4],eventrout:4,everi:4,exampl:[1,3,6,7,8,10],except:4,exclud:8,execut:[4,10],exhaust:2,exist:[4,5,9],expect:[6,7,8,10],experienc:3,explain:[2,8],expos:[3,4],express:4,exten:3,extend:[4,7],extended_packet_str:4,extendedstatu:4,extern:[0,4,6,7,8,9],extract:[4,5,8],face:4,facilit:4,facilitati:0,factori:4,faithfulli:[0,1],fals:[4,8],featur:9,femtoadapt:4,femtodevic:4,field:4,file:[4,5],find:4,finsih:4,firefox:5,first:[1,4,6,7,8],fit:5,fix:[4,5],flag:4,flake8:5,flow:4,flux:[4,6,8],follow:[1,4,5,6,7,8,10],form:8,format:[3,4,5,8,10],forward:4,found:4,four:3,framework:[3,4,6,7,8],free:5,from:[0,1,3,4,5,6,8,9],from_component_config:4,from_inverse_wir:4,from_pack:4,from_wir:4,full:4,fulli:4,g:0,ga:4,gain:4,gas_error:4,gas_flow:4,gas_heat:4,gas_set_point:4,gas_temp:4,gener:[0,4],get:[4,5,8],get_curr:4,get_first_wakeup:4,get_gain:4,get_hidden:4,get_interfac:4,get_observed_byt:4,get_observed_str:4,get_posit:[4,8],get_spe:4,get_stat:4,get_statu:4,get_target:[4,8],get_unobserved_byt:4,get_unobserved_str:4,getter:4,git:[5,9],github:[3,4,5,9],gitlab:5,give:4,given:4,goe:4,got:[6,7,8,10],great:5,group:[4,8],guid:[2,10],ha:[1,3,4,9],had:[1,4],halt:4,handl:[0,4,5],handle_input:4,handle_messag:4,handler:4,hard:4,hardwar:4,hardware_typ:4,hardwaretyp:4,hashabl:4,have:[1,2,4,5,7],head:5,headl:5,heater:4,held:4,helper:4,here:[2,3],hidden:4,high:0,hold:4,host:[4,8],how:[0,4,5,6,7,8,10],html:5,http:[3,4],i:4,idea:5,identifi:4,immedi:[0,4,8],immut:[4,6,7,8,10],implement:[0,4,6],implent:4,implment:4,importing_convers:4,improv:5,includ:[0,4,7,8],indefinit:4,index:5,indic:4,infinit:0,influenc:0,inform:[2,4,10],inherit:[6,8],initi:[0,4,6,8,10],initial_curr:4,initial_gain:4,initial_hidden:4,initial_observ:4,initial_posit:[4,6,8],initial_spe:4,initial_st:4,initial_tim:4,initial_unobserv:4,initialis:4,inject:[4,8],inmap:4,input:[1,3,4,6,7,8,10],input_compon:4,input_curr:4,input_top:4,inputrecord:4,insid:9,instal:[3,5,10],instanc:[1,4,10],instanti:[4,6,8],instruct:[6,9],intend:[4,9],interact:[0,1],interfac:[4,8,9],interfer:9,intern:[0,5,9],internalstateconsum:4,internalstateproduc:4,internalstateserv:4,interper:4,interpret:8,interrupt:[0,4,8],intersect:4,intial:4,invers:4,inverse_component_tre:4,inverse_wir:4,inverse_wiring_struct:4,inversewir:4,invert:4,involv:5,io:3,ioc:4,ioc_nam:4,is_tagged_union:4,isort:5,issu:5,iter:4,its:[0,4],just:2,k:4,kafka:10,kafkastateconsum:4,kafkastateproduc:4,kei:4,keyerror:4,know:[2,6],known:4,kwarg:4,kwd:4,l:4,lambda:4,last:4,last_tim:[6,8],later:9,launch:10,lazyconvers:4,length:4,level:[0,4,7],librari:[3,5],lifetim:4,like:[2,6,7],limit:4,line:8,line_pressur:4,link:3,link_input_on_interrupt:4,list:[4,7],listen:4,load_records_without_dtyp_field:4,localhost:[4,8],locat:10,log:4,logger:3,logic:4,lookup:4,m:[6,7,8,9,10],made:8,magic:[6,8],mai:[0,1,4,6,7,8,10],maintain:4,make:[4,5],manag:8,map:[4,6,7,8,10],master:3,masterschedul:[4,10],match:[4,8],materi:3,max:[4,6],maximum:4,mean:8,memori:4,messag:[4,8,10],metaclass:4,method:[3,4,6,8],might:5,min:[4,6],minimis:1,misc:4,miss:4,mock:4,mode:4,modifi:4,modul:4,more:[1,3],most:5,move:[4,6],movement:4,multi:3,multipl:[4,6,8],must:[4,6,7,8,10],my_shutt:6,my_shutter_adapt:8,my_shutter_simul:[6,8],my_simul:7,mypi:5,n:[3,4,8],name:[1,3,4,6,7,8],nanosecond:[4,6],need:9,nest:[0,4],never:4,next:[1,4,6,8],none:[3,4,6,7,8,10],noqa:3,note:5,noth:4,notifi:4,now:[1,7,9],number:[4,5,8],numer:4,o:4,object:[0,4,6,8],observ:[0,3,4],occur:4,off:4,on_connect:4,on_db_load:4,on_tick:4,on_upd:4,onc:[3,4,6,7,10],one:[1,4,5,6],onli:[1,4],open:[4,6,7,8],oper:[6,8],option:[4,6,8,10],orchestr:[0,3,4],order:[0,4,5,6,7,8,10],other:[1,6],otherwis:[1,4],our:[6,7,8],out:10,outmap:4,output:[1,3,4,6,7,8,10],output_compon:4,output_curr:4,output_flux:6,output_top:4,outputrecord:4,over:4,overrid:[4,8],overse:0,overwrit:6,p:[4,8],pack:4,packet:4,page:5,pair:4,paramet:4,parenthes:8,pars:4,particular:2,pass:[4,6,8],path:[4,9],pattern:4,paus:4,pep440:5,per:6,perform:[1,4,6,7,8,10],period:[0,4,6],phase:4,phase_id:4,phaseid:4,physic:4,pip:[3,9],pipenv:[5,9],plat:4,pleas:[5,9],plu:4,pneumaticadapt:4,pneumaticdevic:4,poke:4,port:[4,6,8],portid:4,posit:[4,6,8],possibl:4,posterior:4,power:4,practic:3,pre:[4,8],prefer:[6,7,8],prepend:4,previou:4,previous:[1,4],print:4,prior:[4,8,10],prioriti:4,process:[4,6,8],produc:[4,6,10],progress:[3,4],project:[3,5],propag:4,properti:4,protocol:4,provid:[3,4],publish:4,pull:5,purg:4,push:[4,5],py:[5,6,8],pypi:[3,5],python3:9,python:[4,6,7,8,10],qualifi:4,queu:4,queue:4,quickli:4,quickstart:10,r:[3,4,8],rais:[0,4],raise_interrupt:[4,8],raiseinterrupt:4,ramp:4,ramp_rat:4,rand_tramp:[7,10],randint:3,random:[3,4,6],randomtrampolin:[3,4,7],randomtrampolinedevic:[3,4],rang:4,rate:[4,6],re:4,reach:4,read:[4,5,8],read_config:4,readback:4,readi:4,real:4,rec_subclass:4,reciev:[1,4,6,8],recommend:9,record:4,recurs:4,reduc:5,refer:4,referenc:8,regex:4,regex_command:8,regexcommand:[4,8],regist:[4,8],registri:4,regular:4,regularli:4,relat:4,releas:9,relev:10,remain:[1,4,5],remote_control:3,remotecontrol:[3,4],remotecontrolledadapt:[3,4],remotecontrolleddevic:4,remov:[1,4],remove_top:4,repli:4,report:5,repositori:5,repres:4,request:[0,4,5,8],requir:[4,6,9],resolut:1,resolv:[1,4],respect:[4,8],respons:[0,4,8],restart:4,restrict:4,result:[0,1,4,6],resum:4,retriev:4,root:[1,4],rout:4,router:4,rst:[3,5],run:[0,4,6,8],run_al:4,run_all_forev:4,run_forev:4,run_mod:4,run_tim:4,runmod:4,runnabl:4,s:[0,4,6,7,8],said:8,same:[4,5,6,8],sampl:4,satisfi:4,satisfy_extern:4,save:4,schedul:[0,6,7,8,10],schedule_interrupt:4,schedule_possible_upd:4,scope:5,second:1,see:[6,7,8,9,10],self:[3,6,8],send:[4,8],sent:[4,8],sequenc:[0,1,4],serial:4,serialiaz:4,serv:1,server:[3,8],servic:10,set:[4,5,6,8],set_curr:4,set_gain:4,set_hidden:4,set_observed_byt:4,set_observed_str:4,set_spe:4,set_stat:4,set_status_format:4,set_target:[4,8],set_unobserved_byt:4,set_unobserved_str:4,setup:4,sever:[4,7],shall:[6,7,8,10],shcedul:4,shedul:4,should:[4,6,8,9,10],show:[2,6,7,8,10],shown:[1,4,8],shutter:[6,8],shutter_st:4,shutter_tim:4,shutteradapt:[4,8],shutterdevic:[4,6,8],side:3,signal:4,signatur:4,significantli:5,similar:8,similarli:1,simpl:[4,6,8],simtim:[3,4,6],simul:[0,1,3,4,6,8],simulation_spe:4,sinc:8,singl:[4,6,8],singlton:4,sink:[3,6,7,8],sinkdevic:4,slave:0,slaveschedul:4,sleep_tim:4,so:[4,6,8,9],soft:4,softwar:9,software_vers:4,someon:2,someth:5,sourc:[3,5,6,7,8,9,10],sourcedevic:4,specif:7,specifi:[0,4,6,8],speed:4,spend:5,split:3,stand:4,standard:[4,5,8],start:[3,4,8,10],state:[0,1,8],state_consum:4,state_produc:4,stateconsum:4,stateinterfac:4,stateproduc:4,staticmethod:6,status_bytes_str:4,status_format:4,step:[1,3,10],still:4,stop:4,store:[1,4,6,8],str:[4,8],string:[4,8],struct:4,sub:4,subclass:4,subscrib:4,subscript:4,subsequ:4,suct_heat:4,suct_temp:4,suit:4,sunk:[6,7,8,10],superclass:4,suppli:4,support:4,sure:5,system:[0,1,4,7],systemsimul:4,systemsimulationcompon:4,t:[2,4,5,8],tag:[4,5],take:[4,6,7],target:[4,6,7,8,10],target_posit:[6,8],target_temp:4,task:4,tcp:[0,8],tcp_contr:3,tcpserver:[3,4,8],technic:3,telnet:8,temperatur:4,termin:9,text:7,thei:[1,2,8,9],them:[4,7],themselv:1,thi:[1,3,4,5,6,7,8,9,10],thing:4,thinli:4,those:4,through:[3,5,6,8],tick:[0,1,4,6,7,8,10],ticker:[0,8],ticket:[5,8],tickit:[2,5,6,7,8,9,10],time:[0,3,4,5,6,7,8,10],time_to_fil:4,titl:5,to_upd:1,togeth:[4,7],toggl:4,toi:4,tool:5,top:[4,7],topic:[4,10],total_hour:4,tramp_sink:[7,10],trampolin:[7,10],trampolinedevic:4,transmiss:[6,8],transmit:4,tree:4,trigger:4,trivial:4,tupl:4,turbo:4,turbo_mod:4,turbo_on:4,tutori:[2,6,7,8,10],two:[6,8],typ:4,type:[4,5,6,8,9],type_statu:4,typeddict:[3,6],typedef:6,typevar:4,typic:[0,4],typing_extens:6,un:4,under:4,underlin:5,uninstanti:4,union:4,unit:5,unknown:4,unknown_command:4,unobserv:4,unpredict:0,unspecifi:6,until:4,up:[1,4,6],updat:[0,3,4,6,8],update_compon:4,update_temperatur:4,upon:[0,4,8],us:[2,4,7,9,10],usag:3,user:[0,3],utf:[4,8],util:10,valid:4,valid_component_id:4,valu:[3,4,6,7,8],valueerror:4,vari:[6,8],variou:[4,8],venv:9,version:[4,5],versiongit:4,via:[4,10],wa:[1,4],wai:3,wakeup:[0,4,6,7,8,10],walk:[6,8],want:[2,5],we:[1,5,6,7,8,10],welcom:5,well:[6,7,8],were:[1,4],what:2,when:[1,4,5,6,7,8,10],whenev:[3,4],where:[1,4,8],whether:[1,4],whicb:4,which:[0,3,4,6,7,8,10],whilst:[1,4],who:[1,2],why:3,wire:[0,1,3,4,7],wiring_struct:4,wish:[6,7,8],within:4,without:4,woken:4,work:[3,4,9],world:[0,4],would:[1,2],wrap:[0,4],wrapper:4,yaml:[4,6,7,8,10],yet:4,yield:4,yield_observ:4,you:[2,4,5,9],your:5},titles:["Glossary","How component updates are ordered","How to accomplish a task","tickit","API","Contributing","Creating a Device","Creating a Simulation","Creating an Adapter","Installation Tutorial","Running a Simulation"],titleterms:{"class":[6,8],In:1,about:3,accomplish:2,across:10,ad:7,adapt:[4,8],an:[1,8],api:4,ar:1,base:4,byte_format:4,check:9,code:5,command:[4,8],command_interpret:4,compon:[1,4],componentconfig:6,compos:4,configur:[4,6,7,8],constructor:[6,8],contribut:5,core:4,creat:[6,7,8,9],cryostream:4,depth:1,determin:1,devic:[4,6,7],device_simul:4,document:[3,5],environ:9,epicsadapt:4,event_rout:4,exampl:4,explan:3,femto:4,file:[6,7,8],glossari:0,guid:3,handl:1,how:[1,2,3],incomplet:1,instal:9,intern:4,interpret:4,kafka:4,librari:9,load:4,logic:6,manag:4,master:4,modul:[6,8],multipl:10,order:1,pneumat:4,possibl:1,process:[5,10],python:9,refer:3,regex_command:4,releas:5,remote_control:4,requir:1,respons:1,run:[5,7,10],runner:4,schedul:[1,4],server:4,shutter:4,simul:[7,10],singl:10,singleton:4,sink:4,slave:4,sourc:4,state:4,state_interfac:4,statu:4,structur:3,style:5,system_simul:4,task:2,tcp:4,test:5,through:1,ticker:4,tickit:[3,4],topic_nam:4,trampolin:4,tutori:[3,9],typedef:4,updat:1,us:[6,8],util:4,version:9,virtual:9,walk:1,which:1,within:10,your:9}})