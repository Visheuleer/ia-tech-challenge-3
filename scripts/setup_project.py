from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import os
import tempfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = ROOT_DIR / "frontend"
DATA_DIR = ROOT_DIR / "data"

DATABASE_PATH = DATA_DIR / "medical_assistant.db"
VECTOR_STORE_PATH = DATA_DIR / "vector_store"

MEDQUAD_DIR = DATA_DIR / "raw" / "datasets" / "medquad"
MEDQUAD_REPOSITORY = "https://github.com/abachaa/MedQuAD.git"

MEDQUAD_DATASETS = [
    "4_MPlus_Health_Topics_QA",
    "5_NIDDK_QA",
    "8_NHLBI_QA_XML",
    "11_MPlusDrugs_QA",
]

PROCESSED_DATASETS = [
    DATA_DIR / "processed" / "train.jsonl",
    DATA_DIR / "processed" / "validation.jsonl",
    DATA_DIR / "processed" / "test.jsonl",
]

ENV_PATH = ROOT_DIR / ".env"
ENV_EXAMPLE_PATH = ROOT_DIR / ".env.example"


def print_header(message: str) -> None:
    print()
    print("=" * 72)
    print(message)
    print("=" * 72)


def get_npm_command() -> str:
    if os.name == "nt":
        return "npm.cmd"

    return "npm"

def run_command(
    command: list[str],
    cwd: Path = ROOT_DIR,
) -> None:
    print()
    print("> " + " ".join(command))

    subprocess.run(
        command,
        cwd=cwd,
        check=True,
    )


def check_command(command: str) -> None:
    if shutil.which(command) is None:
        raise RuntimeError(
            f"Required command not found: {command}"
        )


def check_requirements(
    runtime_only: bool,
) -> None:
    print_header(
        "CHECKING SYSTEM REQUIREMENTS"
    )

    commands = [
        "uv",
        "node",
        "npm",
    ]

    if not runtime_only:
        commands.append("git")

    for command in commands:
        check_command(command)
        print(f"✓ {command} found")


def create_env_file() -> None:
    print_header(
        "CONFIGURING ENVIRONMENT"
    )

    if ENV_PATH.exists():
        print("✓ .env already exists")
        return

    if ENV_EXAMPLE_PATH.exists():
        shutil.copy(
            ENV_EXAMPLE_PATH,
            ENV_PATH,
        )

        print(
            "✓ .env created from .env.example"
        )
        return

    print(
        "⚠ .env.example not found. "
        "Skipping .env creation."
    )


def install_backend_dependencies(
    runtime_only: bool,
) -> None:
    print_header(
        "INSTALLING PYTHON DEPENDENCIES"
    )

    if runtime_only:
        run_command(
            [
                "uv",
                "sync",
            ]
        )

        print(
            "✓ Runtime dependencies installed"
        )
        return

    # Installs project dependencies plus every dependency group,
    # including dev and training.
    run_command(
        [
            "uv",
            "sync",
            "--all-groups",
        ]
    )

    print(
        "✓ Runtime, development and training dependencies installed"
    )


def install_frontend_dependencies() -> None:
    print_header(
        "INSTALLING FRONTEND DEPENDENCIES"
    )

    if not FRONTEND_DIR.exists():
        raise RuntimeError(
            "frontend directory not found."
        )

    package_json = (
        FRONTEND_DIR
        / "package.json"
    )

    if not package_json.exists():
        raise RuntimeError(
            "frontend/package.json not found."
        )

    # Prefer npm ci when a lock file exists because it is deterministic.
    if (
        FRONTEND_DIR
        / "package-lock.json"
    ).exists():
        command = [
            "npm",
            "ci",
        ]
    else:
        command = [
            "npm",
            "install",
        ]

    run_command(
        [
            get_npm_command(),
            "install",
        ],
        cwd=FRONTEND_DIR,
    )

    print(
        "✓ Frontend dependencies installed"
    )


