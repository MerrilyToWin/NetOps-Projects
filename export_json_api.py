from flask import Flask, jsonify
import pymongo

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["ztp_project"]

@app.route("/compliance")
def get_compliance():
    data = list(db.compliance_results.find({}, {"_id":0}))
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

