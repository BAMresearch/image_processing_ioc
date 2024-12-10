# import epics # attention, pyepics cuts the path after 4 characters!
import caproto.threading.pyepics_compat as epics

epics.caput('image:ImagePathPrimary', "/mnt/vsi-db/Measurements/SAXS002/data/2024/20241118/20241118_1/beam_profile/eiger_0051112_data_000001.h5")
epics.caput('image:ImagePathSecondary', "/mnt/vsi-db/Measurements/SAXS002/data/2024/20241118/20241118_1/beam_profile_through_sample/eiger_0051113_data_000001.h5")

print(epics.caget("image:ratio"))
