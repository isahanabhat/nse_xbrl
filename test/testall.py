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

def get_context_test(test_case, filename):
    fileobj = open(filename, 'r')
    fileContents = fileobj.read()
    xbrl_parser_obj = xbrl_parser.XBRLCorporateFilingParser(symbol='x', xbrl_str=fileContents)
    value = ""
    for attr in test_case.keys():
        param = test_case[attr]
        value = xbrl_parser_obj.get_contexts(param[0])
    fileobj.close()
    return value

def get_all_context(filename):
    fileobj = open(filename, 'r')
    fileContents = fileobj.read()
    xbrl_parser_obj = xbrl_parser.XBRLCorporateFilingParser(symbol='x', xbrl_str=fileContents)
    value = xbrl_parser_obj.get_all_attributes()
    fileobj.close()
    return value

if __name__ == '__main__':
    file_bank = r'../data/BANKING_97822_965308_21102023041426.xml'
    file_default = r'../data/INDAS_97985_968429_26102023083837.xml'

    filename_1 = r"..\data\SHP_174992_773230_19012023040253_WEB.xml"
    filename_2 = r"..\data\SHP_176970_822215_17042023063024_WEB.xml"
    filename_3 = r"..\data\SHP_180207_897374_21072023041902_WEB.xml"
    filename_4 = r"..\data\SHP_182533_961547_19102023082402_WEB.xml"
    filename_5 = r"..\data\SHP_186842_1092869_15042024070218_WEB.xml"
    filename_6 = r"..\data\SCR_1137910_24052024063625_WEB.xml"
    # dataList = [filename_1, filename_2, filename_3, filename_4, filename_5]
    dataList = [filename_5]

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

    """print("Banking format:")
    testCaseEvaluater({"Banking Format": ["result_type", "OneD"]}, file_bank)
    print("Default:")
    testCaseEvaluater(test_cases_default, file_default)"""

    # print("get_contexts test: ")
    context = get_context_test({"Banking Format": ["n_shareholders"]}, filename_5)
    # print(context)

    allContext = get_all_context(filename_5)
    print(allContext)

    """dataStrings = []
    fileContents = ""
    for i in dataList:
        fileobj = open(i, 'r')
        fileContents = fileobj.read()
        dataStrings.append(fileContents)
        fileobj.close()
    metric_trend = xbrl_metric_trend.MetricTrend(dataStrings)
    #print(metric_trend.get('n_shareholders'))
    print(metric_trend.get('is_psu'))

    xbrl_obj = xbrl_parser.XBRLCorporateFilingParser(symbol='x', xbrl_str=fileContents)
    # print(xbrl_obj.get('is_psu', 'OneI'))
    print()"""
