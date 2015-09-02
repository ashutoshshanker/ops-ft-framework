# Topology definition

topoDict = {
    "topoExecution": 1000,
    "topoTarget": "dut01",
    "topoDevices": "dut01 workstn01",
    "topoLinks": "lnk01:workstn01:dut01",
    "topoFilters": "dut01:system-category:switch"
    }

LogOutput('info', 'Sample test case code.')

# Grab the name of the switch from the eTree

switchElement = XmlGetElementsByTag(headers.TOPOLOGY,
        ".//device/system[vendor='Edgecore']/name", allElements=True)
numSwitches = len(switchElement)
for switchE in switchElement:
    switchName = switchE.text

# Connect to the switch via console

LogOutput('info', '########################################')
LogOutput('info', 'Connecting to switch via console'
                 + switchName)
LogOutput('info', '########################################')
switchConsoleConn = switch.Connect(switchName)
if switchConsoleConn is None:
    LogOutput('error', 'Failed to connect to switch console'
                     + switchName)
    exit(1)

# Configure management IP on eth0 interface of the switch so that later we can connect to the switch via mgmt interface via host

LogOutput('info',
                 '################################################################################'
                 )
LogOutput('info',
                 'Configuring management IP on management interface eth0 to switch via console'
                  + switchName)
LogOutput('info',
                 '################################################################################'
                 )

mgmtIpAddress = '20.20.20.3'
netMask = 24

command = 'ip addr add %s/%d dev eth0' % (mgmtIpAddress, netMask)

retStruct = switch.DeviceInteract(connection=switchConsoleConn,
                                  command=command)

if retStruct['returnCode']:
    LogOutput('error',
                     'Failed to configure mgmt interface on the switch '
                      + switchName)

   # exit(1)

# Grab the name of the host from the topology xml eTree

hostElement = XmlGetElementsByTag(headers.TOPOLOGY,
        ".//device/system[category='workstation']/name",
        allElements=True)
numHosts = len(hostElement)

for hostE in hostElement:
    hName = hostE.text

# Enable Topology link

linkList = [headers.topo['lnk01']]
returnStruct = topology.LinkStatusConfig(links=linkList, enable=1)
returnCode = ReturnJSONGetCode(json=returnStruct)
if returnCode != 0:
    LogOutput('error', 'Failed to enable link01')
    exit(1)

# Initiate 3 host telnet sessions to connect to switch via management interface SSH sessions

hostTelnetSessionForSwitchVtyshShell = None
hostTelnetSessionForSwitchBroadcomDriverShell = None
hostTelnetSessionForSwitchBashShell = None

for i in range(0, 3):

   # Connect to the device

    LogOutput('info', '########################################')
    LogOutput('info', 'Connecting to host ' + hName)
    LogOutput('info', '########################################')
    if i == 0:
        hostTelnetSessionForSwitchVtyshShell = host.Connect(hName)
        if hostTelnetSessionForSwitchVtyshShell is None:
            LogOutput('error',
                             'Failed to connect to host for switch vtysh shell'
                              + hName)
            exit(1)
    elif i == 1:
        hostTelnetSessionForSwitchBroadcomDriverShell = \
            host.Connect(hName)
        if hostTelnetSessionForSwitchBroadcomDriverShell is None:
            LogOutput('error',
                             'Failed to connect to host for switch broadcom driver shell'
                              + hName)
            exit(1)
    elif i == 2:
        hostTelnetSessionForSwitchBashShell = host.Connect(hName)
        if hostTelnetSessionForSwitchBashShell is None:
            LogOutput('error',
                             'Failed to connect to host for switch bash shell'
                              + hName)
            exit(1)

# Configuring IPv4 on the host ethernet eth1 interface with bash host connection handle

ipAddr = '20.20.20.2'
LogOutput('info', 'Configuring host IP' + hName)
retStruct = host.NetworkConfig(
    connection=hostTelnetSessionForSwitchBashShell,
    eth='eth1',
    ipAddr=ipAddr,
    netMask='255.255.255.0',
    broadcast='20.20.20.1',
    clear=0,
    )
