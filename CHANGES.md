v1.4.0 (2018-08-15)
===================

- Add archive management option to CLI.
  [\#83](https://github.com/SUSE/ipa/pull/83)
- openSUSE Leap requires auto import of repo keys.
  [\#98](https://github.com/SUSE/ipa/pull/98)
- Update Leap test description.
  [\#99](https://github.com/SUSE/ipa/pull/99)
- Sync tests should not raise exception.
  [\#100](https://github.com/SUSE/ipa/pull/100)
- Use the GCE service account in the launched instance.
  [\#107](https://github.com/SUSE/ipa/pull/107)
- Add serviceAccountUser role requirement for GCE.
- Rename pretty\_name to be generic value.
  [\#108](https://github.com/SUSE/ipa/pull/108)
- Use temp directory for results in tests.
  [\#109](https://github.com/SUSE/ipa/pull/109)
- Move docs to markdown for better support.
  [\#110](https://github.com/SUSE/ipa/pull/110)
- Determine provider and region from instance.
  [\#113](https://github.com/SUSE/ipa/pull/113)
- Add SLE\_15 repos.
  [\#116](https://github.com/SUSE/ipa/pull/116)
- Update GCE services test.
  [\#117](https://github.com/SUSE/ipa/pull/117)
- Rename `--ssh-private-key` option.
  [\#119](https://github.com/SUSE/ipa/pull/119)
- Add ip address option for SSH testing.
- Add SSH provider.
  [\#115](https://github.com/SUSE/ipa/pull/115)

v1.3.0 (2018-07-23)
===================

- Add ec2 tests to check billing code in metadata.
  [\#81](https://github.com/SUSE/ipa/pull/81)
- Using token normalize breaks region shortcode. Remove region
  shortcode which overlaps running instance id.
  [\#92](https://github.com/SUSE/ipa/pull/92)
- Allow new paths for history log option. when testing.
  [\#95](https://github.com/SUSE/ipa/pull/95)
- If a test dir does not exist just continue.
  [\#104](https://github.com/SUSE/ipa/pull/104)
- Update GCE setup/configuration docs.
- Move requirements to txt files.
- Raise useful exception msg if GCE service account file is invalid.
  [\#106](https://github.com/SUSE/ipa/pull/106)
- Add certifi requirement for Libcloud GCE driver.
- Update pycrypto requirement to pycryptodome.

v1.2.0 (2018-06-14)
===================

- Add SLES test to ensure root user has no password.
  [\#90](https://github.com/SUSE/ipa/pull/90)
- Fix typo in force new reg test.
- Add \--timeout cli and configuration option.
  [\#86](https://github.com/SUSE/ipa/pull/86)
- Add a test to wait on registration for on-demand instances.
  [\#87](https://github.com/SUSE/ipa/pull/87)
- Add azure tests to check billing tag in metadata.
  [\#88](https://github.com/SUSE/ipa/pull/88)
- Handle custom Azure image vhd id's.
  [\#89](https://github.com/SUSE/ipa/pull/89)

v1.1.1 (2018-05-16)
===================

- Cleanup typo in docs.
- Explicitly close SSH connections.
  [\#79](https://github.com/SUSE/ipa/pull/79)

v1.1.0 (2018-05-15)
===================

- Add requirements and external test injection with the `--inject`
  option. [\#78](https://github.com/SUSE/ipa/pull/78)
    - Adds the option to inject packages, archives and files. Also
      provides the ability to execute commands and install packages
      from an existing repository.

v1.0.0 (2018-03-30)
===================

- Tests argument is now optional.
  [\#56](https://github.com/SUSE/ipa/pull/56)
    - This allows for the use of `--no-cleanup` option to start an
      instance in the given framework.
- Add regression test to check for valid UUID on SLES instance in EC2.
  [\#57](https://github.com/SUSE/ipa/pull/57)
- Add regression test to confirm lscpu binary returns successful exit
  code. [\#58](https://github.com/SUSE/ipa/pull/58)
- Subnet option has been added to launch a new instance in the given
  network/subnet (`--subnet-id`).
  [\#59](https://github.com/SUSE/ipa/pull/59)
- Remove requirement on case with distro and provider options.
  [\#60](https://github.com/SUSE/ipa/pull/60) &
  [\#65](https://github.com/SUSE/ipa/pull/65)
- Use Testinfra run module to check hostname. System Info module was
  removed from package. [\#61](https://github.com/SUSE/ipa/pull/61)
- Migrate Azure provider to the ARM (resource manager API).
  [\#63](https://github.com/SUSE/ipa/pull/63)
- Add option to use user-data for loading SSH public key to instance
  in EC2. [\#68](https://github.com/SUSE/ipa/pull/68)
- Add delete history item option to results command.
  [\#69](https://github.com/SUSE/ipa/pull/69)
    - Split up results command into separate subcommands.

v0.5.1 (2017-12-11)
===================

- Cleanup MANIFEST.
- Fix README.

v0.5.0 (2017-12-11)
===================

- Use cpe\_name to determine SAP product in SLES tests.
- Allow EC2 testing without a config file.
- Update README overview with more info.
- Provide log\_file and results\_file in results dict.
- Other formatting and bug fixes.

v0.4.0 (2017-10-12)
===================

- Migrate EC2 provider to apache-libcloud.
- Remove vcrpy integration tests.

v0.3.0 (2017-09-20)
===================

- Add test\_dirs to args for test endpoint.
- Fix bug if test fails before sync point.
- Add SLES update infrastructure tests.
- Add command line option \--no-default-test-dirs.
- Add skipped tests to results output.
- Update man pages and and cleanup docs.

v0.2.0 (2017-09-07)
===================

- Add test suite for testing SLES images.
- Add SLES tests to MANIFEST.
- Fix change log in MANIFEST.
- Ignore SLES tests in setup.cfg.
- Fix ipa provider test, include region and platform in results dict.
- Add tests package to spec and mv to python3-ipa.spec.
- Pass region and platform to pytest for use in tests.

v0.1.3 (2017-09-05)
===================

- Check format of unit/integration tests with flake8 in tox/travis.
- Cleanup flake8 format in azure integration test.

v0.1.2 (2017-08-31)
===================

- After soft and hard reboot ensure host key has not changed.

v0.1.1 (2017-08-30)
===================

- Python3 format spec instead of Python single spec.
- Add missing requirements for GCE to spec.

v0.1.0 (2017-08-30)
===================

- Integrate GCE provider using apache-libcloud.

v0.0.5 (2017-08-29)
===================

- Explicit ignore of tests/data directory in spec file.

v0.0.4 (2017-08-29)
===================

- Account for classes and parameterized tests.

v0.0.3 (2017-08-29)
===================

- Cleanup azure unit tests.

v0.0.2 (2017-08-22)
===================

- Update Travis to build only master + tags.
- Use deault dicts in results summary.
- Clenaup error message usage.
- Add shebang to shell script.
- Use yaml safe\_load.
- Spelling fixes.
- Cleanup spec file.

v0.0.1 (2017-08-15)
===================

- Initial release.
