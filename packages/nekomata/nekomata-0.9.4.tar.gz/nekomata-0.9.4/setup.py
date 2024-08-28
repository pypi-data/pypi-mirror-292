# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['neko',
 'neko._annotations',
 'neko._annotations..ipynb_checkpoints',
 'neko._methods',
 'neko._methods..ipynb_checkpoints',
 'neko._outputs',
 'neko._visual',
 'neko.core',
 'neko.data',
 'neko.inputs',
 'neko.inputs._db']

package_data = \
{'': ['*']}

install_requires = \
['graphviz',
 'jupyterlab',
 'networkx',
 'notebook',
 'pandas',
 'pycurl',
 'toml',
 'unipressed',
 'yfiles_jupyter_graphs']

setup_kwargs = {
    'name': 'nekomata',
    'version': '0.9.4',
    'description': 'Package to extract, visualize, convert and study interactions from database into executable activity flow based model',
    'long_description': "==================\nNeKo\n==================\n\n.. image:: https://github.com/sysbio-curie/Neko/actions/workflows/build.yaml/badge.svg\n   :target: https://github.com/sysbio-curie/Neko/actions/workflows/build.yaml\n   :alt: Tests\n\n.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg\n   :target: https://sysbio-curie.github.io/Neko/\n   :alt: Documentation\n\nNeKo: Network Konstructor\n-------------------------------------------------------------------\n\nNeko is a Python package for extracting, visualizing, converting, and studying interactions from databases into executable activity flow-based models. It's built on top of `Omnipath <https://github.com/saezlab/omnipath>`_, `Pypath <https://github.com/saezlab/pypath>`_, and `Atopo <https://github.com/druglogics/atopo>`_.\n\n**Note**: Neko is currently in development and approaching its final stages. It is not yet available on PyPI.\n\nFeatures\n--------\n\n- Network creation and manipulation\n- Connection of nodes and subnetworks\n- Gene-to-phenotype mapping\n- Network visualization\n- Interaction database integration\n\nInstallation\n------------\n\n`NeKo` is still in its alpha version. You can install it from PyPI and also install the necessary external dependencies.\n\n1. **Install `NeKo` from PyPI**:\n\n   First, install the main package from PyPI (nekomata, do not confuse with pip install neko or pip install pyneko, those are other packages):\n\n   .. code-block:: bash\n\n       pip install nekomata\n\n2. **Install External Dependencies**:\n\n   `NeKo` requires some external dependencies that are not available on PyPI. To install these dependencies, run:\n\n   .. code-block:: bash\n\n       pip install -r https://raw.githubusercontent.com/sysbio-curie/Neko/requirements.txt\n\nThis two-step process will install both the core `NeKo` package and its external dependencies.\n\nInstallation from Source\n------------------------\n\nFor the latest development version, you can still clone the repository and install directly from the source:\n\n.. code-block:: bash\n\n    git clone https://github.com/sysbio-curie/Neko.git\n    cd Neko\n    pip install .\n    pip install -r requirements.txt\n\nThis will give you the latest version of `NeKo` (not officially released, so be aware there could be some bugs) along with the necessary external dependencies.\n\n\nDocumentation\n-------------\n\nFor full documentation, including API reference and detailed tutorials, visit our `GitHub Pages documentation <https://sysbio-curie.github.io/Neko/>`_.\n\nJupyter Notebooks\n-----------------\n\nWe provide a comprehensive set of Jupyter notebooks that offer a detailed and user-friendly explanation of the package. These notebooks cover all modules of NeKo and provide a complete overview of how to use the package:\n\n\n1) Usage\n2) Build network using user-defined resources\n3) Stepwise connection: a focus on the INE algorithm\n4) Connect to upstream components\n5) Build network based on kinase-phosphosite interactions\n6) Connect to downstream Gene Ontology terms.\n7) Map tissue expression\n8) Network comparison\n9) Re-creating famous pathways from SIGNOR and WIKIPATHWAYS using NeKo\n\n\nYou can find these notebooks in the `notebooks` directory of the repository.\n\nAcknowledgements\n----------------\n\nThis project is a collaborative effort with Dénes Turei and Asmund Flobak.\n\nCurrent contributors: Marco Ruscone, Eirini Tsirvouli, Andrea Checcoli, Dénes Turei.\n\nversion 0.9.4\n--------------\n\n- Network creation and manipulation: The package allows for the creation of a network of nodes and edges, with various methods for enrichment analysis. This includes adding and removing nodes and edges, loading a network from a SIF (Simple Interaction Format) file, and adding paths to the edge list of the network.\n- Database integration: The package provides methods to integrate interactions from databases such as Omnipath, Signor, HURI and others. The user can also integrate personal resource to mine for interactions.\n- Database translation: The package provides methods to convert the identifiers of a database storing edges list, into Uniprot.\n- Connection of nodes: The package provides several methods to connect nodes in the network. This includes connecting all nodes, connecting a subgroup of nodes, connecting all nodes of a network object, and connecting subcomponents of a network object.\n- Connection of genes to phenotype: The package provides a method to connect genes to a phenotype based on provided parameters. This includes retrieving phenotype markers, identifying unique Uniprot genes, and connecting them to the network. There is also an option to compress the network by substituting specified genes with the phenotype name.\n",
    'author': 'Marco Ruscone',
    'author_email': 'marco.ruscone@curie.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sysbio-curie/Neko',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
