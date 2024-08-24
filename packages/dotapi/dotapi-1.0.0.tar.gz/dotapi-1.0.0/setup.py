# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dotapi',
 'dotapi._extras',
 'dotapi._utils',
 'dotapi.cli',
 'dotapi.cli._api',
 'dotapi.cli._api.chat',
 'dotapi.cli._tools',
 'dotapi.lib',
 'dotapi.lib.streaming',
 'dotapi.resources',
 'dotapi.resources.audio',
 'dotapi.resources.beta',
 'dotapi.resources.beta.threads',
 'dotapi.resources.beta.threads.runs',
 'dotapi.resources.beta.vector_stores',
 'dotapi.resources.chat',
 'dotapi.resources.fine_tuning',
 'dotapi.resources.fine_tuning.jobs',
 'dotapi.types',
 'dotapi.types.audio',
 'dotapi.types.beta',
 'dotapi.types.beta.chat',
 'dotapi.types.beta.threads',
 'dotapi.types.beta.threads.runs',
 'dotapi.types.beta.vector_stores',
 'dotapi.types.chat',
 'dotapi.types.fine_tuning',
 'dotapi.types.fine_tuning.jobs',
 'dotapi.types.shared',
 'dotapi.types.shared_params']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.5.0,<4.0.0',
 'distro>=1.7.0,<2.0.0',
 'httpx>=0.23.0,<0.24.0',
 'pydantic>=1.9.0,<2.0.0',
 'sniffio',
 'tqdm>=4,<5',
 'typing-extensions>=4.7,<5.0']

extras_require = \
{':python_version < "3.8"': ['cached-property']}

entry_points = \
{'console_scripts': ['dotapi = dotapi.cli:main']}

setup_kwargs = {
    'name': 'dotapi',
    'version': '1.0.0',
    'description': 'The official Python library for the dotapi API',
    'long_description': '# DotAPI Python API library\n\nThe DotAPI Python library provides convenient access to the DotAPI REST API from any Python 3.7+\napplication.\n\n## Installation\n\n```sh\npip install dotapi\n```\n\n## Usage\n\n```python\nfrom dotapi import OpenAI\n\nclient = OpenAI(\n    api_key="My DotAPI Key",  # defaults to os.environ.get("DOTROUTER_API_KEY")\n)\n\nchat_completion = client.chat.completions.create(\n    messages=[\n        {\n            "role": "user",\n            "content": "Say this is a test",\n        }\n    ]\n    # No need to pass model, dotapi will decide the best model for your query!\n)\n```',
    'author': 'DotAgent',
    'author_email': 'contact@dotagent.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/dotagent/dotapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
