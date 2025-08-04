=====
Usage
=====

img-proof provides two entry points, a command line interface and a controller class
that can be used directly from Python code.

CLI
---

The command line interface is written using the `Click`_ package. The API
documentation can be found at :doc:`api`.

.. _Click: https://click.palletsprojects.com/en/7.x/

Verbosity
~~~~~~~~~

As seen in the example the CLI output verbosity can be controlled via options:

**\-\-debug**
    Display debug level logging to console. Including full stack trace
    if there is an exception.

**\-\-verbose**
    (Default) Display logging info to console.

**\-\-quiet**
    Silence logging information on test run.


Instance Options
~~~~~~~~~~~~~~~~

The **instance-option** arguments provide a way to enable instance options
that will be activated when launching instances. This is a multi-option
value. To provide multiple options in a single command split each option
into a separate argument. An example for tests in Google:

.. code-block:: console

   img-proof test gce ... \
     --instance-option SEV_SNP_CAPABLE \
     --instance-option GVNIC

The Google instance options includes the guest os feature flags. See
https://cloud.google.com/compute/docs/images/create-custom#guest-os-features
for more details. Also, the ip stack state can be set via instance
options. As seen above an example for Google looks like:

.. code-block:: console

   img-proof test gce ... \
     --instance-option SEV_SNP_CAPABLE
     --instance-option STACK_STATE=IPV4_IPV6

The Amazon options are the different options available when running the
run instances command. These can be found at
https://docs.aws.amazon.com/cli/latest/reference/ec2/run-instances.html.

To provide an instance option for testing in Amazon the type of option
and the key/val are provided in the following format: "OptType=key.val".
Example usage to enable SEV SNP looks like:

.. code-block:: console

   img-proof test ec2 ... \
     --instance-option CpuOptions=AmdSevSnp.enabled


Where the key is derived from the CLI reference page provided above. In
this case the AWS CLI option is --cpu-options which becomes "CpuOptions".
"AmdSevSnp" is the key and the value is "enabled".

Cleanup
~~~~~~~

By default the instance will be terminated if all tests pass. If a test
fails the instance will remain running for debugging purposes. This
behavior can be configured with the ``--cleanup`` and ``--no-cleanup``
flags.

**\-\-cleanup**
    Instance will always be terminated.

**\-\-no-cleanup**
    Instance will always remain running.

ANSI Style
~~~~~~~~~~

By default the command line output will be colored. To disable color
output use the ``--no-color`` option.

Early Exit
~~~~~~~~~~

The early exit option will stop the test run on the first failure.
``--early-exit`` is passed to Pytest as ``-x``.

See `Pytest docs`_ for more info.

.. _Pytest docs: https://docs.pytest.org/en/latest/usage.html#stopping-after-the-first-or-n-failures

Requirements and external test injection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the ``--inject`` option; packages, archives and files can be
injected on the test instance. This also provides the ability to install
packages in an existing repository and run commands on the test
instance.

The following sections may be provided in a YAML style config
file. Each section can be a single item or a list of items. All files
are copied and extracted to the default SSH location for the test
instance. This is generally the user’s home directory.

**inject_packages**
    an rpm path or list of rpm paths which will be copied and installed on
    the test instance.

**inject_archives**
    an archive or list of archives which will be copied and extracted on the
    test instance.

**inject_files**
    a file path or list of file paths which will be copied to the test
    instance.

**execute**
    a command or list of commands to run on the test instance.

**install**
    a package name or list of package names to install from an existing repo
    on the test instance.

The order of processing for the sections is as follows:

#. inject_packages
#. inject_archives
#. inject_files
#. execute
#. install

**Example**
^^^^^^^^^^^

**testing_injection.yaml.**

.. code-block:: yaml

   inject_packages: /home/user/test.noarch.rpm
   inject_archives: /home/user/test.tar.xz
   inject_files: /home/user/test.py
   install:
     - python3
     - python3-Django
   execute: python test.py

.. code-block:: console

   > img-proof test ... --inject testing_injection.yaml

Code
----

**img-proof** can also be imported and invoked directly in Python 3 code through
the controller class. It is installed as a Python site package and can be
imported as follows:

.. code-block:: python3

   from img_proof.ipa_controller import test_image

   status, results = test_image(
       cloud_framework,
       access_key_id,
       ...
       storage_container,
       tests
   )

See :doc:`modules/img_proof.ipa_controller` for specific methods that can be
invoked.
