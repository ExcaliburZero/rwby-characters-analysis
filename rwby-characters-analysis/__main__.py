from dataclasses import dataclass
from typing import Any, Dict, IO, List

import argparse
import csv
import sys

VOLUME_COLUMNS = [
    "Trailers",
    "Volume 1",
    "Volume 2",
    "Volume 3",
    "Volume 4",
    "Volume 5",
    "Volume 6",
    "Volume 7",
    "Volume 8",
]


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("characters_by_volume_csv")
    parser.add_argument(
        "--output_character_appearances_csv", default="character_appearances.csv"
    )

    args = parser.parse_args(argv)

    pre_process(args)


def pre_process(args: argparse.Namespace) -> None:
    with open(args.characters_by_volume_csv, "r") as input_stream:
        character_entries = read_character_appearances(input_stream)

    with open(args.output_character_appearances_csv, "w") as output_stream:
        write_character_appearances(output_stream, character_entries)
    print("Wrote character appearances to:", args.output_character_appearances_csv)


@dataclass
class CharacterAppearance:
    name: str
    volume: str
    appearance_type: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "volume": self.volume,
            "appearance_type": self.appearance_type,
        }


def read_character_appearances(input_stream: IO[str]) -> List[CharacterAppearance]:
    entries = []

    reader = csv.DictReader(input_stream)
    for row in reader:
        validate_characters_by_volume_row(row)

        name = row["Name"]

        for volume in VOLUME_COLUMNS:
            entries.append(CharacterAppearance(name, volume, row[volume]))

    return entries


def validate_characters_by_volume_row(row: Dict[str, Any]) -> None:
    assert "Name" in row

    for volume in VOLUME_COLUMNS:
        assert volume in row


def write_character_appearances(
    output_stream: IO[str], character_entries: List[CharacterAppearance]
) -> None:
    writer = csv.DictWriter(
        output_stream, fieldnames=["name", "volume", "appearance_type"]
    )

    writer.writeheader()
    for entry in character_entries:
        writer.writerow(entry.to_dict())


if __name__ == "__main__":
    main(sys.argv[1:])