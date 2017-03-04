"""Single module to wrap command validation, security, and other business logic.

A note for the future- we're currently using Fabric under the hood, but alternatives exist such
as Ansible, spur, paramiko, or even shelling out to ssh directly. Ideally we stay with a
higher-level library and don't worry about the particulars.
"""

from __future__ import print_function

from fabric import state
from fabric.api import env, run
from fabric.tasks import execute, Task
from fabric.exceptions import NetworkError


class Error(Exception):
    """Problem performing operation on another host."""

class ConnectionError(Error):
    """Could not connect to remote host."""

class ReturnOutput(object):
    """
    The return value of `fabric.operations.run` is an
    [`_AttributeString`](https://github.com/fabric/fabric/blob/1.11.1/fabric/operations.py#L47)
    which dynamically adds attributes after execution, making testing difficult.

    To make our usecase easier, we're going to convert the output into a more formally defined
    object, which will make testing and an eventual fabric upgrade (or migration) easier.

    For future reference, as of `fabric==1.11.1`, the best place to find out what attributes are
    available is in
    [`_run_command`](https://github.com/fabric/fabric/blob/1.11.1/fabric/operations.py#L934).
    """

    def __init__(self, stdout, stderr, return_code, succeeded):
        self._stdout = stdout
        self._stderr = stderr
        self._return_code = return_code
        self._succeeded = succeeded

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr

    @property
    def return_code(self):
        return self._return_code

    @property
    def succeeded(self):
        return self._succeeded

    @property
    def failed(self):
        return not self._succeeded

    def __str__(self):
        # The %.25s format trims output to 25 characters via 'precision'
        # https://docs.python.org/2/library/stdtypes.html#string-formatting
        return '<ReturnOutput stdout: %.25s, stderr: %.25s, return_code: %d, succeeded: %s, failed:%s>' % (self._stdout,
                                                                                                           self._stderr,
                                                                                                           self._return_code,
                                                                                                           self._succeeded,
                                                                                                           self.failed)
    def __repr__(self):
        return self.__str__()


def multiprocessing_execute(hostnames, command_string, quiet=False):
    """Run a command across multiple hosts at once.

    :rtype: dictionary with hostnames as key, ReturnOutput as value
    """
    env.use_ssh_config = True
    env.parallel = True

    class CustomTask(Task):
        """Small wrapper around the `fabric` task to execute commands in parallel."""
        name = 'tools task'
        # Run on 10 hosts at a time
        pool_size = 10
        def run(self):
            try:
                fabric_output = run(command_string, warn_only=True, quiet=quiet)
            except NetworkError as error:
                return ReturnOutput('', '%s' % error, -1, False)
            return ReturnOutput(fabric_output.stdout,
                                fabric_output.stderr,
                                fabric_output.return_code,
                                fabric_output.succeeded)
    if quiet: # TODO: find a better way to override it. See https://github.com/fabric/fabric/issues/424
        state_output_running = state.output.running
        state.output.running = False
        results = execute(CustomTask(), hosts=hostnames)
        state.output.running = state_output_running
    else:
        results = execute(CustomTask(), hosts=hostnames)
    env.parallel = False
    return results


def execute_command(hostname, command_string, quiet=False):
    """Connect to an external machine, run a command, and return its status.

    This should be used to handle any necessary side effects or preparation for connection.
    """
    env.use_ssh_config = True
    env.host_string = hostname
    try:
        fabric_output = run(command_string, warn_only=True, quiet=quiet)
    except NetworkError as error:
        return ReturnOutput('', '%s' % error, -1, False)

    return ReturnOutput(fabric_output.stdout,
                        fabric_output.stderr,
                        fabric_output.return_code,
                        fabric_output.succeeded)
