import pytest

import xml.etree.ElementTree as ET


SLE_12_BASE = [
    'SLES12-Debuginfo-Pool',
    'SLES12-Debuginfo-Updates',
    'SLES12-Pool',
    'SLES12-Updates',
    'SLE-SDK12-Debuginfo-Pool',
    'SLE-SDK12-Debuginfo-Updates',
    'SLE-SDK12-Pool',
    'SLE-SDK12-Updates'
]

SLE_12_MODULES = [
    'SLE-Module-Adv-Systems-Management12-Debuginfo-Pool',
    'SLE-Module-Adv-Systems-Management12-Debuginfo-Updates',
    'SLE-Module-Adv-Systems-Management12-Pool',
    'SLE-Module-Adv-Systems-Management12-Updates',
    'SLE-Module-Containers12-Debuginfo-Pool',
    'SLE-Module-Containers12-Debuginfo-Updates',
    'SLE-Module-Containers12-Pool',
    'SLE-Module-Containers12-Updates',
    'SLE-Module-Legacy12-Debuginfo-Pool',
    'SLE-Module-Legacy12-Debuginfo-Updates',
    'SLE-Module-Legacy12-Pool',
    'SLE-Module-Legacy12-Updates',
    'SLE-Module-Public-Cloud12-Debuginfo-Pool',
    'SLE-Module-Public-Cloud12-Debuginfo-Updates',
    'SLE-Module-Public-Cloud12-Pool',
    'SLE-Module-Public-Cloud12-Updates',
    'SLE-Module-Toolchain12-Debuginfo-Pool',
    'SLE-Module-Toolchain12-Debuginfo-Updates',
    'SLE-Module-Toolchain12-Pool',
    'SLE-Module-Toolchain12-Updates',
    'SLE-Module-Web-Scripting12-Debuginfo-Pool',
    'SLE-Module-Web-Scripting12-Debuginfo-Updates',
    'SLE-Module-Web-Scripting12-Pool',
    'SLE-Module-Web-Scripting12-Updates'
]

SLE_12_SAP = [
    'SLE12-SAP-Debuginfo-Pool',
    'SLE-12-SAP-Debuginfo-Updates',
    'SLE12-SAP-Pool',
    'SLE12-SAP-Source-Pool',
    'SLE-12-SAP-Updates',
    'SLE-HA12-Debuginfo-Pool',
    'SLE-HA12-Debuginfo-Updates',
    'SLE-HA12-Pool',
    'SLE-HA12-Source-Pool',
    'SLE-HA12-Updates'
]

SLE_12_SP1_BASE = [
    'SLES12-SP1-Debuginfo-Pool',
    'SLES12-SP1-Debuginfo-Updates',
    'SLES12-SP1-Pool',
    'SLES12-SP1-Updates',
    'SLE-SDK12-SP1-Debuginfo-Pool',
    'SLE-SDK12-SP1-Debuginfo-Updates',
    'SLE-SDK12-SP1-Pool',
    'SLE-SDK12-SP1-Updates'
]

SLE_12_SP1_MODULES = SLE_12_MODULES

SLE_12_SP1_SAP = [
    'SLE12-SP1-SAP-Debuginfo-Pool',
    'SLE-12-SP1-SAP-Debuginfo-Updates',
    'SLE12-SP1-SAP-Pool',
    'SLE12-SP1-SAP-Source-Pool',
    'SLE-12-SP1-SAP-Updates',
    'SLE-HA12-SP1-Debuginfo-Pool',
    'SLE-HA12-SP1-Debuginfo-Updates',
    'SLE-HA12-SP1-Pool',
    'SLE-HA12-SP1-Source-Pool',
    'SLE-HA12-SP1-Updates'
]

SLE_12_SP2_BASE = [
    'SLES12-SP2-Debuginfo-Pool',
    'SLES12-SP2-Debuginfo-Updates',
    'SLES12-SP2-Pool',
    'SLES12-SP2-Updates',
    'SLE-SDK12-SP2-Debuginfo-Pool',
    'SLE-SDK12-SP2-Debuginfo-Updates',
    'SLE-SDK12-SP2-Pool',
    'SLE-SDK12-SP2-Updates'
]

SLE_12_SP2_MODULES = SLE_12_SP1_MODULES + [
    'SLE-Module-HPC12-Debuginfo-Pool',
    'SLE-Module-HPC12-Debuginfo-Updates',
    'SLE-Module-HPC12-Pool',
    'SLE-Module-HPC12-Updates'
]

