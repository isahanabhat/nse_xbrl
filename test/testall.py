from main_code import xbrl_parser
from main_code import xbrl_metric_trend

def testCaseEvaluater(test_case, filename):
    fileobj = open(filename, 'r')
    fileContents = fileobj.read()
    xbrl_parser_obj = xbrl_parser.XBRLCorporateFilingParser(symbol='x', xbrl_str=fileContents)
    for attr in test_case.keys():
        param = test_case[attr]
        value = xbrl_parser_obj.get(param[0], param[1])
        if attr == value:
            print("Test case passed for", param[0])
        else:
            print("Test failed")
            print("Expected: %s, Actual: %s" % (attr, value))
        print("=============================================")
    fileobj.close()


if __name__ == '__main__':
    file_bank = r'../data/BANKING_97822_965308_21102023041426.xml'
    file_default = r'../data/INDAS_97985_968429_26102023083837.xml'

    filename_1 = r"..\data\SHP_174992_773230_19012023040253_WEB.xml"
    filename_2 = r"..\data\SHP_176970_822215_17042023063024_WEB.xml"
    filename_3 = r"..\data\SHP_180207_897374_21072023041902_WEB.xml"
    filename_4 = r"..\data\SHP_182533_961547_19102023082402_WEB.xml"
    dataList = [filename_1, filename_2, filename_3, filename_4]

    test_cases_default = {"ASIANPAINT": ["symbol", "OneD"],
                          36961.0: ["profit_before_interest_and_tax", "FourD"],
                          "default": ["result_type", "OneD"],
                          1: ["face_value_of_share", "OneD"],
                          15075.1: ["EBIT", "OneD"],
                          17.78: ["EBIT Margin", "OneD"]
                          }

    test_cases_banking = {"ICICIBANK": ["symbol", "OneD"],
                          264933.2: ["profit_before_interest_and_tax", "FourD"],
                          "Banking Format": ["result_type", "OneD"],
                          2: ["face_value_of_share", "OneD"],
                          244824.4: ["EBIT", "OneD"],
                          60.16: ["EBIT Margin", "OneD"]
                          }

    print("Banking format:")
    testCaseEvaluater(test_cases_banking, file_bank)
    print("Default:")
    testCaseEvaluater(test_cases_default, file_default)

    dataStrings = []
    for i in dataList:
        fileobj = open(i, 'r')
        fileContents = fileobj.read()
        dataStrings.append(fileContents)
        fileobj.close()
    metric_trend = xbrl_metric_trend.MetricTrend(dataStrings)
    print(metric_trend.get('n_shareholders'))
