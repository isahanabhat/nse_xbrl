from nse_xbrl.main_code import xbrl_parser
import pandas as pd
import os

class MetricTrend:
    def __init__(self, listOfData, verbosity=1):
        self.verbosity = verbosity
        self.infoDict = []

        full_path = os.path.abspath(__file__)
        path_parts = full_path.split("\\")
        base_path = ""
        for i in range(0, len(path_parts) - 2):
            base_path += path_parts[i] + "\\"
        # print(base_path)

        file = base_path + r"data\nse_xbrl_attribute_map.xlsx"
        self.attributeMap = pd.read_excel(file, sheet_name='attribute_map_shp')
        self.resultType = 'any'

        # to get attribute map with that particular result type
        self.attribute_df = self.attributeMap.loc[
            self.attributeMap['result_type'].str.contains(self.resultType, na=False)]

        self.parsedDataList = []
        i = 0
        for dataString in listOfData:
            xbrl = xbrl_parser.XBRLCorporateFilingParser(symbol='x', xbrl_str=dataString)
            self.parsedDataList.append(xbrl.parsedDataFrame)
            i += 1

        if self.verbosity >= 1:
            print(self.attribute_df)
        if self.verbosity == 2:
            print("Data list:")
            print(self.parsedDataList)

    def get(self, attribute):
        for dataframe in self.parsedDataList:
            attributeName = self.attribute_df.loc[(self.attribute_df.attribute == attribute) &
                                                  (self.attribute_df['result_type'].str.contains(self.resultType,
                                                                                                 na=False))] \
                                                  .value_expr.reset_index(drop=True)
            df = dataframe.loc[(dataframe.Tags == attributeName[0])].reset_index(drop=True)
            parsedDataDict = df.set_index('contextRef')['Value'].to_dict()
            self.infoDict.append(parsedDataDict)

            if self.verbosity >= 1:
                print("Attribute Name = ", attributeName)
                print("---------------------------------------")
                print("next part\n",dataframe.loc[dataframe.Tags == 'DateOfReport'])
                print("---------------------------------------")
                print("Parsed dict: ")
                print(parsedDataDict)
                print("---------------------------------------")
        if self.verbosity == 2:
            print("Total list content:")
            print(self.infoDict)

        return self.infoDict