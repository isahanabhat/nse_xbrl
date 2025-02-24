import xml.etree.ElementTree as ET
import re
import pandas as pd
import os

class XBRLCorporateFilingParser:
    def __init__(self, symbol, xbrl_str, exchange='nse', currency_unit=1E6, verbosity=0):
        self.verbosity = verbosity
        self.currency_unit = currency_unit
        tree = ET.ElementTree(ET.fromstring(xbrl_str))
        root = tree.getroot()
        self.type = ''

        pattern = r'[{}]'
        count = 0
        rowlist = []
        for child in root:
            tags = re.split(pattern, child.tag)
            attributes = child.attrib

            if 'in-bse-fin' in tags[1]:
                self.type = 'fin'
            elif 'in-bse-shp' in tags[1]:
                self.type = 'shp'

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

        # to get the attribute map
        full_path = os.path.abspath(__file__)
        path_parts = full_path.split("\\")
        base_path= ""
        for i in range(0, len(path_parts) - 2):
            base_path += path_parts[i] +"\\"
        # print(base_path)
        attributeFile = base_path + r"data\nse_xbrl_attribute_map.xlsx"

        if self.type == 'fin':
            self.attributeMap = pd.read_excel(attributeFile, sheet_name='attribute_map_fr')
            self.resultType = self.parsedDataFrame.loc[self.parsedDataFrame.Tags == 'ResultType'] \
                .Value.reset_index(drop=True)
            if len(self.resultType) == 0:
                self.resultType = 'default'
            else:
                self.resultType = self.resultType[0]

        elif self.type == 'shp':
            self.attributeMap = pd.read_excel(attributeFile, sheet_name='attribute_map_shp')
            self.resultType = 'any'

        # to get the dataframe which has the result types
        self.attribute_df = self.attributeMap.loc[
            self.attributeMap['result_type'].str.contains(self.resultType, na=False)]

        # save to csv
        directory = base_path + r"output"
        if not os.path.exists(directory):
            os.mkdir(directory)
        scr_output_file = base_path + r"output\xbrl_data_1.csv"
        if self.verbosity >= 1:
            self.parsedDataFrame.to_csv(scr_output_file)

        if self.verbosity >= 1:
            print("Root tag:", root.tag)
            print("Root attribute:", root.attrib)
            print('Result type: ', self.resultType)
            print("Type = ", self.type)
            print("Count = ", count)
            print("attribute_df: ")
            print(self.attribute_df)
        if self.verbosity == 2:
            for i in rowlist:
                print("Current row: ", i)

    def calcXbrl_recursion(self, attribute, context):
        formula = self.attribute_df.loc[(self.attribute_df.attribute == attribute) &
                                        (self.attributeMap['result_type'].str.contains(self.resultType, na=False))] \
            .value_expr.reset_index(drop=True)[0]
        pattern = "[\[\]]"
        formulaList = re.split(pattern, formula)
        formulaString = ""

        operands = dict(zip(self.attribute_df.attribute, self.attribute_df.attribute_type))

        if self.verbosity >= 1:
            print("attribute_df:")
            print(self.attribute_df)
            print("Formula:", formulaList)
            print("Operands: ")
            print(operands)

        for val in formulaList:
            if val in list(operands.keys()) and operands[val] == 'raw_xbrl':
                actualAttribute = self.attribute_df.loc[(self.attribute_df.attribute == val) &
                                                        (self.attribute_df['result_type'].str.contains(self.resultType,
                                                                                                       na=False))] \
                    .value_expr.reset_index(drop=True)[0]
                if self.verbosity >= 1:
                    print("series for numVal:")
                    print(self.parsedDataFrame.loc[(self.parsedDataFrame.Tags == actualAttribute) &
                                                   (self.parsedDataFrame.contextRef == context)].Value.reset_index(
                        drop=True))

                numVal = self.parsedDataFrame.loc[(self.parsedDataFrame.Tags == actualAttribute) &
                                                  (self.parsedDataFrame.contextRef == context)].Value.reset_index(
                    drop=True)[0]

                formulaString += numVal
            elif val in list(operands.keys()) and operands[val] == 'calc_xbrl':
                tempVal = str(self.calcXbrl_recursion(val, context))
                formulaString += tempVal
            else:
                formulaString += val
        # Last step to check for any dangerous command
        if self.verbosity >= 1:
            print("evaluation now: ", formulaString)
        assert 'os' not in formulaString and 'system' not in formulaString, \
            'Aborting!!! Dangerous command: %s' % formulaString
        return eval(formulaString)

    def get(self, attribute, context):
        # attribute map with particular attribute & result type
        x = self.attribute_df.loc[(self.attribute_df.attribute == attribute) &
                                  (self.attributeMap['result_type'].str.contains(self.resultType, na=False))] \
            .reset_index(drop=True)
        if self.verbosity >= 1:
            print("x dataframe:")
            print(x)

        if x.attribute_type[0] == 'raw_xbrl':
            attributeName = self.attribute_df.loc[(self.attribute_df.attribute == attribute) &
                                                  (self.attribute_df['result_type'].str.contains(self.resultType,
                                                                                                 na=False))] \
                .value_expr.reset_index(drop=True)

            if attributeName[0] == "ResultType" and self.resultType == 'default':
                resultValue = 'default'
            else:
                data = self.parsedDataFrame.loc[(self.parsedDataFrame.Tags == attributeName[0]) &
                                                (self.parsedDataFrame.contextRef == context)].reset_index(drop=True)
                resultValue = data.Value[0]
                if self.verbosity >= 1:
                    print('\nAttribute: ', attribute)
                    print('\nActual attribute: ', attributeName[0])
                    print('\nContext: ', context)
                    print("\nData:")
                    print(data)

        elif x.attribute_type[0] == 'calc_xbrl':
            resultValue = self.calcXbrl_recursion(x.attribute[0], context)
            if self.verbosity >= 1:
                print("Calculated value = ", resultValue)
        else:
            return float('nan')

        if x.value_type[0] == 'string':
            if self.verbosity >= 1:
                print("Result (string) = ", resultValue)
            return str(resultValue)
        elif x.value_type[0] == 'float':
            return round((float(resultValue)) / self.currency_unit, 2)
        elif x.value_type[0] == 'ratio':
            return round(float(resultValue), 2)
        elif x.value_type[0] == 'int':
            return int(float(resultValue))
        elif x.value_type[0] == 'boolean':
            if self.verbosity >= 1:
                print("Result (bool) = ", resultValue)
            return bool(resultValue)

    def get_contexts(self, attribute):
        x = self.attribute_df.loc[(self.attribute_df.attribute == attribute) &
                                  (self.attributeMap['result_type'].str.contains(self.resultType, na=False))] \
            .reset_index(drop=True)
        if self.verbosity >= 1:
            print("ATTRIBUTE = ", attribute)
            print("\n\nX dataframe: ")
            print(x)
        attributeName = self.attribute_df.loc[(self.attribute_df.attribute == attribute)&
                                              (self.attribute_df['result_type'].str.contains(self.resultType, na=False))] \
            .value_expr.reset_index(drop=True)


        data = self.parsedDataFrame.loc[(self.parsedDataFrame.Tags == attributeName[0])].reset_index(drop=True)
        if self.verbosity >= 1:
            print("attributeName[0] = ", attributeName[0])
            print('\nAttribute: ', attribute)
            print('Actual attribute: ', attributeName[0])
            print("Data:")
            print(data)
            print("\ncolumns = ", data.columns)
        return data["contextRef"].unique()

    def get_all_attributes(self):
        context_list = list(self.parsedDataFrame["contextRef"].unique())
        raw_data_dict = {}
        for context in context_list:
            data = self.parsedDataFrame.loc[self.parsedDataFrame["contextRef"] == context][["Tags", "Value"]].reset_index(drop=True)
            # print("\n",data)
            item = {}
            for row in data.itertuples():
                item[row.Tags] = row.Value
            raw_data_dict[context] = item
        return raw_data_dict


if __name__ == '__main__':
    print()
