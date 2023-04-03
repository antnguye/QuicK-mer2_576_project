from qm2_human_rarity import compare_against_1000
import os

test_file = "qm2_human_rarity/DM09_subset.qm2.bed"
output_table, output_dict = compare_against_1000.read_in_qm2(test_file, False)

test_dups = compare_against_1000.find_dups(output_table, output_dict)

test_dels = compare_against_1000.find_deletions(output_table, output_dict)


def test_write_dups_and_dels_complete_transfer():
    compare_against_1000.write_dups_and_dels(output_dict, test_dups, test_dels, "dm09_test")
    assert os.path.exists("dm09_test_duplications.bed") == 1, "A file with the specified name was not created"
    test_output = open("dm09_test_duplications.bed", "r")
    line_counter = 0
    for line in test_output:
        line_counter += 1
    assert line_counter == (len(test_dups)), "Entries in the bed file differ from the number of duplications provided."
    test_output.close()
    os.remove("dm09_test_duplications.bed")


def test_write_dups_and_dels_confirm_results():
    compare_against_1000.write_dups_and_dels(output_dict, test_dups, test_dels, "dm09_test")
    test_output = open("dm09_test_deletions.bed", "r")
    test_line = test_output.readline()
    test_line = test_line.split("\t")
    assert (test_line[0]) == "chr1", "File output contents do not match expected format or order"
    test_output.close()
    os.remove("dm09_test_deletions.bed")

