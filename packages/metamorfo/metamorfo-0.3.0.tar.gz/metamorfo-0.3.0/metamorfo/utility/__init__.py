import hashlib


def hexa_sha256(data):
    response = hashlib.sha256(data.encode()).digest()
    return response.hex()


def list_in_query(lista, name_param_lista, query, parametros):
    listaitems = [f":{name_param_lista}_{i}" for i, _ in enumerate(lista)]
    query = query.replace(f":{name_param_lista}", ",".join(listaitems))
    for i, x in enumerate(listaitems):
        parametros[x.replace(":", "")] = lista[i]

    return query, parametros
