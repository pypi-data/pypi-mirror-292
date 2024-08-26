_P='{\n        "showTicks": True,\n        "renderTicks": {\n            "showTicks": True,\n            "divisions": 10,\n        },\n        "zones":{"bInvertColor":True,"bMiddleColor":True,"colorLeft":"#20FF86","colorMiddle":"#F8E61C","colorRight":"#FF0000","maxHeightDeviation":5,"tiltZones":55}\n    }'
_O="{'min': 0, 'max': 100, 'value': 34}"
_N='gauge1'
_M='12px'
_L='center'
_K='blue'
_J='font-size'
_I='text-align'
_H='color'
_G='from spartaqube import Spartaqube as Spartaqube'
_F='from api.spartaqube import Spartaqube as Spartaqube'
_E='Example to plot a simple gauge with gauge.js'
_D='code'
_C='sub_description'
_B='description'
_A='title'
import json
from django.conf import settings as conf_settings
def sparta_f168ee99a4(type=_N):
	if conf_settings.IS_DEV:B=_F
	else:B=_G
	D={_H:_K,_I:_L,_J:_M};A=_O;C='{\n        "showTicks": True,\n        "renderTicks": {\n            "showTicks": True,\n            "divisions": 10,\n        },\n    }';return[{_A:f"{type.capitalize()}",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  title=['{type} example'], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with custom options",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  title=['{type} example'], 
  options={C},
  height=500
)
plot_example"""}]
def sparta_4ce15b1565():return sparta_f168ee99a4(type=_N)
def sparta_bf00666eff():return sparta_f168ee99a4(type='gauge2')
def sparta_f29b040ca3():
	type='gauge3'
	if conf_settings.IS_DEV:B=_F
	else:B=_G
	D={_H:_K,_I:_L,_J:_M};A={'min':0,'max':100,'value':34};C=_P;return[{_A:f"{type.capitalize()}",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  title=['Gauge3 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom zones",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  gauge_zones=[0,10,30,80,100],
  title=['Gauge3 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom zones and labels",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A},
  gauge_zones=[0,10,30,80,100],
  gauge_zones_labels=['label 0','label 10','label 30','label 80','label 100'],
  title=['Gauge3 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom options",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A},
  gauge_zones=[0,10,30,80,100],
  title=['Gauge3 example'], 
  options={C},
  height=500
)
plot_example"""}]
def sparta_776f74fe0e():
	type='gauge4'
	if conf_settings.IS_DEV:B=_F
	else:B=_G
	D={_H:_K,_I:_L,_J:_M};A=_O;C=_P;return[{_A:f"{type.capitalize()}",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  title=['Gauge4 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom zones",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A}, 
  gauge_zones=[0,10,30,80,100],
  title=['Gauge4 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom zones and labels",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A},
  gauge_zones=[0,10,30,80,100],
  gauge_zones_labels=['label 0','label 10','label 30','label 80','label 100'],
  title=['Gauge4 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom zones, labels and heights",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A},
  gauge_zones=[0,10,30,80,100],
  gauge_zones_labels=['label 0','label 10','label 30','label 80','label 100'],
  gauge_zones_height=[2,6,10,14,18],
  title=['Gauge4 example'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom options",_B:_E,_C:'',_D:f"""{B}
spartaqube_obj = Spartaqube()
gauge_data_dict = {A}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={A},
  gauge_zones=[0,10,30,80,100],
  title=['Gauge4 example'], 
  options={C},
  height=500
)
plot_example"""}]