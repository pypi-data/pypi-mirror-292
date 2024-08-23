#!/usr/bin/env python3
# Telometer v0.9
# Created by: Santiago E Sanchez
# Artandi Lab, Stanford University, 2024
# Measures telomeres from ONT or PacBio long reads aligned to a T2T genome assembly
# Simple Usage: telometer -b sorted_t2t.bam -o output.tsv

import pysam
import regex as re
import pandas as pd
import time
import argparse
from multiprocessing import Pool, cpu_count


def reverse_complement(seq):
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'N': 'N'}
    return "".join(complement[base] for base in reversed(seq))


def get_telomere_repeats():
    telomere_repeats = ['CCCTAA', 'TTAGGG']
    telomere_repeats_rc = [reverse_complement(repeat) for repeat in telomere_repeats]
    return telomere_repeats + telomere_repeats_rc


def identify_telomere_regions(seq, telomere_motifs, window_size=100, step_size=10, density_threshold=0.1, max_gap_length=50):
    telomere_regions = []
    current_start = None
    gap_length = 0
    has_large_gap = False
    densities = []

    combined_motif_pattern = '|'.join(f'({motif})' for motif in telomere_motifs)

    for i in range(0, len(seq) - window_size + 1, step_size):
        window_seq = seq[i:i + window_size]
        motif_count = len(re.findall(combined_motif_pattern, window_seq))
        density = motif_count / (window_size / len(telomere_motifs[0]))  # Assuming all motifs have similar lengths
        densities.append(density)

        if density >= density_threshold:
            if current_start is None:
                current_start = i
            gap_length = 0
        else:
            if current_start is not None:
                gap_length += step_size
                if gap_length > max_gap_length:

                    mismatch_motif_count = len(re.findall(f"({combined_motif_pattern}){{e<=1}}", window_seq))
                    mismatch_density = mismatch_motif_count / (window_size / len(telomere_motifs[0]))

                    if mismatch_density >= density_threshold:

                        gap_length = 0
                    else:
                        has_large_gap = True
                        telomere_regions.append((current_start, i - gap_length + step_size))
                        current_start = None
                        gap_length = 0

    if current_start is not None:
        telomere_regions.append((current_start, len(seq)))

    return telomere_regions, densities, has_large_gap, combined_motif_pattern


def measure_telomere_length(seq, telomere_motifs, window_size=100, step_size=10, density_threshold=0.1, max_gap_length=50):
    telomere_regions, densities, has_large_gap, combined_motif_pattern = identify_telomere_regions(seq, telomere_motifs, window_size, step_size, density_threshold, max_gap_length)

    if not telomere_regions:
        return 0, 0, 0, densities, has_large_gap, combined_motif_pattern


    terminus_regions = []
    for start, end in telomere_regions:
        if start < 100 or end > len(seq) - 100:
            terminus_regions.append((start, end))

    if not terminus_regions:
        return 0, 0, 0, densities, has_large_gap, combined_motif_pattern


    telomere_start, telomere_end = terminus_regions[0]
    telomere_length = telomere_end - telomere_start

    return telomere_start, telomere_end, telomere_length, densities, has_large_gap, combined_motif_pattern


def process_read(read_data, telomere_motifs, max_gap_length, min_read_len):
    if read_data['is_unmapped'] or read_data['reference_name'] == 'chrM':
        return None

    if read_data['reference_start'] > 30000 and read_data['reference_end'] < read_data['reference_length'] - 30000:
        return None

    seq = read_data['query_sequence']
    if seq is None or len(seq) < min_read_len:
        return None


    alignment_start = read_data['reference_start']
    alignment_end = read_data['reference_end']
    reference_genome_length = read_data['reference_length']

    if alignment_start < 15000 and alignment_end <= reference_genome_length - 30000:
        arm = "p"
    else:
        arm = "q"

    direction = "rev" if read_data['is_reverse'] else "fwd"


    telomere_start, telomere_end, telomere_length, densities, has_large_gap, combined_motif_pattern = measure_telomere_length(seq, telomere_motifs, max_gap_length=max_gap_length)
    if telomere_length < 1:
        return None
    return {
        'chromosome': read_data['reference_name'],
        'reference_start': alignment_start,
        'reference_end': alignment_end,
        'telomere_length': telomere_length,
        #'subtel_boundary_length': telomere_end - telomere_start,
        'read_id': read_data['query_name'],
        'mapping_quality': read_data['mapping_quality'],
        'read_length': len(seq),
        'arm': arm,
        'direction': direction
        #'has_large_gap': has_large_gap
    }


