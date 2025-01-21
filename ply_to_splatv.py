# MIT Licensed (c) 2024 Christopher Howard
# Adapted from Kevin Kwok's ply2spat.py

import math
from plyfile import PlyData
import numpy as np
import argparse
import json
from io import BytesIO

HDR_PROTO="""[{"type":"splat","size":30146560,"texwidth":4096,"texheight":460,"cameras":[{"id":0,"img_name":"00001","width":1959,"height":1090,"position":[-3.0089893469241797,-0.11086489695181866,-3.7527640949141428],"rotation":[[0.876134201218856,0.06925962026449776,0.47706599800804744],[-0.04747421839895102,0.9972110940209488,-0.057586739349882114],[-0.4797239414934443,0.027805376500959853,0.8769787916452908]],"fy":1164.6601287484507,"fx":1159.5880733038064}]}]"""
MAGIC=0x674b


def packHalf2x16(a):

    x=a[np.ix_(*[range(0,i,2) for i in a.shape])]
    y=a[np.ix_(*[range(1,i,2) for i in a.shape])]

    assert (x.shape == y.shape)
    assert (len(x.shape) == 1)

    # Allocate output data
    n = x.shape[0]
    uint32_data = np.ndarray((n,), dtype=np.uint32)

    # Create view
    f16_data = np.lib.stride_tricks.as_strided(
        uint32_data.view(dtype=np.float16),
        shape=(2, n),
        strides=(1 * 2, 2 * 2),
        writeable=True,
    )

    # Convert from whatever type x and y use
    f16_data[0] = x
    f16_data[1] = y

    return uint32_data

def process_ply_to_splatv(ply_file_path):
    plydata = PlyData.read(ply_file_path)
    vert = plydata["vertex"]
    sorted_indices = np.argsort(
        -np.exp(vert["scale_0"] + vert["scale_1"] + vert["scale_2"])
        / (1 + np.exp(-vert["opacity"]))
    )
    buffer = BytesIO()

    #BUILD HEADER
    hdr=json.loads(HDR_PROTO)

    vertexCount=len(sorted_indices)
    texwidth= 1024*4
    texheight= math.ceil((4 * vertexCount) / texwidth)
    size=texwidth * texheight * 16

    hdr[0]['texwidth']=texwidth
    hdr[0]['texheight'] = texheight
    hdr[0]['size']= size
    hdrstr=json.dumps(hdr,separators=(',', ':'))

    #write magic
    buffer.write(np.array([MAGIC,len(hdrstr)],dtype=np.uint32).tobytes())
    #write header
    buffer.write(bytes(hdrstr,'utf-8'))

    for idx in sorted_indices:
        v = plydata["vertex"][idx]

        position = np.array([v["x"], v["y"], v["z"]], dtype=np.float32)

        rotscales = np.array(
            [v["rot_0"], v["rot_1"], v["rot_2"], v["rot_3"],
                    math.exp(v["scale_0"]), math.exp(v["scale_1"]), math.exp(v["scale_2"]),0.0],
                  dtype=np.float32,
        )
        rotscales[7] = 0.0

        fdc = np.array(
                [max(0, min(255, v["f_dc_0"] * 255)),
                 max(0, min(255, v["f_dc_1"] * 255)),
                 max(0, min(255, v["f_dc_2"] * 255)),
                 (1 / (1 + math.exp(-v["opacity"]))) * 255],
                dtype=np.uint8,
            )

        motion = np.array(
            [v["motion_0"], v["motion_1"], v["motion_2"],v["motion_3"],
                   v["motion_4"], v["motion_5"], v["motion_6"],v["motion_7"],
                   v["motion_8"], 0.0          , v["omega_0"] ,v["omega_1"] ,
                   v["omega_2"], v["omega_3"], v["trbf_center"],math.exp(v["trbf_scale"])],
            dtype=np.float32,
        )

        #asdaf

        buffer.write(position.tobytes())
        buffer.write(packHalf2x16(rotscales).tobytes())
        buffer.write(fdc.tobytes())
        buffer.write(packHalf2x16(motion).tobytes())

    return buffer.getvalue()


def save_splat_file(splat_data, output_path):
    with open(output_path, "wb") as f:
        f.write(splat_data)


def main():
    parser = argparse.ArgumentParser(description="Convert PLY files to SPLATV format.")
    parser.add_argument(
        "input_files", nargs="+", help="The input PLY files to process."
    )
    parser.add_argument(
        "--output", "-o", default="output.splat", help="The output SPLAT file."
    )
    args = parser.parse_args()
    for input_file in args.input_files:
        print(f"Processing {input_file}...")
        splat_data = process_ply_to_splatv(input_file)
        output_file = (
            args.output if len(args.input_files) == 1 else input_file + ".splatv"
        )
        save_splat_file(splat_data, output_file)
        print(f"Saved {output_file}")


if __name__ == "__main__":
    main()