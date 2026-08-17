import nox

ANSIBLE_VERSIONS = [
    "2.19",
    "2.20",
    "2.21",
]

nox.options.reuse_existing_virtualenvs = True
nox.options.default_venv_backend = "uv"


@nox.session(python="3.12")
@nox.parametrize(
    "ansible",
    ANSIBLE_VERSIONS,
    ids=[f"ansible{v}" for v in ANSIBLE_VERSIONS],
)
def molecule(session: nox.Session, ansible: str) -> None:
    session.install(
        f"ansible-core~={ansible}.0",
        "molecule>=26",
        "pytest-testinfra",
    )
    session.run("molecule", "test", "-s", "default", *session.posargs)
