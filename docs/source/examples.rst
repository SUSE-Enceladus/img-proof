========
Examples
========

The following examples are based on testing a SLES image using
the test suite provided from the Open Build Service. For more information
on installing the test suite see the :doc:`tests` documentation.

Launch & Test a new instance
============================

To launch and test a new instance of an image provide the `--image-id` or
`-i` option.

The image ID will look different for all cloud frameworks. See the examples
below for the three supported clouds:

- Azure: SUSE:SLES:12-SP3:latest
- EC2:   ami-0f7c9a39e20a9adea
- GCE:   sles-12-sp3-v20180814

To see what test modules are available there is an `ipa list` command. You
can invoke the command with `-v` option to see a verbose list of all tests
within each module.

.. code-block:: console

   $ ipa list
   test_sles_guestregister
   test_sles_haveged
   test_sles_hostname
   test_sles_install_migration
   test_sles_lscpu
   test_sles_motd
   test_sles_repos
   test_sles

Once you have a set of tests installed and chosen you can run ipa against an
image. For this example we will test the Azure image and only run the base
SLES tests:

.. code-block:: console

   $ ipa test azure -i SUSE:SLES:12-SP3:latest \
     --region southcentralus \
     --service-account-file /path/to/service_account.json \
     --ssh-private-key-file /path/to/private_key_file \
     --distro sles test_sles

   Starting instance
   Running tests /home/{user}/ipa/tests/test_sles.py
   PASSED tests=1|pass=1|fail=0|error=0

By default ipa will launch the instance with a small instance size. For Azure
this is `Standard_B1ms`. Also, if the tests pass the instance will be
terminated and resource group will be cleaned up in Azure. This behavior can
be modified with the `--cleanup` and `--no-cleanup` options.

There are many options available when running an ipa test which can be listed
via the help command:

.. code-block:: console

   $ ipa test --help

Test an existing instance
=========================

If you want to run tests on an existing instance you can provide the
`--running-instance-id` or `-r` option. All options and tests that are
available for a new instance can be run against an existing one. When
testing a running instance the instance will not be terminated when the
tests pass.

.. code-block:: console

   $ ipa test azure --running-instance-id "an-existing-instance-id" \
     --region southcentralus \
     --service-account-file /path/to/service_account.json \
     --ssh-private-key-file /path/to/private_key_file \
     --distro sles test_sles

   Running tests /home/{user}/ipa/tests/test_sles.py
   PASSED tests=1|pass=1|fail=0|error=0

After running a test you can view the results using the results command:

.. code-block:: console

   $ ipa results show
   PASSED tests=1|pass=1|skip=0|fail=0|error=0

More information can be displayed by providing the verbose option `-v`:

.. code-block:: console

   $ ipa results show 1 -v
   PASSED tests=1|pass=1|skip=0|fail=0|error=0

   platform: azure
   region: southcentralus
   distro: sles
   image: SUSE:SLES:12-sp3:Latest
   instance: azure-ipa-test-kntgp
   timestamp: 20180925170409
   log_file: /home/{user}/ipa/results/azure/SUSE:SLES:12-sp3:Latest/azure-ipa-test-kntgp/20180925170409.log
   results_file: /home/{user}/ipa/results/azure/SUSE:SLES:12-sp3:Latest/azure-ipa-test-kntgp/20180925170409.results

   test_sles::test_sles[paramiko://10.0.0.1] PASSED

Testing with SSH only
=====================

If you have a running instance that has an accessible IP address you can run
ipa tests without the use of a cloud provider framework. This means the
instance must have an SSH key pair setup. Without cloud framework credentials
the instance cannot be terminated after tests and must be running.

Instead of providing the image `--image-id` or instance
`--running-instance-id` you are required to provide an IP address
`--ip-address`.

.. code-block:: console

   $ ipa test ssh --ip-address 10.0.0.1 \
     --ssh-private-key-file /path/to/private_key_file \
     --distro sles test_sles

   Running tests /home/{user}/ipa/tests/test_sles.py
   PASSED tests=1|pass=1|fail=0|error=0
