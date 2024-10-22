v7.34.0(2024-10-22)
===================

- Add stack type option handling for GCE
- Handle ipv6 addresses in SMT reg test

v7.33.0(2024-10-17)
===================

- Handle ipv6 addresses in smt registration test
- Handle suma 4.x and 5.x scenarios in is_suma check
- Drop GCE SSDs by default when terminating instances

v7.32.0(2024-07-25)
===================

- Fix grow root test for terabyte drives

v7.31.0(2024-07-17)
===================

- Add option to skip hardened test

v7.30.0(2024-07-16)
===================

- Skip haveged service test in sp6+ and micro 6 images
- Handle micro 6 images in motd test. Motd header is in a new location

v7.29.8(2024-06-07)
===================

- Fix license test for 15-sp6 final license
- Fixes issue with fixtures in pytest 7.4.x

v7.29.7 (2024-05-28)
===================

- Fix tests subpackage name

v7.29.6 (2024-05-28)
===================

- Add missing python_files macro to tests subpackage in spec file

v7.29.5 (2024-05-28)
===================

- Add missing python_files macro to spec file

v7.29.4 (2024-05-24)
===================

- Add fdupes to spec build

v7.29.3 (2024-05-24)
===================

- Add python subpackages macro

v7.29.2 (2024-05-23)
===================

- Add missing biuld dependencies for wheel

v7.29.1 (2024-05-23)
===================

- Fix pytest call in spec file

v7.29.0 (2024-05-22)
===================

- Update spec build to python 3.11

v7.28.0 (2024-05-13)
===================

- Do not print btrfs mount point in grow root test commands
- Do not include var dir in grow root test calculation
  if var is mounted to the same partition as root dir

v7.27.0 (2024-05-09)
===================

- Add latest iteration of license content for SLES
- Do not search for keys if SSH connection fails with provided key+user
- Do not retry SLES hardened image test if SCAP report is already generated

v7.26.0 (2024-04-05)
===================

- Fix hardened test to handled multiple tries
- Fix hardened test to clean up swap before assertion

v7.25.0 (2024-03-28)
===================

- Add 15 SP6 repos to SLES PAYG test
- Skip vm info collection if instance fails reboot

v7.24.0 (2024-02-22)
===================

- Add instance options cli option
- Add sev-snp support for Google testing
- Add sev-snp test to SLES test suite

v7.23.0 (2024-01-25)
===================

- Enhance OpenSCAP test with logging and report generation.

v7.22.0 (2023-12-19)
===================

- Register skipinbeta marker
- Add readthedocs config file
- Handle suma payg in ec2 billing code test
- Add OpenSCAP test for hardened images
- Update sles 15 sp3 repos list

v7.21.0 (2023-10-03)
===================

- Exits on certain ssh key exceptions
- Includes a CLI parameter to include cpu-options in AWS instances

v7.20.0 (2023-05-03)
===================

- Includes VARIANT-ID 'sles-sap-hardened' in test_sles_ec2_billing_code
- Remove the Legacy module from the repo test

v7.19.0 (2023-02-27)
===================

- Add SLES 15 SP5 repos

v7.18.0 (2022-12-07)
===================

- Use full path to dmidecode in determine provider
- Skip sap motd check for hardened images
- Run dmesg as root in gce sev test
- Add a short wait period and retry checking for init system

v7.17.0 (2022-11-03)
===================

- Skip motd check in hardened images
- Fix bug when using user-data in ec2 to set ssh key

v7.16.2 (2022-10-03)
===================

- Fix Azure kernel commandline args test for arm64.

v7.16.1 (2022-08-30)
===================

- Fix exclude attr to accept any iterable.
- Exclude alsocasts str to list

v7.16.0 (2022-08-16)
===================

- Skip micro in kernel version test
- Add beta blag to skip marked tests (skipinbeta)
- Cleanup formatting errors in conftest modules
- Add option to skip test files by name

v7.15.0 (2022-07-18)
===================

- Revert to v1 api version

v7.14.0 (2022-07-11)
===================

