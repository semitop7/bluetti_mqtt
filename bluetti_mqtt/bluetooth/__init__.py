import logging
import re
from typing import Set
from bleak import BleakScanner

from ..core import AC200M, AC200L, AC300, AC500, AC60, AC70, AC180, EP500, EP500P, EP600, EB3A
from .client import BluetoothClient
from .exc import BadConnectionError, ModbusError, ParseError
from .manager import MultiDeviceManager


DEVICE_NAME_RE = re.compile(r'^(AC200M|AC200L|AC200PL|AC300|AC500|AC60|AC70|AC70P|AC180|AC180P|EP500P|EP500|EP600|EB3A)(\d+)$')


async def scan_devices():
    print('Scanning....')
    devices = await BleakScanner.discover()
    if len(devices) == 0:
        print('0 devices found - something probably went wrong')
    else:
        bluetti_devices = [d for d in devices if d.name and DEVICE_NAME_RE.match(d.name)]
        for d in bluetti_devices:
            print(f'Found {d.name}: address {d.address}')


def build_device(address: str, name: str):
    match = DEVICE_NAME_RE.match(name)
    if not match:
        raise Exception("device not supported (does not match device name regexp)")
    if match[1] == 'AC200M':
        return AC200M(address, match[2])
    if match[1] in ['AC200L', 'AC200PL']:
        return AC200L(address, match[2])
    if match[1] == 'AC300':
        return AC300(address, match[2])
    if match[1] == 'AC500':
        return AC500(address, match[2])
    if match[1] == 'AC60':
        return AC60(address, match[2])
    if match[1] in ['AC70', 'AC70P']:
        return AC70(address, match[2])
    if match[1] in ['AC180', 'AC180P']:
        return AC180(address, match[2])
    if match[1] == 'EP500':
        return EP500(address, match[2])
    if match[1] == 'EP500P':
        return EP500P(address, match[2])
    if match[1] == 'EP600':
        return EP600(address, match[2])
    if match[1] == 'EB3A':
        return EB3A(address, match[2])


async def check_addresses(addresses: Set[str]):
    logging.debug(f'Checking we can connect: {addresses}')
    devices = await BleakScanner.discover()
    filtered = [d for d in devices if d.address in addresses]
    logging.debug(f'Found devices: {filtered}')

    if len(filtered) != len(addresses):
        return []

    return [build_device(d.address, d.name) for d in filtered]
