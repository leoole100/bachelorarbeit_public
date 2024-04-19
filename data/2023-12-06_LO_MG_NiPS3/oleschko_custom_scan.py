#use_autocreated_file:#0#locked:#0#
"""
created: 06.12.2023 Leon Oleschko

TODO: set magnet heater to persist after measurement
"""

FIELDS = np.arange(9.8, 10, .1)
ANGLES = np.linspace(0, 45, 5)
file = MeasurementFile(
    "R:/Raw_data/10T/y2023/m12/2023-12-06_LO_MG_NiPS3/d005_script_test"
)
APT_DEVICE = 83839391 

FIELD_MAX = 10

def pre_measurement():

    assert np.abs(FIELDS).max() <= FIELD_MAX,\
        f"fields magnitude must be <= FIELD_MAX={FIELD_MAX}"

    print(f"magnetic fields:\t{FIELDS}")
    print(f"detector angles:\t{ANGLES}")
    print(f"measurements:\t{len(FIELDS)*len(ANGLES)}")
    print(f"time per:\t{spectrometer.get_measurement_time():.2f} s")
    time = spectrometer.get_measurement_time()*len(FIELDS)*len(ANGLES)/60
    print(f"total time:\t{time//60:.0f}:{time%60:.0f} h")
    print(f"saving to:\t{file.filename}")
    
def post_measurement():
    file.close()

def measurement():
    progress(0)
    for i, field in enumerate(FIELDS):
        magnet.set_field(field) # is blocking

        for j, angle in enumerate(ANGLES):
            progress((i * len(ANGLES) + j) / (len(FIELDS) * len(ANGLES)))
            
            apt.move_absolute(APT_DEVICE, angle)
            while not apt.is_stopped(APT_DEVICE): ...


            spectrometer.start_acquisition()
            while spectrometer.acquisition_status() != 'idle': ...
            wavelength, counts = spectrometer.get_latest_data()

            position = [anc350.get_position(ax) for ax in anc350.axes()]

            file.save_snapshot(
                magnet_field=field,
                apt_angle=angle,
                wavelength=wavelength,
                counts=counts,
                temperature=oxford_itc.get_T(),
                time=time.time(),
                position=position,
            )

    progress(1)


pre_measurement()
try: 
    measurement()
finally:
    post_measurement()