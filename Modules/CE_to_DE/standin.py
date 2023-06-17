import os
from pprint import pprint

BOM_folder = '/Users/jzhang14/GitHub/Pluto-DC-BOM'

file_list = [
    './RBOAccount/bom/account.bom',
    './RBOAccount/bom/wallet.bom',
    './RBOCache/bom/FlexKey.bom',
    './RBOCache/bom/GenericCache.bom',
    './RBOIRuleResult/bom/result.bom',
    './RBOMisc/bom/ctxrequest.bom',
    './RBONBCollection/bom/nbcollection.bom',
    './RBORisk/bom/riskdata.bom',
    './RBORisk/bom/riskprofile.bom',
    './RBOTxn/bom/transaction.bom'
]

bom_file_count = len(file_list)
CP = 'FundingStandIn'

result = {}
data = []


def process(file_path):
    with open(file_path, 'r') as f:
        line = f.readline()
        while line:
            line = line.strip()

            bom_class = None
            bom_method = []
            in_bom = False
            # match BOM class
            if line.startswith("public"):
                bom_class = line
                print(line)

                if line == 'public interface Result':
                    pass

                line = f.readline()
                while line:
                    line = line.strip()
                    if line.startswith('{'):
                        in_bom = True
                        # go into BOM method
                        break

                    if CP in line:
                        result[bom_class] = []

                    line = f.readline()

                line = f.readline()
                while line:
                    line = line.strip()

                    if in_bom and line.startswith('domain'):
                        if line.endswith('}'):
                            pass
                        else:
                            line = f.readline()
                            while line:
                                line = line.strip()
                                if line.startswith('}'):
                                    # end of domain
                                    line = f.readline()
                                    break
                                line = f.readline()

                    if line.startswith('}'):
                        # end BOM class
                        break

                    if line.startswith("public"):
                        bom_method = line

                        if line.endswith(';'):
                            pass
                        else:
                            line = f.readline()
                            while line:
                                line = line.strip()

                                if 'categories' in line and CP in line:
                                    if bom_class not in result:
                                        result[bom_class] = []
                                    result[bom_class].append(bom_method)
                                    data.append({'bom_class': bom_class, 'bom_variable': bom_method})

                                if line.endswith(';'):
                                    break
                                line = f.readline()
                    line = f.readline()

            line = f.readline()


if __name__ == '__main__':
    file_path = os.path.join(BOM_folder, file_list[4])
    process(file_path)
    pprint(result)
