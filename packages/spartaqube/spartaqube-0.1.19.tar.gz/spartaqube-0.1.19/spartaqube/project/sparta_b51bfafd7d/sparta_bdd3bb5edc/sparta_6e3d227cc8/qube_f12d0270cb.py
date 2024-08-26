_B='default'
_A=None
import io,sys,pandas as pd,json,requests
from project.sparta_b51bfafd7d.sparta_bdd3bb5edc.qube_e41187c546 import EngineBuilder
from project.sparta_b51bfafd7d.sparta_b3fc7394e9.qube_7a8ddad505 import sparta_a7bc85aeac
class JsonApiConnector(EngineBuilder):
	def __init__(self,json_url,dynamic_inputs=_A,py_code_processing=_A):super().__init__(host=_A,port=_A);self.connector=self.build_json_api(json_url=json_url,dynamic_inputs=dynamic_inputs,py_code_processing=py_code_processing);self.json_url=json_url;self.dynamic_inputs=dynamic_inputs;self.py_code_processing=py_code_processing
	def test_connection(self):
		self.error_msg_test_connection=''
		if self.dynamic_inputs is not _A:
			if len(self.dynamic_inputs)>0:
				for input_dict in self.dynamic_inputs:self.json_url=self.json_url.replace('{'+str(input_dict['input'])+'}',input_dict[_B])
		response=requests.get(self.json_url)
		if response.status_code==200:return True
		else:self.error_msg_test_connection=f"Could not establish connection with status code response: {response.status_code}";return False
	def sparta_3520202e7f(self,b_get_print_buffer=True):
		self.error_msg_test_connection=''
		if self.dynamic_inputs is not _A:
			if len(self.dynamic_inputs)>0:
				for input_dict in self.dynamic_inputs:self.json_url=self.json_url.replace('{'+str(input_dict['input'])+'}',input_dict[_B])
		print('JSON URL');print(self.json_url);response=requests.get(self.json_url)
		if response.status_code==200:
			resp=response.text;print_buffer_content=''
			if self.py_code_processing is not _A:
				try:
					self.py_code_processing=self.py_code_processing+'\nresp_preview = resp'
					if b_get_print_buffer:stdout_buffer=io.StringIO();sys.stdout=stdout_buffer;exec(self.py_code_processing,globals(),locals());print_buffer_content=stdout_buffer.getvalue();sys.stdout=sys.__stdout__
					else:exec(self.py_code_processing,globals(),locals())
					resp=eval('resp_preview')
				except Exception as e:raise Exception(e)
			return resp,print_buffer_content
		else:raise Exception(f"Could not establish connection with status code response: {response.status_code}")
	def get_json_api_dataframe(self):resp,_=self.preview_output_connector(b_get_print_buffer=False);resp=sparta_a7bc85aeac(resp);return resp