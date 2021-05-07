
# reporting functions

def save_results(assets_sell, assets_purchase, final_cf_combined):
    assets_sell.to_csv("./data/results/Assets_to_sell.csv")
    assets_purchase.to_csv("./data/results/Assets_to_purchase.csv")
    final_cf_combined.to_csv("./data/results/Current_ALM_Status.csv")