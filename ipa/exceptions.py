# -*- coding: utf-8 -*-


class PrufeException(Exception):
    """Generic exception for the Prufe package."""


class ImageNotFoundException(PrufeException):
    """Exception for image not found on cloud provider."""


class InstanceException(PrufeException):
    """Generic exception for the overridden instance methods."""


class LaunchInstanceException(PrufeException):
    """An exception occurs when launching an instance."""


class StartInstanceException(PrufeException):
    """An exception occurs when starting an instance."""


class StopInstanceException(PrufeException):
    """An exception occurs when stopping an instance."""


class TerminateInstanceException(PrufeException):
    """An exception occurs when terminating an instance."""


class TestException(PrufeException):
    """Generic exception for errors during tests."""


class LoadTestException(TestException):
    """An exception occurs during load of test."""


class RunTestException(TestException):
    """An exception occurs during test run."""


class TestResultsException(TestException):
    """An exception occurs collecting or aggregating test results."""
