# netmikio
A lightweight package for asynchronous SSH-handling based on Netmiko for managing network devices.  
Built on top of [netmiko](https://github.com/ktbyers/netmiko) by Kirk Byers.

## Important Note
While netmikio provides an asynchronous interface for interacting with network devices, it is important to understand that it is not fully asynchronous. The underlying `netmiko` library is synchronous and blocking by design. This package uses asyncio to offload blocking operations to a thread pool, allowing you to manage multiple SSH connections concurrently, but the operations themselves are still blocking.

However, this package is particularly useful when you have other asynchronous tasks running in parallel, such as handling I/O operations, making API calls, or managing multiple coroutines. By integrating SSH operations within an asyncio event loop, you can still benefit from the concurrency provided by Python’s async ecosystem.

If you require true non-blocking, asynchronous SSH communication, consider using a library like `asyncssh`, which is built specifically for fully async SSH connections.

## Features
- Asynchronous interface for SSH operations using Python's asyncio with blocking operations offloaded to a thread pool.
- Short and simplified method names similar to Netmiko.
- Handles connection management, timeouts, and authentication errors in an asynchronous context.

## How Does It Work?
`netmikio` follows a similar approach to `netmiko` but introduces shorter, simplified method names:
- `send_com()`: Send a command and retrieve the output.
- `send_com_timing()`: Send a command with timing support.
- `send_conf_set()`: Send a configuration command set.

### Example: Sending the command `show power inline` to multiple devices asynchronously
```python
from netmikio import aioConnectHandler
import asyncio

async def my_func(dev):
    """
    Send a command and gather the output.
    """
    async with aioConnectHandler(**dev) as ssh:  # Connect asynchronously like in Netmiko but with 'async'.
        output = await ssh.send_com('show power inline')  # Send command and retrieve output asynchronously.
    print(f"{dev['host']}:\n{output}\n")

async def main():
    """
    Main function where tasks are created and executed.
    """
    devices = [
        {
            'device_type': 'cisco_ios',
            'host': 'sw1.test.local',
            'username': 'admin',
            'password': '12345678'
        },
        {
            'device_type': 'cisco_ios',
            'host': 'sw2.test.local',
            'username': 'admin',
            'password': '12345678'
        }
    ]
    tasks = [my_func(dev) for dev in devices]  # Create tasks for each device.
    await asyncio.gather(*tasks)  # Run the tasks asynchronously.

if __name__ == '__main__':
    asyncio.run(main())  # Execute the main function.
```

Output:
```bash
sw1.test.local:
Available:240.0(w)  Used:137.8(w)  Remaining:102.2(w)

Interface Admin  Oper       Power   Device              Class Max
                            (Watts)
--------- ------ ---------- ------- ------------------- ----- ----
Gi0/1     auto   on         13.9    AIR-AP1542D-B-K9    3     30.0
Gi0/2     auto   on         13.9    AIR-AP1542D-B-K9    3     30.0
Gi0/3     auto   on         26.6    AIR-AP2802E-B-K9    4     30.0
Gi0/4     auto   on         13.9    AIR-AP1542D-B-K9    3     30.0
Gi0/5     auto   off        0.0     n/a                 n/a   30.0
Gi0/6     auto   on         13.9    Ieee PD             4     30.0
Gi0/7     auto   on         13.9    AIR-AP1542I-B-K9    3     30.0
Gi0/8     auto   off        0.0     n/a                 n/a   30.0
Gi0/9     auto   on         13.9    AIR-AP1542D-B-K9    3     30.0
Gi0/10    auto   on         13.9    AIR-AP1542I-B-K9    3     30.0
Gi0/11    auto   on         13.9    AIR-AP1542I-B-K9    3     30.0
Gi0/12    auto   off        0.0     n/a                 n/a   30.0

sw2.test.local:
Available:240.0(w)  Used:99.3(w)  Remaining:140.7(w)

Interface Admin  Oper       Power   Device              Class Max
                            (Watts)
--------- ------ ---------- ------- ------------------- ----- ----
Gi0/1     auto   on         13.9    AIR-AP1542I-B-K9    4     30.0
Gi0/2     auto   on         13.9    AIR-AP1542I-B-K9    3     30.0
Gi0/3     auto   on         29.8    AIR-AP1562D-B-K9    4     30.0
Gi0/4     auto   on         13.9    AIR-AP1542I-E-K9    3     30.0
Gi0/5     auto   on         13.9    AIR-AP1542I-B-K9    3     30.0
Gi0/6     auto   on         13.9    AIR-AP1542D-B-K9    3     30.0
Gi0/7     auto   off        0.0     n/a                 n/a   30.0
Gi0/8     auto   off        0.0     n/a                 n/a   30.0
Gi0/9     auto   off        0.0     n/a                 n/a   30.0
Gi0/10    auto   off        0.0     n/a                 n/a   30.0
Gi0/11    auto   off        0.0     n/a                 n/a   30.0
Gi0/12    auto   off        0.0     n/a                 n/a   30.0
```

---
*thamuppet - Anton Hultberg* <br>
*antonhultberg@gmail.com* <br>

