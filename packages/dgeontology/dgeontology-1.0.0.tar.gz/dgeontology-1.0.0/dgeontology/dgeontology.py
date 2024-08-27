import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Wedge
from collections import defaultdict
from scipy.stats import hypergeom

__all__ = ['dgeont_plot']

def get_sign(pval: float, trend: str) -> tuple[str, str]:
    '''
    For a p-value falling into a given bin and a trend
    returns a string of asterisks and a hex color.

    Required positional arguments:
    pval  -- p-value, a float value.
    trend -- trend (under/normal/over), a string value.

    Returns:
    sign  -- a string of asterisk or an empty string value.
    color -- color encoded in a hex string value.
    '''
    sign  = ''
    color = 'black'
    if trend == 'over':
        if pval <= 0.001:
            sign = '***'
        elif pval <= 0.01:
            sign = '**'
        elif pval <= 0.05:
            sign = '*'
        if pval <= 0.05:
            color = '#990000' #if trend == 'over' else '#0044aa'
    return sign, color


def hypgeoprob(total_size: int, sample_size: int, total_cases: int,
               sample_cases: int) -> float:
    '''
    Providex a cumulative probability from hypogeometric distribution for
    a given total_size of a population, total_cases in the whole population,
    a sample_size sample from the population that contains sample_cases.
    That is a probability of drawing sample_cases or less when having given
    sample_size, total_size and total_cases. Or the probability of
    sample_cases or more,  whichever smaller.

    Required positional arguments:
    total_size   -- the number of elements in the total set, an integer value.
    sample_size  -- the number of element in a sample from the total set,
                    an integer value.
    total_cases  -- the number of elements of interest in the total set,
                    an integer value.
    sample_cases -- the number of elements of interest in the from
                    the total set, an integer value.

    Returns:
    prob_1 or prob_2 -- the left tail or right tail cumulative probability,
                        whichever smaller, a float value. The left tail
                        cumulative probability is given a minus sign that
                        symbolises under-representation in the sample.
    '''
    # Left tail cumulative probability of sample_cases or less.
    prob_1 = hypergeom.cdf(sample_cases, total_size, total_cases, sample_size)
    # Right tail cumulative probability of sample_cases or more.
    prob_2 = hypergeom.sf(sample_cases-1, total_size, total_cases, sample_size)
    if prob_1 <= prob_2: 
        return -1*prob_1
    else: 
        return prob_2


def count_onts(fin_df: pd.DataFrame, onts_col: str, type_col: str,
               bont_col: str, bont_label: str) -> defaultdict[int]:
    '''
    Given a DataFrame with DGE results that are merged on index column with
    semicolon-separated ontology labels from the onts_col column, 'ncRNA'
    and 'tRNA' types in the type_col column as well as not-NA values
    in the bont_col column (labeled as bont_label), counts occurrences
    of all ontology labels across all rows and puts the results
    in a dictionary ontology label -> count

    Required positional arguments:
    fin_df     -- a Pandas DataFrame that contains DGE results merged with
                  the onts_col and type_col columns from metadate DataFrame
                  on index columns.
    onts_col   -- the name of the column in fin_df that contains ontology labels,
                  a string value.
    type_col   -- the name of the column in fin_df that describes the sequence
                  type, a string value. The column is solely used with respect to
                  'ncRNA' and 'tRNA' values. Importantly, when type_col is not None,
                  any other ontology labels, if provided in the remaining columns,
                  are ignored for rows described as 'ncRNA' or 'tRNA'.
                  Set to None not to use 'ncRNA' and 'tRNA' sequence types as
                  ontology labels.
    bont_col   -- the column name in fin_df that contains additional ontology
                  data, a string value. The values of the column are treated as
                  binary(true or false, whether the values are empty/NA or
                  any non-empty value) and described with the label (bnt_label).
                  If bont_col is not None, bont_label is merged with labels
                  provided in onts_col. Set to None not to use any extra
                  ontology column.
    bont_label -- If bont_col is not None, bont_label must be a string value
                  that will be treated as ontology label for any non-empty
                  with respect to bont_col row. Set to None if no extra
                  ontology column is used.

    Returns:
    ont_counts -- ontology label -> results count dictionary, a defaultdict
                  with 0 as the default value.
    '''
    # Create a copy of the DataFrame being processed
    # and a default dictionary with ontology label counts
    fin_df = fin_df.copy()
    ont_counts = defaultdict(int)

    # Update onts_col column using bont_col column
    # if this optional column is present.
    if bont_col is not None:
        bonts_nona = fin_df[bont_col].notna()
        onts_na    = fin_df[onts_col].isna()
        fin_df.loc[bonts_nona & onts_na,  onts_col] =  bont_label
        fin_df.loc[bonts_nona & ~onts_na, onts_col] += '; ' + bont_label

    # Update onts_col column using type_col column
    # if this optional column is present.
    if type_col is not None:
        for gb_key in['ncRNA', 'tRNA']:
            type_onts = fin_df[type_col] == gb_key
            onts_na   = fin_df[onts_col].isna()
            fin_df.loc[type_onts & onts_na,  onts_col] =  gb_key
            fin_df.loc[type_onts & ~onts_na, onts_col] += '; ' + gb_key

    # Assign 'Function unknown' label to remaining empty onts_col values 
    fin_df[onts_col] = fin_df[onts_col].fillna('Function unknown')
    
    # Fetch semicolon-separated ontologies from the onts_col column.
    for onts in fin_df[onts_col]:
        for item in onts.split(';'):
            ont_counts[item.strip()] += 1
    
    return ont_counts


