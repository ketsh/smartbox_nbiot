from flask import Flask, request, jsonify
from sendPackage import UDPSender

app = Flask(__name__)


@app.route('/open_door', methods=['GET'])
def open_door():
    boardID = request.args.get('boardID')
    doorID = request.args.get('doorID')
    simID = request.args.get('simID')
    if not boardID or not doorID:
        return jsonify({"error": "Missing boardID or doorID"}), 400

    inputvar = f"{boardID},{doorID}"
    udp = UDPSender()
    try:
        udp.close()
    except:
        pass
    udp.open(simID)
    udp.send(command="Open Door", inputvar=inputvar)
    udp.close()
    return jsonify({"status": "success"}), 200


@app.route('/open_all_doors', methods=['GET'])
def open_all_doors():
    simID = request.args.get('simID')
    maxBoardID = request.args.get('maxBoardID', default=1, type=int)  # Default to 1
    maxDoorID = request.args.get('maxDoorID', default=50, type=int)  # Default to 50

    # Validate inputs
    if maxBoardID < 0 or maxDoorID < 1:
        return jsonify({"error": "maxBoardID must be >= 0 and maxDoorID must be >= 1"}), 400

    udp = UDPSender()
    try:
        udp.close()
    except:
        pass
    udp.open(simID)

    for boardID in range(maxBoardID + 1):  # 0 to maxBoardID inclusive
        for doorID in range(1, maxDoorID + 1):  # 1 to maxDoorID inclusive
            inputvar = f"{boardID},{doorID}"
            udp.send(command="Open Door", inputvar=inputvar)

    udp.close()
    return jsonify(
        {"status": "success", "message": f"All doors opened for boards 0-{maxBoardID} and doors 1-{maxDoorID}"}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)