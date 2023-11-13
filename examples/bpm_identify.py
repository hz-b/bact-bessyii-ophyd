from bact_bessyii_ophyd.devices.pp.bpm import BPM

prefix = ""
bpm = BPM(prefix + "MDIZ2T5G", name="bpm")
if not bpm.connected:
    bpm.wait_for_connection()



# print("# ---- data")
# print("# ---- end data ")

threshold = 300
cnt = 0

while True:
    cnt +=1
    stat = bpm.trigger()
    stat.wait(3)
    data = bpm.read()
    print(f"read      {cnt}")
    for bpm_data in data['bpm_elem_data']['value']:
        xr = bpm_data['x']['pos_raw']
        yr = bpm_data['y']['pos_raw']
        name = bpm_data['name']
        # selected_name = "BPMZ5D4R"
        selected_name = "none"
        if abs(xr)  > threshold or abs(yr) > threshold or name == selected_name:
            print(f"{bpm_data['name']:20s}\t {xr: 6.0f}\t {yr: 6.0f}")
    # print(data['bpm_elem_data']['value'][-1])
    #break
