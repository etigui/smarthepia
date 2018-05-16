from pysolar.solar import *


# https://astral.readthedocs.io/en/stable/index.html

import datetime
date = datetime.datetime.utcnow()
print(date)
print(get_altitude(46.2092845, 6.1355531, date))

print(get_azimuth(46.2092845, 6.1355531, date))
#date = datetime.datetime(2007, 2, 18, 15, 13, 1, 130320, tzinfo=datetime.timezone.utc)
#print(get_altitude(42.206, -71.382, date))