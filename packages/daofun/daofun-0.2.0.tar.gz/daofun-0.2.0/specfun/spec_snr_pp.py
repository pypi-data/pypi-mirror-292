#!/usr/bin/env python
# -*-encoding:utf-8 -*-

r'''
    SNR
      derivates SNR per pixel
'''

import numpy as np
import pandas as pd
import argparse
import os


# def snr_measure(spec):
#   """
#   Calculates the signal-to-noise ratio of a stellar spectrum using the derivative-based estimator.

#   Args:
#     flux: A numpy array of flux values.

#   Returns:
#     The signal-to-noise ratio.
#   """
#   flux = spec.flux.values

#   # Calculate the median of the flux values.
#   median_flux = np.median(flux)

#   noise = 1.482602 / np.sqrt(6.0) * np.median([np.abs(2 * flux[i]- flux[i-2] - flux[i+2]) for i in range(2, len(flux)-2)])

#     # Calculate the signal-to-noise ratio.
#   snr = median_flux / noise

#   return snr



def snr_measure_pp(spec, save_files, output_folder, verbose=False):
    snrout_rvdat_path = os.path.join(output_folder, "spec_SNR.csv")
    snr_out = np.nanmean(spec.flux.values/spec.flux_sig.values)
    # noise = np.nanmean(spec.flux_sig.values)

    if save_files:
        os.makedirs(output_folder, exist_ok=True)
        salida = {"filn":[os.path.basename(output_folder)], "snr":[snr_out]}
        pd.DataFrame(salida).to_csv(snrout_rvdat_path, index=False)
        if verbose:
            print(f"[Info] Results written in {snrout_rvdat_path}\n")

    return snr_out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("InFile", help="Input spectrum to be corrected")
    
    args = parser.parse_args()
    
    infile = args.InFile
    spec = pd.read_csv(infile)

    snr = snr_measure(spec)

    return snr



if __name__ == "__main__":
    main()