def collect_folds(filt_df: pd.DataFrame, fold_col: str, onts_col: str,
                  type_col: str, bont_col: str, bont_label: str) \
-> defaultdict[ list[float] ]:
    '''
    Given a DataFrame with filtrated (considered as differentiating)
    DGE results merged on index columns with semicolon-separated ontologies
    in the onts_col column, 'ncRNA' and 'tRNA' types in the type_col column
    as well as not-NA values in the bont_col column (labeled as bont_label),
    collects fold_col values for occurrences of all ontology labels across
    all rows and puts the resutls in a dictionary ontology label ->
    [fold_1, fold_2, ...].

    Required positional arguments:
    filt_df    -- a Pandas DataFrame that contains filtrated DGE results merged
                  with the ontology and sequence type columns (onts_col and
                  type_col) from the metadata DataFrame on the index column.
    fold_col   -- the name of the column in filt_df that contains fold change values,
                  a string value.
    onts_col   -- the name of the column in filt_df that contains ontology labels,
                  a string value.
    type_col   -- the name of the column in filt_df that describes the sequence
                  type, a string value. The column is solely used with respect to
                  'ncRNA' and 'tRNA' values. Importantly, when type_col is not None,
                  any other ontology labels, if provided in the remaining columns,
                  are ignored for rows described as 'ncRNA' or 'tRNA'.
                  Set to None not to use 'ncRNA' and 'tRNA' sequence types as
                  ontology labels.
    bont_col   -- the column name in filt_df that contains additional ontology
                  data, a string value. The values of the column are treated as
                  binary(true or false, whether the values are empty/NA or
                  any non-empty value) and described with the label (bnt_label).
                  If bont_col is not None, bont_label is merged with labels
                  provided in onts_col. Set to None not to use any extra
                  ontology column.
    bont_label -- If bont_col is not None, bont_label must be a string value
                  that will be treated as ontology label for any non-empty
                  with respect to bont_col row. Set to None if no extra
                  ontology column is used.

    Returns:
    folds -- ontology label -> [fold_1, fold_2, ...] dictionary, a defaultdict
             with an empt list [] as the default value).
    '''
    # Create a copy of the DataFrame being processed and a default dictionary
    # with ontology label fold change values
    filt_df = filt_df.copy()
    folds = defaultdict(list)

    # Update onts_col column using bont_col column
    # if this optional column is present.
    if bont_col is not None:
        bonts_nona = filt_df[bont_col].notna()
        onts_na    = filt_df[onts_col].isna()
        filt_df.loc[bonts_nona & onts_na, onts_col] = bont_label
        filt_df.loc[bonts_nona & ~onts_na, onts_col] += '; ' + bont_label

    # Update onts_col column using type_col column
    # if this optional column is present.
    if type_col is not None:
        for gb_key in['ncRNA', 'tRNA']:
            type_onts = filt_df[type_col] == gb_key
            onts_na   = filt_df[onts_col].isna()
            filt_df.loc[type_onts & onts_na,  onts_col] =  gb_key
            filt_df.loc[type_onts & ~onts_na, onts_col] += '; ' + gb_key

    # Assign 'Function unknown' label to remaining empty onts_col values 
    filt_df[onts_col] = filt_df[onts_col].fillna('Function unknown')

    # Collect fold change values from fold_col column for each of
    # semicolon-separated ontology label from the onts_col column.
    for _, (fold, onts) in filt_df[ [fold_col, onts_col] ].iterrows():
        for item in onts.split(';'):
            folds[item.strip()].append(fold)
    folds = { ont : np.array(values) for ont, values in folds.items() }

    return folds


def gsea(fin_df: pd.DataFrame, filt_df: pd.DataFrame, fold_col: str, onts_col: str,
         type_col: str, bont_col: str, bont_label: str) \
