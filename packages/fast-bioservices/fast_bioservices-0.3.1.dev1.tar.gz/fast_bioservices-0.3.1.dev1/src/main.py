from fast_bioservices import ensembl
from fast_bioservices.ensembl import CrossReference, GetHomology
from fast_bioservices.ensembl.cross_references import EnsemblReference


def main():
    refseq_id = "NP_000005"

    homology = GetHomology()
    r = homology.by_species_with_symbol_or_id(
        reference_species="human",
        ensembl_id_or_symbol=refseq_id,
        target_species="macaca_mulatta",
    )
    print(r)


if __name__ == "__main__":
    main()