def download_medquad(
    refresh: bool,
) -> None:
    print_header(
        "PREPARING MEDQUAD DATASET"
    )

    MEDQUAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    missing = [
        dataset
        for dataset in MEDQUAD_DATASETS
        if not (
            MEDQUAD_DIR
            / dataset
        ).exists()
    ]

    if not missing and not refresh:
        print(
            "✓ Required MedQuAD subsets already exist"
        )
        return

    if refresh:
        for dataset in MEDQUAD_DATASETS:
            target = (
                MEDQUAD_DIR
                / dataset
            )

            if target.exists():
                shutil.rmtree(
                    target
                )

        print(
            "✓ Existing MedQuAD subsets removed"
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        clone_path = (
            Path(temp_dir)
            / "MedQuAD"
        )

        run_command(
            [
                "git",
                "clone",
                "--depth",
                "1",
                MEDQUAD_REPOSITORY,
                str(clone_path),
            ]
        )

        for dataset in MEDQUAD_DATASETS:
            source = (
                clone_path
                / dataset
            )

            target = (
                MEDQUAD_DIR
                / dataset
            )

            if not source.exists():
                raise RuntimeError(
                    "Expected MedQuAD directory "
                    f"not found: {dataset}"
                )

            if target.exists():
                shutil.rmtree(
                    target
                )

            shutil.copytree(
                source,
                target,
            )

            print(
                f"✓ Copied {dataset}"
            )

    print(
        "✓ MedQuAD subsets prepared"
    )


def prepare_training_data() -> None:
    print_header(
        "PREPARING TRAINING DATA"
    )

    run_command(
        [
            "uv",
            "run",
            "python",
            "-m",
            "training.parse_medquad",
        ]
    )

    run_command(
        [
            "uv",
            "run",
            "python",
            "-m",
            "training.prepare_dataset",
        ]
    )

    print(
        "✓ MedQuAD parsed and processed datasets generated"
    )


def initialize_database(
    reset: bool,
) -> None:
    print_header(
        "INITIALIZING DATABASE"
    )

    database_existed = (
        DATABASE_PATH.exists()
    )

    if (
        reset
        and database_existed
    ):
        DATABASE_PATH.unlink()

        database_existed = False

        print(
            "✓ Existing database removed"
        )

    run_command(
        [
            "uv",
            "run",
            "python",
            "scripts/init_database.py",
        ]
    )

    print(
        "✓ Database tables initialized"
    )

    if not database_existed:
        run_command(
            [
                "uv",
                "run",
                "python",
                "scripts/seed_database.py",
            ]
        )

        print(
            "✓ Synthetic patients inserted"
        )
    else:
        print(
            "✓ Existing database preserved"
        )


def build_vector_store(
    rebuild: bool,
) -> None:
    print_header(
        "PREPARING VECTOR STORE"
    )

    if (
        VECTOR_STORE_PATH.exists()
        and not rebuild
    ):
        print(
            "✓ Vector store already exists"
        )
        return

    if (
        VECTOR_STORE_PATH.exists()
        and rebuild
    ):
        shutil.rmtree(
            VECTOR_STORE_PATH
        )

        print(
            "✓ Existing vector store removed"
        )

    run_command(
        [
            "uv",
            "run",
            "python",
            "scripts/build_vector_store.py",
        ]
    )

    print(
        "✓ FAISS vector store generated"
    )


def verify_setup(
    runtime_only: bool,
) -> None:
    print_header(
        "VERIFYING SETUP"
    )

    checks = [
        (
            DATABASE_PATH.exists(),
            "SQLite database available",
        ),
        (
            VECTOR_STORE_PATH.exists(),
            "FAISS vector store available",
        ),
        (
            (
                FRONTEND_DIR
                / "node_modules"
            ).exists(),
            "Frontend dependencies available",
        ),
    ]

    if not runtime_only:
        checks.extend(
            [
                (
                    all(
                        (
                            MEDQUAD_DIR
                            / dataset
                        ).exists()
                        for dataset
                        in MEDQUAD_DATASETS
                    ),
                    "Required MedQuAD subsets available",
                ),
                (
                    all(
                        path.exists()
                        for path
                        in PROCESSED_DATASETS
                    ),
                    "Processed train/validation/test datasets available",
                ),
            ]
        )

    failed = False

    for success, message in checks:
        marker = (
            "✓"
            if success
            else "✗"
        )

        print(
            f"{marker} {message}"
        )

        if not success:
            failed = True

    if failed:
        raise RuntimeError(
            "One or more setup checks failed."
        )


def print_next_steps(
    runtime_only: bool,
) -> None:
    print_header(
        "SETUP COMPLETED"
    )

    if runtime_only:
        print(
            "Mode: runtime only"
        )
    else:
        print(
            "Mode: full project setup"
        )

    print()
    print("Backend:")
    print(
        "  uv run uvicorn "
        "medical_assistant.main:app "
        "--reload"
    )

    print()
    print("Frontend:")
    print("  cd frontend")
    print("  npm run dev")

    print()
    print("Application:")
    print(
        "  http://localhost:3000"
    )

    print()
    print("FastAPI docs:")
    print(
        "  http://127.0.0.1:8000/docs"
    )

    if not runtime_only:
        print()
        print(
            "Training data is ready. "
            "Fine-tuning is NOT started automatically."
        )
        print()
        print(
            "To run fine-tuning manually:"
        )
        print(
            "  uv run python -m training.train"
        )
        print()
        print(
            "To run model evaluation:"
        )
        print(
            "  uv run python -m training.evaluate"
        )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare the Medical Assistant "
            "development environment."
        )
    )

    parser.add_argument(
        "--runtime-only",
        action="store_true",
        help=(
            "Install only runtime dependencies "
            "and skip MedQuAD/training data preparation."
        ),
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help=(
            "Recreate the SQLite database "
            "and synthetic data."
        ),
    )

    parser.add_argument(
        "--rebuild-vector-store",
        action="store_true",
        help=(
            "Force regeneration of the "
            "FAISS vector store."
        ),
    )

    parser.add_argument(
        "--refresh-medquad",
        action="store_true",
        help=(
            "Download the selected MedQuAD "
            "subsets again."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    try:
        check_requirements(
            runtime_only=args.runtime_only,
        )

        create_env_file()

        install_backend_dependencies(
            runtime_only=args.runtime_only,
        )

        install_frontend_dependencies()

        if not args.runtime_only:
            download_medquad(
                refresh=args.refresh_medquad,
            )

            prepare_training_data()

        initialize_database(
            reset=args.reset,
        )

        build_vector_store(
            rebuild=(
                args.rebuild_vector_store
            ),
        )

        verify_setup(
            runtime_only=args.runtime_only,
        )

        print_next_steps(
            runtime_only=args.runtime_only,
        )

    except subprocess.CalledProcessError as exc:
        print()
        print(
            "Setup failed while running:"
        )

        print(
            " ".join(
                str(part)
                for part
                in exc.cmd
            )
        )

        sys.exit(
            exc.returncode
        )

    except RuntimeError as exc:
        print()
        print(
            f"Setup failed: {exc}"
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
