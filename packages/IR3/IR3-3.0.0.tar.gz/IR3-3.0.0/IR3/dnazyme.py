
# Import necessary libraries
import pandas as pd
import numpy as np
import re
import sys
# from colorama import Fore, Style
from tqdm.auto import tqdm

def read_mutationTable(file_name):
  data = pd.read_csv(file_name)
  return data

#function of load substrate sequence
def read_s2(file_name):
  with open(file_name, 'r') as file:
    s2 = file.read().replace('\n', '')
  return s2

def pre_processing_table(data, col_name ='mutation'):
  pre_table = data
  pre_table[col_name] = pre_table[col_name].str.replace(r'[A-Za-z](?=\d)', '', regex=True)
  return pre_table

def extract_subsequences(input_sequence, length=37):
    subsequences = []
    sequence_length = len(input_sequence)

    for i in range(sequence_length - length + 1):
        subsequence = input_sequence[i:i+length]
        subsequences.append(subsequence)

    return subsequences

def split_subsequence(subsequence):
    p2 = subsequence[:14]
    core = subsequence[14:21]
    p1 = subsequence[21:]

    return p2, core, p1

def find_core_differences(core_sequence, WT_type='GTTGAAG'):
    differences = []

    for i, (core_base, WT_base) in enumerate(zip(core_sequence, WT_type)):
        if core_base != WT_base:
            position = i + 11  # Adjusting for the 0-based index
            differences.append((position, core_base))

    return differences

def format_differences(differences):
    return ' '.join([f"{position}{base}" for position, base in differences])

def get_relative_activity_for_differences(diff, mutation_df):
    max_relative_activity = -1
    selected_mutation = None
    for index, row in mutation_df.iterrows():
        mutation_differences = set(row['mutation'].split())
        if set(diff.split()).issubset(mutation_differences):
            relative_activity = row['Relative Activity']

            if relative_activity > max_relative_activity:
                max_relative_activity = relative_activity
                selected_mutation = row['mutation']

    return selected_mutation, max_relative_activity

def get_position(mutation_str):

  mutation_string = mutation_str
  matches = re.findall(r'(\d+)', mutation_string)
  position = [int(match) for match in matches]
  mutationTo = re.findall(r'\d([A-Za-z])', mutation_string)

  return position, mutationTo

def design_core_with_mutation(base_core, position_list, mutationTo):
    designed_core = list(base_core)

    for position, new_base in zip(position_list, mutationTo):
        index = position - 1  # Adjusting for 1-based index
        if index < len(designed_core):
            designed_core[index] = new_base

    return ''.join(designed_core)

def generate_complementary_sequence(sequence):
    complementary_dict = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    complementary_sequence = [complementary_dict[base] for base in sequence]
    return ''.join(complementary_sequence)

def reverse_sequence(sequence):
    return sequence[::-1]

def format_sequence(p2, core, p1):
    formatted_sequence = f"5'-{p1}-{core}-{p2}-3'"
    return formatted_sequence

def insert_bars_and_activity(sequence, activity_dicts):
    result_sequence = list(sequence)

    pos = 0
    for activity_dict in activity_dicts.values():
        index = activity_dict['index']+1  # Adjusting for 1-based index
        if 0 <= index < len(result_sequence):
            activity_value = activity_dict['Relative Activity']
            result_sequence.insert(index + pos, f"|({activity_value:.3f})")  # Insert after the specified index
            pos += 1

    return ''.join(result_sequence)

def format_output(result):
    cut_site = result["cut_site"]
    dzyme = result["dzyme"]
    substrate = result["substrate"]
    activity = result["activity"]

    enzyme_length = len(dzyme.split('-')[1])
    substrate_length = len(substrate.split('-')[2])

    formatted_output = f"Cut-site #{cut_site}\n\n"
    formatted_output += f"{' ' * 27}1,2,3,4,5,6,7,8,9,10,P2\n"
    formatted_output += f"(16nt) {dzyme} enzyme    (14nt)\n"
    formatted_output += f"(13nt) {substrate} substrate (13nt)\n"
    formatted_output += f"{' ' * 27}17,16,15,14,13,12,11\n"
    formatted_output += f"Relative-Activity: {activity}\n"
    formatted_output += "To Ensure Activity, Enforce: G-C or A-T (enzyme-substrate) at position SII.\n"
    formatted_output += f"\n"

    return formatted_output

import re
from tqdm import tqdm

