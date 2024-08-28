from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from deepwell_processing_shared.variant import Variant, create_variants_index


def plot_box_plots(variants: List[Variant], columns=None, normalize_by_cell_density=False, save_path=None, show=True):
    if columns is None:
        columns = variants[0].raw_df.columns  # Use all columns if none are specified

    num_columns = len(columns)

    # Set the color palette for the variants
    palette = sns.color_palette("husl", len(variants))

    # Create a subplot grid
    fig, axes = plt.subplots(1, num_columns, figsize=(5 * num_columns, 6))

    if num_columns == 1:
        axes = [axes]  # Ensure axes is iterable if only one column

    for ax, col in zip(axes, columns):
        data = []
        for variant in variants:
            for value in variant.get_column_data(col, normalize_by_cell_density):
                data.append({
                    'Variant': variant.name,
                    'Value': value,
                })

        df = pd.DataFrame(data)
        sns.boxplot(x='Variant', y='Value', data=df, ax=ax, palette=palette)
        ax.set_title(f'{col}')
        ax.set_xlabel('Variant')
        ax.set_ylabel('Value')
        ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    if show:
        plt.show()


def plot_normal_distributions(variants: List[Variant], columns=None, normalize_by_cell_density=False, save_path=None):
    if columns is None:
        columns = variants[0].raw_df.columns  # Use all columns if none are specified

    num_columns = len(columns)

    # Set the color palette for the variants
    palette = sns.color_palette("husl", len(variants))

    # Define a list of line styles to alternate between
    line_styles = ['-', '--', '-.', ':']

    fig, axes = plt.subplots(1, num_columns, figsize=(5 * num_columns, 6))

    if num_columns == 1:
        axes = [axes]  # Ensure axes is iterable if only one column

    for ax, col in zip(axes, columns):
        # Compute the x-axis range based on the min and max across all variants
        x_min = min([variant.get_column_stats_by(col, normalize_by_cell_density)[0] - 3 *
                     variant.get_column_stats_by(col, normalize_by_cell_density)[1] for variant in variants])
        x_max = max([variant.get_column_stats_by(col, normalize_by_cell_density)[0] + 3 *
                     variant.get_column_stats_by(col, normalize_by_cell_density)[1] for variant in variants])
        x = np.linspace(x_min, x_max, 200)

        for variant, color, style in zip(variants, palette, line_styles * len(variants)):
            mean, std_dev = variant.get_column_stats_by(col, normalize_by_cell_density)
            y = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std_dev) ** 2)
            ax.plot(x, y, label=variant.name, color=color, linestyle=style)

        ax.set_title(f'{col}')
        ax.set_xlabel('Value')
        ax.set_ylabel('Density')
        ax.legend()

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()

if __name__ == "__main__":

    file_name = "washedcells_plate1"
    # f_p_ = file_name + '.csv'
    f_p_ = "/home/jd/git/private/biotec_scripts/deepwell_flourescence_analysis/data/in/plate_1/washedcells_plate1.csv"

    data_frame = pd.read_csv(f_p_)

    variant_names_ = ["sterile", "BSYBG10_Nr.6", "BSYBG10_Nr.7", "BSYBG10_Nr.10", "BSYBG10_Nr.11", "BSYBG10_E6", "BSYBG10_E8", "BSYBG10_D9", "BSYBG10_D10", "BSYBG10_C9", "BSYBG10_B8", "BSYBG10_ctrl"
]
    readings_per_variant_ = 8
    variant_index = create_variants_index(variant_names_, f_p_, readings_per_variant_)

    base_path = "/home/jd/Downloads/"

    plot_box_plots(list(variant_index.values()), normalize_by_cell_density=False, save_path=base_path + file_name + "raw.png")
    plot_box_plots(list(variant_index.values()), normalize_by_cell_density=True, save_path=base_path + file_name + "normalized_by_cell_density.png")
