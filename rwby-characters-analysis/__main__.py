from dataclasses import dataclass
from typing import Any, Dict, IO, List

import argparse
import csv
import sys

import numpy as np
import pandas as pd
import plotnine as plt9

APPEARANCE_TYPES = [
    "Main",
    "Secondary",
    "Minor",
    "One Appearance",
    "Voice Cameos",
    "Voice Cameo",
    "Cameo",
    "Cameo (Corpse)",
    "Mentioned",
    #    "Deceased",
    #    "No Appearance",
    #    "???",
]

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
    parser.add_argument(
        "--output_num_characters_by_volume_plot", default="num_characters_by_volume.png"
    )
    parser.add_argument(
        "--output_characters_appearances", default="characters_appearances.png"
    )

    args = parser.parse_args(argv)

    pre_process(args)

    data = Data.from_files(args)
    plot_num_characters_by_volume(args, data.appearances)
    plot_characters_appearances(args, data.appearances)


def pre_process(args: argparse.Namespace) -> None:
    with open(args.characters_by_volume_csv, "r") as input_stream:
        character_entries = read_character_appearances(input_stream)

    with open(args.output_character_appearances_csv, "w") as output_stream:
        write_character_appearances(output_stream, character_entries)
    print("Wrote character appearances to:", args.output_character_appearances_csv)


def plot_num_characters_by_volume(args: argparse.Namespace, data: pd.DataFrame) -> None:
    plot = (
        plt9.ggplot(data, plt9.aes("volume", fill="appearance_type"))
        + plt9.geom_bar(stat="count")
        + plt9.geom_text(
            plt9.aes(label="stat(count)", size=1.0),
            stat="count",
            position=plt9.position_stack(vjust=0.5),
            show_legend=False,
        )
        + plt9.ggtitle("Num Characters per Volume")
        + plt9.xlab("Volume")
        + plt9.ylab("Num characters in volume")
        + plt9.scale_fill_hue(name="Appearance")
    )

    plot.save(args.output_num_characters_by_volume_plot, dpi=300, height=9, width=8)
    print(
        "Wrote num characters by volume plot to:",
        args.output_num_characters_by_volume_plot,
    )


def plot_characters_appearances(args: argparse.Namespace, data: pd.DataFrame) -> None:
    plot = (
        plt9.ggplot(data, plt9.aes("volume", "name", fill="appearance_type"))
        + plt9.geom_tile(plt9.aes(tile_width=1.0, tile_height=1.0))
        + plt9.ggtitle("Character appearances")
        + plt9.xlab("Volume")
        + plt9.ylab("Character")
        + plt9.scale_fill_hue(name="Appearance")
    )

    plot.save(
        args.output_characters_appearances, dpi=300, height=45, width=8, limitsize=False
    )
    print(
        "Wrote character appearances plot:",
        args.output_characters_appearances,
    )


@dataclass
class Data:
    appearances: pd.DataFrame

    @staticmethod
    def from_files(args: argparse.Namespace) -> "Data":
        appearances = Data.load_appearances(args)

        return Data(appearances)

    @staticmethod
    def load_appearances(args) -> pd.DataFrame:
        data = pd.read_csv(args.output_character_appearances_csv)

        # Filter out cases that aren't actual appearances
        appearances = data[
            (data["appearance_type"] != "No Appearance")
            & (data["appearance_type"] != "???")
            & (data["appearance_type"] != "Deceased")
        ].copy()

        # Sort the appearance type categories by the degree of appearance
        appearances["appearance_type"] = pd.Categorical(
            appearances["appearance_type"],
            categories=APPEARANCE_TYPES[::-1],
        )

        # Use the existing ordering of names for plots
        appearances["name"] = pd.Categorical(
            appearances["name"],
            categories=appearances["name"].unique()[::-1],
        )

        return appearances


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
