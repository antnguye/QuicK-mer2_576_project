import numpy as np


def read_in_qm2(filename, is_human=False):
    """
    Read in a BED file produced by QuicK-mer2, and create a numpy array with one row
    and 2300498 windows, where eachvalue is the copy number for that particular window
    is_human: a Boolean value to indicate human sample processed by GrCH38
    Return: sample_table, the numpy array
    """
    # set variables
    human_window_count = 2300498
    # the number of QM2 windows produced by a sample that has been processed to GrCH38
    table_key = 0
    sample_dict = {}

    # open file
    f = open(filename, 'rt')
    inFile = f.readlines()
    file_size = len(inFile)
    sample_table = np.zeros(file_size, dtype=np.single)

    if is_human is True and file_size != human_window_count:
        # error catch for if the BED file is not mapped to GrCH38
        f.close()
        raise Exception(
            "The windows of this sample is not equal to the number of GrCH38 windows. "
            "Double-check that this sample has been mapped to GrCH38, and has been "
            "processed through QuicK-mer2.")
    # parse file
    for line in inFile:
        line = line.rstrip().split()
        coord = (line[0], line[1], line[2])
        # key = table_index/window number, coord = coordinates of the window
        sample_dict[table_key] = coord
        # assigning the correct column with the copy number as a float
        sample_table[table_key] = float(line[3])
        table_key += 1
    f.close()
    return sample_table, sample_dict


def find_deletions(sample_table, sample_dict):
    """
    :param sample_dict: a dictionary provided by file read-in, where key = table index
    and value = coordinates of the window
    :param sample_table: the read-in QM2 file converted into a numpy array
    :return: final_dels, a list which contains lists which contains pairs, where each
    pair is a copy number that is below 1.5 and its corresponding window index,
    each list is a series of at least 3 consecutive windows that all have their
    copy number below 1.5, and the overall list that contains the series of deletions
    found in sample_table
    """
    if sample_table is None:
        return "No table provided."
    dele = False
    final_dels = []
    current = []
    current_chro = ""
    window_index = 0
    for cn in sample_table:
        if dele is True:
            if cn < 1.5:  # deletion found
                sample_chro = sample_dict[window_index][0]
                # deletion found, still on same chromosome
                if sample_chro == current_chro:
                    current.append([cn, window_index])
                else:
                    # deletion found, but different chromosome
                    if len(current) >= 3:
                        final_dels.append(current)
                    current = [[cn, window_index]]
                    current_chro = sample_dict[window_index][0]
            else:  # deletion searching ended, reset current = [] and dele = False
                if len(current) >= 3:
                    final_dels.append(current)
                current = []
                dele = False
        else:
            if cn < 1.5:
                current_chro = sample_dict[window_index][0]  # pull chromosome
                dele = True
                current.append([cn, window_index])

        window_index += 1

    if len(current) >= 3:  # if sample ends on a valid deletion, add it
        final_dels.append(current)

    if len(final_dels) == 0:
        return "No deletions found in this sample."
    else:
        return final_dels


def find_dups(sample_table, sample_dict):
    """
    :param sample_dict: dictionary provided by file read-in, where key = table index
    and value = coordinates of the window
    :param sample_table: the read-in QM2 file converted in a numpy array
    :return: final_dups, a list which contains lists which contains pairs, where each
    pair is a copy number that is above 2.5 and its corresponding window index,
    each list is a series of at least 3 consecutive windows that all have their
    copy number above 2.5, and the overall list that contains the series
    of duplications found in sample_table
    """
    # tested and implemented
    if sample_table is None:
        return "No table provided."
    dup = False
    final_dups = []
    current = []
    current_chro = ""
    window_index = 0
    for cn in sample_table:
        if dup is True:
            if cn > 2.5:  # duplication found
                sample_chro = sample_dict[window_index][0]
                # duplication found, still on same chromosome
                if sample_chro == current_chro:
                    current.append([cn, window_index])
                else:
                    # duplication found, but different chromosome
                    if len(current) >= 3:
                        final_dups.append(current)
                    current = [[cn, window_index]]
                    current_chro = sample_dict[window_index][0]
            else:  # duplication searching ended, reset current = [] and dup = False
                if len(current) >= 3:
                    final_dups.append(current)
                current = []
                dup = False
        else:
            if cn > 2.5:
                current_chro = sample_dict[window_index][0]  # pull chromosome
                dup = True
                current.append([cn, window_index])
        window_index += 1

    if len(current) >= 3:  # if sample ends on a valid duplication, add it
        final_dups.append(current)

    if len(final_dups) == 0:
        return "No duplications found in this sample."
    else:
        return final_dups


