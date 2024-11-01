def update_dict(d, u):
    for k, v in u.items():
        d[k] = update_dict(d.get(k, {}), v) if isinstance(v, dict) else v
    return d
