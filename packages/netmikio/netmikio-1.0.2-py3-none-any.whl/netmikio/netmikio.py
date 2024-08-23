import asyncio
from netmiko import ConnectHandler as CH, NetmikoTimeoutException, NetMikoAuthenticationException

class aioConnectHandler:
    """
    Asynchronous SSH handler based on Netmiko for managing network devices.

    This class provides an asynchronous interface for establishing SSH connections and sending commands
    to network devices using the Netmiko library. It supports connection management and command execution
    in an asynchronous context using asyncio.

    Methods:
        send_com(command): send a standard command to the device.
        send_conf_set(commands): send a set of commands to device.
        send_com_timing(command): send a command with timing to the device.
    
    Exceptions:
        TimeoutException: Raised if the SSH connection times out.
        AuthenticationException: Raised if authentication to the SSH server fails.
    """

    class TimeoutException(Exception):
        pass

    class AuthenticationException(Exception):
        pass

    def __init__(self, **host):
        self.host = host
        self.connection = None

    async def __aenter__(self):
        loop = asyncio.get_event_loop()
        try:
            self.connection = await loop.run_in_executor(None, lambda: CH(**self.host))
            return self
        
        except NetmikoTimeoutException:
            raise aioConnectHandler.TimeoutException(f'Connection timed out.')
        
        except NetMikoAuthenticationException:
            raise aioConnectHandler.AuthenticationException(f'Authentication failed.')

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.connection.disconnect)

    async def send_com(self, command):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.connection.send_command(command))
    
    async def send_conf_set(self, commands):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.connection.send_config_set(commands))
        
    async def send_com_timing(self, command):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.connection.send_command_timing(command))
    
