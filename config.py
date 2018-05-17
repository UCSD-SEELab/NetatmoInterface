import configparser

config1 = configparser.RawConfigParser()

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
# In addition, please note that using RawConfigParser's and the raw
# mode of ConfigParser's respective set functions, you can assign
# non-string values to keys internally, but will receive an error
# when attempting to write to a file or when you get it in non-raw
# mode. SafeConfigParser does not allow such assignments to take place.
config1.add_section('User')
config1.set('User', 'email', "mosterta@ucsd.edu")
config1.set('User', 'password', 'HealthyAging65')
config1.set('User', 'client_id', '5ada5ba50f21e17d048b465d')
config1.set('User', 'client_secret', 'kdBUhCMCEujWQg2EoQfMoansi')
config1.set('User', 'mac_address', '70:ee:50:20:be:50')
config1.set('User', 'broker_address', 'iot.eclipse.org')

# Writing our configuration file to 'config.cfg'
with open('config.cfg', 'w') as configfile:
    config1.write(configfile)