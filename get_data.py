import requests
# USE env var SCALE_API_KEY =
params = {
  "project_id": "6250c22ae00b890025224286",
  "status": "completed",
  "limit": "100",
  "project_name": "traffic_light_labelling",
  
}
response = requests.request(
  "GET",
  url="https://api.scale.com/v1/tasks",
  params=params,
  headers={
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}",
  },
)
print(response.json())

import json
with open("data.json", "w") as f: 
    json.dump(response.json(), f) 
"""
{'docs': [{'task_id': '6526eb2365f4f43fdc857211', 'created_at': '2023-10-11T18:36:21.350Z', 'appsheetProjectId': None, 'customerId': '5f
10b47ae6306e05d23078e4', 'completed_at': '2023-10-11T18:37:33.660Z', 'type': 'imageannotation', 'status': 'completed', 'instruction': 'D
raw a polygon around any traffic lights in the image if they exist.', 'params': {'attachment': 'http://i.imgur.com/3Cpje3l.jpg', 'attach
ment_type': 'image', 'annotation_attributes': {'traffic_light_status': {'type': 'category', 'description': 'What color is the traffic li
ght?', 'choices': ['Red', 'Yellow', 'Green', 'Cannot tell'], 'allow_multiple': False}}, 'geometries': {'box': {'objects_to_annotate': ['
Traffic lights'], 'min_width': 0, 'min_height': 0, 'examples': []}}, 'with_labels': True}, 'is_test': False, 'urgency': 'standard', 'met
adata': {}, 'processed_attachments': [], 'project': 'Traffic Light Detection', 'priority': 0, 'postProcessingResults': {}, 'taxonomyVers
ion': '6452f71af688c720a035d407', 'response': {'links': [], 'annotations': [{'label': 'Traffic lights', 'attributes': {'traffic_light_st
atus': 'Green'}, 'uuid': '84c31b07-73b6-4832-9adf-34936a424a9b', 'left': 1484, 'top': 871, 'height': 257, 'width': 93, 'type': 'box'}, {
'label': 'Traffic lights', 'attributes': {'traffic_light_status': 'Green'}, 'uuid': '53650a92-bf7e-483f-a087-ea3bd6c88d5f', 'left': 1928
, 'top': 941, 'height': 198, 'width': 105, 'type': 'box'}, {'label': 'Traffic lights', 'attributes': {'traffic_light_status': 'Green'}, 
'uuid': '09d90861-a82b-460f-ba1f-af198740f8a5', 'left': 3014, 'top': 1309, 'height': 210, 'width': 105, 'type': 'box'}, {'label': 'Traff
ic lights', 'attributes': {'traffic_light_status': 'Cannot tell'}, 'uuid': 'd045c8d5-70ba-49cf-b785-a2d08f1449cf', 'left': 2862, 'top': 
1303, 'height': 234, 'width': 111, 'type': 'box'}], 'global_attributes': {}, 'is_customer_fix': False}, 'project_param_version': 0, 'pro
jectId': '60cb720bf95b6d003baaee6e', 'updated_at': '2024-11-12T19:46:03.121Z', 'work_started': True, 'isProcessed': True}], 'total': 24,
 'offset': 0, 'limit': 1, 'has_more': True, 'next_token': 'eyJpZCI6IjY1MjZlYjIzNjVmNGY0M2ZkYzg1NzIxMSIsImNyZWF0ZWRfYXQiOiIyMDIzLTEwLTExV
DE4OjM2OjIxLjM1MFoifQ=='}
"""
