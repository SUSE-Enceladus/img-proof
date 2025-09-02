===============
Getting Started
===============

Installation
============

SUSE package
------------

**SLES 15**

Ensure you have properly registered SLES then perform the following
commands as root for SLES 15:

.. code-block:: console

   $ SUSEConnect -p sle-module-public-cloud/15.#/x86_64
   $ zypper ar https://download.opensuse.org/repositories/Cloud:Tools:CI/SLE_15_SP#/Cloud:Tools:CI.repo
   $ zypper refresh
   $ zypper in python-img-proof

Replace # with the service pack you are using. Currently support exists for SP5+.

**openSUSE Tumbleweed**

Perform the following commands as root for Tumbleweed:

.. code-block:: console

   $ zypper ar https://download.opensuse.org/repositories/Cloud:Tools:CI/openSUSE_Tumbleweed/Cloud:Tools:CI.repo
   $ zypper refresh
   $ zypper in python-img-proof

.. note::  An openSUSE and SLES test suite is shipped alongside the SUSE package as python3-img-proof-tests.

SUSE test suite
---------------

To install the SLES test suite alongside the package use the following command:

.. code-block:: console

   $ zypper in python-img-proof-tests

PyPI
----

.. code-block:: console

   $ pip install img-proof

Development
-----------

Install the latest development version from GitHub:

.. code-block:: console

   $ pip install git+https://github.com/SUSE-Enceladus/img-proof.git

Branch
------

Install a specific branch from GitHub:

.. code-block:: console

   $ pip install git+https://github.com/SUSE-Enceladus/img-proof.git@{branch/release}

See `PyPI
docs <https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support>`__
for more information on vcs support.

Configuration
=============

img-proof Config
----------------

The **img-proof** configuration file is ini format ~/.config/img_proof/config.
This can be used for any configuration value including cloud framework
specific values.

To override the default configuration location the CLI option ``-C`` or
``--config`` is available.

The config file can have multiple sections. The default section is [img_proof]
and each cloud framework can have its own section such as [{cloud_framework}].
A config file with an [ec2] section may look like the following:

.. code-block:: ini

   [img_proof]
   test_dirs = /custom/tests/path/
   results_dir = /custom/results/dir/

   [ec2]
   region = us-west-1
   ssh_private_key_file = ~/.ssh/id_rsa

There are multiple ways to provide configuration values when using
**img-proof**. All options are available via command line and the configuration
file. Also, for certain clouds **img-proof** will read cloud specific
config files.

All command line options which have a format such as ``--ssh-user`` can be
placed in config with underscores. E.g. ``--ssh-user`` would be ``ssh_user`` in
the config file.

The precedence for values is as follows:

command line -> cloud config -> img-proof config -> defaults

The command line arguments if provided will be used over all other values.

Azure Config
------------

The Azure provider class has no additional config file. Options should be
placed into the **img-proof** config file.

EC2 Config
----------

For testing EC2 instances **img-proof** will look for configuration in multiple
locations. Options can be placed in the **img-proof** config file or the
ec2imgutils configuration file located at ~/.ec2utils.conf.

See
`ec2imgutils <https://github.com/SUSE-Enceladus/ec2imgutils/>`__
for an example configuration file.

To override the EC2 config location the CLI option,
``--cloud-config`` is available. In order for **img-proof** to use the ec2imgutils
config file the ``--account-name`` is required.

GCE Config
----------

The GCE  cloud class has no additional config file. Options should be
placed into the **img-proof** config file.

SSH Config
----------

The SSH cloud class has no additional config file. Options should be
placed into the **img-proof** config file.

Aliyun Config
--------------

The Aliyun cloud class has no additional config file. Options should be
placed into the **img-proof** config file.

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
    
   $ az ad sp create-for-rbac --sdk-auth --role Contributor --scopes /subscriptions/{subscription_id} --name "{name}" > mycredentials.json

Once a json credential file is generated for a service principal it can be
used to test images/instances in Azure. The ``--service-account-file``
option should point to the path to this file.

See `Azure docs`_ for more info on creating a service principal json file.

.. _Azure docs: https://docs.microsoft.com/en-us/python/azure/python-sdk-azure-authenticate?view=azure-python#mgmt-auth-file

EC2
---

The EC2 credentials are a ``--secret-access-key`` and ``--access-key-id``.
These can be from a root account but it's suggested to use IAM accounts to
control role based access.

Once you have generated secret key values these can be configured with the
``--secret-access-key`` and ``--access-key-id`` options.

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

   $ img-proof test gce ... --service-account-file {service_account-id}-key.json

Or you can follow the
`Libcloud
docs <http://libcloud.readthedocs.io/en/latest/compute/drivers/gce.html#service-account>`__
or `Google
docs <https://cloud.google.com/iam/docs/creating-managing-service-accounts>`__.

Once a json credential file is generated for a service account it can be
used to test images/instances in GCE. The ``--service-account-file``
option should point to the path to this file.

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

Aliyun
-------

The Aliyun credentials are a ``--access-secret`` and ``--access-key``.
These can be from a root account but it's suggested to use RAM accounts to
control role based access.

See `Aliyun docs`_ for more information on setting up RAM accounts.

.. _Aliyun docs: https://www.alibabacloud.com/help/doc-detail/57445.htm?spm=a3c0i.100866.8498235500.1.4d7e1e4eQPpV5V

