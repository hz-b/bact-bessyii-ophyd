from typing import List

from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder

from bact_mls_ophyd.devices.pp.bpmElem import BpmElementList

router = APIRouter()


@router.post("/", response_description="BPM Element Reading", status_code=status.HTTP_201_CREATED,
             response_model=BpmElementList)
def create_bpm_element_data(request: Request, bpm_elem: BpmElementList = Body(...)):
    bpm_elem = jsonable_encoder(bpm_elem)
    bpm_elem_read = request.app.database["bpmelements"].insert_one(bpm_elem)
    created_bpm_elem = request.app.database["bpmelements"].find_one(
        {"_id": bpm_elem_read.inserted_id}
    )
    return created_bpm_elem


@router.get("/", response_description="List all BPM Element Data", response_model=List[BpmElementList])
def list_bpm_element_data(request: Request):
    bpm_elems = list(request.app.database["bpmelements"].find(limit=100))
    return bpm_elems


@router.get("/{id}", response_description="Get a single bpm element data by id", response_model=BpmElementList)
def find_bpm_element(id: str, request: Request):
    if (bpm_elem := request.app.database["bpmelements"].find_one({"id": id})) is not None:
        return bpm_elem

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Element Data with ID {id} not found")
