import zwave


def main():
    zwave.check_zwave_network()


if __name__ == "__main__":
    main()


'''
## Compare DB(info) & REST(info)

{   battery: 100,
    controller: "Pi 1", "Pi 2", "Pi 3"
    humidity: 29,
    location: "A505",
    luminance: 6,
    motion: false,
    sensor: 3,
    temperature: 26.8,
    updateTime: 1526152996}
    
    
## Check battery
    if(battery <= 20%)
        print(bettry low)
        
## Check uptime
    if(updateTime < now - 1J)
        print(uptime error) => the sensor dont send (give) data anymore
    
'''