
def load_gist(gist_id):
    """Translate Gist ID to URL"""
    from json import load
    from urllib.request import urlopen

    gist_api = urlopen("https://api.github.com/gists/" + gist_id)
    files = load(gist_api)["files"]
    files_head_member = list(files.keys())[0]
    raw_url = files[files_head_member]["raw_url"]

    gist_src = urlopen(raw_url).read().decode("utf-8")
    return gist_src


def import_from_gist(gist_id):
    """Import from Gist"""
    from sys import path
    from tempfile import mkdtemp
    import importlib.util
    import os

    gist_src = load_gist(gist_id)
    temp_dir = mkdtemp()
    module_name = "module_{}".format(gist_id)
    module_path = os.path.join(temp_dir, "{}.py".format(module_name))

    with open(module_path, "w") as f:
        f.write(gist_src)

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    gist_id = "55b8bec6e652c860f287288d98bc507f"
    mod = import_from_gist(gist_id)
    mod.hello()
