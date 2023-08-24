"""
"""
from argparse import ArgumentParser
from prometheus_client import make_wsgi_app
from prometheus_client.core import GaugeMetricFamily, REGISTRY
import requests
import systemd
from wsgiref.simple_server import make_server


class AirZoneCollector(object):
    EXCLUDES = ["name", "errors", "modes", "eco_adapt", "units"]
    HELP_STR = {
            "mode": "System Mode",
            "on": "System running",
            "temperature": "Temperature in Celcius degree",
            "roomTemp": "Temperature in Celcius degree",
            "humidity": "Relative percentage of humidity",
            "aq_mode": "Air Purifier mode",
            "aq_quality": "Estimated air quality",
            "cold_demand": "if the zone requires cooling",
            "head_demand": "if the zone requires heating",
            "setpoint": "requested temperature",
            }

    def collect(self):
        r = requests.post("http://" + self.airzonewebserver + "/api/v1/hvac",
                          None, {"systemID": 1, "zoneID": 0})
        if r.status_code == 200:
            for zone in r.json()['data']:
                for k, v in zone.items():
                    if k in self.EXCLUDES:
                        continue
                    help_str = self.HELP_STR[k] if k in self.HELP_STR else ""
                    g = GaugeMetricFamily("az_" + k, help_str, None, {"room"})
                    # We have silly precision for room temperature, round it
                    if k == "roomTemp":
                        v = round(v, 1)
                    g.add_metric([zone["name"]], str(v))
                    yield g


def main():
    ap = ArgumentParser()
    ap.add_argument("-p", "--port", type=int,
                    help="local WSGI Port", default="8000")
    ap.add_argument("-u", "--uri",
                    help="Webserver URI, for example \"airzone.local:3000\"",
                    default="airzone.local:3000")
    args = ap.parse_args()
    azc = AirZoneCollector()
    azc.airzonewebserver = args.uri
    REGISTRY.register(azc)

    app = make_wsgi_app()
    httpd = make_server('', args.port, app)
    systemd.daemon.notify(systemd.daemon.Notification.READY)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