SLE_12_SP2_SAP = [
    'SLE12-SP2-SAP-Debuginfo-Pool',
    'SLE-12-SP2-SAP-Debuginfo-Updates',
    'SLE12-SP2-SAP-Pool',
    'SLE12-SP2-SAP-Source-Pool',
    'SLE-12-SP2-SAP-Updates',
    'SLE-HA12-SP2-Debuginfo-Pool',
    'SLE-HA12-SP2-Debuginfo-Updates',
    'SLE-HA12-SP2-Pool',
    'SLE-HA12-SP2-Source-Pool',
    'SLE-HA12-SP2-Updates'
]

SLE_12_SP3_BASE = [
    'SLES12-SP3-Debuginfo-Pool',
    'SLES12-SP3-Debuginfo-Updates',
    'SLES12-SP3-Pool',
    'SLES12-SP3-Updates',
    'SLE-SDK12-SP3-Debuginfo-Pool',
    'SLE-SDK12-SP3-Debuginfo-Updates',
    'SLE-SDK12-SP3-Pool',
    'SLE-SDK12-SP3-Updates'
]

SLE_12_SP3_MODULES = SLE_12_SP2_MODULES

SLE_12_SP3_SAP = [
    'SLE12-SP3-SAP-Debuginfo-Pool',
    'SLE-12-SP3-SAP-Debuginfo-Updates',
    'SLE12-SP3-SAP-Pool',
    'SLE12-SP3-SAP-Source-Pool',
    'SLE-12-SP3-SAP-Updates',
    'SLE-HA12-SP3-Debuginfo-Pool',
    'SLE-HA12-SP3-Debuginfo-Updates',
    'SLE-HA12-SP3-Pool',
    'SLE-HA12-SP3-Source-Pool',
    'SLE-HA12-SP3-Updates'
]

SLE_12_SP4_BASE = [
    'SLES12-SP4-Debuginfo-Pool',
    'SLES12-SP4-Debuginfo-Updates',
    'SLES12-SP4-Pool',
    'SLES12-SP4-Updates',
    'SLE-SDK12-SP4-Debuginfo-Pool',
    'SLE-SDK12-SP4-Debuginfo-Updates',
    'SLE-SDK12-SP4-Pool',
    'SLE-SDK12-SP4-Updates'
]

SLE_12_SP4_MODULES = SLE_12_SP3_MODULES

SLE_12_SP4_SAP = [
    'SLE-Live-Patching12-SP4-Debuginfo-Pool',
    'SLE-Live-Patching12-SP4-Debuginfo-Updates',
    'SLE-Live-Patching12-SP4-Pool',
    'SLE-Live-Patching12-SP4-Updates',
    'SLE12-SP4-SAP-Debuginfo-Pool',
    'SLE-12-SP4-SAP-Debuginfo-Updates',
    'SLE12-SP4-SAP-Pool',
    'SLE12-SP4-SAP-Source-Pool',
    'SLE-12-SP4-SAP-Updates',
    'SLE-HA12-SP4-Debuginfo-Pool',
    'SLE-HA12-SP4-Debuginfo-Updates',
    'SLE-HA12-SP4-Pool',
    'SLE-HA12-SP4-Source-Pool',
    'SLE-HA12-SP4-Updates'
]

SLE_12_SP5_BASE = [
    'SLES12-SP5-Debuginfo-Pool',
    'SLES12-SP5-Debuginfo-Updates',
    'SLES12-SP5-Pool',
    'SLES12-SP5-Updates',
    'SLE-SDK12-SP5-Debuginfo-Pool',
    'SLE-SDK12-SP5-Debuginfo-Updates',
    'SLE-SDK12-SP5-Pool',
    'SLE-SDK12-SP5-Updates'
]

SLE_12_SP5_MODULES = SLE_12_SP4_MODULES

SLE_12_SP5_SAP = [
    'SLE-Live-Patching12-SP5-Debuginfo-Pool',
    'SLE-Live-Patching12-SP5-Debuginfo-Updates',
    'SLE-Live-Patching12-SP5-Pool',
    'SLE-Live-Patching12-SP5-Updates',
    'SLE12-SP5-SAP-Debuginfo-Pool',
    'SLE-12-SP5-SAP-Debuginfo-Updates',
    'SLE12-SP5-SAP-Pool',
    'SLE12-SP5-SAP-Source-Pool',
    'SLE-12-SP5-SAP-Updates',
    'SLE-HA12-SP5-Debuginfo-Pool',
    'SLE-HA12-SP5-Debuginfo-Updates',
    'SLE-HA12-SP5-Pool',
    'SLE-HA12-SP5-Source-Pool',
    'SLE-HA12-SP5-Updates'
]