-> tuple[defaultdict[ list[float] ], pd.DataFrame]:
    '''
    Gen Set Enrichment Analysis (GSEA) (ontology enrichment analysis).
    An analysis of over-representaion of ontology labels among
    differentiating cases (filtered results) is performed in relation
    to the distribution of the labels in the complete population
    (raw input results). The analysis is based on hypergeometric distribution.

    Required positional arguments:
    fin_df     -- dge_df merged with meta_df on the index column, a Pandas DataFrame.
    filt_df    -- fin_df filtered with respect to fold_th and fdr_th that is used
                  for GSEA, a Pandas DataFrame.
    fold_col   -- the name of the column in fin_df and filt_df that contains
                  fold change values, a string value.
    onts_col   -- the name of the column in fin_df and filt_df that contains
                  ontology labels, a string value.
    type_col   -- the name of the column in fin_df and filt_df that describes
                  the sequence type, a string value. The column is solely used
                  with respect to 'ncRNA' and 'tRNA' values. Importantly, when
                  type_col is not None, any other ontology labels, if provided
                  in the remaining columns, are ignored for rows described as
                  'ncRNA' or 'tRNA'. Set to None not to use 'ncRNA' and 'tRNA'
                  sequence types as ontology labels.
    bont_col   -- the column name that contains additional ontology data,
                  a string value. The values of the column are treated as
                  binary(true or false, whether the values are empty/NA or
                  any non-empty value) and described with the label (bnt_label).
                  If bont_col is not None, bont_label is merged with labels
                  provided in onts_col. Set to None not to use any extra
                  ontology column.
    bont_label -- If bont_col is not None, bont_label must be a string value
                  that will be treated as ontology label for any non-empty
                  with respect to bont_col row. Set to None if no extra
                  ontology column is used.

    Returns:
    ont_df         -- GSEA results for all ontology labels, a Pandas DataFrame.
    filt_ont_folds -- a dictionary of ontology labels (keys) and lists of fold
                      change values of results linked to those labels.
    '''
    # Total size is the number of all analysed entities,
    # sample size, the number of differentiating cases
    # (filtered results).
    total_size  = fin_df.shape[0]
    sample_size = filt_df.shape[0]
    # Create a new DataFrame for overrepresentation analysis.
    columns = ('ont pval trend total_size sample_size ' +
               'total_cases sample_cases ' +
               'downreg_cases upreg_cases expected').split()
    ont_df = pd.DataFrame(columns=columns)

    # Calculate total number of each ontology occurrences, and
    # the number of occurences of each ontology label among
    # differentiating cases.
    tot_ont_counts = count_onts(fin_df, onts_col, type_col, bont_col, bont_label)
    filt_ont_folds = collect_folds(filt_df, fold_col, onts_col, type_col,
                                   bont_col, bont_label)

    # For each ontology label (sorted by the number of cases
    # in the complete population in a descending order)
    # add a row to ont_df with results of over-representation analysis.
    for ont in sorted(tot_ont_counts, key=lambda ont: tot_ont_counts[ont],
                      reverse=True):
        # Fetch the number of total cases of a given ontologylabel
        # (the number among all entities).
        total_cases  = tot_ont_counts[ont]
        # Fetch the number of sample cases of a given ontology label
        # (the number among differentiating cases).
        if ont in filt_ont_folds:
            # The number of occurences is equal to the number of
            # fold change values in the item list.
            sample_cases = len(filt_ont_folds[ont])
            # Additionaly count separately up and down-regulated cases.
            downreg_cases = sum(filt_ont_folds[ont] <= 0)
            upreg_cases   = sum(filt_ont_folds[ont] > 0)
        else:
            # If the key is not in filt_ont_folds, it means that
            # no occurences are observed.
            sample_cases, downreg_cases, upreg_cases = 0, 0, 0
        # Count the expected number of occurences of a given ontology label
        # among differantiating cases.
        expected = int( round(total_cases/total_size * sample_size) )

        # Calculate cumulative probability and describe every ontology label
        # with a proper trend: under(-represented), over(-represented), normal.
        pval = hypgeoprob(total_size, sample_size, total_cases, sample_cases)
        if pval < -0.05 or pval > 0.05:
            trend = 'normal'
        else:
            trend = 'under' if pval < 0.0 else 'over'
        pval = abs(pval)

        # Put the collected statistics into the ont_df DataFrame.
        ont_df.loc[ ont_df.shape[0] ] = ont, pval, trend, total_size, sample_size, \
                                        total_cases, sample_cases, \
                                        downreg_cases, upreg_cases, expected

    # Replace the default numeric DataFrame index with the values
    # of ontology labels (the 'ont' column).
    ont_df.set_index('ont', drop=True, inplace=True)
    
    return ont_df, filt_ont_folds


