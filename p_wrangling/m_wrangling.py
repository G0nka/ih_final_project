import pandas as pd

# wrangling functions


def assets_adjusts(df):
    df['MATURITY'] = pd.DatetimeIndex(df['FEC_VTO']).year
    df['YRS_TO_MAT'] = pd.DatetimeIndex(df['FEC_VTO']).year - 2020
    df["NOM"] = df["NOM"].str.replace(',', '')
    df["NOM"] = pd.to_numeric(df["NOM"], downcast='float', errors='ignore')
    df["YRS_TO_MAT"] = pd.to_numeric(df["YRS_TO_MAT"], downcast='integer', errors='ignore')
    return df


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


def liab_adjusts(df):
    df.rename(columns={"group": "PLAN", "t_to": "YEAR", "l_cflow_rp": "CF_LIAB"}, inplace=True)
    df['CF_LIAB'] = df['CF_LIAB'] * - 1000
    # Modification in YEAR in order to equalize the info
    df["YEAR"] = df["YEAR"] + 2020
    df = df[df["YEAR"] != 2020]
    return df


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

def wrangle(assets, cf_liabs):
    orig_assets = assets[['PLAN', 'ISIN', 'VALOR', 'CUPON', 'FEC_VTO', 'NOM']]
    assets_mod = assets_adjusts(orig_assets)
    orig_cf_assets = asset_cf_projector(assets_mod)
    orig_cf_assets_gr = asset_cf_grouper(orig_cf_assets)

    cf_liabs = liab_adjusts(cf_liabs)

    orig_cf_combined = asset_liab_combiner(orig_cf_assets_gr, cf_liabs)

    return orig_cf_combined, cf_liabs
