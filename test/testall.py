from main_code import xbrl_parser

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

    testCaseEvaluater(test_cases_banking, file_bank)
    testCaseEvaluater(test_cases_default, file_default)
