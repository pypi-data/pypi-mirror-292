import os


pkg_path = os.path.dirname(__file__)
pkgs = [
    f"zuu.tool.{os.path.splitext(pkg)[0]}"
    for pkg in os.listdir(pkg_path)
    if not os.path.isdir(os.path.join(pkg_path, pkg))
    and not pkg.startswith("__")
    and pkg.endswith(".py")
]

pass
