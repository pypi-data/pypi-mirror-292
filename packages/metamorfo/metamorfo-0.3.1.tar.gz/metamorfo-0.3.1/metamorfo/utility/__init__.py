import hashlib


def hexa_sha256(data):
    response = hashlib.sha256(data.encode()).digest()
    return response.hex()


def list_in_query(lista, nome_parametro, query, parametros):
    listaitems = [f":{nome_parametro}_{i}" for i, _ in enumerate(lista)]
    query = query.replace(f":{nome_parametro}", ",".join(listaitems))
    for i, x in enumerate(listaitems):
        parametros[x.replace(":", "")] = lista[i]

    return query, parametros
