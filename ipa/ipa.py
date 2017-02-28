# -*- coding: utf-8 -*-


class IpaProvider(object):
    def __init__():
        super(IpaProvider, self).__init__()

    def _config(self):
        """Setup configuration."""

    def _create_ssh_config(self):
        """Create ssh config as named temporary file."""

    def _close_ssh_config(self):
        """Unlink temporary file."""

    def get_instance(self):
        raise NotImplementedError('Implement method in child classes.')

    def launch_instance(self):
        raise NotImplementedError('Implement method in child classes.')

    def reboot_instance(self):
        raise NotImplementedError('Implement method in child classes.')

    def start_instance(self):
        raise NotImplementedError('Implement method in child classes.')

    def stop_instance(self):
        raise NotImplementedError('Implement method in child classes.')

    def terminate_instance(self):
        raise NotImplementedError('Implement method in child classes.')

    def test_image(self):
        """The entry point for testing an image.

        This method will perform the following steps:
          - launch_instance() # If a host is passed in this is skipped
          - system_reboot()
          - system_update()
          - reboot_instance()
          - run_tests()
          - terminate_instance() # Optional depends on test results and -c flag
        """

    def run_tests(self):
        """Runs the test suite on the image."""

    def system_reboot(self):
        """Performs a system reboot."""

    def system_update(self):
        """Updates the instace based on OS type.

        E.g. for SUSE `zypper up`
        """

