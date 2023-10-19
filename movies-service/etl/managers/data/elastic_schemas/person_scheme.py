from .scheme_template import scheme_template

person_scheme = {
    **scheme_template,
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "keyword"},
            "full_name": {
                "type": "text",
                "analyzer": "ru_en",
                "fields": {"raw": {"type": "keyword"}},
                "fielddata": "true"
            },
            "films": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "roles": {
                        "type": "text",
                        "analyzer": "ru_en"
                    },
                    "film": {
                        "type": "keyword"
                    },
                }
            }
        },
    },
}