def process_read_wrapper(args):
    return process_read(*args)


def process_bam_file(bam_file_path, output_file_path, max_gap_length=100, min_read_len=1000, num_processes=8):
    start_time = time.time()


    bam_file = pysam.AlignmentFile(bam_file_path, "rb")

    telomere_motifs = get_telomere_repeats()

    results = []
    read_results = {}
    total_reads = 0
    large_gap_count = 0


    read_data_list = [{
        'query_name': read.query_name,
        'is_unmapped': read.is_unmapped,
        'is_reverse': read.is_reverse,
        'reference_start': read.reference_start,
        'reference_end': read.reference_end,
        'reference_name': read.reference_name,
        'mapping_quality': read.mapping_quality,
        'query_sequence': read.query_sequence,
        'reference_length': bam_file.get_reference_length(read.reference_name) if read.reference_name is not None else None
    } for read in bam_file if read.reference_name is not None and read.reference_name != 'chrM']

    # Use multiprocessing Pool for parallel processing
    with Pool(processes=num_processes) as pool:
        for result in pool.imap_unordered(process_read_wrapper, [(rd, telomere_motifs, max_gap_length, min_read_len) for rd in read_data_list]):
            if result:
                total_reads += 1
                #if result['has_large_gap']:
                #    large_gap_count += 1

                # Check for existing results with the same read_id
                existing_result = read_results.get(result['read_id'])
                if existing_result:
                    if (result['mapping_quality'] > existing_result['mapping_quality'] or
                        (result['mapping_quality'] == existing_result['mapping_quality'] and
                         result['telomere_length'] > existing_result['telomere_length'])):
                        read_results[result['read_id']] = result
                else:
                    read_results[result['read_id']] = result

    bam_file.close()

    # Convert results to a DataFrame and save to a TSV file
    results_df = pd.DataFrame(list(read_results.values()))
    results_df.to_csv(output_file_path, sep='\t', index=False)

    # Calculate and print the percentage of telomeres with gaps larger than max_gap_length
    #if total_reads > 0:
    #    large_gap_percentage = (large_gap_count / total_reads) * 100
    #else:
    #    large_gap_percentage = 0

    print(f"Telometer completed successfully. Total telomeres measured: {len(read_results)}")
    print(f"Total processing time: {time.time() - start_time:.2f} seconds")

def run_telometer:
    parser = argparse.ArgumentParser(description='Calculate telomere length from a BAM file.')
    parser.add_argument('-b', '--bam', help='The path to the sorted BAM file.', required=True)
    parser.add_argument('-o', '--output', help='The path to the output file.', required=True)
    parser.add_argument('-m', '--minreadlen', default=1000, type=int, help='Minimum read length to consider (Default: 1000 for telomere capture, use 4000 for WGS). Optional', required=False)
    parser.add_argument('-g', '--maxgaplen', default=100, type=int, help='Maximum allowed gap length between telomere regions. Optional', required=False)
    parser.add_argument('-t', '--threads', default=cpu_count(), type=int, help='Number of processing threads to use. Optional', required=False)
    args = parser.parse_args()
    process_bam_file(args.bam, args.output, max_gap_length=args.maxgaplen, min_read_len=args.minreadlen, num_processes=args.threads)

if __name__ == "__main__":
    run_telometer()
