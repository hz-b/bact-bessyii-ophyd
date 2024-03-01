
import jsons
import pymongo
import uvicorn
from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
import logging
from bact_mls_ophyd.devices.pp import bpm_element_controller
from bact_mls_ophyd.devices.pp.bpm import BPM
from custom.lat2db.controller import machine_controller

app = FastAPI()
config = dotenv_values("../.env")
app.include_router(bpm_element_controller.router, tags=["bpmelements"], prefix="/bpmelem")
app.mongodb_client = MongoClient("mongodb://127.0.0.1:27017/")
app.database = app.mongodb_client["bessyii"]

logger = logging.getLogger("bact")

if __name__ == "__main__":
    # print("#--------")
    # print(bpm_config_data().dtypes)

    # print(mlsinit.bpm[0])
    # mlsinit.bpm
    # how to combine it with the BPM test of the raw type
    prefix = "Pierre:DT:"
    # bpm = BPM("BPMZ1X003GP", name="bpm")
    bpm = BPM(prefix + "MDIZ2T5G", name="bpm")
    if not bpm.connected:
        bpm.wait_for_connection()
    stat = bpm.trigger()
    stat.wait(3)
    data = bpm.read()

    from starlette.testclient import TestClient
    with TestClient(app) as client:
        response = client.post("/bpmelem/", json=jsons.dump(data))
        assert response.status_code == 201