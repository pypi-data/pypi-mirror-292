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
    'version': '0.2.1',
    'description': '',
    'long_description': '![builtapi_python.png](https://builtapipythonimage.s3.eu-west-1.amazonaws.com/builtapi_python.png?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMSJHMEUCICAXCxs%2BTPMsKkqbLtfhPdFykX%2BiivP5Mi4%2FT1%2FXR6KNAiEAkaneayQIvos6IRkqQWx%2BsouXdLhc%2FPNyduPt5wbRYwQqgQMIGBACGgw3MzIxNTg3NjY4MjgiDCdyWWC6uJCqzUKGqSreAvW7c3kLSkvGlpqmLjzFeKuCWpp2DR7xp8%2BhWW1fls6TfOa3iIKVWMU9MdHbCzMmvrPe28P4iTtPwVbFNL27XQRd5HDlUqebk8lfXC1R7y60JjJc%2FkXux4tePJTU1xgmRCVqFFb2OTplNS9ZC55GISIQABfKnw52DVvGMvmcrqjpdUWnIQaP4jfNuqvzA0jxRmnJIx8%2BV%2BSMXFkUI77td6QeIc%2BFYhtXGFAGQQzd6fv%2BHv1R3KSom6UcRdmmKgjxRpy1DWi72KZplkYvtzm9XeDWYgdpfmbgU387M%2Fivb7sfh5afZHjRVcBpy1R%2FHWr8e9GAjqAJNuVWzSLwAEABbhivzLXiGEiAg2gWsHCbnsbGsp%2F23g612o8HjCTA8DVbFr7wqbL9ur8MlScsSA3EmbE66Na9MEwod89skUYvfadDPRa%2B8%2Ffyl%2FvtuQ7ya1CaBY8%2FLzxgbX79z%2Blwcg9SMOjDt7YGOrMCdoFHzV40v68E4E1YXxV2R%2FmB%2BdBbGp7KszFaxr%2BOsTAgUqIQOAYr81reCsKRniJWff4ZpPEkkQaTy5U9s4Zlwd1H%2BhXZkGqpIdqBjXizI44wfJLTadviMHgJQ3ZDD%2Fv7Z4QYEsKyHCRsD9DPV4hL%2FDR8bGy1WPIOYEAsaLPMKXMjbBGmANnunWG%2BGMOJ7pnTYkpx56dhGQPdVXgDWLxoPeXad4oamu%2Bt2NIoDgSOZJuaSRj%2FkvGK98IgYn%2FMziSFvqD7%2Fx8LnGrh7xaIB%2B51ofOpIiet1lE6ayJaDGjHhL%2Bp%2FzTH7vXMEYOMgXgse1fAZfsnxUrmpt%2Fa1%2FW1gOoBTi4fl%2BwsVjRgkePriL9C2Z%2FNwOoVg2PZoanE5sOOmKeLuUBV%2BxbRaiJtRyqY9ZbzPuBL3Q%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240827T142711Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIA2U6AQF3WLVDWFT4M%2F20240827%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=d029f884b57b02a145a4a944ec391b7c50e4a4d28d41c3ab87b9ba830a88403a)\n\n# Quick Start\n\nBuiltAPI Python Client is a library that allows you to interact with the BuiltAPI platform. This quick start guide will help you get started with setting up and using the client.\n\n## Installation\n\nTo install the BuiltAPI Python Client, you can use pip:\n\n```bash\npip install builtapi\n```\n\n## Basic Example\n\nHere\'s a basic example to help you get started with the BuiltAPI Python Client.\n\n### Step 1: Import Necessary Modules\n\nFirst, import the necessary modules from the BuiltAPI library:\n\n```python\nfrom builtapi.token import get_token\nfrom builtapi.api.main import BuiltAPI\n```\n\n### Step 2: Get Authentication Token\n\nGet authentication token using your credentials\n\n```python\ntoken = get_token(\n  username=\'your_username\',\n  password=\'your_password\',\n  client_id=\'your_client_id\',\n  client_secret=\'your_client_secret\',\n)\n```\n\nAll the parameters are required, but can be define in environment variables:\n\n| Environment Variable            | Description                                    | Default Value                                   |\n| ------------------------------- | ---------------------------------------------- | ----------------------------------------------- |\n| `BUILTAPI_CLIENT_ID`            | The client ID for authentication               | None                                            |\n| `BUILTAPI_CLIENT_SECRET`        | The client secret for authentication           | None                                            |\n| `BUILTAPI_CLIENT_USER`          | The username for authentication                | None                                            |\n| `BUILTAPI_CLIENT_PASSWORD`      | The password for authentication                | None                                            |\n| `BUILTAPI_AUDIENCE`             | The audience for the token request             | `https://gateway.builtapi.dev`                  |\n| `BUILTAPI_GATEWAY_URL`          | The URL for the BuiltAPI gateway               | `https://gateway.builtapi.dev`                  |\n| `BUILTAPI_TOKEN_URL`            | The URL for obtaining the authentication token | `https://builtapi-dev.eu.auth0.com/oauth/token` |\n| `BUILTAPI_DEFAULT_WORKSPACE_ID` | The default workspace ID to use for the client | None                                            |\n\n#### Detailed Descriptions\n\n- **BUILTAPI_CLIENT_ID**: The client ID provided by BuiltAPI for accessing the API.\n- **BUILTAPI_CLIENT_SECRET**: The client secret associated with your client ID.\n- **BUILTAPI_CLIENT_USER**: Your BuiltAPI username.\n- **BUILTAPI_CLIENT_PASSWORD**: Your BuiltAPI password.\n- **BUILTAPI_AUDIENCE**: The audience parameter used for the token request. This is optional and defaults to `https://gateway.builtapi.dev`.\n- **BUILTAPI_GATEWAY_URL**: The URL for the BuiltAPI gateway. This is optional and defaults to `https://gateway.builtapi.dev`.\n- **BUILTAPI_TOKEN_URL**: The URL for obtaining the authentication token. This is optional and defaults to `https://builtapi-dev.eu.auth0.com/oauth/token`.\n\n### Step 3: Initialize BuiltAPI Client\n\nInitialize the BuiltAPI client with your workspace ID and the authentication token:\n\n```python\nclient = BuiltAPI(\n  workspace_id=\'your_workspace_id\',\n  token=token,\n)\n```\n\nIf you set all BUILTAPI*CLIENT*\\* environment variables, you can initialize the client without token:\n\n```python\nclient = BuilAPI(workspace_id=\'your_workspace_id\')\n```\n\nIf you set BUILTAPI_DEFAULT_WORKSPACE_ID environment variable, you can initialize the client without workspace_id:\n\n```python\nclient = BuiltAPI()\n```\n\n### Step 4: Interact with the API\n\nNow you can interact with the BuiltAPI using the client. Here are a few examples:\n\n```python\n# Get current entities for workspace\nentities = built_api_client.entities.list()\nprint(f"\\nSuccessfully got entities list: {entities}")\n\n# Create new regular entity\ncreated_entity = built_api_client.entities.create(name=\'entity-test\')\n\nprint(f\'\\nSuccessfully created new entity with ID {created_entity.id} and name {created_entity.name}\')\n\ncreated_entity_by_id = built_api_client.entities.oneById(created_entity.id)\nprint(f"\\nSuccessfully got created entity by ID: {created_entity_by_id}")\n\n# Now delete this entity\ndeleted_entity = built_api_client.entities.remove(created_entity.id)\nprint(f\'\\nSuccessfully deleted recently created entity with ID {deleted_entity.id}\')\n```\n\nConclusion\nThis guide provides a quick overview of how to set up and use the BuiltAPI Python Client. You can now start interacting with the BuiltAPI platform using the Python Client library. For more advanced usage and API references, refer to the [Advanced Usage](./python/advanced) and [API Reference] (./python/api) sections.\n\n## Additional information\n\nLink to the console: https://docs.builtapi.dev/python/quick_start\n',
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