- Add architecture option for GCE testing

v7.13.1 (2022-06-21)
===================

- Fix sles repo list for 15 SP4, remove CAP repos

v7.13.0 (2022-05-18)
===================

- Consolidate the EC2 billing code tests

v7.12.0 (2022-05-16)
===================

- Add kernel command line test for Azure
- Add role and scope to SP creation command

v7.11.0 (2022-05-10)
===================

- Add Python3 modules to 15 SP4 in repos test and remove python2
- Cleanup bugs in test results output
- Check for pretty name in motd and old format
- Add option to test shared gallery images

v7.10.0 (2022-03-30)
===================

- Add SLES 15 SP4 repos to SLES test suite
- Remove definitions for non existing products
- Remove SLES 11 repo configuration, SLES 11 is EOL

v7.9.1 (2022-03-16)
===================

- Fix GCE auth tests to avoid auth request

v7.9.0 (2022-03-16)
===================

- Force GCE auth to provide a useful error message with invalid credentials

v7.8.2 (2022-02-24)
===================

- Handle breaking changes in cloud-regionsrv-client to fix
  SLES registration check.

v7.8.1 (2022-02-17)
===================

- Use -v/--nofsroot option in root grow test to support btrfs
- Account for sle-micro in EC2 Dracut conf test

v7.8.0 (2022-02-09)
===================

- Fix GCE SSH key insertion
- Fix sle-micro integration
- Use strtobool locally instead of from distutils which is deprecated
- Use setup_method in unit tests instead of setup. Setup is no longer
  called before every test.
- Fix flake8 formatting error in test suite
- Update grow root test:
  + To handle sle-micro with btrfs root volume
  + To include /var partition in calculation if it exists
  + To allow for small discrepancies due to rounding errors

v7.7.0 (2022-01-21)
===================

- Add new sle_micro distro

v7.6.0 (2022-01-11)
===================

- Switch testinfra requirement to pytest plugin namespace.

v7.5.2 (2021-12-17)
===================

- Add rpm-macros to build requirements in spec.

v7.5.1 (2021-12-10)
===================

- Fix regression in ipa controller tests

v7.5.0 (2021-12-10)
===================

