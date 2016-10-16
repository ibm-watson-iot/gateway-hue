# IoT Gateway Application for Phillips Hue

Connect your Phillips Hue Bridge to Watson IoT.

- [IBM Watson IoT](https://internetofthings.ibmcloud.com)
- [Phillips Hue](http://www2.meethue.com/)

## Lights

### Automatic Device Registration

Any new type of light connected to your Hue bridge will be auto-registered as a new device type in Watson IoT:

- ``id`` is set to the ``modelid`` reported by Hue
- ``deviceInfo.description`` is set to the ``type`` reported by Hue
- ``deviceInfo.manufacturer`` is set to the ``manufacturername`` reported by Hue
- ``deviceInfo.model`` is set to the ``modelid`` reported by Hue

Likewise, all devices connected to the bridge will be auto-registered by the gateway application:

- ``typeId`` is set to the ``modelid`` reported by Hue
- ``deviceId` is set to the ``uniqueid`` reported by Hue, with ":" replaced by "-" as the delimiter
- ``deviceInfo.description`` is set to the ``type`` reported by Hue
- ``deviceInfo.fwversion`` is set to the ``swversion`` reported by Hue
- ``deviceInfo.manufacturer`` is set to the ``manufacturername`` reported by Hue
- ``deviceInfo.model`` is set to the ``modelid`` reported by Hue


### Events

State updates are published to Watson IoT every 60 seconds (althought this can easily be changed).  For every light connected to your Hue bridge the 
gateway will relay a state event containing all the state data available from your Hue bridge:

```json
{
  "on": true, 
  "hue": 14910, 
  "colormode": "ct", 
  "effect": "none", 
  "alert": "none", 
  "xy": [0.4596, 0.4105], 
  "reachable": true, 
  "bri": 254, 
  "ct": 369, 
  "sat": 144
}
```

### Commands

This version of the gateway only supports publishing state events.  Command control will be added in the future.
