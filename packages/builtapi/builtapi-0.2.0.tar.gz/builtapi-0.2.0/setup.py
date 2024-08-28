# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['builtapi',
 'builtapi.api',
 'builtapi.core',
 'builtapi.core.convert',
 'builtapi.core.modules',
 'builtapi.core.schemas',
 'builtapi.core.validators']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.7.2,<0.8.0',
 'pydantic-core>=2.20.1,<3.0.0',
 'pydantic>=2.6.0,<3.0.0',
 'pytest>=8.0.0,<9.0.0',
 'requests-mock>=1.12.1,<2.0.0',
 'requests>=2.31.0,<3.0.0']

setup_kwargs = {
    'name': 'builtapi',
    'version': '0.2.0',
    'description': '',
    'long_description': "![builtapi_python.png](docs%2Fmedia%2Fbuiltapi_python.png)\n\nPython CLient for BuiltAPI service\n\nDear users, welcome to the repository with Python binding for BuiltAPI.\n\n## Basic usage example\n\n```python\nfrom builtapi.token import get_token\nfrom builtapi.api.main import BuiltAPI\n\n# Create BuiltAPI instance\ntoken = get_token(\n  username='username',\n  password='password',\n  client_id='client_id',\n  client_secret='client_secret',\n)\nclient = BuiltAPI(\n  workspace_id='workspace_id',\n  token=token,\n)\n\n# Get all entities\nentities = client.entities.list()\n\n# Get all records from entity\nrecords = client.records.list(entity_id='entity_id')\n\n# Create new record\nnew_record = client.records.create(\n  entity_id='entity_id',\n  data={\n    'field1': 'value1',\n    'field2': 'value2',\n  }\n)\n```\n\n## Brief introduction\n\nFirst you need to understand how the BuiltAPI platform works. For this purpose it will be useful to review the\nofficial documentation - [BuiltAPI documentation](https://docs.builtapi.dev/). However, to make it shorter we will describe the main building blocks of the service here:\n\n- `Workspace` - group all business entities with separate databases;\n- `Entity` - 'data capacitor' or storage. It is the basic building block in which data is stored;\n- `Record` - individual elements (rows) in an entity (database);\n- `View` - Transformation pipeline for data in an entity;\n\nThe main goal of this library is to provide a simple and convenient way to interact with the BuiltAPI service using Python.\n\n## Repository structure\n\nThis repository consists of the following key elements:\n\n- `applications` - complicated real use cases of this library;\n- `builtapi` - the core of the Python-binding library;\n- `examples` - folder with simple examples how to use this binding (see section Examples below);\n- `tests` - folder with unit and integration tests which cover the vital functionality both of the BuiltAPI platform\n  and Python binding.\n\n### Examples\n\nExamples how to use binding can be found in [examples folder](examples), for example:\n\n- [users_interaction.py](examples/users_interaction.py) - example how to send requests to Users module using latest BuiltAPI version\n- [workspaces_interaction.py](examples/workspaces_interaction.py) - example how to send requests to Workspaces module using latest BuiltAPI version\n- [entities_interaction.py](examples/entities_interaction.py) - example how to send requests to Entities module using latest BuiltAPI version\n- [entities_records_interaction.py](examples/entities_records_interaction.py) - example how to create entities, fill it with data and get data back\n\n### Applications\n\nReal use cases is presented in the [applications](applications) folder:\n\n- [dwell_density.py](applications/dwell_density.py) - merging data from three different sources and providing aggregation logic to calculate sum, mean values and others statistics\n\n## Additional information\n\nLink to the console: https://console.builtapi.dev/\n",
    'author': 'Dreamlone',
    'author_email': 'mik_sar@mail.ru',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
