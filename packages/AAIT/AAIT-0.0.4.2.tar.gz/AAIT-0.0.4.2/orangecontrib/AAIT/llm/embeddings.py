import copy
from Orange.data import Domain, ContinuousVariable, Table


def create_embeddings(table, model, progress_callback=None, argself=None):
    # Copy of input data
    data = copy.deepcopy(table)
    attr_dom = list(data.domain.attributes)
    metas_dom = list(data.domain.metas)
    class_dom = list(data.domain.class_vars)

    # Generate embeddings on column named "content"
    embeddings = None
    rows = []
    for i, row in enumerate(data):
        features = list(data[i])
        metas = list(data.metas[i])
        embeddings = model.encode(str(row["content"]), show_progress_bar=False)
        features += list(embeddings)
        rows.append(features + metas)
        if progress_callback is not None:
            progress_value = float(100 * (i + 1) / len(data))
            progress_callback(progress_value)
        if argself is not None:
            if argself.stop:
                break

    # Generate new Domain to add to data
    n_columns = len(embeddings)
    embeddings_doms = [ContinuousVariable(f"embedding_{i}") for i in range(n_columns)]

    # Create and return table
    domain = Domain(attributes=attr_dom + embeddings_doms, metas=metas_dom, class_vars=class_dom)
    out_data = Table.from_list(domain=domain, rows=rows)
    return out_data
