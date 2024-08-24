from mcstatus import JavaServer  # For Java Edition servers
import time
def checki(srvip, serverport):
    try:
        server = JavaServer(srvip, serverport)
        status = server.status()  # Use server.query() if you need query data
        return {
            'online': True,
            'players': status.players.online,
            'version': status.version.name,
        }
    except Exception as e:
        return {
            'online': False,
            'error': str(e)
        }
class minestats:


    def check(serverip, srvport):
        #host = 'play.chilshop.ir'  # Replace with your Minecraft server IP
        #port = 29211  # Default Minecddraft port

        while True:
            status = checki(serverip, srvport)
            if status['online']:
                print(f"Server is online. Players: {status['players']}. Version: {status['version']}")
            else:
                print(f"Server is offline or unreachable. Error: {status.get('error', 'Unknown error')}")
            time.sleep(60)  # Check every 60 seconds