- Handle breaking change in Azure resource package
  [\#311](https://github.com/SUSE-Enceladus/ipa/pull/311)
- Raise exception if no region provided when using Azure CSP
  [\#312](https://github.com/SUSE-Enceladus/ipa/pull/312)
- Only do a refresh when testing Leap
  [\#316](https://github.com/SUSE-Enceladus/ipa/pull/316)

v7.4.0 (2021-09-14)
===================

- Make the SEV check more lenient
  [\#304](https://github.com/SUSE-Enceladus/ipa/pull/304)
- Fix name check when cleanup up oci network components
  [\#305](https://github.com/SUSE-Enceladus/ipa/pull/305)
- Add grow root test
  [\#306](https://github.com/SUSE-Enceladus/ipa/pull/306)
- Include the default test paths in the CLI help
  [\#308](https://github.com/SUSE-Enceladus/ipa/pull/308)

v7.3.1 (2021-06-24)
===================

- Add new SLES SAP license content string for SP3.

v7.3.0 (2021-05-26)
===================

- Add 15 SP3 repos to on-demand test.
  [\#302](https://github.com/SUSE-Enceladus/ipa/pull/302)
- Check if motd file exists before checking content.

v7.2.0 (2021-05-10)
===================

- Add new SLES license content string for SP3.

v7.1.0 (2021-05-07)
===================

- Add gvnic option to GCE provider.
  [\#298](https://github.com/SUSE-Enceladus/ipa/pull/298)
- Replace native pytest results plugin.
  [\#299](https://github.com/SUSE-Enceladus/ipa/pull/299)

v7.0.0 (2021-04-07)
===================

- Use latest SDK functions and authentication from Azure identity.
  [\#288](https://github.com/SUSE-Enceladus/ipa/pull/288)
- Update install information in docs.
  [\#289](https://github.com/SUSE-Enceladus/ipa/pull/289)
- Add vscode dir to gitignore.
  [\#291](https://github.com/SUSE-Enceladus/ipa/pull/291)
- Add case to handle sapcal in repos test.
  [\#292](https://github.com/SUSE-Enceladus/ipa/pull/292)
- Strip newline from key file if it exists.
  [\#293](https://github.com/SUSE-Enceladus/ipa/pull/293)
- Update default user for Alibaba to ali-user.
  [\#295](https://github.com/SUSE-Enceladus/ipa/pull/295)
- Use cloud config instead of bash script for user data.
  [\#296](https://github.com/SUSE-Enceladus/ipa/pull/296)
- Rename Alibaba to Aliyun.
  [\#297](https://github.com/SUSE-Enceladus/ipa/pull/297)

v6.4.0 (2021-01-15)
===================

- Split kernel command line args before compare.
  [\#283](https://github.com/SUSE-Enceladus/ipa/pull/283)
- Update the GCE services test with latest services.
  [\#284](https://github.com/SUSE-Enceladus/ipa/pull/284)
- Skip EC2 dracut config test if arch not x86_64.
  Skip EC2 dracut config test if SLES > 12SP5.
  [\#287](https://github.com/SUSE-Enceladus/ipa/pull/287)

v6.3.1 (2020-11-20)
===================

- Enable the test for multipath being disabled by default.
  [\#276](https://github.com/SUSE-Enceladus/ipa/pull/276)
- Log pytest exceptions for debugging.
  [\#277](https://github.com/SUSE-Enceladus/ipa/pull/277)
- Add test to ensure we have a dracut configuration.
  [\#278](https://github.com/SUSE-Enceladus/ipa/pull/278)
- Update, cleanup docs.
  [\#279](https://github.com/SUSE-Enceladus/ipa/pull/279)
- Fix typos in dracut test.
  [\#280](https://github.com/SUSE-Enceladus/ipa/pull/280)
- Match instance type list with mash.
  [\#281](https://github.com/SUSE-Enceladus/ipa/pull/281)
- Bump ec2 net test timeout.
  [\#282](https://github.com/SUSE-Enceladus/ipa/pull/282)

v6.3.0 (2020-11-03)
===================

- Fix SEV CAPABLE function.
  [\#273](https://github.com/SUSE-Enceladus/ipa/pull/273)
- Add snippets on Alibaba creds.
  [\#274](https://github.com/SUSE-Enceladus/ipa/pull/274)
- Eager fail for failed registration.
  [\#275](https://github.com/SUSE-Enceladus/ipa/pull/275)

v6.2.0 (2020-10-19)
===================

- Integrate Alibaba cloud class.
  [\#268](https://github.com/SUSE-Enceladus/ipa/pull/268)
  [\#269](https://github.com/SUSE-Enceladus/ipa/pull/269)
- Add SEV_CAPABLE flag in GCE instances.
  [\#270](https://github.com/SUSE-Enceladus/ipa/pull/270)
- Add additional info option for ec2 provider.
  [\#271](https://github.com/SUSE-Enceladus/ipa/pull/271)
- Test that multipath is dsiabled on the kernel command line.
  [\#272](https://github.com/SUSE-Enceladus/ipa/pull/272)

v6.1.0 (2020-09-30)
===================

- Handle Google HttpError explicitly.
  [\#265](https://github.com/SUSE-Enceladus/ipa/pull/265)
- Disable all pytest stdout capturing with -s option.
- Catch unhandled exceptions from pytest.
  [\#266](https://github.com/SUSE-Enceladus/ipa/pull/266)
- SAP has live-patching enabled
  [\#267](https://github.com/SUSE-Enceladus/ipa/pull/267)

v6.0.0 (2020-08-18)
===================

- Use post init workflow.
  [\#261](https://github.com/SUSE-Enceladus/ipa/pull/261)
- Break connection loop on certain exceptions.
  [\#262](https://github.com/SUSE-Enceladus/ipa/pull/262)
- Create empty console log method for ssh backend.
  [\#263](https://github.com/SUSE-Enceladus/ipa/pull/263)

v5.3.0 (2020-08-06)
===================

- Update getting started doc.
  [\#255](https://github.com/SUSE-Enceladus/ipa/pull/255)
- Update list of services for GCE and Azure images.
  [\#256](https://github.com/SUSE-Enceladus/ipa/pull/256)
- Allow no default test dirs in config.
  [\#257](https://github.com/SUSE-Enceladus/ipa/pull/257)
- Add prefix name option.
  [\#258](https://github.com/SUSE-Enceladus/ipa/pull/258)
- Run every test case individually.
  [\#259](https://github.com/SUSE-Enceladus/ipa/pull/259)

v5.2.0 (2020-06-07)
===================

- Allow any calls to API to provide their own logger instance.
  [\#250](https://github.com/SUSE-Enceladus/ipa/pull/250)
- Remove file handler for logging which causes message duplication.
  [\#251](https://github.com/SUSE-Enceladus/ipa/pull/251)
- Add Red Hat family distro module and Fedora distro module.
  [\#252](https://github.com/SUSE-Enceladus/ipa/pull/252)

v5.1.0 (2020-06-01)
===================

- Ensure region hint is in cloudregister log.
  [\#244](https://github.com/SUSE-Enceladus/ipa/pull/244)
-  Enable guest attrs by default in GCE.
  [\#245](https://github.com/SUSE-Enceladus/ipa/pull/245)
- Fix build requires in test clause in spec.
  [\#246](https://github.com/SUSE-Enceladus/ipa/pull/246)
- Integrate OCI console history method.
  [\#247](https://github.com/SUSE-Enceladus/ipa/pull/247)
- Pull disk source name not devicename.
  [\#248](https://github.com/SUSE-Enceladus/ipa/pull/248)
- Pull public ssh key from file.
  [\#249](https://github.com/SUSE-Enceladus/ipa/pull/249)

v5.0.0 (2020-04-21)
===================

- Migrate GCE to Google API.
  [\#242](https://github.com/SUSE-Enceladus/ipa/pull/242)

v4.8.1 (2020-03-10)
===================

- Fix bug and check both CLI output versions for single
  and double quote.

v4.8.0 (2020-03-10)
===================

- Attempt to cleanup instance if error during launch.
  [\#234](https://github.com/SUSE-Enceladus/ipa/pull/234)
- Add distro refresh option.
  [\#235](https://github.com/SUSE-Enceladus/ipa/pull/235)
- Use systemctl to check guestregister status.
  [\#236](https://github.com/SUSE-Enceladus/ipa/pull/236)
- Log only to base logger.
  [\#239](https://github.com/SUSE-Enceladus/ipa/pull/239)
- Handle HPC on-demand repos.
  [\#240](https://github.com/SUSE-Enceladus/ipa/pull/240)
- Add timestamp to file log handler.
  [\#241](https://github.com/SUSE-Enceladus/ipa/pull/241)

v4.7.0 (2020-02-18)
===================

- Cleanup spec file.
  [\#230](https://github.com/SUSE-Enceladus/ipa/pull/230)
- Add list of 15-SP2 repos to SLES on-demand repo test.
  [\#232](https://github.com/SUSE-Enceladus/ipa/pull/232)

v4.6.0 (2020-1-21)
===================

- Edit sap license test to handle 12SP5.
  [\#226](https://github.com/SUSE-Enceladus/ipa/pull/226)
- Skip kernel test if not a latest image version.
  [\#227](https://github.com/SUSE-Enceladus/ipa/pull/227)
- Generate man pages in build with click-man.
  [\#228](https://github.com/SUSE-Enceladus/ipa/pull/228)
- Implement Oracle cloud class (oci).
  [\#229](https://github.com/SUSE-Enceladus/ipa/pull/229)

v4.5.1 (2019-10-28)
===================

- Use sudo with registration command for non root users.
  [\#225](https://github.com/SUSE-Enceladus/ipa/pull/225)

v4.5.0 (2019-10-25)
===================

- Use registerutils functions to check registration.
  [\#224](https://github.com/SUSE-Enceladus/ipa/pull/224)

v4.4.0 (2019-10-14)
===================

- Remove region filter from smt registration test.
  [\#223](https://github.com/SUSE-Enceladus/ipa/pull/223)

v4.3.1 (2019-08-21)
===================

- Remove azure regions map from smt reg test.
- Update get\_smt\_servers to not filter type in smt reg
  test.
  [\#221](https://github.com/SUSE-Enceladus/ipa/pull/221)

v4.3.0 (2019-08-13)
===================

- Move get user data method to base class.
  [\#215](https://github.com/SUSE-Enceladus/ipa/pull/215)
- Update sles repos test for rmt.
  [\#217](https://github.com/SUSE-Enceladus/ipa/pull/217)
- Add repos for sles12-sp5.
  [\#218](https://github.com/SUSE-Enceladus/ipa/pull/218)
- Print serial console output to log.
  [\#219](https://github.com/SUSE-Enceladus/ipa/pull/219)
- Add case for checking kernel config version.
  [\#220](https://github.com/SUSE-Enceladus/ipa/pull/220)

v4.2.1 (2019-07-18)
===================

- Consider location restrictions retryable in GCE.
  [\#212](https://github.com/SUSE-Enceladus/ipa/pull/212)
- Wait longer on soft reboot.
  [\#213](https://github.com/SUSE-Enceladus/ipa/pull/213)
- Add test for azure launch exception.
  [\#213](https://github.com/SUSE-Enceladus/ipa/pull/213)

v4.2.0 (2019-07-16)
===================

- Use the "baseproduct" link as indicator of the SLES product.
  [\#208](https://github.com/SUSE-Enceladus/ipa/pull/208)
- Remove support for py3.4.
  [\#210](https://github.com/SUSE-Enceladus/ipa/pull/210)
- Indicate retryable error (GCE only).
  [\#211](https://github.com/SUSE-Enceladus/ipa/pull/211)

v4.1.1 (2019-07-01)
===================

- Run reboot in background process.
  [\#207](https://github.com/SUSE-Enceladus/ipa/pull/207)
- Make tox env work with python3.7.
  [\#209](https://github.com/SUSE-Enceladus/ipa/pull/209)

v4.1.0 (2019-06-06)
===================

- Make license test fixture generic.
  [\#206](https://github.com/SUSE-Enceladus/ipa/pull/206)

v4.0.0 (2019-05-30)
===================

- Clear ssh cache at start of module.
  [\#196](https://github.com/SUSE-Enceladus/ipa/pull/196)
- Move set_distro to beginning of method.
  [\#199](https://github.com/SUSE-Enceladus/ipa/pull/199)
- Attempt to cleanup instance on ssh fail.
  [\#200](https://github.com/SUSE-Enceladus/ipa/pull/200)
- Echo log file if results file provided.
  [\#201](https://github.com/SUSE-Enceladus/ipa/pull/201)
- Rename ipa to img-proof.
  [\#202](https://github.com/SUSE-Enceladus/ipa/pull/202)

v3.3.1 (2019-05-07)
===================

- Add stable release repository for ipa.
  [\#189](https://github.com/SUSE-Enceladus/ipa/pull/189)
- Check default dirs exist in ipa list.
  [\#191](https://github.com/SUSE-Enceladus/ipa/pull/191)
- Add retry on ec2 image download.
  [\#192](https://github.com/SUSE-Enceladus/ipa/pull/192)

v3.3.0 (2019-03-26)
===================

- Cast timeout to integer.
  [\#184](https://github.com/SUSE-Enceladus/ipa/pull/184)
- Fix Azure service test on SLES 11.
  [\#185](https://github.com/SUSE-Enceladus/ipa/pull/185)
- Combine libcloud class with GCE.
  [\#186](https://github.com/SUSE-Enceladus/ipa/pull/186)
- Cleanup gce tests.
  [\#187](https://github.com/SUSE-Enceladus/ipa/pull/187)
- Rename ipa cloud test module.
  [\#188](https://github.com/SUSE-Enceladus/ipa/pull/188)

v3.2.1 (2019-03-15)
===================

- EC2 instances may have ipv6 addresses set to None.
  [\#183](https://github.com/SUSE-Enceladus/ipa/pull/183)

v3.2.0 (2019-03-14)
===================

- Add repos for 15sp1.
  [\#174](https://github.com/SUSE-Enceladus/ipa/pull/174)
- Use pytest fail instead of raise exception.
  [\#175](https://github.com/SUSE-Enceladus/ipa/pull/175)
- Make ec2 network test more expressive.
  [\#177](https://github.com/SUSE-Enceladus/ipa/pull/177)
- Add replacefiles option to zypper update.
  [\#181](https://github.com/SUSE-Enceladus/ipa/pull/181)
- Use format string for motd check.
  [\#182](https://github.com/SUSE-Enceladus/ipa/pull/182)

v3.1.1 (2019-02-28)
===================

- Add new license directories for SLES test.
  [\#173](https://github.com/SUSE-Enceladus/ipa/pull/173)

v3.1.0 (2019-02-22)
===================

- Check for ssh key file separately in ec2.
  [\#169](https://github.com/SUSE-Enceladus/ipa/pull/169)
- Add specific commands for GCE credentials setup.
  [\#170](https://github.com/SUSE-Enceladus/ipa/pull/170)
- SSH user key in ec2utils config is user.
  [\#171](https://github.com/SUSE-Enceladus/ipa/pull/171)
- Accept availability zones as ec2 region.
  [\#172](https://github.com/SUSE-Enceladus/ipa/pull/172)

v3.0.0 (2019-02-04)
===================

- Add missing security group id to ssh class.
  [\#161](https://github.com/SUSE-Enceladus/ipa/pull/161)
- Add collect vm info to gce class super call.
  [\#162](https://github.com/SUSE-Enceladus/ipa/pull/162)
- Cleanup ini config handling.
  [\#163](https://github.com/SUSE-Enceladus/ipa/pull/163)
- Allow use of ipa config for provider options.
  [\#164](https://github.com/SUSE-Enceladus/ipa/pull/164)
- Compare wait on instance states as lowercase.
  [\#165](https://github.com/SUSE-Enceladus/ipa/pull/165)
- Remove references to provider with cloud, cloud frameworks.
  [\#166](https://github.com/SUSE-Enceladus/ipa/pull/166)
- Don't pass unused args to cloud classes.
  [\#167](https://github.com/SUSE-Enceladus/ipa/pull/167)

v2.6.0 (2019-01-04)
===================

- Remove duplication when logging.
  [\#156](https://github.com/SUSE-Enceladus/ipa/pull/156)
- Allow azure instance to start in existing subnet.
  [\#158](https://github.com/SUSE-Enceladus/ipa/pull/158)
- Treat uuid always lowercase.
  [\#159](https://github.com/SUSE-Enceladus/ipa/pull/159)
- Use base provider waiter method.
  [\#160](https://github.com/SUSE-Enceladus/ipa/pull/160)

v2.5.0 (2018-12-11)
===================

- Add note on installing SLES test suite.
  [\#148](https://github.com/SUSE-Enceladus/ipa/pull/148)
- Add option allowing collect info about VM in cloud.
  [\#149](https://github.com/SUSE-Enceladus/ipa/pull/149)
- With running instance don't cleanup.
  [\#152](https://github.com/SUSE-Enceladus/ipa/pull/152)
- Systemd cleanup in distro.
  [\#153](https://github.com/SUSE-Enceladus/ipa/pull/153)
- Process pytest errors in results.
  [\#154](https://github.com/SUSE-Enceladus/ipa/pull/154)
- Switch EC2 provider back to boto3.
  [\#155](https://github.com/SUSE-Enceladus/ipa/pull/155)

v2.4.0 (2018-12-06)
===================

- Auto deploy IPA package in pypi on new tag release.
  [\#139](https://github.com/SUSE-Enceladus/ipa/pull/139)
- Add security-group-id option for ec2 provider.
  [\#151](https://github.com/SUSE-Enceladus/ipa/pull/151)

v2.3.0 (2018-11-09)
===================

- Move docs to sphinx.
  [\#141](https://github.com/SUSE-Enceladus/ipa/pull/141)
- Update python version support.
  [\#142](https://github.com/SUSE-Enceladus/ipa/pull/142)
- Allow ipa to run without config file.
  [\#137](https://github.com/SUSE-Enceladus/ipa/pull/137)
- No need for gpg auto import keys.
  [\#144](https://github.com/SUSE-Enceladus/ipa/pull/144)
- Add --name option to az creds example.
  [\#145](https://github.com/SUSE-Enceladus/ipa/pull/145)
- Explicit validation of GCE region input.
  [\#146](https://github.com/SUSE-Enceladus/ipa/pull/146)
- Update license tests for content changes.
  [\#147](https://github.com/SUSE-Enceladus/ipa/pull/147)

v2.2.0 (2018-10-31)
===================

- Add network test for sles in ec2.
  [\#134](https://github.com/SUSE-Enceladus/ipa/pull/134)
- Remove azure billing tag test.
  [\#136](https://github.com/SUSE-Enceladus/ipa/pull/136)
- Fix typo in azure services test name.
  [\#138](https://github.com/SUSE-Enceladus/ipa/pull/138)
- Add python3.7 to CI testing.
  [\#140](https://github.com/SUSE-Enceladus/ipa/pull/140)
- Add repos for 12SP4 in conftest
  [\#143](https://github.com/SUSE-Enceladus/ipa/pull/143)

v2.1.0 (2018-10-01)
===================

- Add IPA logo.
- Cloud init services are one-shot in EC2.
  [\#131](https://github.com/SUSE-Enceladus/ipa/pull/131)
- Add azure accelerated networking option.
  [\#132](https://github.com/SUSE-Enceladus/ipa/pull/132)
- Curl directly for placement in metadata when determining
  region.
  [\#133](https://github.com/SUSE-Enceladus/ipa/pull/133)

v2.0.1 (2018-09-12)
===================

- Update project status to stable.
- Update root pass test to work with SLE11.
  [\#125](https://github.com/SUSE-Enceladus/ipa/pull/125)
- Account for sysvinit in SLE11.
  [\#126](https://github.com/SUSE-Enceladus/ipa/pull/126)
- Convert azure regions from id to display format.
  [\#127](https://github.com/SUSE-Enceladus/ipa/pull/127)
- Update repo URL to correct org.
  [\#128](https://github.com/SUSE-Enceladus/ipa/pull/128)

v2.0.0 (2018-08-15)
===================

- Remove deprecated --ssh-private-key option.
  Option was renamed to --ssh-private-key-file.

v1.4.0 (2018-08-15)
===================

- Add archive management option to CLI.
  [\#83](https://github.com/SUSE-Enceladus/ipa/pull/83)
- openSUSE Leap requires auto import of repo keys.
  [\#98](https://github.com/SUSE-Enceladus/ipa/pull/98)
- Update Leap test description.
  [\#99](https://github.com/SUSE-Enceladus/ipa/pull/99)
- Sync tests should not raise exception.
  [\#100](https://github.com/SUSE-Enceladus/ipa/pull/100)
- Use the GCE service account in the launched instance.
  [\#107](https://github.com/SUSE-Enceladus/ipa/pull/107)
- Add serviceAccountUser role requirement for GCE.
- Rename pretty\_name to be generic value.
  [\#108](https://github.com/SUSE-Enceladus/ipa/pull/108)
- Use temp directory for results in tests.
  [\#109](https://github.com/SUSE-Enceladus/ipa/pull/109)
- Move docs to markdown for better support.
  [\#110](https://github.com/SUSE-Enceladus/ipa/pull/110)
- Determine provider and region from instance.
  [\#113](https://github.com/SUSE-Enceladus/ipa/pull/113)
- Add SLE\_15 repos.
  [\#116](https://github.com/SUSE-Enceladus/ipa/pull/116)
- Update GCE services test.
  [\#117](https://github.com/SUSE-Enceladus/ipa/pull/117)
- Rename `--ssh-private-key` option.
  [\#119](https://github.com/SUSE-Enceladus/ipa/pull/119)
- Add ip address option for SSH testing.
- Add SSH provider.
  [\#115](https://github.com/SUSE-Enceladus/ipa/pull/115)

v1.3.0 (2018-07-23)
===================

- Add ec2 tests to check billing code in metadata.
  [\#81](https://github.com/SUSE-Enceladus/ipa/pull/81)
- Using token normalize breaks region shortcode. Remove region
  shortcode which overlaps running instance id.
  [\#92](https://github.com/SUSE-Enceladus/ipa/pull/92)
- Allow new paths for history log option. when testing.
  [\#95](https://github.com/SUSE-Enceladus/ipa/pull/95)
- If a test dir does not exist just continue.
  [\#104](https://github.com/SUSE-Enceladus/ipa/pull/104)
- Update GCE setup/configuration docs.
- Move requirements to txt files.
- Raise useful exception msg if GCE service account file is invalid.
  [\#106](https://github.com/SUSE-Enceladus/ipa/pull/106)
- Add certifi requirement for Libcloud GCE driver.
- Update pycrypto requirement to pycryptodome.

v1.2.0 (2018-06-14)
===================

- Add SLES test to ensure root user has no password.
  [\#90](https://github.com/SUSE-Enceladus/ipa/pull/90)
- Fix typo in force new reg test.
- Add \--timeout cli and configuration option.
  [\#86](https://github.com/SUSE-Enceladus/ipa/pull/86)
- Add a test to wait on registration for on-demand instances.
  [\#87](https://github.com/SUSE-Enceladus/ipa/pull/87)
- Add azure tests to check billing tag in metadata.
  [\#88](https://github.com/SUSE-Enceladus/ipa/pull/88)
- Handle custom Azure image vhd id's.
  [\#89](https://github.com/SUSE-Enceladus/ipa/pull/89)

v1.1.1 (2018-05-16)
===================

- Cleanup typo in docs.
- Explicitly close SSH connections.
  [\#79](https://github.com/SUSE-Enceladus/ipa/pull/79)

v1.1.0 (2018-05-15)
===================

- Add requirements and external test injection with the `--inject`
  option. [\#78](https://github.com/SUSE-Enceladus/ipa/pull/78)
    - Adds the option to inject packages, archives and files. Also
      provides the ability to execute commands and install packages
      from an existing repository.

v1.0.0 (2018-03-30)
===================

- Tests argument is now optional.
  [\#56](https://github.com/SUSE-Enceladus/ipa/pull/56)
    - This allows for the use of `--no-cleanup` option to start an
      instance in the given framework.
- Add regression test to check for valid UUID on SLES instance in EC2.
  [\#57](https://github.com/SUSE-Enceladus/ipa/pull/57)
- Add regression test to confirm lscpu binary returns successful exit
  code. [\#58](https://github.com/SUSE-Enceladus/ipa/pull/58)
- Subnet option has been added to launch a new instance in the given
  network/subnet (`--subnet-id`).
  [\#59](https://github.com/SUSE-Enceladus/ipa/pull/59)
- Remove requirement on case with distro and provider options.
  [\#60](https://github.com/SUSE-Enceladus/ipa/pull/60) &
  [\#65](https://github.com/SUSE-Enceladus/ipa/pull/65)
- Use Testinfra run module to check hostname. System Info module was
  removed from package. [\#61](https://github.com/SUSE-Enceladus/ipa/pull/61)
- Migrate Azure provider to the ARM (resource manager API).
  [\#63](https://github.com/SUSE-Enceladus/ipa/pull/63)
- Add option to use user-data for loading SSH public key to instance
  in EC2. [\#68](https://github.com/SUSE-Enceladus/ipa/pull/68)
- Add delete history item option to results command.
  [\#69](https://github.com/SUSE-Enceladus/ipa/pull/69)
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
