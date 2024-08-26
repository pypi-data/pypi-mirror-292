"""
labrador - markdown
Author :    Calixte Mayoraz
Copyright : (c) 2024
"""
import os
import re
import threading
import time
import shutil
from http.server import SimpleHTTPRequestHandler
import socketserver
import webbrowser
import pytoml as toml
from mdutils import MdUtils
from mkdocs.__main__ import cli as mkdocs_cli
import yaml
from .utils import unsanitize, get_project_root, list_work_packages, list_approaches


def init_doc(folder_path: str = None, description: str = None):
    """
    Creates the documentation Markdown document with the correct formatting ready for documenting.

    Parameters
    ----------
    folder_path: str
        the path to create it in. If no path is specified, will use the current working directory.
    description: str
        if specified, will use this as the description
    """
    if folder_path is None:
        folder_path = os.getcwd()
    if description is None:
        description = "Write a short description for your folder"
    folder = os.path.split(folder_path)[-1]
    doc_file = MdUtils(
        file_name=os.path.join(folder_path, "documentation.md"),
        author="CMA"
    )
    doc_file.new_header(level=1, title=unsanitize(folder))
    doc_file.new_line()
    doc_file.write(f"> {description}")
    doc_file.create_md_file()


def __copy_documentation_md_to_docs(folder_from, doc_dir) -> 'str | None':
    """
    Copies the `documentation.md` from a folder (project / work-package / approach) to the flat
    documentation directory with a different name and returns this value.

    Parameters
    ----------
    folder_from: str
        the project / work-package / approach to copy the documentation.md file from

    doc_dir: str
        the doc directory that mkdocs will read from

    Returns
    -------
    str:
        the output file that was the documentation was copied to (if documentation.md existed)
    None:
        if no documentation.md file was found in `folder_from`
    """
    to_copy = os.path.join(folder_from, "documentation.md")
    if not os.path.exists(to_copy):
        return None

    output_name = "index.md"
    if os.path.exists(os.path.join(folder_from, "..", ".lab")):
        output_name = "wp_" + os.path.split(folder_from)[-1] + ".md"
    elif os.path.exists(os.path.join(folder_from, "..", "..", ".lab")):
        output_name = "ap" + os.path.split(folder_from)[-1] + ".md"
    # pylint:disable=fixme
    # TODO - other cases?
    shutil.copyfile(to_copy, os.path.join(doc_dir, output_name))
    return output_name


def __get_documentation_from_folder(folder_from, increase_headings: int = 0) -> 'list[str]':
    """
    reads and returns the `documentation.md` from a folder (project / work-package / approach).
    If the folder doesn't have any documentation.md file, returns an empty string
    Parameters
    ----------
    folder_from: str
        the project / work-package / approach to read the documentation.md file from
    increase_headings: int
        how much to increase the level of headings in the parsed markdown.

    Returns
    -------
    list[str]:
        the read documentation from the given folder
    """
    to_read = os.path.join(folder_from, "documentation.md")
    if not os.path.exists(to_read):
        return []
    with open(to_read, "r", encoding="utf-8") as infile:
        md_lines = infile.readlines()
    # increase headings
    match_string = '^#{1,' + str(6-increase_headings) + '}[^#]'
    replace_string = '#' * increase_headings
    md_lines = list(
        map(
            lambda line: re.sub(rf'{match_string}', rf'{replace_string}\g<0>', line),
            md_lines
        )
    )

    return md_lines


def create_report():
    """
    Compiles all the reports from all the work-packages and their subsequent approaches in a single
    report.
    """
    os.chdir(get_project_root())
    if os.path.exists("docs"):
        shutil.rmtree("docs")
    os.mkdir("docs")
    with open(".lab", "r", encoding="utf-8") as infile:
        lab_file = toml.load(infile)

    __compile_documentation()

    __save_mkdocs_yml(lab_file['project']['name'])

    # generate with mkdocs
    # pylint:disable=too-many-function-args
    mkdocs_cli(['build'], standalone_mode=False)

    # serve and open browser
    os.chdir("site")
    __tiny_server()


def __tiny_server():
    with socketserver.TCPServer(("", 8080), SimpleHTTPRequestHandler) as httpd:
        print("Showing documentation, use Ctrl-C to exit.")

        def serve_quick():
            try:
                httpd.serve_forever()
            except OSError:
                pass

        server_thread = threading.Thread(target=serve_quick)
        server_thread.start()
        if webbrowser.open_new_tab("http://localhost:8080"):
            time.sleep(5)
        else:
            print("Couldn't open a browser, navigate to http://localhost:8080")
            time.sleep(60)
    server_thread.join()


def __save_mkdocs_yml(project_name):
    with open(os.path.join(os.getcwd(), "mkdocs.yml"), "w", encoding="utf-8") as outfile:
        yaml.dump({
            "site_name": project_name,
            "nav": ['index.md'],
            "extra_javascript": [
                "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/"
                "MathJax.js?config=TeX-AMS-MML_HTMLorMML"
            ],
            "markdown_extensions": ["mdx_math"]
        }, outfile)


def __copy_images_modify_markdown(lines, src_path, dest_path) -> list[str]:
    """
    This function will look in each line and find any local images that are displayed. It copies
    the images to the docs dir, and modifies the markdown to reference the copied image instead
    of the source ones. To ensure that no collisions occur, each image will be deduplicated with an
    incremental id prefix.

    Parameters
    ----------
    lines: list[str]
        the markdown parsed from the documentation file

    src_path: str
        the directory where the markdown was parsed from

    dest_path: str
        the folder where the documentation destination will be located.

    Returns
    -------
    list[str]
        the inputted lines with replaced image
    """
    def copy_image_replace_path(line: str) -> str:
        for img_path in re.findall(r'!\[.*?]\(((?!http://|https://)[^)]*?)\)', line):
            # prepare the new filename
            new_filename = os.path.split(img_path)[-1]
            new_filename = str(len(os.listdir(dest_path))).zfill(2) + "_" + new_filename
            line = line.replace(img_path, new_filename)
            new_filename = os.path.join(dest_path, new_filename)
            # copy the image to the docs path
            shutil.copyfile(os.path.join(src_path, img_path), new_filename)

        return line

    return list(map(copy_image_replace_path, lines))


def __compile_documentation():
    """
    Assuming we are in the project root, this function will compile all the documentation from
    subsequent work packages and approaches. It saves this compiled documentation in a single
    "index.md" file in the documentation directory ("docs")
    """
    docs_dir = os.path.join(os.getcwd(), "docs")
    with open(os.path.join(docs_dir, "index.md"), "w", encoding="utf-8") as outfile:
        # write the index to documentation
        outfile.writelines(
            __copy_images_modify_markdown(
                __get_documentation_from_folder(os.getcwd()),
                os.getcwd(),
                docs_dir
            )
        )
        # for each work package
        for work_package in list_work_packages():
            outfile.writelines(
                __copy_images_modify_markdown(
                    __get_documentation_from_folder(work_package),
                    work_package,
                    docs_dir
                )
            )
            for approach in list_approaches(work_package):
                outfile.writelines(
                    __copy_images_modify_markdown(
                        __get_documentation_from_folder(approach, increase_headings=1),
                        approach,
                        docs_dir
                    )
                )
