from nbformat.v4 import new_code_cell, new_markdown_cell
import re
import textwrap
import pandas as pd
import numpy as np
import black
import hashlib

test_case_name_pattern = r'^\s*_test_case\s*=\s*[\'"](.*)[\'"]'
test_case_points_pattern = r'^\s*_points\s*=\s*(.*)[\s#]*.*[\r\n]'
manual_grading_pattern = r'^\s*_grade_manually\s*=\s*(True|False)'

def extract_test_case_metadata_from_cell(source: str) -> str:
    tc_result = re.search(
        test_case_name_pattern,
        source,
        flags=re.MULTILINE
    )
    
    if not tc_result or len(tc_result.groups()) == 0:
        return None
    
    metadata = {
        'test_case': tc_result.groups()[0],
        'points': 0,
        'grade_manually': False
    }
    
    points_result = re.search(
        test_case_points_pattern,
        source,
        flags=re.MULTILINE
    )
    
    # if the test case code cell does not include _points
    # no points will be assigned (default of zero)
    if points_result and len(tc_result.groups()) > 0:
        metadata['points'] = float(points_result.groups()[0])
        
    manual_grading_result = re.search(
        manual_grading_pattern,
        source,
        flags=re.MULTILINE
    )
    
    if manual_grading_result and len(manual_grading_result.groups()) > 0:
        metadata['grade_manually'] = bool(manual_grading_result.groups()[0])
    
    return metadata



def extract_test_cases_metadata_from_notebook(nb) -> str:
    metadata_list = []

    for cell in nb.cells:
        if cell.cell_type == 'code':
            test_case_metadata = extract_test_case_metadata_from_cell(cell.source)
            
            if test_case_metadata:
                metadata_list.append(test_case_metadata)
                
    return metadata_list



def does_cell_contain_test_case(cell) -> bool:
    search_result = re.search(
        test_case_name_pattern,
        cell.source,
        flags=re.MULTILINE
    )
    
    return search_result and (len(search_result.groups()) > 0)



def is_manually_graded_test_case(cell) -> bool:
    search_result = re.search(
        manual_grading_pattern,
        cell.source,
        flags=re.MULTILINE
    )
    
    return search_result and (len(search_result.groups()) > 0)



def convert_test_case_using_grader_template(cell) -> str:
    if not does_cell_contain_test_case(cell):
        # do nothing if not a test case cell
        return
    
    source = cell.source
    
    if is_manually_graded_test_case(cell):
        grader_template_code = 'jupyter-cell-scripts/grader-manual-template.py'
        source = cell.source
    else:
        grader_template_code = 'jupyter-cell-scripts/grader-template.py'
        source = textwrap.indent(cell.source, '    ')
        
    with open(grader_template_code) as f:
        grader_template_code = f.read()
        
    converted_source = grader_template_code.replace('# TEST_CASE_REPLACE_HERE', source)
    
    cell.source = converted_source



def preprocess_test_case_cells(nb):
    for cell in nb.cells:
        convert_test_case_using_grader_template(cell)
            
    return nb

            

def add_grader_scripts(nb):
    with open('jupyter-cell-scripts/prepend-to-start-of-notebook.py') as f:
        prepend_script = f.read()
        prepend_cell = new_code_cell(prepend_script)
    
    with open('jupyter-cell-scripts/append-to-end-of-notebook.py') as f:
        append_script = f.read()
        append_cell = new_code_cell(append_script)
    
    nb.cells.insert(0, prepend_cell)
    nb.cells.append(append_cell)


    
def remove_grader_scripts(nb):
    # remove prepend, append cells added by LambdaGrader before storing to HTML
    nb.cells.pop(0)  # first cell (added by LambdaGrader)
    nb.cells.pop()   # last cell (added by LambdaGrader)
    
    return nb



# TODO: The current code only extracts code between # YOUR CODE BEGINS and # YOUR CODE ENDS
# This will not work if a learner changes or deletes the comments
# Unused, but may be useful later
def extract_user_code_from_cell_source(source: str) -> str:
    tc_result = re.search(
        r'.*# YOUR CODE BEGINS[\s\n]*(.*)# YOUR CODE ENDS',
        source,
        flags=re.MULTILINE | re.DOTALL
    )
    
    if not tc_result or len(tc_result.groups()) == 0:
        return None
    
    user_code = tc_result.groups()[0]
    user_code = user_code.rstrip()
    
    return user_code



def extract_user_code_from_notebook(nb) -> str:
    full_code = ''

    for cell in nb.cells:
        if (cell.cell_type == 'code') and not does_cell_contain_test_case(cell) and cell.source:
            full_code += cell.source + '\n\n'
                
    return full_code



def remove_comments(source: str) -> str:
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|#[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (# single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return "" # so we will return empty to remove the comment
        else: # otherwise, we will return the 1st group
            return match.group(1) # captured quoted-string
    return regex.sub(_replacer, source)



