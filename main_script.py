import argparse
from p_acquisition import m_acquisition as mac
from p_wrangling import m_wrangling as mwr
from p_analysis import m_analysis as man 
from p_reporting import m_reporting as mre 

def argument_parser():
    parser = argparse.ArgumentParser(description = 'Set chart type')
    args = parser.parse_args()
    return args

def main():
    print('======== Starting pipeline... ========')

    assets, cf_liabs = mac.acquire_inputs()

    combined_orig_cf, cf_liabs = mwr.wrangle(assets, cf_liabs)

    assets_sell, assets_purchase, final_cf_combined = man.analyze_gaps(assets, combined_orig_cf, cf_liabs)

    mre.save_results(assets_sell, assets_purchase, final_cf_combined)

    print('========================= Pipeline is complete. You may find the results in the folder ./data/results =========================')

if __name__ == '__main__':
    arguments = argument_parser()
    main()