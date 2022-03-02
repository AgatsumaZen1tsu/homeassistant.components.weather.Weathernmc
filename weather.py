from datetime import datetime, timedelta

from homeassistant.components.weather import (
    WeatherEntity, ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_TEMP, ATTR_FORECAST_TEMP_LOW, ATTR_FORECAST_TIME, ATTR_FORECAST_WIND_BEARING, ATTR_FORECAST_WIND_SPEED)

from homeassistant.const import (TEMP_CELSIUS, TEMP_FAHRENHEIT, CONF_API_KEY, CONF_NAME)

import requests
import json

VERSION = '1.0.0'
DOMAIN = 'weathernmc'

CONDITION_MAP = {
    '晴': 'sunny',
    '多云': 'cloudy',
    '局部多云': 'partlycloudy',    
    '阴': 'cloudy',
    '雾': 'fog',
    '中雾': 'fog',
    '大雾': 'fog',
    '小雨': 'rainy',
    '中雨': 'rainy',
    '大雨': 'pouring',
    '暴雨': 'pouring',
    '雾': 'fog',
    '小雪': 'snowy',
    '中雪': 'snowy',
    '大雪': 'snowy',
    '暴雪': 'snowy',
    '扬沙': 'fog',
    '沙尘': 'fog',
    '雷阵雨': 'lightning-rainy',
    '冰雹': 'hail',
    '雨夹雪': 'snowy-rainy',
    '大风': 'windy',
    '薄雾': 'fog',
    '雨': 'rainy',
    '雪': 'snowy',
    '9999': 'exceptional',
    
}

def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([NMCWeather(api_key=config.get(CONF_API_KEY),
                                        name=config.get(CONF_NAME, 'weathernmc'))])


class NMCWeather(WeatherEntity):

    def __init__(self, api_key: str,name: str):
        self._api_key = api_key
        self._name = name
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        skycon = self._realtime_data['weather']['info']
        return CONDITION_MAP[skycon]

    @property
    def temperature(self):
        return self._realtime_data['weather']['temperature']

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def humidity(self):
        return float(self._realtime_data['weather']['humidity']) 

    @property
    def wind_speed(self):
        return self._realtime_data['wind']['speed']

    @property
    def wind_bearing(self):
        return self._realtime_data['wind']['direct']

    @property
    def wind_speed(self):
        return self._realtime_data['wind']['power']


    @property
    def pressure(self):
        return round(float(self._realtime_data['weather']['airpressure']) / 100, 2)


    @property
    def attribution(self):
        return 'Powered by WWW.NMC.COM'

    @property
    def aqi(self):
        return self._air_data['data']['air']['aqi']

    @property
    def aqi_description(self):
        return self._air_data['data']['air']['aqi']
        
    @property
    def alert(self):
        return self._realtime_data['data']['real']['warn']['alert']

    @property
    def state_attributes(self):
        data = super(NMCWeather, self).state_attributes
        data['aqi'] = self.aqi 
        return data  

    @property
    def forecast(self):
        forecast_data = []
        for i in range(1, 7):
            time_str = self._forecast_data['data']['predict']['detail'][i]['date']
            data_dict = {
                ATTR_FORECAST_TIME: datetime.strptime(time_str, '%Y-%m-%d'),
                ATTR_FORECAST_CONDITION: CONDITION_MAP[self._forecast_data['data']['predict']['detail'][i]['day']['weather']['info']],
                ATTR_FORECAST_TEMP: self._forecast_data['data']['tempchart'][i+7]['max_temp'],
                ATTR_FORECAST_TEMP_LOW: self._forecast_data['data']['tempchart'][i+7]['min_temp'],
                ATTR_FORECAST_WIND_BEARING: self._forecast_data['data']['predict']['detail'][i]['day']['wind']['direct'],
                ATTR_FORECAST_WIND_SPEED: self._forecast_data['data']['predict']['detail'][i]['day']['wind']['power']
            }
            forecast_data.append(data_dict)

        return forecast_data


    def update(self):

        json_realtimetext = requests.get(str.format("http://www.nmc.cn/f/rest/real/56586")).content
        self._realtime_data = json.loads(json_realtimetext)

        json_forcasttext = requests.get(str.format("http://www.nmc.cn/rest/weather?stationid=56586")).content
        self._forecast_data = json.loads(json_forcasttext)

        json_airtext = requests.get(str.format("http://www.nmc.cn/rest/weather?stationid=56586")).content
        self._air_data = json.loads(json_airtext)