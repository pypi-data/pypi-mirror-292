from ..convert_utils import convert as convert_

# todo: create converter for original data and migrate this converter to use the add_eurocrops function

SOURCES = {
  "https://zenodo.org/records/10118572/files/SI_2021.zip?download=1": ["SI_2021_EC21.shp"]
}

ID = "ec_si"
SHORT_NAME = "Slovenia - Eurocrops, 2021"
TITLE = "Field boundaries for Slovenia from EuroCrops (2021)"
DESCRIPTION = """
This dataset contains the field boundaries for all of Slovenia in 2021. The data was collected by the Slovenian government and harmonized
by the EuroCrops project and is available on Zenodo.

EuroCrops is a dataset collection combining all publicly available self-declared crop reporting datasets from countries of the European Union.
The project is funded by the German Space Agency at DLR on behalf of the Federal Ministry for Economic Affairs and Climate Action (BMWK).
The work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][https://creativecommons.org/licenses/by-sa/4.0/].

The project developed a new **Hierarchical Crop and Agriculture Taxonomy (HCAT)** that harmonises all declared crops across the European Union.
In the data you'll find this as additional attributes:

- `ec:translated_name`: The original crop name translated into English
- `ec:hcat_name`: The machine-readable HCAT name of the crop
- `ec:hcat_code`: The 10-digit HCAT code indicating the hierarchy of the crop
- `EC_nuts3`: The Nomenclature of Territorial Units for Statistics 3 (NUTS3) region, an approximate assignment of a crop parcel to a region

Disclaimer: The Nomenclature of Territorial Units for Statistics 3 (NUTS3) region, which we added by hand, is just an approximate assignment of a
crop parcel to a region. It might happen that a parcel is not correctly allocated to the right region or country. The NUTS3 attribute is only meant
to be an aid for a meaningful spatial division of the dataset into training, validation, and test sets.
"""

PROVIDERS = [
    {
        "name": "EuroCrops",
        "url": "https://github.com/maja601/EuroCrops/wiki/Slovenia",
        "roles": ["producer", "licensor"]
    }
]
ATTRIBUTION = "Ministrstvo za kmetijstvo, gozdarstvo in prehrano"

LICENSE = "CC-BY-4.0"

EXTENSIONS = [
    "https://fiboa.github.io/hcat-extension/v0.1.0/schema.yaml"
]

COLUMNS = {
    'geometry': 'geometry', #fiboa core field
    'ID': 'id', #fiboa core field
    'AREA': 'area', #fiboa core field
    'GERK_PID': 'gerk_pid', #fiboa custom field
    'SIFRA_KMRS': 'crop_type_class', #fiboa custom field
    'RASTLINA': 'rastlina', #fiboa custom field
    'CROP_LAT_E': 'crop_lat_e', #fiboa custom field
    'COLOR': 'color', #fiboa custom field
    'EC_trans_n': 'ec:translated_name', #fiboa hcat extension
    'EC_hcat_n': 'ec:hcat_name', #fiboa hcat extension
    'EC_hcat_c': 'ec:hcat_code', #fiboa hcat extension
    'EC_NUTS3': 'EC_NUTS3', #fiboa custom field
}

COLUMN_MIGRATIONS = {
    'AREA': lambda column: column * 0.0001
}

ADD_COLUMNS = {}

MISSING_SCHEMAS = {
    'required': ['gerk_pid', 'crop_type_class', 'rastlina', 'crop_lat_e', 'color'],
    'properties': {
        'gerk_pid': {
            'type': 'uint64'
        },
        'crop_type_class': {
            'type': 'string'
        },
        'rastlina': {
            'type': 'string'
        },
        'crop_lat_e': {
            'type': 'string'
        },
        'color': {
            'type': 'string'
        },
        'EC_NUTS3': {
            'type': 'string'
        }
    }
}


def convert(output_file, cache = None, **kwargs):
    convert_(
        output_file,
        cache,
        SOURCES,
        COLUMNS,
        ID,
        TITLE,
        DESCRIPTION,
        extensions=EXTENSIONS,
        providers=PROVIDERS,
        missing_schemas=MISSING_SCHEMAS,
        column_migrations=COLUMN_MIGRATIONS,
        column_additions=ADD_COLUMNS,
        attribution=ATTRIBUTION,
        license=LICENSE,
        **kwargs
    )
