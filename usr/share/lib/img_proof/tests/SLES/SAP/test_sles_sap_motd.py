def test_sles_sap_motd(host):
    motd = host.file('/etc/motd')
    assert motd.exists
    assert motd.contains('for SAP Applications')
