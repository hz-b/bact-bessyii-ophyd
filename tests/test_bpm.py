import pytest
from bact_bessyii_ophyd.devices.raw.bpm import BPM


async def test_bpm():
    """read bpm data"""
    prefix = "Pierre:DT:"
    prefix = ""


    bpm = BPM(prefix + "MDIZ2T5G", name="bpm")

    label = bpm.count.name
    await bpm.connect(timeout=1)
    await bpm.new_data_available()
    data = await bpm.read()
    v1 = data[label]["value"]
    await bpm.new_data_available()
    data = await bpm.read()
    v2 = data[label]["value"]

    print(v1, v2)
    assert v1 + 1 == v2


async def test_bpm_aioca():
    """connection using bdata"""
    from aioca import caget, connect

    cnt_name = "MDIZ2T5G:count"
    bdata_name = "MDIZ2T5G:bdata"

    await connect(cnt_name, bdata_name)
    tsk_cnt = caget("MDIZ2T5G:count")
    tsk_bdata = caget("MDIZ2T5G:bdata")
    cnt = await tsk_cnt
    bdata = await tsk_bdata


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_bpm_aioca())
    asyncio.run(test_bpm())
