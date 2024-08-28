from typing import Dict, Union
import pandas as pd

from batch_processing.path_util import read_csv_with_correct_delimiter
from deepwell_processing_shared.schema.parse_schema import VariantSchema


# One variant is a set of N readings in a deep well plate.
# In the first column it contains the cell density values, the rest of the columns contain data readings.
class Variant:
    def __init__(self, identifier, name, raw_df: pd.DataFrame):
        self.id = identifier
        self.name = name
        self.raw_df = raw_df
        self.cell_density = raw_df.iloc[:, 0]

        self.mean = raw_df.mean()
        self.std_dev = raw_df.std()

    def get_column_stats_by(self, col_name_or_idx: Union[str, int],
                            normalize_by_cell_density: bool = False):

        col_data = self.get_column_data(col_name_or_idx, normalize_by_cell_density)
        col_mean = col_data.mean()
        col_std_dev = col_data.std()

        return col_mean, col_std_dev

    def get_column_data(self, col_name_or_idx: Union[str, int],
                        normalize_by_cell_density: bool = False):

        if isinstance(col_name_or_idx, str):
            col_data = self.raw_df[col_name_or_idx]
        else:
            col_data = self.raw_df[col_name_or_idx]

        if normalize_by_cell_density:
            col_data = col_data / self.cell_density
        return col_data


def create_variants_index(file_content: str, schema: VariantSchema) -> Dict[str, Variant]:
    df_ = read_csv_with_correct_delimiter(file_content)

    # Drop all empty rows
    df_ = df_.dropna(how='all').applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df_ = df_[(df_ != '').any(axis=1)]

    # Remove the A1, B1 ... label column
    if schema.remove_first_column:
        df_ = df_.iloc[:, 1:]

    dfs_per_variant_ = {}

    row_pointer = 0

    for variant_name, rows in schema.variants.items():
        block_df = df_.iloc[row_pointer:row_pointer + rows]

        if not block_df.empty:
            dfs_per_variant_[variant_name] = Variant(row_pointer, variant_name, block_df)
        row_pointer += rows

    return dfs_per_variant_


def store_dfs_per_variant(df_):
    i = 1
    for variant_name, variant in df_.items():
        variant.raw_df.to_csv(f'out/v{i}_{variant_name}.csv', index=False)
        i += 1


if __name__ == "__main__":
    f_p_ = 'cell_suspension_deepwell_plate_readings.csv'
    data_frame = pd.read_csv(f_p_)

    variant_names_ = ["sterile", "nr_6", "nr_7", "nr_10", "nr_11",
                      "correction_e6", "e8", "d9", "d10", "c9", "b8", "bsybg10"]
    readings_per_variant_ = 8
    dfs_per_variant = create_variants_index(variant_names_, f_p_, readings_per_variant_)

    store_dfs_per_variant(dfs_per_variant)
