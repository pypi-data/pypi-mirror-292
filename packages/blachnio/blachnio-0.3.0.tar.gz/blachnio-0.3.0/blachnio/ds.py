import os
import hashlib
import pandas as pd
import numpy as np
from time import perf_counter
from _warnings import warn


def diagnose_nb_unique_items_per_grouped_cols(output_name, table, grouped_cols, item_col):
    """Add to table Number of unique entries of 'item_col' for each 'grouped_cols'
    Example: In order to check how manu unique vendors (item_col) we have for each dc-mag combination (grouped_cols)
    """
    table[output_name] = table.groupby(grouped_cols)[item_col].transform(pd.Series.nunique)
    return f'Column "{output_name}" added to dataset'


def diagnose_unique_items_with_measure_per_grouped_cols(output_name, table, grouped_cols, item_col, measure_col,
                                                        use_top_n=None):
    """Add to table unique entries of 'item_col' with share% of measure_col for each 'grouped_cols'
    Example: In order to check how manu unique vendors (item_col) and their share of measure_col,
    we have for each dc-mag combination (grouped_cols).
    use_top_n: int to cut nb of displayed items (can be there's too many)
    """
    df = table.groupby(grouped_cols + [item_col], as_index=False)[measure_col].sum().sort_values(grouped_cols + [measure_col], ascending=[True, False])
    df[measure_col] /= df.groupby(grouped_cols)[measure_col].transform(sum)
    if use_top_n is not None:
        df['rank'] = df.groupby(grouped_cols)[measure_col].transform(lambda x: pd.Series.rank(x, ascending=False))
        df = df[df['rank'] <= use_top_n].copy()
        df.drop(columns=['rank'], inplace=True)
    df[output_name] = df[item_col] + ' (' + np.round(df[measure_col], 3).astype(str) + ')'
    df = df.groupby(grouped_cols, as_index=False)[output_name].agg(lambda x: ', '.join(x))
    if output_name in table.columns:
        table.drop(columns=output_name, inplace=True)
    outcome = table.merge(df, how='left', on=grouped_cols)
    table[output_name] = outcome[output_name]
    return f'Column "{output_name}" added to dataset'


def change_attributes_with_masks(df, masks_and_attributes_file, use_worksheets_starting_with='input'):
    """Apply changes to dataframe based on masks and attributes provided in Excel file.
    In input file, attribute columns must start with 'attr_', masks with 'mask_'.
    Empty masks are ignored.
    Mask columns are currently passed to str.contain(mask_, regex=False)
    """
    use_worksheets = [worksheet for worksheet in pd.ExcelFile(masks_and_attributes_file).sheet_names if worksheet.startswith(use_worksheets_starting_with)]
    print(f'Worksheets used: {", ".join(use_worksheets)}')
    logics = []
    for worksheet in use_worksheets:
        logic = pd.read_excel(masks_and_attributes_file, sheet_name=worksheet).dropna(how='all')
        logics.append(logic)

    for logic in logics:
        # Check if all masks exist in df
        columns_with_mask = [col for col in logic.columns[logic.columns.str.contains('mask_')]]
        columns_with_attributes = [col for col in logic.columns[logic.columns.str.contains('attr_')]]
        warn_not_in_mapper([col.replace('mask_', '') for col in columns_with_mask], df.columns, msg=f'Columns not in mats. Check file {masks_and_attributes_file}')

        # Remove columns without mask_, attr_
        logic = logic[logic.columns[logic.columns.str.contains('mask_|attr_', regex=True)]]

        # Generating masks based on Excel rows input
        for ix, row in logic.iterrows():
            # Select only relevant masks for row
            cols_mask = row[~row.isna() & row.index.isin(columns_with_mask)]
            cols_attr = row[~row.isna() & row.index.isin(columns_with_attributes)]
            # Create mask for mats
            mask = pd.Series(index=df.index, data=True)
            for col_mask, mask_value in cols_mask.items():
                mask = mask & df[col_mask.replace('mask_', '')].str.contains(mask_value, regex=False)
            # Set attributes to mats dataset
            for col_attr, attr_value in cols_attr.items():
                df.loc[mask, col_attr.replace('attr_', '')] = attr_value
    return df


