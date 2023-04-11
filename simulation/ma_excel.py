from datetime import tzinfo, date
from locale import currency
import pandas as pd


def create_line_chart(
        workbook:   pd.ExcelWriter.book, 
        start_row:  int, 
        end_row:    int, 
        labels_col: int, 
        data_col:   int, 
        title:      str, 
        sheetname:  str):
    chart = workbook.add_chart({"type" : "line"})
    chart.add_series({
        "categories" : [sheetname, start_row, labels_col, end_row, labels_col],
        "values" : [sheetname, start_row, data_col, end_row, data_col],
    })
    chart.set_title({"name" : title})
    chart.set_legend({"none" : True})
    return chart


def add_chart(currency_pair: str, cross: str, df: pd.DataFrame, excel_writer: pd.ExcelWriter):
    workbook = excel_writer.book
    worksheet = excel_writer.sheets[currency_pair]
    title = f"cumulative_gain for {currency_pair} {cross}"
    chart = create_line_chart(workbook, 1, df.shape[0], 11, 12, title, currency_pair)
    chart.set_size({"x_scale": 2.5, "y_scale": 2.5})
    worksheet.insert_chart("O1", chart)


def add_currency_pair_charts(df_ma_results: pd.DataFrame, df_ma_trades: pd.DataFrame, excel_writer: pd.ExcelWriter):
    columns = ["time", "cumulative_gain"]
    df_temp = df_ma_results.drop_duplicates(subset="currency_pair")

    for _, row in df_temp.iterrows():
        df_temp2 = df_ma_trades[(df_ma_trades.cross == row.cross)&(df_ma_trades.currency_pair == row.currency_pair)].copy()
        df_temp2[columns].to_excel(excel_writer, sheet_name=row.currency_pair, index=False, startrow=0, startcol=11)
        add_chart(row.currency_pair, row.cross, df_temp2, excel_writer)


def add_currency_pair_sheets(df_ma_results: pd.DataFrame, excel_writer: pd.ExcelWriter):
    for currency_pair in df_ma_results.currency_pair.unique():
        df_temp = df_ma_results[df_ma_results.currency_pair == currency_pair]
        df_temp.to_excel(excel_writer, sheet_name=currency_pair, index=False)


def prepare_data(df_ma_results: pd.DataFrame, df_ma_trades: pd.DataFrame):
    df_ma_results.sort_values(by=['currency_pair', 'total_gain'], ascending=[True, False], inplace=True)
    df_ma_trades.time = [x.replace(tzinfo=None) for x in df_ma_trades.time]


def process_data(df_ma_results: pd.DataFrame, df_ma_trades: pd.DataFrame, excel_writer: pd.ExcelWriter):
    prepare_data(df_ma_results, df_ma_trades)
    add_currency_pair_sheets(df_ma_results, excel_writer)
    add_currency_pair_charts(df_ma_results, df_ma_trades, excel_writer)


def create_excel(df_ma_results: pd.DataFrame, df_ma_trades: pd.DataFrame, granularity: str):
    filename = f"./data/ma_simulation_{granularity}.xlsx"
    excel_writer = pd.ExcelWriter(filename, engine="xlsxwriter")

    process_data(
        df_ma_results[df_ma_results.granularity == granularity].copy(), 
        df_ma_trades[df_ma_trades.granularity == granularity].copy(), 
        excel_writer
    )

    excel_writer.save()


def create_moving_average_result(granularity: str):
    today = date.today()
    df_ma_results: pd.DataFrame = pd.read_pickle(f"./data/ma_results_{today.strftime('%Y%m%d')}.pkl")
    df_ma_trades: pd.DataFrame = pd.read_pickle(f"./data/ma_trades_{today.strftime('%Y%m%d')}.pkl")
    create_excel(df_ma_results, df_ma_trades, granularity)


if __name__ == "__main__":
    today = date.today()
    df_ma_results = pd.read_pickle(f"../data/ma_results_{today.strftime('%Y%m%d')}.pkl")
    df_ma_trades = pd.read_pickle(f"../data/ma_trades_{today.strftime('%Y%m%d')}.pkl")
    create_excel(df_ma_results, df_ma_trades, "H1")
    create_excel(df_ma_results, df_ma_trades, "H4")