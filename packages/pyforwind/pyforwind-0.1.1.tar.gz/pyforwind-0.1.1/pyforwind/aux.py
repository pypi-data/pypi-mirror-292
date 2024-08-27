import numpy as np

def writeBLgrid(FileName, velocity, dy, dz, dt, zOffset, z0, SummVars):
    fileFmt = 'int16'

    fc = 4  # should be 4 to allow turbulence intensity to be stored in the header
    lat = 0  # latitude (deg)

    zHub = SummVars[0]  # hub height [m]
    MFFWS = SummVars[2]  # mean full-field wind speed
    TI_U = SummVars[3]  # Turbulence Intensity of u component (%)
    TI_V = SummVars[4]  # Turbulence Intensity of v component (%)
    TI_W = SummVars[5]  # Turbulence Intensity of w component (%)

    nt, nffc, ny, nz = velocity.shape  # determin dimensions of windfield, e.g. [1286,3,23,23]

    z1 = zHub - dz * (nz - 1) / 2  # this is the bottom of the grid

    dx = dt * MFFWS  # delta x in m
    nt_header = int(nt / 2)  # half the number of time steps

    len_FileName = len(FileName)
    ending = FileName[-4:]

    if ending.lower() == '.wnd':
        FileName = FileName[:-4]

    with open(f"{FileName}.wnd", 'wb') as fid_wnd:
        fid_wnd.write(np.int16(-99))  # number of components
        fid_wnd.write(np.int16(fc))  # should be 4 to allow turbulence intensity to be stored in the header
        fid_wnd.write(np.int32(nffc))  # number of components (should be 3)
        fid_wnd.write(np.float32(lat))  # latitude (deg)
        fid_wnd.write(np.float32(z0))  # Roughness length (m)
        fid_wnd.write(np.float32(zOffset))  # Reference height (m) = Z(1) + GridHeight / 2.0
        fid_wnd.write(np.float32(TI_U))  # Turbulence Intensity of u component (%)
        fid_wnd.write(np.float32(TI_V))  # Turbulence Intensity of v component (%)
        fid_wnd.write(np.float32(TI_W))  # Turbulence Intensity of w component (%)

        fid_wnd.write(np.float32(dz))  # delta z in m
        fid_wnd.write(np.float32(dy))  # delta y in m
        fid_wnd.write(np.float32(dx))  # delta x in m
        fid_wnd.write(np.int32(nt_header))  # half the number of time steps
        fid_wnd.write(np.float32(MFFWS))  # mean full-field wind speed

        fid_wnd.write(np.zeros(3, dtype=np.float32))  # unused variables (for BLADED): write zeros
        fid_wnd.write(np.zeros(2, dtype=np.int32))  # unused variables (for BLADED): write zeros
        fid_wnd.write(np.int32(nz))  # number of points in vertical direction
        fid_wnd.write(np.int32(ny))  # number of points in horizontal direction
        fid_wnd.write(np.zeros(3 * (nffc - 1), dtype=np.int32))  # unused variables (for BLADED): write zeros

    Scale = 0.00001 * MFFWS * SummVars[3:6]
    Offset = [MFFWS, 0, 0]

    if SummVars[1] > 0:  # clockwise rotation
        y_ix = np.arange(ny - 1, -1, -1)  # flip the y direction
    else:
        y_ix = np.arange(ny)

    v = np.zeros(nz * ny * nffc, dtype=np.int16)

    with open(f"{FileName}.wnd", 'ab') as fid_wnd:
        for it in range(nt):
            cnt = 0
            for iz in range(nz):
                for iy in y_ix:
                    for k in range(nffc):
                        v[cnt] = (velocity[it, k, iy, iz] - Offset[k]) / Scale[k]
                        cnt += 1
            fid_wnd.write(v.tobytes())