SLE_15_BASE = [
    'SLE-Module-Basesystem15-Debuginfo-Pool',
    'SLE-Module-Basesystem15-Debuginfo-Updates',
    'SLE-Module-Basesystem15-Pool',
    'SLE-Module-Basesystem15-Updates'
]

SLE_15_PRODUCTS = [
    'SLE-Product-SLES15-Pool',
    'SLE-Product-SLES15-Updates'
]

SLE_15_MODULES = [
    'SLE-Module-Desktop-Applications15-Debuginfo-Pool',
    'SLE-Module-Desktop-Applications15-Debuginfo-Updates',
    'SLE-Module-Desktop-Applications15-Pool',
    'SLE-Module-Desktop-Applications15-Updates',
    'SLE-Module-DevTools15-Debuginfo-Pool',
    'SLE-Module-DevTools15-Debuginfo-Updates',
    'SLE-Module-DevTools15-Pool',
    'SLE-Module-DevTools15-Updates',
    'SLE-Module-Legacy15-Debuginfo-Pool',
    'SLE-Module-Legacy15-Debuginfo-Updates',
    'SLE-Module-Legacy15-Pool',
    'SLE-Module-Legacy15-Updates',
    'SLE-Module-Public-Cloud15-Debuginfo-Pool',
    'SLE-Module-Public-Cloud15-Debuginfo-Updates',
    'SLE-Module-Public-Cloud15-Pool',
    'SLE-Module-Public-Cloud15-Updates',
    'SLE-Module-Server-Applications15-Debuginfo-Pool',
    'SLE-Module-Server-Applications15-Debuginfo-Updates',
    'SLE-Module-Server-Applications15-Pool',
    'SLE-Module-Server-Applications15-Updates',
    'SLE-Module-Web-Scripting15-Debuginfo-Pool',
    'SLE-Module-Web-Scripting15-Debuginfo-Updates',
    'SLE-Module-Web-Scripting15-Pool',
    'SLE-Module-Web-Scripting15-Updates'
]

SLE_15_X86_64_MODULES = [
    'SLE-Module-CAP-Tools15-Debuginfo-Pool',
    'SLE-Module-CAP-Tools15-Debuginfo-Updates',
    'SLE-Module-CAP-Tools15-Pool',
    'SLE-Module-CAP-Tools15-Updates',
    'SLE-Module-Containers15-Debuginfo-Pool',
    'SLE-Module-Containers15-Debuginfo-Updates',
    'SLE-Module-Containers15-Pool',
    'SLE-Module-Containers15-Updates'
]

SLE_15_SAP = [
    'SLE-Module-Live-Patching15-Debuginfo-Pool',
    'SLE-Module-Live-Patching15-Debuginfo-Updates',
    'SLE-Module-Live-Patching15-Pool',
    'SLE-Module-Live-Patching15-Updates',
    'SLE-Module-SAP-Applications15-Debuginfo-Pool',
    'SLE-Module-SAP-Applications15-Debuginfo-Updates',
    'SLE-Module-SAP-Applications15-Pool',
    'SLE-Module-SAP-Applications15-Updates',
    'SLE-Product-HA15-Debuginfo-Pool',
    'SLE-Product-HA15-Debuginfo-Updates',
    'SLE-Product-HA15-Pool',
    'SLE-Product-HA15-Updates',
    'SLE-Product-SLES_SAP15-Debuginfo-Pool',
    'SLE-Product-SLES_SAP15-Debuginfo-Updates',
    'SLE-Product-SLES_SAP15-Pool',
    'SLE-Product-SLES_SAP15-Updates'
]

SLE_15_SP1_BASE = [
    'SLE-Module-Basesystem15-SP1-Debuginfo-Pool',
    'SLE-Module-Basesystem15-SP1-Debuginfo-Updates',
    'SLE-Module-Basesystem15-SP1-Pool',
    'SLE-Module-Basesystem15-SP1-Updates'
]

SLE_15_SP1_PRODUCTS = [
    'SLE-Product-SLES15-SP1-Pool',
    'SLE-Product-SLES15-SP1-Updates'
]