retCode = retStruct.get('returnCode')
retBuff = retStruct.get('buffer')
if retCode:
    LogOutput('error', 'Failed to configure IP %s on  host %s '
                     % (ipAddr, hName))
else:
    LogOutput('info',
                     'Succeeded in configuring IP  %s on host %s '
                     % (ipAddr, hName))

# Initiate SSH sessions to switch based on  host telnet sessions

for i in range(0, 3):
    mgmtIpAddress = '20.20.20.3'

   # Connect to the device

    LogOutput('info', '########################################')
    LogOutput('info', 'Connecting to switch ' + switchName)
    LogOutput('info', '########################################')

    if i == 0:
        result = host.DeviceConnect(switchName,
                                    hostConnHandle=hostTelnetSessionForSwitchVtyshShell,
                                    mgmtIpAddress=mgmtIpAddress)
        if result is None:
            LogOutput('error',
                             'Failed to connect to switch for vtysh shell '
                              + switchName)
            continue
        LogOutput('info', 'Get to vtysh shell ' + switchName)
        retStruct = \
            switch.CLI.VtyshShell(connection=hostTelnetSessionForSwitchVtyshShell)
        retCode = ReturnJSONGetCode(json=retStruct)
        if retCode != 0:
            LogOutput('error', 'Failed to get vtysh shell '
                             + switchName)
        else:
            LogOutput('info', 'Success in getting vtysh shell '
                             + switchName)
            data = ReturnJSONGetData(json=retStruct)
            print data
    elif i == 1:

        result = host.DeviceConnect(switchName,
                                    hostConnHandle=hostTelnetSessionForSwitchBroadcomDriverShell,
                                    mgmtIpAddress=mgmtIpAddress)
        if result is None:
            LogOutput('error',
                             'Failed to connect to switch for broadcom shell '
                              + switchName)
            continue
        LogOutput('info', 'Get to broadcom shell ' + switchName)
        retStruct = \
            switch.CLI.BroadcomShell(connection=hostTelnetSessionForSwitchBroadcomDriverShell)
        retCode = ReturnJSONGetCode(json=retStruct)
        if retCode != 0:
            LogOutput('error', 'Failed to get broadcom shell '
                             + switchName)
        else:
            LogOutput('info',
                             'Success in getting broadcom shell '
                             + switchName)
        data = ReturnJSONGetData(json=retStruct)
        print data

        command = 'LS'
        LogOutput('info', 'Execute LS cmd on  broadcom shell '
                         + switchName)
        retStruct = \
            switch.CLI.BroadcomShell(connection=hostTelnetSessionForSwitchBroadcomDriverShell,
                configOption='execute', cmd=command)
        retCode = ReturnJSONGetCode(json=retStruct)
        if retCode != 0:
            LogOutput('error', 'Failed to execute the command : '
                              + command)
        else:
            LogOutput('info',
                             'Successfully executed the command : '
                             + command)
        data = ReturnJSONGetData(json=retStruct)
        print data
    else:

        command = 'pwd'
        result = host.DeviceConnect(switchName,
                                    hostConnHandle=hostTelnetSessionForSwitchBashShell,
                                    mgmtIpAddress=mgmtIpAddress)
        if result is None:
            LogOutput('error',
                             'Failed to connect to switch bash shell '
                             + switchName)
            continue
        LogOutput('info',
                         'Get to bash shell and executing bash command pwd '
                          + switchName)
        retStruct = \
            switch.DeviceInteract(connection=hostTelnetSessionForSwitchBashShell,
                                  command=command)
        print retStruct['buffer']

# cleanup
# Clear management IP on eth0 interface of the switch via console

LogOutput('info',
                 '################################################################################'
                 )
LogOutput('info',
                 'Clearing management IP on management interface eth0 to switch via console'
                  + switchName)
LogOutput('info',
                 '################################################################################'
                 )

mgmtIpAddress = '20.20.20.3'
netMask = 24

command = 'ip addr delete %s/%d dev eth0' % (mgmtIpAddress, netMask)

retStruct = switch.DeviceInteract(connection=switchConsoleConn,
                                  command=command)

if retStruct['returnCode']:
    LogOutput('error',
                     'Failed to clear mgmt interface on the switch '
                     + switchName)