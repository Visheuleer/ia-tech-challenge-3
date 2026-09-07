from pathlib import Path
import subprocess


MEDQUAD_REPOSITORY = "https://github.com/abachaa/MedQuAD.git"

OUTPUT_DIRECTORY = Path(
    "data/raw/datasets/medquad"
)


def main() -> None:
    if OUTPUT_DIRECTORY.exists():
        print(
            f"MedQuAD already exists at {OUTPUT_DIRECTORY}."
        )
        return

    OUTPUT_DIRECTORY.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            MEDQUAD_REPOSITORY,
            str(OUTPUT_DIRECTORY),
        ],
        check=True,
    )

    print(
        f"MedQuAD downloaded successfully to "
        f"{OUTPUT_DIRECTORY}."
    )


if __name__ == "__main__":
    main()