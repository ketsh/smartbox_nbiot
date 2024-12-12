from sendPackage import UDPSender


if __name__ == "__main__":
    udp = UDPSender()
    try:
        udp.close()
    except:
        pass
    udp.open("8988228066603096577")
    udp.send(command="Open Door", inputvar="0,11")
    udp.close()