def plot(
    ont_df         : pd.DataFrame,
    filt_ont_folds : defaultdict[ list[float] ],
    
    sel_onts  : list[str],
    skip_onts : list[str],
    min_size  : int,
    
    fig_w : float,
    fig_h : float,
    dpi   : float,
    xmin  : float,
    xmax  : float,
    
    pie_r           : float,
    scale           : float,
    angle_offset    : float,
    margin          : float,
    label_at        : float,
    label_height    : float,
    label_font      : float,
    num_font        : float,
    scale_bar_label : str,
    sbar_font       : float,
    max_fold  : float
) -> tuple[plt.Figure, plt.Axes, plt.Axes]:
    '''
    GSEA results combined with fold change values for all differentiating
    cases are visualised as a pie chart. Dimensions of wedges of the chart
    are proportional to the number of cases described by each ontology label
    (the numbers are also given in the chart, next to wedges).
    Pieces of wedges corresponding to down-regulated cases shoot inwards
    from the scaffold circle, whereas those corresponding to up-regulated ones,
    outwards. Fold change values are mapped to blues and reds, respectively.
    The chart is of very specific requirements, thus it is not rendered with
    any high-level Matplotlib plotting function. Instead Matplotlib patches,
    such as the Circle and Wedge, have been utilised and the chart is plotted
    based on manually calculated coordinates.

    Required main positional argument:
    ont_df         -- the results of GSEA (gene set enrichment analysis)
                      that are to be depicted, a Pandas DataFrame.
    filt_ont_folds -- a dictionary of ontology labels (keys) and lists of
                      fold change values of results linked to those labels.

    Required positional arguments used to modify the set of ontology labels being used:
    sel_onts  -- ontology labels that are to be depicted in the final pie chart,
                 a list of string values.
    skip_onts -- ontology labels that are NOT to be depicted in the final
                 pie chart, a list of string values.
    min_size  -- a minimal count of results (rows from the filtered dge_df)
                 assigned to an ontology label that are required for the label
                 to be depicted in the final pie chart, an integer value.
                
    Required positional arguments used to modify the formatting of the final
    pie chart figure and axes:
    fig_w -- Matplotlib Figure width in inches, a float value.
             Default value: 10.0.
    fig_h -- Matplotlib Figure height in inches, a float value.
             Default value: 3.0.
    dpi   -- Matplotlib Figure resolution in DPI (dots per inch), a float value.
             Default value: 150.0.
    xmin  -- the lower limit value for the X axis, a float value.
             Default value: -2.5.
    xmax  -- the upper limit value for the X axis, a float value.
             Default value: 2.5.

    Required positinal arguments used to modify the formatting of the final
    pie chart elements:
    pie_r           -- the radius of the pie chart scaffold circle, a float value.
    scale           -- general scale factor, a float value.
    angle_offset    -- the angle offset for placing wedges on the scaffold circle
                       in degrees (0.0 - 360.0), a float value.
    margin          -- margin between each wedge and the number of cases
                       as well as that number and the terminal parts of connectors
                       that join wedges and labels, a float value.
    label_at        -- the X coordinate at which ontology (wedge) labels are
                       left-aligned on the right side of the pie chart, or -X
                       at which ontology (wedge) labels are right-aligned
                       on the left side of the pie chart, a float value.
    label_height    -- the vertical span a label is assumed to occupy,
                       a float value.
    label_font      -- the font size for ontology labels, a float value.
    num_font        -- the font size for numbers of results, a float value.
    scale_bar_label -- A label that appears above the scale bar, a string value.
    sbar_font       -- The scale bar font size, a float value.
    max_fold        -- the maximum fold value for the fold scale, a float value.

    Returns:
    fig     -- Matplotlib Figure with the final pie chart.
    ax      -- Matplotlib Axes with the final pie chart.
    ax_bar  -- Matplitlib Axes with the scale bar.
    '''
    # Collect ontology labels to which at least one differentiating
    # result is assigned. Sort them according to the manual list
    # of labels, if provided, or the number of transcirpts
    # that fall in each ontology in a descending order (default).
    # Skip selected labels if such indicated.
    if sel_onts != None and len(sel_onts) > 0:
        onts_list = [ [ontname, filt_ont_folds[ontname]] for ontname in sel_onts
                      if ontname in filt_ont_folds ]
    else:
        onts_list = [ [ontname, folds] for ontname, folds
                      in filt_ont_folds.items() ]
        onts_list = sorted(onts_list, key=lambda items: len(items[1]),
                           reverse=True)
    if skip_onts is None:
        skip_onts = []
    onts_list = [ [ontname, folds] for ontname, folds in onts_list
                  if len(folds) >= min_size and ontname not in skip_onts ]

    # Find the maximal absolute fold change value (for scaling the heatmap).
    if max_fold is None:
        max_fold = np.max([ np.abs(folds).max() for _, folds in onts_list ])

    # Collect sizes (lengths, the number of cases) for each ontology.
    # Square-root sizes (scaling). Next calculate arc sizes (360° scaffold
    # circle pieces) proportional to scaled ontology sizes. Base on the arc
    # sizes assign to each ontology wedge its beginning radius (theta).
    # Shift each theta in order the third ontology starts at hour 12 (0°).
    sizes   = np.array( [ len(ont[1]) for ont in onts_list ] )
    scaled  = np.sqrt(sizes)
    arcs    = 360*scaled / scaled.sum()
    thetas  = np.append([0], arcs[:-1]).cumsum() + 90 - arcs[:2].sum() + angle_offset

    # Calculate the fraction of positive fold change values
    # for each ontology lanbel.
    possizes = [ len([ value for value in ont[1] if value >= 0.0 ])
                 for ont in onts_list ]
    posfracs = possizes / sizes
    
    # Draw a pie chart depicting of fold change values
    # within ontology labels found among differentiating cases.
    # Make each wedge (ontology label) radial and arc dimensions
    # proportional to the number of cases falling into the label.
    # Draw each result as a subwedge of color proportinal to
    # its fold change value. Draw the part of each wedge that
    # corresponds to up-regulated cases outwards in respect
    # to the scaffold circle, and the down-regulated inwards.

    # Calculate the ratio of the figure dimensions.
    # That is necessary to calculate ranges of axes in order
    # to avoid the circular shape turning into eliptical.
    ratio = fig_h/fig_w

    # Create a figure and axes.
    fig = plt.figure(figsize=(fig_w,fig_h), facecolor='white', dpi=dpi)

    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()

    # Create a new DataFrame to which geometrical measures of each
    # ontology wedge will be collected. These measures will be
    # used to position connectors and lables:
    # theta -- start radius
    # r_in  -- radial width of the wegde portion directed inwards
    #          the scaffold circle (log2FoldChange < 0)
    # r_out -- radial width of the wegde portion directed outwards
    #          the scaffold circle (log2FoldChange > 0)
    # text  -- wedge label (ontology name)
    # sign  -- asterisks denoting significance thresholds for
    #          up-regulated transcripts
    # color -- label color (red if an ontology is over-represented)
    label_cols = 'theta r_in r_out text sign color'.split()
    labels_df = pd.DataFrame(columns=label_cols)

    # Iterate over calculated thetas, arc sizes, scaled sizes, positive fractions
    # and ontology list to fill up the labels_df DataFrame, i.e. measures of wedges
    # corresponding to ontologies, as well as to draw subwedges corresponding
    # to cases within each ontology.
    for theta, arc, size, posfrac, rawdata in zip(
        thetas, arcs, scaled, posfracs, onts_list):
        # Calculate the "real" radial width of a wedge, i.e. the actual
        # radial width of a wedge based on the scaled number of cases falling
        # into an ontology and an arbitrarily assumed scale.
        real_w = size*scale
        
        # Collect the ontology name as well as the positive and negative
        # fold change values
        ontname  = rawdata[0]
        negfolds = sorted([ abs(fold) for fold in rawdata[1] if fold <  0.0 ])
        posfolds = sorted([ fold      for fold in rawdata[1] if fold >= 0.0 ])

        # Draw subwedges. Calculate their radial span as a fraction of the real
        # radial width of a wedge. Use a colors proportinal to fold change values
        # scaled against the maximal value (max_fold). Use scale of reds for
        # up-regulated transcripts and of blues for down-regulated ones.
        for i, fold in enumerate(negfolds):
            span = real_w*(1.0-posfrac) / len(negfolds)
            color = (1.0-abs(fold)/max_fold, 1.0-abs(fold)/max_fold, 1.0)
            ax.add_patch( Wedge((0.0, 0.0), pie_r-span*i, theta, theta+arc,
                                width=span, linewidth=0.5, edgecolor=color,
                                facecolor=color) )

        for i, fold in enumerate(posfolds):
            span = real_w*posfrac / len(posfolds)
            color = (1.0, 1.0-abs(fold)/max_fold, 1.0-abs(fold)/max_fold)
            ax.add_patch( Wedge((0.0, 0.0), pie_r+span*(i+1), theta, theta+arc,
                                width=span, linewidth=0.5, edgecolor=color,
                                facecolor=color) )

        # Sketch a wedge frame around already drawn subwedges.
        ax.add_patch( Wedge((0.0, 0.0), pie_r+posfrac*real_w, theta, theta+arc,
                            width=real_w, fill=False, linewidth=0.3) )
        
        # Assigned color and optionally add asterisks to an ontology (wedge) label
        # if the ontology happens to be over-represented.
        sign, color = get_sign(*ont_df.loc[ontname, ['pval', 'trend']])

        # Recalculate degrees into radians. Add all collected and
        # calculated measures to labels_df DataFrame.
        theta_rad = (theta+0.5*arc)/180*np.pi
        labels_df.loc[ labels_df.shape[0] ] = theta_rad,      \
            pie_r-(1.0-posfrac)*real_w, pie_r+posfrac*real_w, \
            ontname, sign, color

    # Sketch the scaffold circle arcross already drawn wedges.
    ax.add_patch( Circle((0.0, 0.0), pie_r, fill=False, linewidth=0.2,
                         color='black') )

    # Based on values from different columns from labels_df DataFrame, calculate
    # coordinates of connectors fragments, number of transcript labels and
    # ontology labels. Add the coordinates to labels_df DataFrame.
    # numup_       -- labels for number of up-regulated transcripts,
    #                 (outwards the wedges)
    # numupdown_   -- labels for number of down-regulated transcripts,
    #                 (inwards the wedges)
    # Coordinates of connector points starting at a wedge and finishing at
    # an ontology (wedge) label:
    # conn_term_   -- start points at the wedge
    # conn_proxy_  -- points on the outer scaffold circle
    # conn_middle_ -- x and y values shared by next two middle points
    # conn_init_   -- points at ontology (wedge) labels
    labels_df['numup_x']   = np.cos(labels_df['theta']) *  \
                             (labels_df['r_out'] + margin)
    labels_df['numup_y']   = np.sin(labels_df['theta']) *  \
                             (labels_df['r_out'] + margin)

    labels_df['numdown_x'] = np.cos(labels_df['theta']) *  \
                             (labels_df['r_in'] - margin)
    labels_df['numdown_y'] = np.sin(labels_df['theta']) *  \
                             (labels_df['r_in'] - margin)

    labels_df['conn_term_x'] = np.cos(labels_df['theta']) *      \
                               (labels_df['r_out'] + 2.0*margin)
    labels_df['conn_term_y'] = np.sin(labels_df['theta']) *      \
                               (labels_df['r_out'] + 2.0*margin)

    proxy_r = labels_df['r_out'].max() + 3.0*margin

    labels_df['conn_proxy_x'] = np.cos(labels_df['theta']) * (proxy_r)
    labels_df['conn_proxy_y'] = np.sin(labels_df['theta']) * (proxy_r)

    labels_df.sort_values('conn_proxy_y', ascending=False, inplace=True)
    sub_index_left = labels_df.loc[ labels_df['conn_proxy_x'] <= 0.0 ].index
    sub_index_right = labels_df.index.difference(sub_index_left, sort=False)

    for sub_index in sub_index_left, sub_index_right:
        max_rank = sub_index.shape[0] // 2
        labels_df.loc[sub_index, 'rank'] = pd.Series(
            range(max_rank, max_rank-sub_index.shape[0], -1), index=sub_index)

    labels_df.loc[sub_index_left, 'rank_norm'] =              \
        (labels_df.loc[sub_index_left, 'rank'] +              \
        np.abs(labels_df.loc[sub_index_left,  'rank'].min()))
    labels_df.loc[sub_index_left, 'rank_norm'] =        \
        labels_df.loc[sub_index_left, 'rank_norm'] /    \
        labels_df.loc[sub_index_left,'rank_norm'].max()

    labels_df.loc[sub_index_right, 'rank_norm'] =              \
        (labels_df.loc[sub_index_right, 'rank'] +              \
        np.abs(labels_df.loc[sub_index_right,  'rank'].min()))
    labels_df.loc[sub_index_right, 'rank_norm'] =        \
        labels_df.loc[sub_index_right, 'rank_norm'] /    \
        labels_df.loc[sub_index_right,'rank_norm'].max()

    labels_df['rank_norm'] = labels_df['rank_norm'].fillna(0.0)

    labels_df['conn_init_y'] = label_height * labels_df['rank']
    labels_df.loc[labels_df['conn_term_x'] <  0, 'conn_init_x'] = label_at * -1
    labels_df.loc[labels_df['conn_term_x'] >= 0, 'conn_init_x'] = label_at

    conn_range = label_at - proxy_r

    # Upper right quarter labels (if x-axis reveresed, default).
    sub_index = labels_df[
        (labels_df['conn_init_x'] < 0) &
        (labels_df['conn_init_y'] < labels_df['conn_proxy_y'])
    ].index
    if sub_index.shape[0] != 0:
        step = conn_range / sub_index.shape[0]
        labels_df.loc[sub_index, 'conn_middle_x'] = -1* proxy_r - \
            step * np.arange(sub_index.shape[0]-1, -1, -1)

    # Upper left quarter labels (if x-axis reveresed, default).
    sub_index = labels_df[
        (labels_df['conn_init_x'] > 0) &
        (labels_df['conn_init_y'] < labels_df['conn_proxy_y'])
    ].index
    if sub_index.shape[0] != 0:
        step = conn_range / sub_index.shape[0]
        labels_df.loc[sub_index, 'conn_middle_x'] = proxy_r + \
            step * np.arange(sub_index.shape[0]-1, -1, -1)

    # Lower right quarter labels (if x-axis reveresed, default).
    sub_index = labels_df[
        (labels_df['conn_init_x'] < 0) &
        (labels_df['conn_init_y'] > labels_df['conn_proxy_y'])
    ].index
    if sub_index.shape[0] != 0:
        step = conn_range / sub_index.shape[0]
        labels_df.loc[sub_index, 'conn_middle_x'] = -proxy_r - \
            step * np.arange(1, sub_index.shape[0]+1, 1)

    # Lower left quarter labels (if x-axis reveresed, default).
    sub_index = labels_df[
        (labels_df['conn_init_x'] > 0) &
        (labels_df['conn_init_y'] > labels_df['conn_proxy_y'])
    ].index
    if sub_index.shape[0] != 0:
        step = conn_range / sub_index.shape[0]
        labels_df.loc[sub_index, 'conn_middle_x'] = proxy_r + \
            step * np.arange(1, sub_index.shape[0]+1, 1)

    # Iterate over labels_df DataFrame and based on alread calculated
    # geometric measures draw connectors and labels.
    for i, row in labels_df.iterrows():
        x, y = row['numup_x'], row['numup_y']
        ax.text(x, y, ont_df.loc[row['text'], 'upreg_cases'],
                va='center', ha='center', fontsize=num_font)

        x, y = row['numdown_x'], row['numdown_y']
        ax.text(x, y, ont_df.loc[row['text'], 'downreg_cases'],
                va='center', ha='center', fontsize=num_font)
        
        X = row['conn_init_x conn_middle_x conn_middle_x'.split() +
                'conn_proxy_x conn_term_x'.split()]
        Y = row['conn_init_y conn_init_y conn_proxy_y'.split() +
                'conn_proxy_y conn_term_y'.split()]
        ax.plot(X, Y, linewidth=0.4, color='black', solid_joinstyle='round',
                solid_capstyle='round')

        x, y, text, sign, color = \
            row['conn_init_x conn_init_y text sign color'.split()]
        if x < 0:
            x -= margin
            label = f'{text} {sign}'
            ha    = 'left'
        else:
            x += margin
            label = f'{sign} {text}'
            ha    = 'right'
        ax.text(x, y, label, va='center', ha=ha, color=color, fontsize=label_font)

    # Draw the log2FoldChange scale bar (heatmap) on separate axes, assuming
    # arbitrary number of cells (color bands) and their widths (sizes).
    bar_cell_size  = 0.05
    bar_cell_count = 7
    ax_bar = fig.add_axes([0.88, 0.1, bar_cell_size*ratio*bar_cell_count,
                           bar_cell_size])
    ax_bar.set_yticks([])
    for spine in ['left', 'top', 'right', 'bottom']:
        ax_bar.spines[spine].set_linewidth(0.6)
    ax_bar.tick_params(width=0.6, labelsize=6.0)
    steps  = np.linspace(0.0, 1.0, 50)
    colors = np.stack([steps, steps, np.ones(steps.shape[0])], axis=1)
    steps  = np.linspace(1.0, 0.0, 50)[1:]
    colors = np.vstack([colors, np.stack([np.ones(steps.shape[0]), steps, steps],
                        axis=1)])
    ax_bar.imshow(
        colors.reshape((1,99,3)),
        extent = (-max_fold, max_fold, 0, max_fold/(bar_cell_count + 1))
    )
    ax_bar.set_title(scale_bar_label, fontsize=sbar_font)

    # Set x-axis limits. Based on figure
    # fig_h/fig_w ratio, calculate y-axis limits.
    xrange = np.abs(xmax - xmin)
    xmin_p = -xrange - xmin
    xmax_p =  xrange - xmax
    ax.set_xlim(xmax_p, xmin_p)
    ax.set_ylim(-xrange/2*ratio, xrange/2*ratio)
    
    return fig, ax, ax_bar


