def test_server(control):
    control.main(command="server", argv=["stop"])

    control.main(command="server", argv=["stop"])

    print ("test_server")
    pass
