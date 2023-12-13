import xml.etree.ElementTree as ET
import re
import pandas as pd

class XBRLCorporateFilingParser:
    def __init__(self, symbol, xbrl_str, exchange='nse', currency_unit=1E6, verbosity=1):
        self.verbosity = verbosity
        tree = ET.ElementTree(ET.fromstring(xbrl_str))
        root = tree.getroot()

        if self.verbosity >= 1:
            print(root.tag)
            print(root.attrib)

        pattern = r'[{}]'
        count = 0
        rowlist = []
        for child in root:
            tags = re.split(pattern, child.tag)
            attributes = child.attrib
            if 'in-bse-fin' in tags[1]:
                row = {'Tags': tags[-1]}
                for key, val in attributes.items():
                    row[key] = val
                row['Value'] = str(child.text)
                rowlist.append(row)
                count += 1
                if self.verbosity == 2:
                    print("Row appended:")
                    print(row, '\n')
        self.parsedDataFrame = pd.DataFrame(rowlist).reset_index(drop=False)

        attributeFile = r"..\data\nse_xbrl_attribute_map.xlsx"
        self.attributeMap = pd.read_excel(attributeFile)

        self.resultType = self.parsedDataFrame.loc[self.parsedDataFrame.Tags == 'ResultType']\
            .Value.reset_index(drop=True)
        if len(self.resultType) == 0:
            self.resultType = 'default'
        else:
            self.resultType = self.resultType[0]

        if self.verbosity >= 1:
            print('Result type: ', self.resultType)
        if self.verbosity == 2:
            print(count)
            for i in rowlist:
                print(i)


    def get(self, attribute, context):
        attributeName = self.attributeMap.loc[(self.attributeMap.attribute == attribute) &
                                              (self.attributeMap.result_type == self.resultType)]\
                        .value_expr.reset_index(drop=True)

        data = self.parsedDataFrame.loc[(self.parsedDataFrame.Tags == attributeName[0]) &
                                        (self.parsedDataFrame.contextRef == context)].reset_index(drop=True)
        if self.verbosity >= 1:
            print('Attribute: ', attribute)
            print('Actual attribute: ', attributeName)
            print('Context: ', context)
        return data.Value[0]


if __name__ == '__main__':
    file_bank = r'../data/BANKING_ICICIBANK.xml'
    file_default = r'../data/justSample.xml'
    fileobj = open(file_default, 'r')
    fileContents = fileobj.read()

    xbrl_parser = XBRLCorporateFilingParser(symbol='x', xbrl_str=fileContents)
    xbrl_parser.parsedDataFrame.to_csv(r"..\output\xbrl_data.csv", index=False)
    value = xbrl_parser.get('operating_revenue', 'OneD')
    print('Value: ', value)

    fileobj.close()
    exit()
