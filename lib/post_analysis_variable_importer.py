import csv
import os


class Config:
    def __init__(self, config_file):
        self.DIR, self.SCE, self.TOI, self.ROUTE, self.LAKE, self.MAP, self.STATS = self.read_config(config_file)

    def read_config(self, config_file):
        # read the config file and store the values in a dictionary using the csv module
        with open(config_file, mode='r') as file:
            reader = csv.reader(file)
            # remove comments starting with '#' and empty lines
            rows = [row for row in reader if row and not row[0].startswith('#')]
        
        # if value is number, change it to float or int
        for row in rows:
            if row[2].replace('.','',1).isdigit():
                if '.' in row[2]:
                    row[2] = float(row[2])
                else:
                    row[2] = int(row[2])
        # if value is boolean, change it to boolean
            try:
                if 'true' in row[2].lower() or 'false' in row[2].lower():
                    if row[2].lower() == 'true':
                        row[2] = True
                    elif row[2].lower() == 'false':
                        row[2] = False
            except:
                pass
        
        DIR = {}
        SCE = {}
        TOI = {}
        ROUTE = {}
        LAKE = {}
        MAP = {}
        STATS = {}

        for row in rows:
            section, parameter, value, note = row
            if section == 'DIR':
                DIR[parameter] = value
            elif section == 'SCE':
                SCE[parameter] = value
            elif section == 'TOI':
                TOI[parameter] = value
            elif section == 'ROUTE':
                ROUTE[parameter] = value
            elif section == 'LAKE':
                LAKE[parameter] = value
            elif section == 'MAP':
                MAP[parameter] = value
            elif section == 'STATS':
                STATS[parameter] = value


        return DIR, SCE, TOI, ROUTE, LAKE, MAP, STATS
    
    