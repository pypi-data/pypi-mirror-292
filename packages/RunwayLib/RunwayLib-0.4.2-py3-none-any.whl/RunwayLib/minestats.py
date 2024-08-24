from mcstatus import JavaServer
import time

def checki(serverip, serverport):
    try:
        server = JavaServer(serverip, serverport)
        status = server.status()
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
    @staticmethod
    def check(serverip, serverport):
        while True:
            status = checki(serverip, serverport)
            if status['online']:
                print(f"Server is online. Players: {status['players']}. Version: {status['version']}")
            else:
                print(f"Server is offline or unreachable. Error: {status.get('error', 'Unknown error')}")
            time.sleep(60)  # Check every 60 seconds

