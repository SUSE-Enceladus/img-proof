========
Examples
========

The following are a few use case examples for **img-proof**. The test suite
in use is provided by the Open Build Service `python3-img-proof-test`.
For more information on installing the test suite see the :doc:`tests`
documentation.

Launch & Test a new instance in Azure
=====================================

The first step to testing an image is determining the image ID. The image
ID will look different for all cloud frameworks. See the examples below for
the three supported clouds:

- Azure: SUSE:SLES:12-SP3:latest
- EC2:   ami-0f7c9a39e20a9adea
- GCE:   sles-12-sp3-v20180814

To launch and test a new instance of a given image the `--image-id` or
`-i` option is required.

The next step is to determine what tests you want to run against the instance.
To see what test modules are available there is an `img-proof list` command. You
can invoke the command with `-v` option to see a verbose list of all tests
within each module.

.. code-block:: console

   $ img-proof list
   test_sles_guestregister
   test_sles_haveged
   test_sles_hostname
   test_sles_install_migration
   test_sles_lscpu
   test_sles_motd
   test_sles_repos
   test_sles

By default img-proof looks in two directories for test modules:

- ~/img_proof/tests/
- /usr/share/lib/img_proof/tests/

This can be overridden with the `--test-dirs` option. The option is expected
to be a comma separated list of absolute test directory paths.

Once you have a set of tests installed and chosen you can run img-proof against an
image. For this example we will test the Azure image and only run the base
SLES tests:

.. code-block:: console

   $ img-proof test azure -i suse:sles-15-sp2-byos:gen2:Latest \
     --distro sles test_sles

   Starting instance
   Testing soft reboot
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_motd.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_license.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_root_pass.py
   Testing hard reboot
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_hostname.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_haveged.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_lscpu.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_kernel_version.py
   Running test /share/lib/img_proof/tests/SLES/test_sles_multipath_off.py
   PASSED tests=10|pass=10|fail=0|error=0

You can see that test_sles is a "test description". It's a YAML file that contains
an ordered list of test modules to run. To find out more info on tests and test
structure see the :doc:`tests` documentation.

By default img-proof will launch the instance with a small instance size. For Azure
this is `Standard_B1ms`. Also, if the tests pass the instance will be
terminated and resource group will be cleaned up in Azure. This behavior can
be modified with the `--cleanup` and `--no-cleanup` options.

There are many options available when running an img-proof test which can be listed
via the help command:

.. code-block:: console

   $ img-proof test --help

Test an existing instance in Azure
==================================

If you want to run tests on an existing instance you can provide the
`--running-instance-id` or `-r` option. All options and tests that are
available for a new instance can be run against an existing one. When
testing a running instance the instance will not be terminated if the
tests pass. To terminate an already running instance the `--cleanup`
option is required.

The running instance ID is different based on cloud provider. It
can either be an ID or a name. For Azure the instance "ID" is an instance
name.

.. code-block:: console

   $ img-proof test azure --running-instance-id img-proof-zephl \
     --distro sles test_sles

   Testing soft reboot
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_motd.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_license.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_root_pass.py
   Testing hard reboot
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_hostname.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_haveged.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_lscpu.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_kernel_version.py
   Running test /share/lib/img_proof/tests/SLES/test_sles_multipath_off.py
   PASSED tests=10|pass=10|fail=0|error=0

After running a test you can view the results using the results command:

.. code-block:: console

   $ img-proof results show
   PASSED tests=10|pass=10|skip=0|fail=0|error=0

More information can be displayed by providing the verbose option `-v`:

.. code-block:: console

   $ img-proof results show -v
   FAILED tests=10|pass=10|skip=0|fail=0|error=0

   platform: azure
   distro: sles
   image: 10.0.0.1
   timestamp: 20201118151743
   log_file: /home/{user}/img_proof/results/azure/suse:sles-15-sp2-byos:gen2:Latest/img-proof-zephl/20201118151743.log
   results_file: /home/{user}/img_proof/results/azure/suse:sles-15-sp2-byos:gen2:Latest/img-proof-zephl/20201118151743.results
   region: southcentralus
   instance: img-proof-zephl

   test_soft_reboot PASSED
   test_sles_motd::test_sles_motd[paramiko://10.0.0.1] PASSED
   test_sles_license::test_sles_license[paramiko://10.0.0.1] PASSED
   test_sles_root_pass::test_sles_root_pass[paramiko://10.0.0.1] PASSED
   test_hard_reboot PASSED
   test_sles_hostname::test_sles_hostname[paramiko://10.0.0.1] PASSED
   test_sles_haveged::test_sles_haveged[paramiko://10.0.0.1] PASSED
   test_sles_lscpu::test_sles_lscpu[paramiko://10.0.0.1] PASSED
   test_sles_kernel_version::test_sles_kernel_version[paramiko://10.0.0.1] PASSED
   test_sles_multipath_off::test_sles_multipath_off[paramiko://10.0.0.1] PASSED

Testing with SSH only
=====================

If you have a running instance that has an accessible IP address you can run
img-proof tests without the use of a cloud provider framework. This means the
instance must have an SSH key pair setup. Without cloud framework credentials
the instance cannot be terminated after tests and must be running. There is
also no way to do a framework reboot test.

Instead of providing the image `--image-id` or instance
`--running-instance-id` you are required to provide an IP address
`--ip-address`.

.. code-block:: console

   $ img-proof test ssh --ip-address 10.0.0.1 \
     --distro sles test_sles

   Testing soft reboot
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_motd.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_license.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_root_pass.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_hostname.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_haveged.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_lscpu.py
   Running test /usr/share/lib/img_proof/tests/SLES/test_sles_kernel_version.py
   Running test /share/lib/img_proof/tests/SLES/test_sles_multipath_off.py
   PASSED tests=10|pass=10|fail=0|error=0