SLE_15_SP1_MODULES = [
    'SLE-Module-Desktop-Applications15-SP1-Debuginfo-Pool',
    'SLE-Module-Desktop-Applications15-SP1-Debuginfo-Updates',
    'SLE-Module-Desktop-Applications15-SP1-Pool',
    'SLE-Module-Desktop-Applications15-SP1-Updates',
    'SLE-Module-DevTools15-SP1-Debuginfo-Pool',
    'SLE-Module-DevTools15-SP1-Debuginfo-Updates',
    'SLE-Module-DevTools15-SP1-Pool',
    'SLE-Module-DevTools15-SP1-Updates',
    'SLE-Module-Legacy15-SP1-Debuginfo-Pool',
    'SLE-Module-Legacy15-SP1-Debuginfo-Updates',
    'SLE-Module-Legacy15-SP1-Pool',
    'SLE-Module-Legacy15-SP1-Updates',
    'SLE-Module-Public-Cloud15-SP1-Debuginfo-Pool',
    'SLE-Module-Public-Cloud15-SP1-Debuginfo-Updates',
    'SLE-Module-Public-Cloud15-SP1-Pool',
    'SLE-Module-Public-Cloud15-SP1-Updates',
    'SLE-Module-Python2-15-SP1-Pool',
    'SLE-Module-Python2-15-SP1-Updates',
    'SLE-Module-Server-Applications15-SP1-Debuginfo-Pool',
    'SLE-Module-Server-Applications15-SP1-Debuginfo-Updates',
    'SLE-Module-Server-Applications15-SP1-Pool',
    'SLE-Module-Server-Applications15-SP1-Updates',
    'SLE-Module-Web-Scripting15-SP1-Debuginfo-Pool',
    'SLE-Module-Web-Scripting15-SP1-Debuginfo-Updates',
    'SLE-Module-Web-Scripting15-SP1-Pool',
    'SLE-Module-Web-Scripting15-SP1-Updates'
]

SLE_15_SP1_X86_64_MODULES = [
    'SLE-Module-CAP-Tools15-SP1-Debuginfo-Pool',
    'SLE-Module-CAP-Tools15-SP1-Debuginfo-Updates',
    'SLE-Module-CAP-Tools15-SP1-Pool',
    'SLE-Module-CAP-Tools15-SP1-Updates',
    'SLE-Module-Containers15-SP1-Debuginfo-Pool',
    'SLE-Module-Containers15-SP1-Debuginfo-Updates',
    'SLE-Module-Containers15-SP1-Pool',
    'SLE-Module-Containers15-SP1-Updates'
]

SLE_15_SP1_SAP = [
    'SLE-Module-Live-Patching15-SP1-Debuginfo-Pool',
    'SLE-Module-Live-Patching15-SP1-Debuginfo-Updates',
    'SLE-Module-Live-Patching15-SP1-Pool',
    'SLE-Module-Live-Patching15-SP1-Updates',
    'SLE-Module-SAP-Applications15-SP1-Debuginfo-Pool',
    'SLE-Module-SAP-Applications15-SP1-Debuginfo-Updates',
    'SLE-Module-SAP-Applications15-SP1-Pool',
    'SLE-Module-SAP-Applications15-SP1-Updates',
    'SLE-Product-HA15-SP1-Debuginfo-Pool',
    'SLE-Product-HA15-SP1-Debuginfo-Updates',
    'SLE-Product-HA15-SP1-Pool',
    'SLE-Product-HA15-SP1-Updates',
    'SLE-Product-SLES_SAP15-SP1-Debuginfo-Pool',
    'SLE-Product-SLES_SAP15-SP1-Debuginfo-Updates',
    'SLE-Product-SLES_SAP15-SP1-Pool',
    'SLE-Product-SLES_SAP15-SP1-Updates'
]

