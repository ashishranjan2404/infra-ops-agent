"""Tests for package_arxiv.py — synthetic complete + incomplete LaTeX trees."""
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import package_arxiv as pkg  # noqa: E402


MAIN_OK = r"""
\documentclass{article}
\author{Jane Real (Some Lab)}
\begin{document}
\input{sections/intro}
\bibliographystyle{plain}
\bibliography{refs}
\end{document}
"""


def _write(p: Path, text: str = "x"):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _complete_tree(root: Path):
    _write(root / "main.tex", MAIN_OK)
    _write(root / "sections" / "intro.tex", "Hello world section.\n")
    _write(root / "refs.bbl", r"\begin{thebibliography}{1}\end{thebibliography}")
    _write(root / "main.aux", "junk")  # should be excluded
    return root


def test_complete_tree_is_ready(tmp_path):
    src = _complete_tree(tmp_path / "src")
    rc = pkg.main(["--src", str(src), "--out", str(tmp_path / "out")])
    assert rc == 0
    assert (tmp_path / "out" / "arxiv_submission.tar.gz").exists()


def test_empty_input_blocks(tmp_path):
    src = _complete_tree(tmp_path / "src")
    (src / "sections" / "intro.tex").write_text("", encoding="utf-8")  # empty
    rc = pkg.main(["--src", str(src), "--out", str(tmp_path / "out")])
    assert rc == 1
    assert (tmp_path / "out" / "arxiv_submission.tar.gz").exists()  # still written
    man = (tmp_path / "out" / "MANIFEST.txt").read_text()
    assert "EMPTY_INPUT" in man


def test_missing_bbl_blocks(tmp_path):
    src = _complete_tree(tmp_path / "src")
    (src / "refs.bbl").unlink()
    rc = pkg.main(["--src", str(src), "--out", str(tmp_path / "out")])
    assert rc == 1
    assert "NO_BBL" in (tmp_path / "out" / "MANIFEST.txt").read_text()


def test_no_main_is_fatal(tmp_path):
    src = tmp_path / "src"
    _write(src / "notes.tex", "no documentclass here")
    rc = pkg.main(["--src", str(src), "--out", str(tmp_path / "out")])
    assert rc == 2
    assert not (tmp_path / "out" / "arxiv_submission.tar.gz").exists()


def test_tarball_deterministic(tmp_path):
    src = _complete_tree(tmp_path / "src")
    pkg.main(["--src", str(src), "--out", str(tmp_path / "o1")])
    pkg.main(["--src", str(src), "--out", str(tmp_path / "o2")])
    a = (tmp_path / "o1" / "arxiv_submission.tar.gz").read_bytes()
    b = (tmp_path / "o2" / "arxiv_submission.tar.gz").read_bytes()
    assert a == b


def test_junk_excluded(tmp_path):
    src = _complete_tree(tmp_path / "src")
    pkg.main(["--src", str(src), "--out", str(tmp_path / "out")])
    with tarfile.open(tmp_path / "out" / "arxiv_submission.tar.gz") as tf:
        names = tf.getnames()
    assert not any(n.endswith(".aux") for n in names)
    assert "main.tex" in names
    assert "sections/intro.tex" in names