def get_test_cases_hash(nb) -> str:
    test_cases_code = ''

    for cell in nb.cells:
        if (cell.cell_type == 'code') and does_cell_contain_test_case(cell):
            # standardize code before hasing
            # by removing comments and formatting the code using the Black formatter
            standardized_code = remove_comments(cell.source)
            standardized_code = black.format_str(standardized_code, mode=black.Mode())
            
            # concatenate to test_cases_code
            test_cases_code += standardized_code
    
    # generate an MD5 hash
    hash_str = hashlib.md5(test_cases_code.encode('utf-8')).hexdigest()
    return hash_str



def generate_text_summary(graded_result) -> str:
    summary = ''
    summary += f"File: {graded_result['filename']}\n"
    summary += f"Autograded Score: {graded_result['learner_autograded_score']} out of {graded_result['max_autograded_score']}\n"
    summary += f"Passed {graded_result['num_passed_cases']} out of {graded_result['num_autograded_cases']} autograded test cases\n"
    
    if graded_result['num_manually_graded_cases'] > 0:
        summary += f"{graded_result['num_manually_graded_cases']} items will be graded manually.\n"
        summary += f"{graded_result['max_manually_graded_score']} points are available on manually graded items.\n"
        summary += f"{graded_result['max_total_score']} total points are available.\n"
    
    summary += f"Grading took {graded_result['grading_duration_in_seconds']} seconds\n\n"
    summary += 'Test Case Summary\n'

    for o in graded_result['results']:
        summary += "-----------------\n"
        summary += f"{o['test_case_name']} {'passed' if o['pass'] else 'failed'}: {o['points']} out of {o['available_points']} points\n"

        if not o['pass']:
            summary += f"[Autograder Output]\n{o['message']}\n\n"
            
    return summary



def add_graded_result(nb, graded_result):
    gr = graded_result
    gr_cells = []

    # add result summary
    gr_cells.append(new_markdown_cell('# 🧭 LambdaGrader Summary'))
    
    learner_score_in_percentage = f" ({round(gr['learner_autograded_score'] / gr['max_autograded_score'] * 100, 2)}%)" if gr['max_autograded_score'] != 0 else None
    
    gr_dict_for_df = {
        '**Autograded Score**': f"**{gr['learner_autograded_score']} out of {gr['max_autograded_score']}** {learner_score_in_percentage}",
        'Autograded Test Cases': f"Passed {gr['num_passed_cases']} out of {gr['num_autograded_cases']} cases",
        'Pending Test Cases': f"⌛ {gr['num_manually_graded_cases']} item{'s' if gr['num_manually_graded_cases'] > 1 else ''} worth a total of {gr['max_manually_graded_score']} point{'s' if gr['max_manually_graded_score'] > 1 else ''} require manual grading",
        'Total Available Points': gr['max_total_score'],
        'Filename': gr['filename'],
        'Autograder Finished At': gr['grading_finished_at'],
        'Autograder Duration': f"{gr['grading_duration_in_seconds']} second{'' if gr['grading_duration_in_seconds'] == 0 else 's'}",
        'Test Cases MD5 Hash': gr['test_cases_hash'],
        'Submission File MD5 Hash': gr['submission_notebook_hash'],
        'Autograder Python Version': f"Python {gr['grader_python_version']}",
        'Autograder Platform': gr['grader_platform']
    }
    
    if gr['num_manually_graded_cases'] == 0:
        del gr_dict_for_df['Pending Test Cases']
    
    df_metadata = pd.DataFrame({
        'item': gr_dict_for_df.keys(),
        'description': gr_dict_for_df.values()
    })
    gr_cells.append(new_markdown_cell(df_metadata.to_markdown(index=False)))
    gr_cells.append(new_markdown_cell('## Test cases result'))

    df_r = pd.DataFrame(gr['results'])
    
    df_r.loc[df_r['grade_manually'], 'points'] = '-'
    df_r['available_points'] = df_r['available_points'].astype(str)
    
    # inner function to generate a human-readable result
    def get_human_readable_result(row):
        if row['grade_manually']:
            return '⌛ Requires manual grading'
        else:
            return '✔️ Pass' if row['pass'] else '❌ Fail'

    df_r['pass'] = df_r.apply(get_human_readable_result, axis=1)
    df_r.rename(columns={
        'available_points': 'max_score',
        'pass': 'result',
        'points': 'learner_score'
    }, inplace=True)
    df_r.drop(columns=['grade_manually'], inplace=True)

    gr_cells.append(new_markdown_cell(df_r.to_markdown()))
    gr_cells.append(new_markdown_cell('\n---\n'))
    
    nb.cells = gr_cells + nb.cells
    
    return nb