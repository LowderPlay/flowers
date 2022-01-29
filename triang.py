import asyncio

from wled import WLED


async def main():
    async with WLED("192.168.0.25") as led:
        while True:
            device = await led.update()
            dist = 10 ** ((-40 - device.info.wifi.rssi)/(10*2))
            print(device.info.wifi, dist)

            await led.master(on=dist < 5, brightness=100)
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
