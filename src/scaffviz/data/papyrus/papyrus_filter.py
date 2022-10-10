import os.path

import pandas as pd
from papyrus_scripts.reader import read_papyrus
from papyrus_scripts.preprocess import keep_quality, keep_accession
from papyrus_scripts.preprocess import consume_chunks

def papyrus_filter(acc_key: list, quality: str, outdir : str, prefix : str = None, drop_duplicates: bool = True, chunk_size : int = 1e5, use_existing : bool = True, stereo : bool = False, plusplus : bool = False):
    """
    Filters the downloaded papyrus dataset for quality and accession key (UniProt) and outputs a .tsv file of all compounds fulfilling these requirements.

    Args:
        acc_key: list of UniProt accession keys
        quality: str with minimum quality of dataset to keep
        outdir: path to the location of Papyrus data
        prefix: prefix for the output file
        drop_duplicates: boolean to drop duplicates from the final dataset
        chunk_size: integer of chunks to process one at the time
        use_existing: if `True`, use existing data if available
        stereo: if `True`, read stereochemistry data (if available)
        plusplus: if `True`, read high quality Papyrus++ data (if available)
    Output:
        .tsv file with all compounds fulfilling the requirements
    """
    prefix = prefix or f"{'_'.join(acc_key)}_{quality}"
    outfile = os.path.join(outdir, f"{prefix}.tsv")

    if use_existing and os.path.exists(outfile):
        print(f"Using existing data from {outfile}...")
        return pd.read_table(outfile, sep="\t", header=0), outfile

    # read data
    sample_data = read_papyrus(is3d=stereo, chunksize=chunk_size, source_path=outdir, plusplus=plusplus)
    print("Read all data.")

    # data filters
    filter1 = keep_quality(data=sample_data, min_quality=quality)
    filter2 = keep_accession(data=filter1, accession=acc_key)
    print("Initialized filters.")

    # filter data per chunk
    filtered_data = consume_chunks(generator=filter2)
    print(f"Number of compounds:{filtered_data.shape[0]}")

    # filter out duplicate InChiKeys
    if drop_duplicates:
        print("Filtering out duplicate molecules")
        amnt_mols_i = len(filtered_data["InChIKey"])
        filtered_data.drop_duplicates(subset=["InChIKey"], inplace=True, ignore_index=True)
        amnt_mols_f = len(filtered_data["InChIKey"])
        print(f"Filtered out {amnt_mols_i - amnt_mols_f} duplicate molecules")

    # write filtered data to .tsv file
    filtered_data.to_csv(outfile, sep= "\t", index=False)
    print(f"Wrote data to file '{outfile}'.")

    return filtered_data, outfile



