from bact_bessyii_ophyd.devices.pp.power_converter import ResettingPowerConverter


async def test_stop():
    pc = ResettingPowerConverter(prefix="Pierre:DT:VS3P2T1R:", atol=1e-2, rtol=1e-4,
                                 ref_val_suffix="set", timeout=1.0)
    await pc.connect(timeout=1)

    # set it to a defined vale
    await pc.set(0.0, timeout=2)
    val = await pc.readback.get_value()
    assert val == 0.0


    async def test_func():
        await pc.set(2, timeout=2)
        val = await pc.readback.get_value()
        assert val == 2.0

        await pc.stop()
        val = await pc.readback.get_value()
        print("stopped", val)
        assert val == 0.0

    try:
        await pc.stage()
        await test_func()
    finally:
        await pc.unstage()

async def main():
    pc = ResettingPowerConverter(prefix="Pierre:DT:VS3P2T1R:", atol=1e-2, rtol=1e-4)
    await pc.connect(timeout=1)
    data = await pc.read()
    print("start  ", data)
    await pc.set(0.0, timeout=2)
    data = await pc.read()
    print("set 0  ", data)
    await pc.set(0.2, timeout=2)
    data = await pc.read()
    print("set 0.2", data)
    await pc.set(0.0, timeout=2)
    data = await pc.read()
    print("set 0.0", data)


if __name__ == "__main__":
    import asyncio
    # asyncio.run(main())
    asyncio.run(test_stop())