def console_msg(msg=None, execution_time=True):
    """Prints in console info about executed function.

    This decorator accepts arguments and thus requires execution with @printout().
    Arguments:
    - msg: short statement of what is happening. If None, name of function is used.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            print('\n', end='')
            title = msg if msg else f"Running function: <{func.__name__}>"
            print(f'= {title} '.ljust(80, '='))
            time_start = perf_counter()
            func_output = func(*args, **kwargs)
            if execution_time:
                print(f'Execution time: {perf_counter() - time_start:0.1f}sec.')
            print('-' * 80)
            return func_output
        return wrapper
    return decorator


def describe_column(column, show_top_count_entries=15):
    """Displays statistics about column (pandas.Series) in dataset"""
    justification_width = 25
    print(f'\nColumn: {column.name} (type: {column.dtype})\n{"-"*(justification_width*2+1)}')
    print(f'Rows:'.ljust(justification_width), f'{column.shape[0]:0,.0f}'.rjust(justification_width))
    print(f'Unique values:'.ljust(justification_width), f'{column.nunique():0,.0f}'.rjust(justification_width))
    print(f'Null values:'.ljust(justification_width), f'{column.isnull().sum():0,.0f}'f' ({column.isnull().sum()/column.shape[0]:3.0%})'.rjust(justification_width))
    # Statistics for numeric values
    if column.dtype in ['float64', 'int']:
        print(f"Zero values:".ljust(justification_width), f"{(column==0).sum():0,.0f}"f' ({(column==0).sum()/column.shape[0]:3.0%})'.rjust(justification_width))
        print(f"Negative values:".ljust(justification_width), f"{(column<0).sum():0,.0f}"f' ({(column<0).sum()/column.shape[0]:3.0%})'.rjust(justification_width))
        print(f"Sum:".ljust(justification_width), f"{column.sum():0,.0f}".rjust(justification_width))
        print(f"Max:".ljust(justification_width), f"{column.max():0,.0f}".rjust(justification_width))
        for quantile in [0.95, 0.75, 0.5, 0.25, 0.05]:
            print(f"Q{int(quantile*100):0>2}:".ljust(justification_width), f"{column.quantile(quantile):0,.0f}".rjust(justification_width))
        print(f"Min:".ljust(justification_width), f"{column.min():0,.0f}".rjust(justification_width))

    print(f'\nTop {show_top_count_entries} entries:\n{column.value_counts(dropna=False).head(show_top_count_entries)}')
    print(f'\nTop {show_top_count_entries} entries length:\n{column.astype(str).str.len().value_counts(dropna=False).head(show_top_count_entries)}')
    clipboard_text = f"'{column.name}': '',"
    print(f"{'-'*50}\nText: {clipboard_text} copied to clipboard.")
    pd.DataFrame([clipboard_text]).to_clipboard(index=False, header=False)


class FastLoader:
    """FastLoader allows caching contents of files, which are frequently opened.
    During initial load, extra copy is pickled in '__fastloader__' folder.

    Functionality:
    - read_excel(*args, **kwargs) - reads Excel format files including xlsb. If engine in not specified,
      files will use pyxlsb automatically. *args, **kwargs are sames as pandas.
    """

    CACHE_FOLDER_NAME = '__fastloader__'

    @staticmethod
    def read_excel_via_cache(func):
        """Decorator for pandas.read_excel"""
        def wrapper(*args, **kwargs):
            # print(f'args: {args}')
            # print(f'kwargs: {kwargs}')

            # Get needed file attributes
            file_attributes = FastLoader.get_file_attributes(args, kwargs)
            # for k, v in file_attributes.items():
            #     print(k, v)

            # Add engine to kwargs
            FastLoader.update_kwargs_with_engine(file_attributes['engine'], kwargs)

            # Get file content
            time_start = perf_counter()
            if not file_attributes['hash_in_cache_folder']:
                print('Reading file from Excel... ', end='')
                df = func(*args, **kwargs)
                print(f'Done. ({perf_counter()-time_start:0.3f}s). ', end='')
                df.to_pickle(os.path.join(file_attributes['cache_folder'],
                                          file_attributes['hash']))
                print('Saved to cache.')
            else:
                print('Reading file from Cache... ', end='')
                df = pd.read_pickle(os.path.join(file_attributes['cache_folder'], file_attributes['hash']))
                print(f'Done ({perf_counter()-time_start:0.3f}s).')
            return df
        return wrapper

    @staticmethod
    def get_file_attributes(args, kwargs):
        # IO (input path)
        file_io = kwargs.get('io')
        if file_io is None:
            file_io = args[0]

        # Get absolute path file names and mod time
        file_path, file_fullname = os.path.split(os.path.abspath(file_io))
        file_name, file_extension = os.path.splitext(file_fullname)
        file_modification_time = os.stat(file_io).st_mtime

        # Cache folder. Create if not exist
        cache_folder = os.path.join(file_path, FastLoader.CACHE_FOLDER_NAME)
        if not os.path.exists(cache_folder):
            os.mkdir(cache_folder)
            print(f'Cache Folder {FastLoader.CACHE_FOLDER_NAME} was created.')

        # Get engine: Default is xlrd. For binary files, engine is set to pyxlsb.
        if file_extension in ['.xlsb']:
            engine = 'pyxlsb'
        elif file_extension in ['.xls']:
            engine = 'xlrd'
        else:
            engine = 'openpyxl'

        # Get sheet name (not sequence number)
        if kwargs.get('sheet_name') is not None:
            sheet_name = kwargs.get('sheet_name')
        elif len(args) >= 2:
            sheet_name = args[1]
        else:
            sheet_name = 0
        if isinstance(sheet_name, int):
            sheet_name = pd.ExcelFile(file_io, engine=engine).sheet_names[sheet_name]

        # Hash contains: file name, worksheet, modification time, extension items
        # Hash Extension items: combination of all kwargs ('key:value') not in ['io', 'sheet_name', 'engine']
        hash_extension_items = []
        for k, v in kwargs.items():
            if k not in ['io', 'sheet_name', 'engine']:
                hash_extension_items.append(f'{k}:{v}')
        hash_extension = ''.join(hash_extension_items)
        string_for_hash = f'{file_name}{sheet_name}{file_modification_time}{hash_extension}'.encode()
        _hash = hashlib.sha1(string_for_hash).hexdigest()
        hash_in_cache_folder = _hash in os.listdir(cache_folder)

        output_dict = {'file_io': file_io,
                       'file_path': file_path,
                       'file_fullname': file_fullname,
                       'file_name': file_name,
                       'file_extension': file_extension,
                       'file_modification_time': file_modification_time,
                       'engine': engine,
                       'sheet_name': sheet_name,
                       'hash': _hash,
                       'cache_folder': cache_folder,
                       'hash_in_cache_folder': hash_in_cache_folder}
        return output_dict

    @staticmethod
    def update_kwargs_with_engine(engine, kwargs):
        # Add engine to kwargs (to automatically set it for xlsb files)
        if engine not in kwargs:
            kwargs['engine'] = engine


@FastLoader.read_excel_via_cache
def read_excel(*args, **kwargs):
    """Cached version of pandas read excel"""
    return pd.read_excel(*args, **kwargs)


def merge_dfs(df_left, df_right, id_col, right_names_dict, report_missing=True):
    """Merge two df with specified and renamed columns
    @param df_left: DataFrame
    @param df_right: DataFrame
    @param id_col: str - left_df column name that will become id
    @param right_names_dict: {original_column_name: new_column_name}. Note: one must be assigned to 'id'
    @return: DataFrame with merged columns
    """

    # Drop new_column_names if exist in current database
    columns_exist_in_df_left = []
    for col in right_names_dict.values():
        if col in df_left.columns:
            columns_exist_in_df_left.append(col)
    if columns_exist_in_df_left:
        print(f'Columns {columns_exist_in_df_left} already exist in df_left. Will be dropped.')
        df_left.drop(columns=columns_exist_in_df_left, inplace=True)

    df_left['id'] = df_left[id_col]
    shape_before = df_left.shape[0]
    df_left = df_left.merge(df_right[list(right_names_dict)].rename(columns=right_names_dict), how='left', on='id')
    shape_after = df_left.shape[0]

    # Warn about not unique ids in right table
    if shape_after > shape_before:
        warn(f'IDs in df_right are not unique! Rows increased from {shape_before} to {shape_after}')

    # Warn about missing rows after merging
    if report_missing:
        added_columns = [right_names_dict[item] for item in right_names_dict if right_names_dict[item] != 'id']
        merging_successful = True
        for column in added_columns:
            missing_rows = df_left[column].isna().sum()
            if missing_rows:
                merging_successful = False
                print(f'After merging report: missing in column [{column}]: {missing_rows:0,.0f} ({missing_rows/ shape_after:0,.3%})')
        if not merging_successful:
            print(f'Missing {df_left.loc[df_left[added_columns[0]].isna()][id_col].nunique()} ids: <{df_left.loc[df_left[added_columns[0]].isna()][id_col].unique()}>')
    return df_left.drop(columns='id')


def warn_not_in_mapper(lookup_items, mapper_items, allowed_missing=None, msg='Missing mapper items!', only_warn=False):
    """Raise an exception about missing mapper items.
    @param msg: message to user
    @param only_warn: False - stop script; True - only console warning
    @param lookup_items: list
    @param mapper_items: list
    @param allowed_missing: str or list
    """

    unknown_items = [item for item in lookup_items if item not in mapper_items]

    # Exclude allowed items
    if allowed_missing is not None:
        if isinstance(allowed_missing, (str, float, int)):
            allowed_missing = [allowed_missing]
        unknown_items = [item for item in unknown_items if item not in allowed_missing]
    if only_warn:
        warn(f'{msg}: {unknown_items}')
    else:
        assert not unknown_items, print(f'\n[Program stopped] {msg}: {unknown_items}\n')
