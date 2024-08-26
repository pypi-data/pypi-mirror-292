import os, sys
from xuse.more.interactive import get_input_zh


def get_expr_text(k: str):
    def h(s):
        return f"{s} #:{k}:#"

    exprs = []
    if k == "docker":
        url = get_input_zh("Docker Registry", required=True)
        expr = h(f"export BARWEX_BASHRC_DOCKER_REGISTRY='{url}'")
        exprs.insert(0, expr)
    elif k == "ps1":
        hostname = input("[可选]设置PS1显示的主机名(默认显示系统主机名): ").strip()
        if hostname != "":
            exprs.append(h(f"export BARWEX_BASHRC_PS1_HOST='{hostname}'"))
    exprs.append(h(f"source $BARWEX_BASHRC_DIR/{k}.sh"))
    return "\n".join(exprs)


class BashrcIO(object):
    def __init__(self, root_dir: str = None) -> None:
        self.root_dir = root_dir
        self.filepath = os.path.join(os.environ.get("HOME"), ".bashrc")
        self.start_flag = "# >>> barwex-bashrc initialize >>>"
        self.end_flag = "# <<< barwex-bashrc initialize <<<"
        self.is_first = True

    def _read(self):
        with open(self.filepath, "r") as rf:
            return rf.read()

    def _write(self, content: str):
        with open(self.filepath, "w") as wf:
            wf.write(content)

    def is_initialized(self):
        return self.start_flag in self._read()

    def initialize(self):
        text = self._read().rstrip() + "\n"
        lines = [self.start_flag]
        lines.append(f'export BARWEX_BASHRC_DIR="{self.root_dir}/data"')
        lines.append(self.end_flag)
        text += "\n" + "\n".join(lines) + "\n"
        self._write(text)

    def exit_if_not_initialized(self):
        if not self.is_initialized():
            print("barwex-bashrc has not been initialized. Please run 'barwex-bashrc init' first.")
            sys.exit(1)

    def _get_app_text(self):
        text = self._read()
        start = text.index(self.start_flag)
        end = text.index(self.end_flag) + len(self.end_flag)
        return text[start:end], text

    def add(self, k: str):
        sk = f"#:{k}:#"
        k_text = get_expr_text(k)
        app_text, full_text = self._get_app_text()
        if sk in app_text:
            self.remove(k)
            app_text, full_text = self._get_app_text()

        new_app_text = app_text.replace(self.end_flag, f"{k_text}\n{self.end_flag}")
        self._write(full_text.replace(app_text, new_app_text))

    def remove(self, k: str):
        sk = f"#:{k}:#"
        app_text, full_text = self._get_app_text()
        if sk not in app_text:
            return

        new_app_lines = [i for i in app_text.split("\n") if sk not in i]
        self._write(full_text.replace(app_text, "\n".join(new_app_lines)))

    def fulltext(self):
        return self._read()

    def uninstall(self):
        app_text, full_text = self._get_app_text()
        self._write(full_text.replace(app_text, "").rstrip() + "\n")
