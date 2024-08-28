"""
URL Form
--------
https://rest.kegg.jp/<operation>/<argument>[/<argument2[/<argument3> ...]]
<operation> = info | list | find | get | conv | link | ddi


Database name
-------------
<database> = KEGG databases (Table 1) and Outside databases integrated in KEGG (Table 2)

           = pathway | brite | module | ko | <org> | vg | vp | ag | genome | compound |
             glycan | reaction | rclass | enzyme | network | variant | disease |
             drug | dgroup | disease_ja | drug_ja | dgroup_ja | compound_ja |
             genes | ligand | kegg | <outside_db>

<org> = KEGG organism code

<outside_db> = pubmed | ncbi-geneid | ncbi-proteinid | uniprot | pubchem | chebi |
               atc | jtc | ndc | yj


Database entry identifier
-------------------------
<dbentry> = <kid> | <org>:<gene> | <database>:<entry>

<kid> = KEGG identifier
<gene> = Gene entry name or accession
<entry> = Database entry name or accession

<dbentries> = <dbentry>1[+<dbentry>2...]

Naming conventions
------------------
Table 1. KEGG databases

DB name	Abbrev	Content	Web page	kid prefix
pathway	path	KEGG pathway maps	KEGG PATHWAY	map, ko, ec, rn, <org>
brite	br	BRITE functional hierarchies	KEGG BRITE	br, jp, ko, <org>
module	md	KEGG modules	KEGG MODULE	M, <org>_M
orthology	ko	KO functional orthologs	KEGG ORTHOLOGY	K
genes	<org>
vg
vp
ag	Genes in KEGG organisms
Genes in viruses category
Mature peptides in viruses
Genes in addendum category	KEGG GENES	-
genome	gn	KEGG organisms	KEGG GENOME	T
compound	cpd	Small molecules	KEGG COMPOUND	C
glycan	gl	Glycans	KEGG GLYCAN	G
reaction	rn	Biochemical reactions	KEGG REACTION	R
rclass	rc	Reaction class		RC
enzyme	ec	Enzyme nomenclature	KEGG ENZYME	-
network	ne	Network elements	KEGG NETWORK	N
variant	hsa_var	Human gene variants		-
disease	ds	Human diseases	KEGG DISEASE	H
drug	dr	Drugs	KEGG DRUG	D
dgroup	dg	Drug groups		DG
disease_ja	ds_ja	H number	KEGG DISEASE (in Japanese)
drug_ja	dr_ja	D number	KEGG DRUG (in Japanese)
dgroup_ja	dg_ja	DG number
compound_ja	cpd_ja	C number

"genes" is a composite database consisting of KEGG organisms with three- or four-letter <org> codes, and viruses (vg, vp) and addendum (ag) categories (see KEGG GENES).
"pathway", "brite" and "module" consist of manually created reference datasets and computationally generated organism-specific datasets (see KEGG Pathway Maps).
"kegg" stands for the collection of all databases shown above.
"ligand" stands for the collection of chemical databases: compound, glycan, reaction and enzyme.


Table 2. Outside databases integrated in KEGG

DB name	Abbrev	Entry ID	Web page	Remark
pubmed	pmid	PubMed ID	NCBI PubMed
ncbi-geneid		Gene ID	NCBI Gene	conv only
ncbi-proteinid		Protein ID	NCBI Protein	conv only
uniprot	up	UniProt Accession	UniProt	conv only
pubchem		PubChem SID	NCBI PubChem	conv only
chebi		ChEBI ID	ChEBI	conv only
atc	7-letter ATC code	ATC classification	link only
jtc	Therapeutic category code	Therapeutic category in Japan	link only
ndc	National Drug Code	Drug products in the USA	ddi only
yj	YJ code	Drug products in Japan	ddi only
"""

from fast_bioservices.base import BaseModel
from fast_bioservices.fast_http import FastHTTP
from fast_bioservices.settings import default_workers


class KEGG(BaseModel, FastHTTP):
    def __init__(
        self,
        max_workers: int = default_workers,
        show_progress: bool = False,
        cache: bool = True,
    ) -> None:
        self._url = "https://rest.kegg.jp"
        BaseModel.__init__(self, url=self._url)
        FastHTTP.__init__(
            self,
            cache=cache,
            workers=max_workers,
            max_requests_per_second=3,
            show_progress=show_progress,
        )

    def info(self, database: str):
        path = f"/info/{database}"
        response = self._get(self._url + path)
        return response[0].text

    def organisms(self) -> dict[str, list[str]]:
        # T01001  hsa     Homo sapiens (human)    Eukaryotes;Animals;Vertebrates;Mammals
        # T01005  ptr     Pan troglodytes (chimpanzee)    Eukaryotes;Animals;Vertebrates;Mammals

        response = self._get(f"{self._url}/list/organism")
        parsed = {"kegg_id": [], "kegg_shorthand": [], "name": [], "classification": []}
        for line in response[0].text.split("\n"):
            if line == "":
                print("GOT BLANK")
                continue
            split = line.split("\t")
            parsed["kegg_id"].append(split[0])
            parsed["kegg_shorthand"].append(split[1])
            parsed["name"].append(split[2])
            parsed["classification"].append(split[3])

        return parsed

    def list(self, database: str):
        path = f"/list/{database}"
        response = self._get(self._url + path)
        print("\n".join(response[0].text.split("\n")[0:5]))


def main():
    k = KEGG(max_workers=1, show_progress=True, cache=True)
    k.organisms()


if __name__ == "__main__":
    main()
