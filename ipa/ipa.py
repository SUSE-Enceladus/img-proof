# -*- coding: utf-8 -*-


class TestProvider:

    def __init__(self):
        super(TestProvider, self).__init__()

    def launch_instance(self):
        raise NotImplementedError('Implement method in child classes.')

    def start_instance(self):
        raise NotImplementedError('Implement method in child classes.')

    def stop_instance(self):
        raise NotImplementedError('Implement method in child classes.')

    def terminate_instance(self):
        raise NotImplementedError('Implement method in child classes.')

    def test_image(self):
        """Run tests on image using the test configuration."""

    def load_test(self):
        """Load necessary files/scripts for the given test."""

    def run_test(self):
        """Run the given test."""

    def collect_test_results(self):
        """Gather and save results for the given test."""

    def aggregate_test_results(self):
        """Aggregate all test results and provide single output."""

    def save_test_results(self):
        """Save aggregated test results for test run."""
