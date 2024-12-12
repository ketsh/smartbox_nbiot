from flask import Flask, request, jsonify
from sendPackage import UDPSender

app = Flask(__name__)

@app.route('/open_door', methods=['GET'])
def open_door():
    boardID = request.args.get('boardID')
    doorID = request.args.get('doorID')
    if not boardID or not doorID:
        return jsonify({"error": "Missing boardID or doorID"}), 400

    inputvar = f"{boardID},{doorID}"
    udp = UDPSender()
    try:
        udp.close()
    except:
        pass
    udp.open(boardID)
    udp.send(command="Open Door", inputvar=inputvar)
    udp.close()
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)