SLE_15_SP1_HPC = [
    'SLE-Product-HPC-15-SP1-Pool',
    'SLE-Product-HPC-15-SP1-Updates',
    'SLE-Product-HPC15-SP1-Debuginfo-Pool',
    'SLE-Product-HPC15-SP1-Debuginfo-Updates',
    'SLE-Product-HPC15-SP1-Source-Pool',
    'SLE-Module-Containers15-SP1-Debuginfo-Pool',
    'SLE-Module-Containers15-SP1-Debuginfo-Updates',
    'SLE-Module-Containers15-SP1-Pool',
    'SLE-Module-Containers15-SP1-Updates',
    'SLE-Module-Desktop-Applications15-SP1-Debuginfo-Pool',
    'SLE-Module-Desktop-Applications15-SP1-Debuginfo-Updates',
    'SLE-Module-Desktop-Applications15-SP1-Pool',
    'SLE-Module-Desktop-Applications15-SP1-Updates',
    'SLE-Module-DevTools15-SP1-Debuginfo-Pool',
    'SLE-Module-DevTools15-SP1-Debuginfo-Updates',
    'SLE-Module-DevTools15-SP1-Pool',
    'SLE-Module-DevTools15-SP1-Updates',
    'SLE-Module-Public-Cloud15-SP1-Debuginfo-Pool',
    'SLE-Module-Public-Cloud15-SP1-Debuginfo-Updates',
    'SLE-Module-Public-Cloud15-SP1-Pool',
    'SLE-Module-Public-Cloud15-SP1-Updates',
    'SLE-Module-Python2-15-SP1-Pool',
    'SLE-Module-Python2-15-SP1-Updates',
    'SLE-Module-Server-Applications15-SP1-Debuginfo-Pool',
    'SLE-Module-Server-Applications15-SP1-Debuginfo-Updates',
    'SLE-Module-Server-Applications15-SP1-Pool',
    'SLE-Module-Server-Applications15-SP1-Updates',
    'SLE-Module-Web-Scripting15-SP1-Debuginfo-Pool',
    'SLE-Module-Web-Scripting15-SP1-Debuginfo-Updates',
    'SLE-Module-Web-Scripting15-SP1-Pool',
    'SLE-Module-Web-Scripting15-SP1-Updates'
]

SLE_15_SP2_BASE = [
    'SLE-Module-Basesystem15-SP2-Debuginfo-Pool',
    'SLE-Module-Basesystem15-SP2-Debuginfo-Updates',
    'SLE-Module-Basesystem15-SP2-Pool',
    'SLE-Module-Basesystem15-SP2-Updates'
]

SLE_15_SP2_PRODUCTS = [
    'SLE-Product-SLES15-SP2-Pool',
    'SLE-Product-SLES15-SP2-Updates'
]

SLE_15_SP2_MODULES = [
    'SLE-Module-Desktop-Applications15-SP2-Debuginfo-Pool',
    'SLE-Module-Desktop-Applications15-SP2-Debuginfo-Updates',
    'SLE-Module-Desktop-Applications15-SP2-Pool',
    'SLE-Module-Desktop-Applications15-SP2-Updates',
    'SLE-Module-DevTools15-SP2-Debuginfo-Pool',
    'SLE-Module-DevTools15-SP2-Debuginfo-Updates',
    'SLE-Module-DevTools15-SP2-Pool',
    'SLE-Module-DevTools15-SP2-Updates',
    'SLE-Module-Legacy15-SP2-Debuginfo-Pool',
    'SLE-Module-Legacy15-SP2-Debuginfo-Updates',
    'SLE-Module-Legacy15-SP2-Pool',
    'SLE-Module-Legacy15-SP2-Updates',
    'SLE-Module-Public-Cloud15-SP2-Debuginfo-Pool',
    'SLE-Module-Public-Cloud15-SP2-Debuginfo-Updates',
    'SLE-Module-Public-Cloud15-SP2-Pool',
    'SLE-Module-Public-Cloud15-SP2-Updates',
    'SLE-Module-Python2-15-SP2-Pool',
    'SLE-Module-Python2-15-SP2-Updates',
    'SLE-Module-Server-Applications15-SP2-Debuginfo-Pool',
    'SLE-Module-Server-Applications15-SP2-Debuginfo-Updates',
    'SLE-Module-Server-Applications15-SP2-Pool',
    'SLE-Module-Server-Applications15-SP2-Updates',
    'SLE-Module-Web-Scripting15-SP2-Debuginfo-Pool',
    'SLE-Module-Web-Scripting15-SP2-Debuginfo-Updates',
    'SLE-Module-Web-Scripting15-SP2-Pool',
    'SLE-Module-Web-Scripting15-SP2-Updates'
]

SLE_15_SP2_X86_64_MODULES = [
    'SLE-Module-CAP-Tools15-SP2-Debuginfo-Pool',
    'SLE-Module-CAP-Tools15-SP2-Debuginfo-Updates',
    'SLE-Module-CAP-Tools15-SP2-Pool',
    'SLE-Module-CAP-Tools15-SP2-Updates',
    'SLE-Module-Containers15-SP2-Debuginfo-Pool',
    'SLE-Module-Containers15-SP2-Debuginfo-Updates',
    'SLE-Module-Containers15-SP2-Pool',
    'SLE-Module-Containers15-SP2-Updates'
]