def get_coords(start, end, sample_dict):
    """
    :param start: window index of the beginning of the duplication/deletion
    :param end: window index of the end of the duplication/deletion
    :param sample_dict: dictionary made by read_in_qm2 with window -> coordinates
    conversion
    :return: a list, with the chromosome, start genomic bp, and end genomic bp
    """
    chro = sample_dict[start][0]
    chro_check = sample_dict[end][0]
    if chro != chro_check:
        raise Exception("Chromosomes do not match between start and end windows.")
    start_coord = sample_dict[start][1]
    end_coord = sample_dict[end][2]
    if int(start_coord) >= int(end_coord):
        raise Exception("End coordinate is greater than start - double-check "
                        "arguments.")
    else:
        return [chro, start_coord, end_coord]


def compare_1000_genomes(sample_dict, normalcy_file_path, final_dups=None,
                         final_dels=None):
    """
    :param sample_dict: dictionary initialized by read_in_qm2 with window  ->
    coordinates conversion
    :param normalcy_file_path: file path as a string to where the
    "99_normalcy_range_tenk_genomes.npy" file is located
    :param final_dups: dups produced by find_dups
    :param final_dels: deletions produced by find_deletions
    :return: dup_normal_bool and del_normal_bool; both are dictionaries, with
    key = coordinates in UCSC format and value is True or False, depending on
    whether or not that duplication or deletion is rare; rarity is defined as the
    median copy number of the sample duplication/deletion falling outside of 99% of
    the 1000 Genomes range for those same windows
    """
    normalcy = np.load(normalcy_file_path)
    dup_normal_bool = {}
    del_normal_bool = {}
    if final_dups is not None:
        for dup in final_dups:
            if dup[0][0] >= 2297329 or dup[0][1] >= 2297329:
                break
            cn_list = []
            dup_windows = []
            for window in dup:
                cn_list.append(window[0])
                dup_windows.append(window[1])
            median_sample_cn = np.median(cn_list)
            max_normal = np.max(normalcy[dup_windows[0]:dup_windows[-1]])
            sample_dup = get_coords(dup_windows[0], dup_windows[-1], sample_dict)
            sample_dup_str = "{}:{}-{}".format(sample_dup[0], sample_dup[1],
                                               sample_dup[2])
            if median_sample_cn > max_normal:
                dup_normal_bool[sample_dup_str] = True
            else:
                dup_normal_bool[sample_dup_str] = False
    if final_dels is not None:
        for dele in final_dels:
            if dele[0][0] >= 2297329 or dele[0][1] >= 2297329:
                break
            cn_list = []
            del_windows = []
            for window in dele:
                cn_list.append(window[0])
                del_windows.append(window[1])
            median_sample_cn = np.median(cn_list)
            min_normal = np.min(normalcy[del_windows[0]:del_windows[-1]])
            sample_del = get_coords(del_windows[0], del_windows[-1], sample_dict)
            sample_del_str = "{}:{}-{}".format(sample_del[0], sample_del[1],
                                               sample_del[2])
            if median_sample_cn < min_normal:
                del_normal_bool[sample_del_str] = True
            else:
                del_normal_bool[sample_del_str] = False

    return dup_normal_bool, del_normal_bool


def write_dups_and_dels(sample_dict, final_dups=None, final_dels=None,
                        sample_name="sample"):
    """
    :param final_dups: duplications passed by find_dups, defaults to None
    :param final_dels: deletions passed by find_dels, defaults to None
    :param sample_dict: dictionary with coord conversion initialized by read_in_qm2
    :param sample_name: name of the sample for writing, defaults to "sample"
    :return: N/A, writes files
    """
    if final_dups is not None:
        f = open("{}_duplications.bed".format(sample_name), 'w')
        for dup in final_dups:
            start_window = dup[0][1]
            end_window = dup[-1][1]
            coords = get_coords(start_window, end_window, sample_dict)
            all_cn = []
            for windows in dup:
                all_cn.append(windows[0])
            dup_cn = np.median(all_cn)
            f.write('\t'.join(coords) + '\t' + str(dup_cn) + '\n')
        f.close()
    if final_dels is not None:
        f = open("{}_deletions.bed".format(sample_name), 'w')
        for dele in final_dels:
            start_window = dele[0][1]
            end_window = dele[-1][1]
            coords = get_coords(start_window, end_window, sample_dict)
            all_cn = []
            for windows in dele:
                all_cn.append(windows[0])
            dele_cn = np.median(all_cn)
            f.write('\t'.join(coords) + '\t' + str(dele_cn) + '\n')
        f.close()


def write_rarity(sample_name, dup_rarity_dict, del_rarity_dict):
    """
    :param sample_name: name of the sample to study
    :param dup_rarity_dict: the dict of rare duplications produced by
    compare_1000_genomes
    :param del_rarity_dict: the dict of rare deletions produced by compare_1000_genomes
    :return: N/A
    """
    f = open("{}.rare_duplications.csv".format(sample_name), 'w')
    for dup, rarity in dup_rarity_dict.items():
        f.write(str(dup) + ',' + str(rarity) + '\n')
    f.close()

    f = open("{}.rare_deletions.csv".format(sample_name), 'w')
    for dup, rarity in del_rarity_dict.items():
        f.write(str(dup) + ',' + str(rarity) + '\n')
    f.close()
