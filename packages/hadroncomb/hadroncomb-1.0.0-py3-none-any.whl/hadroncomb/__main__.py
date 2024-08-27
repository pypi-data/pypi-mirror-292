###############################################################################
# (c) Copyright 2024 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import argparse
import itertools as it
import os
import ROOT as R
import uproot as up

import matplotlib.pyplot as plt
import mplhep as hep

hep.style.use("LHCb2")

parser = argparse.ArgumentParser()
parser.add_argument(
    "input", type=str, help="Input sample, should be of format <path>:<tree>"
)
parser.add_argument(
    "hadrons",
    type=str,
    help="Should be of format <h1>:<p1>,<h2>:<p2>,... where <h1>,<h2>,... are the names of hadrons in the input sample and <p1>,<p2>,... are their identities in the sample",
)
parser.add_argument("output", type=str, help="Path to write out results to")

parser.add_argument(
    "--cut", type=str, required=False, help="Cut to be applied to sample as a prefilter"
)
parser.add_argument(
    "--misid",
    type=str,
    required=False,
    help="Enables calculations with single, double,... mis-ID of hadrons, should be of format <p1>,<p2>,... where <p1>,<p2>,... are possible particle hypotheses, e.g., k,pi",
)
parser.add_argument(
    "--nbins",
    type=int,
    default=100,
    help="Sets number of bins to use in each histogram",
)
parser.add_argument("--threads", type=int, default=1, help="Number of threads to use")

parser.add_argument(
    "--plot-errors", action="store_true", help="Plot histograms with errors."
)
parser.add_argument(
    "--plot-label",
    type=str,
    default="Preliminary",
    help="Label to include on plots beside LHCb",
)
parser.add_argument(
    "--plot-path",
    type=str,
    required=False,
    help="Path to save plots to. If not set, no plots are saved.",
)
args = parser.parse_args()

if args.threads > 1:
    R.EnableImplicitMT(args.threads)

path, tree = args.input.rsplit(":", 1)
rdf = R.RDataFrame(tree, path)

if args.cut:
    rdf = rdf.Filter(args.cut)

branches = list(rdf.GetColumnNames())
hadrons = dict(h.split(":", 1) for h in args.hadrons.split(","))
misids = (
    [
        "",
    ]
    + args.misid.split(",")
    if args.misid
    else None
)
momenta = ("PE", "PX", "PY", "PZ")
hists = {}

combinations = [
    c for n in range(2, len(hadrons) + 1) for c in it.combinations(hadrons.keys(), n)
]

if misids:
    masses = {  # All sourced from S. Navas et al. (Particle Data Group), to be published in Phys. Rev. D 110, 030001 (2024)
        "mu": "105.658",
        "pi": "139.570",
        "k": "493.677",
        "p": "938.272",
    }
    assert all(m in masses.keys() or not (m) for m in misids)
    combinations = [
        tuple(
            f"{part}{'as' if misid_prefix else ''}{misid_prefix}"
            for part, misid_prefix in zip(combination, misid_prefixes)
        )
        for combination in combinations
        for misid_prefixes in it.product(misids, repeat=len(combination))
    ]


def check_hadrons(hadron):
    # Checks if misID is applying any change
    if "as" in hadron:
        base_hadron, misid_particle = hadron.rsplit("as", 1)
        return hadrons[base_hadron] != misid_particle
    return True  # No need to check if not applying misID to the hadron!


for combination in combinations:
    label = "_".join(combination)
    if not misids or all(check_hadrons(h) for h in combination):
        for p in momenta:
            if "as" in label:
                for hadron in combination:
                    if "as" in hadron and f"{hadron}_{p}" not in branches:
                        base_hadron, misid_particle = hadron.rsplit("as", 1)
                        if p == "PE":
                            rdf = rdf.Define(
                                f"{hadron}_{p}",
                                f"sqrt(pow({masses[misid_particle]}, 2) + {' + '.join(f'pow({base_hadron}_{hp}, 2)' for hp in momenta[1:])})",
                            )
                        else:
                            rdf = rdf.Define(f"{hadron}_{p}", f"{base_hadron}_{p}")
                        branches += [f"{hadron}_{p}"]

            rdf = rdf.Define(
                f"{label}_{p}", " + ".join([f"{hadron}_{p}" for hadron in combination])
            )
            branches += [f"{label}_{p}"]

        rdf = rdf.Define(
            f"{label}_M", f"sqrt({' - '.join(f'pow({label}_{p}, 2)' for p in momenta)})"
        )
        branches += [f"{label}_M"]

        hists[f"{label}_M"] = rdf.Histo1D(
            (f"{label}_M", f"{label}_M", args.nbins, 0.0, 0.0), f"{label}_M"
        )

R.RDF.RunGraphs(hists.values())

if misids:
    organised_hists = {f"{n}misID": {} for n in range(len(hadrons) + 1)}
    for name, hist in hists.items():
        n_misid = name.count("as")
        organised_hists[f"{n_misid}misID"][name] = hist

with R.TFile.Open(args.output, "RECREATE") as f:
    if misids:
        for dir_name, hists in organised_hists.items():
            hist_dir = f.mkdir(dir_name)
            hist_dir.cd()
            for name, hist in hists.items():
                hist_dir.WriteObject(hist.GetValue(), name)
    else:
        for name, hist in hists.items():
            f.WriteObject(hist.GetValue(), name)

if args.plot_path:  # Plot each histogram in a pdf

    def plot(path, hist):
        fig = plt.figure(figsize=(12, 10))

        py_hist = up.from_pyroot(hist.GetValue())
        values, edges = py_hist.to_numpy()

        midpoints = (edges[1:] + edges[:-1]) / 2
        widths = edges[1:] - edges[:-1]
        if args.plot_errors:
            errors = py_hist.errors

            plt.errorbar(midpoints, values, xerr=widths, yerr=errors / 2)
        else:
            plt.bar(midpoints, values, width=widths)

        rlabel = path.rsplit("/", 1)[1].rsplit(".", 1)[0]
        rlabel = (
            rlabel.replace("_M", "")
            .replace("_", ", ")
            .replace("asmu", " as $\\mu$")
            .replace("aspi", " as $\\pi$")
            .replace("ask", " as $K$")
            .replace("asp", " as $p$")
        )

        hep.lhcb.label(label=args.plot_label, data=True, rlabel=rlabel, loc=0)

        plt.xlabel(r"Invariant mass, $m$ / MeV$c^{-2}$")
        plt.ylabel(f"Candidates / {widths[0]:.1f} MeV$c^{-2}$")

        fig.savefig(path)
        plt.close()

        return

    if misids:
        for dir_name, hists in organised_hists.items():
            path = os.path.join(args.plot_path, dir_name)
            for name, hist in hists.items():
                os.makedirs(path, exist_ok=True)
                plot(os.path.join(path, f"{name}.pdf"), hist)
    else:
        for name, hist in hists.items():
            os.makedirs(args.plot_path, exist_ok=True)
            plot(os.path.join(args.plot_path, f"{name}.pdf"), hist)