SLE_15_SP2_SAP = [
    'SLE-Module-Live-Patching15-SP2-Debuginfo-Pool',
    'SLE-Module-Live-Patching15-SP2-Debuginfo-Updates',
    'SLE-Module-Live-Patching15-SP2-Pool',
    'SLE-Module-Live-Patching15-SP2-Updates',
    'SLE-Module-SAP-Applications15-SP2-Debuginfo-Pool',
    'SLE-Module-SAP-Applications15-SP2-Debuginfo-Updates',
    'SLE-Module-SAP-Applications15-SP2-Pool',
    'SLE-Module-SAP-Applications15-SP2-Updates',
    'SLE-Product-HA15-SP2-Debuginfo-Pool',
    'SLE-Product-HA15-SP2-Debuginfo-Updates',
    'SLE-Product-HA15-SP2-Pool',
    'SLE-Product-HA15-SP2-Updates',
    'SLE-Product-SLES_SAP15-SP2-Debuginfo-Pool',
    'SLE-Product-SLES_SAP15-SP2-Debuginfo-Updates',
    'SLE-Product-SLES_SAP15-SP2-Pool',
    'SLE-Product-SLES_SAP15-SP2-Updates'
]

SLE_15_SP2_HPC = [
    'SLE-Product-HPC-15-SP2-Pool',
    'SLE-Product-HPC-15-SP2-Updates',
    'SLE-Product-HPC15-SP2-Debuginfo-Pool',
    'SLE-Product-HPC15-SP2-Debuginfo-Updates',
    'SLE-Product-HPC15-SP2-Source-Pool',
    'SLE-Module-Containers15-SP2-Debuginfo-Pool',
    'SLE-Module-Containers15-SP2-Debuginfo-Updates',
    'SLE-Module-Containers15-SP2-Pool',
    'SLE-Module-Containers15-SP2-Updates',
    'SLE-Module-Desktop-Applications15-SP2-Debuginfo-Pool',
    'SLE-Module-Desktop-Applications15-SP2-Debuginfo-Updates',
    'SLE-Module-Desktop-Applications15-SP2-Pool',
    'SLE-Module-Desktop-Applications15-SP2-Updates',
    'SLE-Module-DevTools15-SP2-Debuginfo-Pool',
    'SLE-Module-DevTools15-SP2-Debuginfo-Updates',
    'SLE-Module-DevTools15-SP2-Pool',
    'SLE-Module-DevTools15-SP2-Updates',
    'SLE-Module-Public-Cloud15-SP2-Debuginfo-Pool',
    'SLE-Module-Public-Cloud15-SP2-Debuginfo-Updates',
    'SLE-Module-Public-Cloud15-SP2-Pool',
    'SLE-Module-Public-Cloud15-SP2-Updates',
    'SLE-Module-Python2-15-SP2-Pool',
    'SLE-Module-Python2-15-SP2-Updates',
    'SLE-Module-Server-Applications15-SP2-Debuginfo-Pool',
    'SLE-Module-Server-Applications15-SP2-Debuginfo-Updates',
    'SLE-Module-Server-Applications15-SP2-Pool',
    'SLE-Module-Server-Applications15-SP2-Updates',
    'SLE-Module-Web-Scripting15-SP2-Debuginfo-Pool',
    'SLE-Module-Web-Scripting15-SP2-Debuginfo-Updates',
    'SLE-Module-Web-Scripting15-SP2-Pool',
    'SLE-Module-Web-Scripting15-SP2-Updates'
]

BASE_15 = SLE_15_BASE + SLE_15_MODULES + SLE_15_PRODUCTS
BASE_15_SAP = SLE_15_SAP + SLE_15_BASE + SLE_15_MODULES
BASE_15_SP1 = SLE_15_SP1_BASE + SLE_15_SP1_MODULES + SLE_15_SP1_PRODUCTS
BASE_15_SP1_SAP = SLE_15_SP1_SAP + SLE_15_SP1_BASE + SLE_15_SP1_MODULES
BASE_15_SP1_HPC = SLE_15_SP1_BASE + SLE_15_SP1_HPC
BASE_15_SP2 = SLE_15_SP2_BASE + SLE_15_SP2_MODULES + SLE_15_SP2_PRODUCTS
BASE_15_SP2_SAP = SLE_15_SP2_SAP + SLE_15_SP2_BASE + SLE_15_SP2_MODULES
BASE_15_SP2_HPC = SLE_15_SP2_BASE + SLE_15_SP2_HPC

BASE_15_SP3 = [
    repo.replace('SP2', 'SP3') for repo in BASE_15_SP2
    if ('Python2' not in repo and 'Legacy' not in repo)
]
BASE_15_SP3_SAP = [
    repo.replace('SP2', 'SP3') for repo in BASE_15_SP2_SAP
    if ('Python2' not in repo and 'Legacy' not in repo)
]
BASE_15_SP3_HPC = [
    repo.replace('SP2', 'SP3') for repo in BASE_15_SP2_HPC
]
SLE_15_SP3_X86_64_MODULES = [
    repo.replace('SP2', 'SP3') for repo in SLE_15_SP2_X86_64_MODULES
]

