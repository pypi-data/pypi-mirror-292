import re
from argparse import ArgumentParser
from barwex_vscodews import barwexutils as xt

code_path = xt.SUBPROCESS.check_output("which code")
app_data_dir = xt.get_barwex_app_data_dir("vscodews")


def make_desktop_entry(name: str, path: str):
    """建立桌面快捷方式"""
    lines = ["[Desktop Entry]", "Type=Application"]
    lines.append(f"Name=${name}")
    lines.append(f"Comment=VSCode Workspace Named {name}")
    lines.append(f"Exec={code_path} {path}")
    lines.append(f"Icon=com.visualstudio.code")
    lines.append("Terminal=false")
    destop = xt.join(xt.USER_DESKTOP_DIR, f"vscodews.{name}.desktop")
    if xt.exists(destop):
        xt.os.remove(destop)
    xt.IO.write_text("\n".join(lines), destop)


def conf_local(path: str):
    """为本地项目生成配置"""
    return {
        "folders": [{"path": path}],
        "settings": {},
    }


def conf_remote(host: str, path: str):
    return {
        "folders": [{"uri": f"vscode-remote://ssh-remote+{host}{path}"}],
        "remoteAuthority": f"ssh-remote+{host}",
        "settings": {},
    }


def main():
    parser = ArgumentParser()
    parser.add_argument("-d", "--project-dir", required=True, help="支持本地路径（如/a/b）和远程路径（如it:/a/b）")
    parser.add_argument("-n", "--workspace-name", dest="workspace_name", help="workspace name")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if mt := re.match(r"([\w-]+):(.*)", args.project_dir):
        host = mt.group(1)
        project_dir = mt.group(2)
        data = conf_remote(host, project_dir)
    else:
        project_dir: str = xt.abspath(args.project_dir)
        data = conf_local(project_dir)

    ws_name: str = args.workspace_name or xt.basename(project_dir)
    ws_fn = xt.join(app_data_dir, f"{ws_name}.code-workspace")
    if xt.exists(ws_fn):
        if args.force:
            xt.os.remove(ws_fn)
        else:
            raise FileExistsError(ws_fn)
    xt.IO.write_json(data, ws_fn)
    make_desktop_entry(ws_name, ws_fn)