def dgeont_plot(
    dge_df  : pd.DataFrame,
    meta_df : pd.DataFrame,
    *,
    
    fold_col : str,
    pval_col : str,
    onts_col : str,
    fold_th  : float,
    fdr_th   : float,
    
    type_col   : str = None,
    bont_col   : str = None,
    bont_label : str = None,
    sel_onts   : list[str] = None,
    skip_onts  : list[str] = None,
    min_size   : int = 0,
    
    fig_w : float =  10.0,
    fig_h : float =   3.0,
    dpi   : float = 150.0,
    xmin  : float =  -2.5,
    xmax  : float =   2.5,
    
    pie_r           : float = 0.30,
    scale           : float = 0.03,
    angle_offset    : float = 0.00,
    margin          : float = 0.03,
    label_at        : float = 0.70,
    label_height    : float = 0.08,
    scale_bar_label : str   = 'Log$_{2}$ fold change',
    label_font      : float = 8.5,
    num_font        : float = 6.0,
    sbar_font       : float = 8.0,
    max_fold        : float = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, plt.Figure, plt.Axes, plt.Axes]:
    '''
    The main dgeontology module function that performs GSEA (Gene Set Enrichment
    analysis) and plots its results combined with fold change values. Required
    parameters are two Pandas DataFrames, both indexed with the same set of IDs
    of analysed entities (transcripts, genes, proteins). The first contains DGE
    (differential gene expression) or similar differential analysis data for
    a complete population of analysed entities (e.g. all possible/potentially
    expected transcripts). Next to the ID column (the index column), it must
    provide two other columns with, respectively, fold change values and FDR values
    (false discovery rate). The second DataFrame contains metadata that link
    IDs (the index column values) to ontology labels.

    Required positional arguments:
    dge_df  -- Pandas DataFrame containing DGE results. The DataFrame must be
               indexed with analysed entities IDs (e.g. transcript IDs).
    meta_df -- Pandas DataFrame linking entities IDs to ontology labels.
               The DataFrame must also be indexed with analysed entities IDs.

    Required keyword arguments:
    fold_col -- the name of the column in dge_df that contains fold change values,
                a string value.
    pval_col -- the name of the column in dge_df that contains FDR values,
                a string value.
    onts_col -- the name of the column in meta_df that contains ontology labels,
                a string value.
    fold_th  -- a minimal threshold value for fold_col (fold change) absolute
                values used for filtering the results in dge_df, a float value.
    fdr_th   -- a maximal threshold value for pval_col (FDR) used for
                filtering the results in dge_df, a float value.

    Optional keyword arguments that allow to use additional ontology data:
    type_col   -- the name of the column in meta_df that describes the sequence
                  type, a string value. The column is solely used in respect
                  to 'ncRNA' and 'tRNA' values. Importantly, when type_col
                  is not None, any other ontology labels, if provided in the 
                  remaining columns, are ignored for rows described as 'ncRNA'
                  or 'tRNA'.
                  Default value: None (do not use 'ncRNA' and 'tRNA' sequence
                  types as ontology labels).
    bont_col   -- the column name that contains additional ontology data,
                  a string value. The values of the column are treated as
                  binary(true or false, whether the values are empty/NA or
                  any non-empty value) and assigned with bnt_label.
                  If bont_col is not None, bont_label is merged with labels
                  provided in onts_col.
                  Default value: None (no binary ontology column is provided).
    bont_label -- If bont_col is not None, bont_label must be a string value
                  that will be treated as an extra ontology label for any row
                  that is non-empty with respect to bont_col.
                  Default value: None (no binary ontology column is provided).

    Optional keyword arguments that allow to modify the set of ontology labels
    being used:
    sel_onts  -- ontology labels that are to be depicted in the final pie chart,
                 a list of string values.
                 Default value: None (depict all ontology labels).
    skip_onts -- ontology labels that are NOT to be depicted in the final
                 pie chart, a list of string values.
                 Default value: None (do not skip any ontology label).
    min_size  -- a minimal count of results (rows from the filtered dge_df)
                 assigned to an ontology label that are required for the label
                 to be depicted in the final pie chart, an integer value.
                 Default value: 0 (depict all ontology labels).
                
    Optional keyword arguments that allow to modify the formatting of the final
    pie chart figure and axes:
    fig_w -- Matplotlib Figure width in inches, a float value.
             Default value: 10.0.
    fig_h -- Matplotlib Figure height in inches, a float value.
             Default value: 3.0.
    dpi   -- Matplotlib Figure resolution in DPI (dots per inch), a float value.
             Default value: 150.0.
    xmin  -- the lower limit value for the X axis, a float value.
             Default value: -2.5.
    xmax  -- the upper limit value for the X axis, a float value.
             Default value: 2.5.

    Optional keyword arguments that allow to modify the formatting of the final
    pie chart elements:
    pie_r           -- the radius of the pie chart scaffold circle, a float value.
                       Default value: 0.30.
    scale           -- general scale factor, a float value. Change to increase
                       or decrease the relative wedge radial sizes, especially
                       if inner parts pass through the middle of the chart.
                       Default value: 0.03.
    angle_offset    -- the angle offset for placing wedges on the scaffold circle
                       in degrees (0.0 - 360.0), a float value. By default
                       the third wedge/slice starts at 12:00 o'clock, top center,
                       which seems to be optimal for size-ordered slices.
                       Default value: 0.00.
    margin          -- margin between each wedge and the number of cases as well as
                       that number and the terminal part of the connector that
                       join a wedge and a label, a float value.
                       Default value: 0.03.
    label_at        -- the X coordinate at which ontology (wedge) labels are
                       left-aligned on the right side of the pie chart, or -X
                       at which ontology (wedge) labels are right-aligned
                       on the left side of the pie chart, a float value.
                       Change it to bring labels closer or move further from
                       the pie chart.
                       Default value: 0.70.
    label_height    -- the vertical span a label is assumed to occupy,
                       a float value. Change to increase or decrease the vertical
                       spacing between adjacent labels, especially in case of
                       overlapping labels.
                       Default value: 0.08.
    label_font      -- the font size for ontology labels, a float value.
                       Default value: 8.5.
    num_font        -- the font size for numbers of results, a float value
                       Default value: 6.0.
    scale_bar_label -- A label that appears above the scale bar, a string value.
                       Default value: 'Log$_{2}$ fold change',
    sbar_font       -- The scale bar font size, a float value.
                       Default value: 8.0.
    max_fold        -- the maximum fold value for the fold scale, a float value.
                       If None, it is set automatically to the highest absolute
                       fold value. Set it manually if you want to generate charts
                       that depict results in a fixed scale.
                       Default value: None (automatic scale).

    Returns:
    fin_df  -- dge_df merged with meta_df on the index column, a Pandas DataFrame.
    filt_df -- fin_df filtered with respect to fold_th and fdr_th that is used
               for GSEA, a Pandas DataFrame.
    ont_df  -- GSEA results for all ontology labels, a Pandas DataFrame.
    fig     -- Matplotlib Figure with the final pie chart.
    ax      -- Matplotlib Axes with the final pie chart.
    ax_bar  -- Matplitlib Axes with the scale bar.
    '''
    # Merge DGE results with metadata on index columns.
    fin_df = dge_df.merge(meta_df, left_index=True, right_index=True, how='left')
    
    # Filter fin_df (all DGE results merged with metadata) based on
    # fold_col column agains fold_th and pval_col against fdr_th.
    filt_df = fin_df[
        (fin_df[fold_col].abs() >= fold_th) &
        (fin_df[pval_col] <= fdr_th)
    ]
    
    # Perform GSEA (gene set enrichment analysis).
    ont_df, filt_ont_folds = gsea(fin_df, filt_df, fold_col, onts_col, type_col,
                                  bont_col, bont_label)
    
    # Plot the final chart combining GSEA analysis with fold change values.
    fig, ax, ax_bar = plot(ont_df, filt_ont_folds, sel_onts, skip_onts, min_size,
                           fig_w, fig_h, dpi, xmin, xmax, pie_r, scale, angle_offset,
                           margin, label_at, label_height, label_font, num_font,
                           scale_bar_label, sbar_font, max_fold,)

    # Return merged data (fin_df), also filtered with respect to fold_th and fdr_th
    # (filt_df), GSEA analysis DataFrame (ont_df), references to the final
    # Matplotlib Figure as well as plot and scale bar Axex
    return fin_df, filt_df, ont_df, fig, ax, ax_bar

