import pandas as pd
import numpy as np
# analysis functions

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def sell_detector(assets, combined_cf):
    portfolios = assets["PLAN"].unique().tolist()
    assets_sell = pd.DataFrame(columns=['PLAN', 'ISIN', 'VALOR', 'CUPON', 'FEC_VTO', 'NOM', 'MATURITY', 'YRS_TO_MAT'])
    available_cash = {}

    for portfolio in portfolios:

        aux_df = combined_cf[combined_cf["PLAN"] == portfolio]
        aux_df2 = pd.DataFrame(columns=['PLAN', 'ISIN', 'VALOR', 'CUPON', 'FEC_VTO', 'NOM', 'MATURITY', 'YRS_TO_MAT'])

        elegible_years = aux_df.nlargest(3, ['GAP'])["YEAR"].tolist()

        for year in elegible_years:
            sells_df = pd.DataFrame(
                columns=['PLAN', 'ISIN', 'VALOR', 'CUPON', 'FEC_VTO', 'NOM', 'MATURITY', 'YRS_TO_MAT'])

            goal = int(aux_df[aux_df["YEAR"] == year]["GAP"])
            plan = assets["PLAN"] == portfolio
            maturity = assets["MATURITY"] == year
            alternatives = assets[plan & maturity]["NOM"]
            target_asset = find_nearest(alternatives, goal)
            sells_df = assets[plan & maturity][assets[plan & maturity]["NOM"] == target_asset]
            aux_df2 = aux_df2.append(sells_df)
            available_cash[portfolio] = aux_df2["NOM"].sum()

        assets_sell = assets_sell.append(aux_df2)
    return assets_sell, available_cash


def purchase_detector(assets, combined_cf, available_cash):
    portfolios = assets["PLAN"].unique().tolist()
    assets_purchase = pd.DataFrame(
        columns=['PLAN', 'ISIN', 'VALOR', 'CUPON', 'FEC_VTO', 'NOM', 'MATURITY', 'YRS_TO_MAT'])

    for portfolio in portfolios:

        aux_df = combined_cf[combined_cf["PLAN"] == portfolio]
        aux_df2 = pd.DataFrame(columns=['PLAN', 'ISIN', 'VALOR', 'CUPON', 'FEC_VTO', 'NOM', 'MATURITY', 'YRS_TO_MAT'])

        gap_years = aux_df.nsmallest(5, ['GAP'])["YEAR"].tolist()
        cash = available_cash[portfolio]

        for year in gap_years:
            purchase_df = pd.DataFrame(
                columns=['PLAN', 'ISIN', 'VALOR', 'CUPON', 'FEC_VTO', 'NOM', 'MATURITY', 'YRS_TO_MAT'])

            if cash >= abs(aux_df.GAP[aux_df["YEAR"] == year].item()):
                purchase_df = pd.DataFrame({'PLAN': portfolio,
                                            'ISIN': ["GEN_CORP_BOND_" + str(year)],
                                            'VALOR': ["Generic corporate bond with maturity " + str(year)],
                                            'CUPON': 5,
                                            'FEC_VTO': year,
                                            'NOM': abs(int(aux_df.GAP[aux_df["YEAR"] == year].item())),
                                            'MATURITY': year,
                                            'YRS_TO_MAT': year - 2020})

                cash = cash - purchase_df.iloc[0]['NOM']

                aux_df2 = aux_df2.append(purchase_df)
                aux_df2 = aux_df2.reset_index(drop=True)
        #        else:
        #            assets_purchase.iloc[0]['NOM'] = assets_purchase.iloc[0]['NOM'] + available_cash

        assets_purchase = assets_purchase.append(aux_df2)

    assets_purchase.replace(
        {"GEN_CORP_BOND_2021": "CASH", "Generic corporate bond with maturity 2021": "Maintain Cash allocation"},
        inplace=True)

    return assets_purchase

def final_asset_lister(assets,sell, purchase):
    final_assets = pd.concat([assets, sell]).drop_duplicates(keep=False)
    final_assets = final_assets.append(purchase)
    final_assets = final_assets.reset_index(drop=True)
    return final_assets

def asset_cf_projector(df):
    total_assets = df.shape[0]
    cf_projection = pd.DataFrame(columns=['PLAN', 'ISIN', 'VALOR', 'COUPON', 'PRINCIPAL', 'YEAR'])

    # Lets perform the bonds projection:

    for x in range(total_assets):
        maturity = int(df.iloc[x]["YRS_TO_MAT"])

        aux_df = pd.DataFrame({'PLAN': df.iloc[x]["PLAN"],
                               'ISIN': df.iloc[x]["ISIN"],
                               'VALOR': df.iloc[x]["VALOR"],
                               'COUPON': [df.iloc[x]["NOM"] * 0.01 * df.iloc[x]["CUPON"] for i in
                                          range(maturity)],
                               'PRINCIPAL': 0,
                               'YEAR': [2021 + i for i in range(maturity)]})

        aux_df["PRINCIPAL"][maturity - 1] = df.iloc[x]["NOM"]

        cf_projection = cf_projection.append(aux_df)

    cf_projection["CF_ASSET"] = cf_projection["COUPON"] + cf_projection["PRINCIPAL"]
    return cf_projection

def asset_cf_grouper(df):
    cf_assets_grouped = df.groupby(["PLAN", "YEAR"], as_index=False).agg(
        {"COUPON": "sum", "PRINCIPAL": "sum", "CF_ASSET": "sum"})
    return cf_assets_grouped

def asset_liab_combiner(df, df_liabs):
    cf_combined = df.merge(df_liabs, left_on=["PLAN", "YEAR"], right_on=["PLAN", "YEAR"])
    portfolios = cf_combined["PLAN"].unique().tolist()
    auxiliaries = ['u106', 'u107', 'u201', 'u215', 'u218', 'u305']
    for x in auxiliaries:
        portfolios.remove(x)

    cf_complete = pd.DataFrame(columns=['PLAN', 'YEAR', 'CF_ASSET', 'CF_LIAB', 'CF_CUM_ASSET', 'CF_CUM_LIAB'])

    for portfolio in portfolios:
        aux_df = cf_combined[cf_combined["PLAN"] == portfolio]

        aux_df['CF_CUM_ASSET'] = aux_df['CF_ASSET'].cumsum()
        aux_df['CF_CUM_LIAB'] = aux_df['CF_LIAB'].cumsum()

        cf_complete = cf_complete.append(aux_df, sort=False)

    cf_complete['GAP'] = cf_complete['CF_ASSET'] - cf_complete['CF_LIAB']
    cf_complete['CF_CUM'] = cf_complete['CF_CUM_ASSET'] - cf_complete['CF_CUM_LIAB']

    return cf_complete

def analyze_gaps(assets, combined_orig_cf, cf_liabs):
    assets_sell, available_cash = sell_detector(assets, combined_orig_cf)
    assets_purchase = purchase_detector(assets, combined_orig_cf, available_cash)

    final_assets = final_asset_lister(assets,assets_sell, assets_purchase)

    final_cf_assets = asset_cf_projector(final_assets)
    final_cf_assets_gr = asset_cf_grouper(final_cf_assets)

    final_cf_combined = asset_liab_combiner(final_cf_assets_gr,cf_liabs)

    return assets_sell, assets_purchase, final_cf_combined