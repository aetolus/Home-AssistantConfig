import appdaemon.plugins.hass.hassapi as hass
#
# Crypto Arbritrage
#
# Args:
#


class CryptoArbitrage(hass.Hass):

    def initialize(self):
        global oldDifference
        oldDifference = 0
        self.listen_state(self.check_arbitrage, entity='sensor.btcmarkets_xrp')
        self.listen_state(self.check_arbitrage, entity='sensor.kraken_xrp')

    def check_arbitrage(self, entity, attribute, old, new, kwargs):
        global oldDifference
        # Load notifications app
        notifications = self.get_app("notifications")
# Calculate Percentage Difference
        btcm = self.get_state('sensor.btcmarkets_xrp')
        kraken = self.get_state('sensor.kraken_xrp')
        kraken = kraken[2:7]
        exchangerate = self.get_state('sensor.exchange_rate')
        krakenaud = float(kraken) * float(exchangerate)
        increase = float(btcm) - float(krakenaud)
        percentagedifference = float(increase) / float(krakenaud) * 100
        percentagedifference = float(percentagedifference)
# Store Difference
        if percentagedifference > 10 and oldDifference < 10:
            self.call_service("mqtt/publish", topic="notifications/newmsg", payload='Arbitrage gap is greater than 10%')
            oldDifference = percentagedifference
        elif percentagedifference > 5 and oldDifference < 5:
            self.call_service("mqtt/publish", topic="notifications/newmsg", payload='Arbitrage gap is greater than 5%')
            oldDifference = percentagedifference
        elif percentagedifference < 10 and oldDifference > 10:
            self.call_service("mqtt/publish", topic="notifications/newmsg", payload='Arbitrage gap has dropped below 10%')
            oldDifference = percentagedifference
        elif percentagedifference < 5 and oldDifference > 5:
            self.call_service("mqtt/publish", topic="notifications/newmsg", payload='Arbitrage gap has dropped below 5%')
            oldDifference = percentagedifference