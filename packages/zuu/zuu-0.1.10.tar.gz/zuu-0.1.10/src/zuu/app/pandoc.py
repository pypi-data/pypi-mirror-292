import os
from zuu.core.markdown import create_yaml_properties


PANDOC_CMD = (
    'pandoc {input_md} -o {outname} -f markdown -t {outtype} --template="{template}"'
)


def gen_file(
    workdir: str, outtype: str, template: str, data: dict, outname: str = "pandoc.out"
):
    os.makedirs(workdir, exist_ok=True)

    create_yaml_properties(os.path.join(workdir, "input.md"), data)

    os.system(
        PANDOC_CMD.format(
            input_md=os.path.join(workdir, "input.md"),
            outname=os.path.join(workdir, outname),
            outtype=outtype,
            template=template,
        )
    )
