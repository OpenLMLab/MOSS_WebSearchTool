import argparse

import httpx
import msgpack  # type: ignore

parser = argparse.ArgumentParser(
    prog="stable diffusion client demo",
)
parser.add_argument(
    "-p", "--prompt", default="a photo of an astronaut riding a horse on mars"
)
parser.add_argument(
    "-o", "--output", default="stable_diffusion_result.jpg", help="output filename"
)
parser.add_argument(
    "--port",
    default=7002,
    type=int,
    help="service port",
)


args = parser.parse_args()
resp = httpx.post(
    f"http://10.176.52.114:{args.port}/inference",
    data=msgpack.packb(args.prompt),
    timeout=httpx.Timeout(20),
)
if resp.status_code == 200:
    data = msgpack.unpackb(resp.content)
    with open(args.output, "wb") as f:
        f.write(data)
else:
    print(f"ERROR: <{resp.status_code}> {resp.text}")