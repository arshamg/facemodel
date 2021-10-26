## usdzconvert-docker

This is a Docker image for running Apple's USD tools.

The usdzconvert tool included in this repo is copied directly from USDPython 0.63; 
the full installer is available from developer.apple.com. 

The original license for USDPython is in LICENSE.txt.

### Example usage:

```bash 
# -- On host:
$ docker run -it --mount 'type=bind,source=/Users/me/Desktop/models,target=/mnt/models,ro' summertriangle/usdzconvert-docker

# -- In container:
$ cd /mnt/models
$ usdzconvert -iOS12 ./helmet.glb /tmp/helmet.usdz 
Input file: ./helmet.glb
Converting in iOS12 compatiblity mode.
Output file: /tmp/helmet.usdz
usdARKitChecker: [Pass] /tmp/helmet.usdz
```
