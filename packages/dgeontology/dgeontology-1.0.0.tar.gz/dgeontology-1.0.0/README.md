# The library overview
The `dgeontology` library provides a simple way of: (1) performing GSEA (gene set enrichment analysis/ontology analysis) on DGE (differential gene expression) or similar results; (2) visualisation of integrated GSEA and DGE results in one highly informative and visually appealing circular chart. Sizes of the final circular chart slices correspond to the number of results linked to a given ontology label (results falling into a given ontology group/category). Subsequent and adjacent radial fragments of the slices are coloured according to each DGE result fold change value (red for up-regulation and blue for down-regulation). Since the fold change values are first sorted, each slice of the final circular chart becomes a heatmap of fold change scale across a given ontology label (group).

# Library installation using _pip_
Installation of the `dgeontology` library with pip is quite straightforward:
```Bash
pip install dgeontology
```

# A quick example of the library usage
The input data used in this example can be found in the `input` subdirectory in the root directory of [this repository](https://github.com/michalbukowski/dge-ontology). Once you have the `dgeontology` library installed, you can test its functionality using the aforementioned input data and the code below.

```Python
# Import Pandas library for the input data handling and
# the dgeont_plot() function from the dgeontology library
# for rendering DGE/GSEA pie charts.
import pandas as pd
from dgeontology import dgeont_plot

# Load DGE results for a complete population,
# i.e. even for those entities (genes, proteins)
# that could be present in the sample (bacterial transcriptome,
# proteome, etc.) but were not (e.g. non-transcribed genes).
# In this example two groups were compared:
# wt51e_lg - wild type, mt51e_lg - mutant.
# Importantly, the column that contains IDs of analysed
# entities is set to be the DataFrame index.
dge_df = pd.read_csv(
    'input/mt51e_wt51e_DGE.tsv',
    index_col = 'locus_tag',
    sep = '\t'
)

# Load metadata for all entities (genes, transcripts, proteins, etc.).
# Importantly, the column that contains IDs of analysed
# entities is set to be the DataFrame index.
meta_df = pd.read_csv(
    'input/rn.tsv',
    index_col = 'locus_tag',
    sep = '\t'
)

# Run the dgeont_plot() function providing all 5 required arguments
# and additionally modifying values of 3 optional ones in order to center
# the pie chart within the figure better.
fin_df, filt_df, ont_df, fig, ax, ax_bar = dgeont_plot(
    dge_df, meta_df, fold_col='log2FoldChange', pval_col='padj', onts_col='cog',
    fold_th=1.0, fdr_th=0.05, fig_h=2.7, xmin=-1.75, xmax=2.15
)

# Save the rendered pie chart to a PNG file with a non-transparent
# background and the resolution of 300 DPI.
fig.savefig('test_plot.png', transparent=False, dpi=300)
```

# More examples in Jupyter notebooks
The above and more examples of `dgeontology` library usage are presented and described in details in `dgeontology_basic_examples.ipynb` and `dgeontology_extra_examples.ipynb` Jupyter notebooks, which are available in [this repository](https://github.com/michalbukowski/dge-ontology).

# The `dgeont_plot()` function in details
The `dgeont_plot()` function takes DGE or similar results and based on provided metadata (ontology labels) performs GSEA and renders a rich circular chart that depicts the results of the analysis. The function requires 7 obligatory arguments (2 positional and 5 keyword arguments). The default values of other 22 optional keyword arguments can be modified in order to fine-tune the final chart.

Required positional arguments:
- `dge_df` &ndash; Pandas DataFrame containing DGE results. The DataFrame must be indexed with analysed entities IDs (e.g. transcript IDs).
- `meta_df` &ndash; Pandas DataFrame linking entities IDs to ontology labels. The DataFrame must also be indexed with analysed entities IDs.

Required keyword arguments:
- `fold_col` &ndash; the name of the column in `dge_df` that contains fold change values, a string value.
- `pval_col` &ndash; the name of the column in `dge_df` that contains FDR values, a string value.
- `onts_col` &ndash; the name of the column in `meta_df` that contains ontology labels, a string value.
- `fold_th` &ndash; a minimal threshold value for `fold_col` (fold change) absolute values used for filtering the results in `dge_df`, a float value.
- `fdr_th` &ndash; a maximal threshold value for `pval_col` (FDR) used for filtering the results in `dge_df`, a float value.

Optional keyword arguments that allow to use additional ontology data:
- `type_col` &ndash; the name of the column in `meta_df` that describes the sequence type, a string value. The column is solely used in respect to _ncRNA_ and _tRNA_ values. Importantly, when `type_col` is not None, any other ontology labels, if provided in the remaining columns, are ignored for rows described as _ncRNA_ and _tRNA_. Default value: `None` (do not use _ncRNA_ and _tRNA_ sequence types as ontology labels).
- `bont_col` &ndash; the column name that contains additional ontology data, a string value. The values of the column are treated as binary (true or false, whether the values are empty/NA or any non-empty value) and assigned with `bnt_label`. If `bont_col` is not None, `bont_label` is merged with labels provided in `onts_col`. Default value: `None` (no binary ontology column is provided).
- `bont_label` &ndash; If `bont_col` is not None, `bont_label` <u>must be set</u> to a string value that will be treated as an extra ontology label for any row that is non-empty with respect to `bont_col`. Default value: `None` (no binary ontology column is provided).

Optional keyword arguments that allow to modify the set of ontology labels being used:
- `sel_onts` &ndash; ontology labels that are to be depicted in the final pie chart, a list of string values. Default value: `None` (depict all ontology labels ordered in a descending order with respect to the number of results linked to them).
- `skip_onts` &ndash; ontology labels that are <u>not</u> to be depicted in the final pie chart, a list of string values. Default value: `None` (do not skip any ontology label).
- `min_size` &ndash; a minimal count of results (rows from the filtered `dge_df`) assigned to an ontology label that are required for the label to be depicted in the final pie chart, an integer value. Default value: `0` (depict all ontology labels).

Optional keyword arguments that allow to modify the formatting of the final pie chart figure and axes:
- `fig_w` &ndash; Matplotlib Figure width in inches, a float value. Default value: `10.0`.
- `fig_h` &ndash; Matplotlib Figure height in inches, a float value. Default value: `3.0`.
- `dpi` &ndash; Matplotlib Figure resolution in DPI (dots per inch), a float value. Default value: `150.0`.
- `xmin` &ndash; the lower limit value for the X axis, a float value. Default value: `-2.5`.
- `xmax` &ndash; the upper limit value for the X axis, a float value. Default value: `2.5`.

Optional keyword arguments that allow to modify the formatting of the final pie chart elements:
- `pie_r` &ndash; the radius of the pie chart scaffold circle, a float value. Default value: `0.30`. 
- `scale` &ndash; general scale factor, a float value. Change to increase or decrease the relative wedge radial sizes, especially if inner parts pass through the middle of the chart. Default value: `0.03`.
- `angle_offset` &ndash; the angle offset for placing wedges on the scaffold circle in degrees (0.0 - 360.0), a float value. By default the third wedge/slice starts at 12:00 o'clock, top center, which seems to be optimal for size-ordered slices. Default value: `0.0`.
- `margin` &ndash; margin between each wedge and the number of cases as well as that number and the terminal part of the connector that join a wedge and a label, a float value. Default value: `0.03`.
- `label_at` &ndash; the X coordinate at which ontology (wedge) labels are left-aligned on the right side of the pie chart, or -X at which ontology (wedge) labels are right-aligned on the left side of the pie chart, a float value. Change it to bring labels closer or move further from the pie chart. Default value: `0.70`.
- `label_height` &ndash; the vertical span a label is assumed to occupy, a float value. Change to increase or decrease the vertical spacing between adjacent labels, especially in case of overlapping labels. Default value: `0.08`.
- `label_font` &ndash; the font size for ontology labels, a float value. Default value: `8.5`.
- `num_font` &ndash; the font size for numbers of results, a float value Default value: `6.0`.
- `scale_bar_label` &ndash; A label that appears above the scale bar, a string value. Default value: `'Log$_{2}$ fold change'`,
- `sbar_font` &ndash; The scale bar font size, a float value. Default value: `8.0`.
- `max_fold` &ndash; the maximum fold change value for the fold scale, a float value. If None, it is set automatically to the highest absolute fold value. Set it manually if you want to generate charts that depict results in a fixed scale. Default value: `None` (automatic scale).

The function returns a tuple of six elements:
- `fin_df` &ndash; `dge_df` merged with `meta_df` on the index column, a Pandas DataFrame.
- `filt_df` &ndash; `fin_df` filtered with respect to `fold_th` and `fdr_th` that is used for GSEA, a Pandas DataFrame.
- `ont_df` &ndash; GSEA results for all ontology labels, a Pandas DataFrame.
- `fig` &ndash; Matplotlib Figure with the final pie chart.
- `ax` &ndash; Matplotlib Axes with the final pie chart.
- `ax_bar` &ndash; Matplitlib Axes with the scale bar.