def process_substrate(input_sequence_path, mutation_table = 'mutation_table.csv', output_path='output.txt'):

    base_core_sequence = 'TAGTTGAGCT'
    mutation_table = pre_processing_table(read_mutationTable(mutation_table))
    s2 = read_s2(input_sequence_path)


    result = extract_subsequences(s2)

    core_sequences = []
    core_sequences_info = {}

    for i, subsequence in enumerate(result):
        p2, core, p1 = split_subsequence(subsequence)
        core_sequences_info[i] = {'index': f"{i}-{i+37}", 'p2': p2, 'core': core, 'p1': p1}
        core_sequences.append(core)

    difference_sequences = []
    for core_sequence in core_sequences:
        differences = find_core_differences(core_sequence)
        formatted_string = format_differences(differences)
        difference_sequences.append(formatted_string)

    c = 0
    mutations = {}
    for i, difference_sequence in tqdm(enumerate(difference_sequences)):
        subsequence = core_sequences_info[i]
        p1 = subsequence['p1']
        p2 = subsequence['p2']
        mutation, relative_activity = get_relative_activity_for_differences(difference_sequence, mutation_table)

        if relative_activity > -1:
            mutations[c] = {'index': i, 'mutation': mutation, 'Relative Activity': relative_activity}
            c += 1

    s1_core_sequences = {}
    for mIndex in range(len(mutations)):
        m = mutations[mIndex]
        muta = m['mutation']
        if muta != ' ':
            position_list, mutationTo = get_position(muta)
            core = design_core_with_mutation(base_core_sequence, position_list, mutationTo)
        else:
            core = base_core_sequence
        s1_core_sequences[mIndex] = {'core': core}

    s1_sequences = {}
    s2_sequences = {}
    for i in range(len(s1_core_sequences)):
        m = mutations[i]
        inde = m['index']
        cut_cite = inde + 14 + 5
        ful_sequence = core_sequences_info[inde]
        p2 = ful_sequence['p2']
        p1 = ful_sequence['p1']
        p2_s1 = generate_complementary_sequence(p2)
        p1_s1 = generate_complementary_sequence(p1)
        s2_sequences[i] = ful_sequence
        s1_sequences[i] = {'index': cut_cite, 'p2': p2_s1, 'core': s1_core_sequences[i]['core'], 'p1': p1_s1, 'Relative Activity': m['Relative Activity']}

    if len(s2_sequences) == 0:
        with open(output_path, 'w') as output_file:
            output_file.write("The input sequence does not have a matching mutation and activity value in the mutation table.")
    else:
        marked_s2_sequence = "5'-" + insert_bars_and_activity(s2, s1_sequences) + "-3'"
        # print("\nResults of I-R3 Analysis\n")
        # print("I.  Substrate: ", marked_s2_sequence, "\n")

        with open(output_path, 'w') as output_file:
            output_file.write("\nResults of I-R3 Analysis\n")
            output_file.write("\nI.  Substrate: " + marked_s2_sequence + "\n\n")

            dzyme_results = []

            for i in range(len(s1_sequences)):
                s1_raw = s1_sequences[i]
                s2_raw = s2_sequences[i]

                # s1 sequence
                s1_p2 = s1_raw['p2'][::-1]
                s1_p1 = s1_raw['p1'][::-1]

                # s2 sequence
                s2_p2 = s2_raw['p2'][::-1]
                s2_p1 = s2_raw['p1'][::-1]
                s2_p2 = s2_p2[:-1] + "-"
                s2_p1 = '---' + s2_p1[3:]
                s2_core = s2_raw['core'][::-1]
                s2_core = s2_core[:2] + '|' + s2_core[2:] + "--"

                dzyme = f"5' {s1_p1}-{s1_raw['core']}-----------{s1_p2} 3'"
                substrate = f"3' {s2_p1}-{s2_core}-----------{s2_p2} 5'"

                result = {
                    "cut_site": s1_raw['index'],
                    "dzyme": dzyme,
                    "substrate": substrate,
                    "activity": s1_raw['Relative Activity'],
                }
                dzyme_results.append(result)

            # print("II. D-zyme Designs & Targets\n")
            # print("\n")
            output_file.write("\nII. D-zyme Designs & Targets\n")
            output_file.write("\n")
            for i, result in enumerate(dzyme_results, start=1):
                formatted_output = format_output(result)
                # print(formatted_output)
                output_file.write(formatted_output)