BASE_15_SP4 = [
    repo.replace('SP3', 'SP4') for repo in BASE_15_SP3
    if ('Python2' not in repo and 'Legacy' not in repo)
]
BASE_15_SP4_SAP = [
    repo.replace('SP3', 'SP4') for repo in BASE_15_SP3_SAP
    if ('Python2' not in repo and 'Legacy' not in repo)
]
BASE_15_SP4_HPC = [
    repo.replace('SP3', 'SP4') for repo in BASE_15_SP3_HPC
    if ('Python2' not in repo and 'Legacy' not in repo)
]
SLE_15_SP4_X86_64_MODULES = [
    repo.replace('SP3', 'SP4') for repo in SLE_15_SP3_X86_64_MODULES
    if 'CAP' not in repo
]

PYTHON3_MODULE = [
    'SLE-Module-Python3-15-SP4-Pool',
    'SLE-Module-Python3-15-SP4-Updates'
]

BASE_15_SP4 += PYTHON3_MODULE
BASE_15_SP4_SAP += PYTHON3_MODULE
BASE_15_SP4_HPC += PYTHON3_MODULE

BASE_15_SP5 = [
    repo.replace('SP4', 'SP5') for repo in BASE_15_SP4
]
BASE_15_SP5_SAP = [
    repo.replace('SP4', 'SP5') for repo in BASE_15_SP4_SAP
]
BASE_15_SP5_HPC = [
    repo.replace('SP4', 'SP5') for repo in BASE_15_SP4_HPC
]
SLE_15_SP5_X86_64_MODULES = [
    repo.replace('SP4', 'SP5') for repo in SLE_15_SP4_X86_64_MODULES
]

BASE_15_SP6 = [
    repo.replace('SP5', 'SP6') for repo in BASE_15_SP5
]
BASE_15_SP6_SAP = [
    repo.replace('SP5', 'SP6') for repo in BASE_15_SP5_SAP
]
BASE_15_SP6_HPC = [
    repo.replace('SP5', 'SP6') for repo in BASE_15_SP5_HPC
]
SLE_15_SP6_X86_64_MODULES = [
    repo.replace('SP5', 'SP6') for repo in SLE_15_SP5_X86_64_MODULES
]

BASE_15_SP7 = [
    repo.replace('SP5', 'SP7') for repo in BASE_15_SP5
]
BASE_15_SP7_SAP = [
    repo.replace('SP5', 'SP7') for repo in BASE_15_SP5_SAP
]
BASE_15_SP7_HPC = [
    repo.replace('SP5', 'SP7') for repo in BASE_15_SP5_HPC
]
SLE_15_SP7_X86_64_MODULES = [
    repo.replace('SP5', 'SP7') for repo in SLE_15_SP5_X86_64_MODULES
]

SYSTEMS_MGMT_15_MODULE = [
    'SLE-Module-Systems-Management-15-SP7-Pool',
    'SLE-Module-Systems-Management-15-SP7-Updates'
]

BASE_15_SP7 += SYSTEMS_MGMT_15_MODULE
BASE_15_SP7_SAP += SYSTEMS_MGMT_15_MODULE
BASE_15_SP7_HPC += SYSTEMS_MGMT_15_MODULE

