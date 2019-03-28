===============
Getting Started
===============

Installation
============

openSUSE package
----------------

Perform the following commands as root for development version:

.. code-block:: console

   $ zypper ar http://download.opensuse.org/repositories/Cloud:/Tools/<distribution>
   $ zypper refresh
   $ zypper in python3-ipa

Perform the following commands as root for stable release:

.. code-block:: console

   $ zypper ar http://download.opensuse.org/repositories/Cloud:/Tools:/CI/<distribution>
   $ zypper refresh
   $ zypper in python3-ipa

PyPI
----

.. code-block:: console

   $ pip install python3-ipa

Development
-----------

Install the latest development version from GitHub:

.. code-block:: console

   $ pip install git+https://github.com/SUSE-Enceladus/ipa.git

Branch
------

Install a specific branch from GitHub:

.. code-block:: console

   $ pip install git+https://github.com/SUSE-Enceladus/ipa.git@{branch/release}

See `PyPI
docs <https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support>`__
for more information on vcs support.

Requirements
============

-  apache-libcloud
-  azure-common
-  azure-mgmt-compute
-  azure-mgmt-network
-  azure-mgmt-resource
-  certifi
-  Click
-  cryptography
-  paramiko
-  pycryptodome
-  pytest
-  PyYaml
-  testinfra

Configuration
=============

IPA Config
----------

The **IPA** configuration file is ini format ~/.config/ipa/config.
This can be used for any configuration value including cloud framework
specific values.

To override the default configuration location the CLI option ``-C`` or
``--config`` is available.

The ipa section is required. The cloud framework sections are optional and
would be [{cloud_framework}]. For example, the [ec2] section in the following
file.

.. code-block:: ini

   [ipa]
   tests=~/ipa/tests/
   results=~/ipa/results/

   [ec2]
   region=us-west-1

There are multiple ways to provide configuration values when using
**IPA**. All options are available via command line and the configuration
file. Also, for certain clouds **IPA** will read cloud specific
config files.

All command line options which have a format such as ``--ssh-user`` can be
placed in config with underscores. E.g. ``--ssh-user`` would be ssh_user in
the config file.

The precedence for values is as follows:

command line -> cloud config -> ipa config -> defaults

The command line arguments if provided will be used over all other values.

Azure Config
------------

The Azure provider class has no additional config file. Options should be
placed into the **IPA** config file.

EC2 Config
----------

For testing EC2 instances **IPA** will look for the ec2utils configuration
file located at ~/.ec2utils.conf.

See
`ec2utils <https://github.com/SUSE-Enceladus/Enceladus/tree/master/ec2utils>`__
for an example configuration file.

To override the EC2 config location the CLI option,
``--cloud-config`` is available.

GCE Config
----------

The GCE  cloud class has no additional config file. Options should be
placed into the **IPA** config file.

SSH Config
----------

The SSH cloud class has no additional config file. Options should be
placed into the **IPA** config file.

Credentials
===========

Azure
-----

Azure uses service principals for authentication. A service principal
(service account) json file is required to use the Azure cloud via
file based authentication. It is critical the json file is generated with
the endpoint URLs for SDK authentication.

To create the file you will need the `Azure CLI`_.

.. _Azure CLI: https://docs.microsoft.com/en-us/cli/azure/?view=azure-cli-latest

The following command will generate the necessary json file:

.. code-block:: console
    
   $ az ad sp create-for-rbac --sdk-auth --name "{name}" > mycredentials.json

See `Azure docs`_ for more info on creating a service principal json file.

.. _Azure docs: https://docs.microsoft.com/en-us/python/azure/python-sdk-azure-authenticate?view=azure-python#mgmt-auth-file

EC2
---

The EC2 credentials are a ``--secret-access-key`` and ``--access-key-id``.
These can be from a root account but it's sugessted to use IAM accounts to
control role based access.

See `EC2 docs`_ for more information on setting up IAM accounts.

.. _EC2 docs: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html

GCE
---

GCE uses service accounts for file based authentication. The service account is
required to have the following roles:

* Compute Instance Admin (v1) Role
  (`roles/compute.instanceAdmin.v1 <https://cloud.google.com/compute/docs/access/iam>`__)
* Service Account User Role
  (`roles/iam.serviceAccountUser <https://cloud.google.com/compute/docs/access/iam>`__)

Additionally the file must be JSON format and contain a private key.

The following steps will create a service account with gcloud and gsutil:

.. code-block:: console

   $ gcloud --project={project-id} iam service-accounts create {service-account-id}
   $ gcloud --project={project-id} iam service-accounts keys create {service_account-id}-key.json --iam-account {service-account-id}@{project-id}.iam.gserviceaccount.com
   $ gcloud projects add-iam-policy-binding {project-id} --member serviceAccount:{service-account-id}@{project-id}.iam.gserviceaccount.com --role roles/compute.instanceAdmin.v1
   $ gcloud projects add-iam-policy-binding {project-id} --member serviceAccount:{service-account-id}@{project-id}.iam.gserviceaccount.com --role roles/iam.serviceAccountUser

The json file generated by the second command "{service_account-id}-key.json"
is used for GCE authentication.

.. code-block:: console

   $ ipa test gce ... --service-account-file {service_account-id}-key.json

Or you can follow the
`Libcloud
docs <http://libcloud.readthedocs.io/en/latest/compute/drivers/gce.html#service-account>`__
or `Google
docs <https://cloud.google.com/iam/docs/creating-managing-service-accounts>`__.

For more information on updating an existing service account:

-  Create a new JSON private key:
   `creating-managing-service-account-keys <https://cloud.google.com/iam/docs/creating-managing-service-account-keys>`__
-  Granting roles:
   `granting-roles-to-service-accounts <https://cloud.google.com/iam/docs/granting-roles-to-service-accounts>`__

SSH
---

Requires no cloud credentials to test instances. SSH user, SSH
private key can be placed in SSH section of config. The instance to be
tested must be running.