SLES_REPOS = {
    '12-X86_64': SLE_12_BASE + SLE_12_MODULES,
    '12-X86_64-SAP': SLE_12_SAP + SLE_12_BASE + SLE_12_MODULES,
    '12-X86_64-HPC': SLE_12_BASE + SLE_12_MODULES,
    '12-SP1-X86_64': SLE_12_SP1_BASE + SLE_12_SP1_MODULES,
    '12-SP1-X86_64-SAP':
        SLE_12_SP1_SAP + SLE_12_SP1_BASE + SLE_12_SP1_MODULES,
    '12-SP1-X86_64-HPC': SLE_12_SP1_BASE + SLE_12_SP1_MODULES,
    '12-SP2-X86_64': SLE_12_SP2_BASE + SLE_12_SP2_MODULES,
    '12-SP2-X86_64-SAP':
        SLE_12_SP2_SAP + SLE_12_SP2_BASE + SLE_12_SP2_MODULES,
    '12-SP2-X86_64-HPC': SLE_12_SP2_BASE + SLE_12_SP2_MODULES,
    '12-SP3-X86_64': SLE_12_SP3_BASE + SLE_12_SP3_MODULES,
    '12-SP3-X86_64-SAP':
        SLE_12_SP3_SAP + SLE_12_SP3_BASE + SLE_12_SP3_MODULES,
    '12-SP3-X86_64-HPC': SLE_12_SP3_BASE + SLE_12_SP3_MODULES,
    '12-SP4-X86_64': SLE_12_SP4_BASE + SLE_12_SP4_MODULES,
    '12-SP4-X86_64-SAP':
        SLE_12_SP4_SAP + SLE_12_SP4_BASE + SLE_12_SP4_MODULES,
    '12-SP4-X86_64-HPC': SLE_12_SP4_BASE + SLE_12_SP4_MODULES,
    '12-SP5-X86_64': SLE_12_SP5_BASE + SLE_12_SP5_MODULES,
    '12-SP5-X86_64-SAP':
        SLE_12_SP5_SAP + SLE_12_SP5_BASE + SLE_12_SP5_MODULES,
    '12-SP5-X86_64-HPC': SLE_12_SP5_BASE + SLE_12_SP5_MODULES,
    '15-AARCH64': BASE_15,
    '15-X86_64': BASE_15 + SLE_15_X86_64_MODULES,
    '15-X86_64-SAP': BASE_15_SAP + SLE_15_X86_64_MODULES,
    '15-SP1-AARCH64': BASE_15_SP1,
    '15-SP1-X86_64': BASE_15_SP1 + SLE_15_SP1_X86_64_MODULES,
    '15-SP1-X86_64-SAP': BASE_15_SP1_SAP + SLE_15_SP1_X86_64_MODULES,
    '15-SP1-X86_64-HPC': BASE_15_SP1_HPC,
    '15-SP2-AARCH64': BASE_15_SP2,
    '15-SP2-X86_64': BASE_15_SP2 + SLE_15_SP2_X86_64_MODULES,
    '15-SP2-X86_64-SAP': BASE_15_SP2_SAP + SLE_15_SP2_X86_64_MODULES,
    '15-SP2-X86_64-HPC': BASE_15_SP2_HPC,
    '15-SP3-AARCH64': BASE_15_SP3,
    '15-SP3-X86_64': BASE_15_SP3 + SLE_15_SP3_X86_64_MODULES,
    '15-SP3-X86_64-SAP': BASE_15_SP3_SAP + SLE_15_SP3_X86_64_MODULES,
    '15-SP3-X86_64-HPC': BASE_15_SP3_HPC,
    '15-SP4-AARCH64': BASE_15_SP4,
    '15-SP4-X86_64': BASE_15_SP4 + SLE_15_SP4_X86_64_MODULES,
    '15-SP4-X86_64-SAP': BASE_15_SP4_SAP + SLE_15_SP4_X86_64_MODULES,
    '15-SP4-X86_64-HPC': BASE_15_SP4_HPC,
    '15-SP5-AARCH64': BASE_15_SP5,
    '15-SP5-X86_64': BASE_15_SP5 + SLE_15_SP5_X86_64_MODULES,
    '15-SP5-X86_64-SAP': BASE_15_SP5_SAP + SLE_15_SP5_X86_64_MODULES,
    '15-SP5-X86_64-HPC': BASE_15_SP5_HPC,
    '15-SP6-AARCH64': BASE_15_SP6,
    '15-SP6-X86_64': BASE_15_SP6 + SLE_15_SP6_X86_64_MODULES,
    '15-SP6-X86_64-SAP': BASE_15_SP6_SAP + SLE_15_SP6_X86_64_MODULES,
    '15-SP6-X86_64-HPC': BASE_15_SP6_HPC,
    '15-SP7-AARCH64': BASE_15_SP7,
    '15-SP7-X86_64': BASE_15_SP7 + SLE_15_SP7_X86_64_MODULES,
    '15-SP7-X86_64-SAP': BASE_15_SP7_SAP + SLE_15_SP7_X86_64_MODULES,
    '15-SP7-X86_64-HPC': BASE_15_SP7_HPC,
}


@pytest.fixture()
def get_sles_repos():
    def f(version):
        return SLES_REPOS.get(version)
    return f


@pytest.fixture()
def get_instance_repos(host):
    def f():
        repos = []

        zypper_lr = host.run('zypper -x lr').stdout.strip()
        root = ET.fromstring(zypper_lr)

        for repo in root.iter('repo'):
            repos.append(repo.get('name'))

        return repos
    return f
