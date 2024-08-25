import pathlib
from typing import Union

from mdutils.mdutils import MdUtils


def add_documentation(ml_collection, outfile: Union[str, pathlib.Path]):
    if isinstance(outfile, str):
        outfile = pathlib.Path(outfile)
    outfile.parent.mkdir(parents=True, exist_ok=True)

    # Create the README.md file
    mdFile = MdUtils(file_name=outfile)

    # Create yaml header ------------------------------------
    mdFile.new_line("---")
    mdFile.new_line(f"license: {ml_collection.license}")
    mdFile.new_line(f"task_categories:")
    for item in ml_collection.ml_task:
        mdFile.new_line(f"  - {item}")
    mdFile.new_line(f"language:")
    mdFile.new_line(f"- en")
    if ml_collection.keywords is not None:
        mdFile.new_line(f"tags:")
        for tag in ml_collection.keywords:
            mdFile.new_line(f"  - {tag}")
    mdFile.new_line(f"pretty_name: {ml_collection.id}")
    mdFile.new_line("---")

    # Set title, subtitle and description --------------------
    mdFile.new_header(level=1, title=f"{ml_collection.id}")
    if ml_collection.title is not None:
        mdFile.new_line(f"{ml_collection.title}", bold_italics_code="cib")
    mdFile.new_paragraph(f"{ml_collection.description}\n")
    mdFile.new_paragraph(f"ML-STAC Snippet", bold_italics_code="b")

    # Add code snippet ---------------------------------------
    mdFile.new_line("```python")
    mdFile.new_line(f"import mlstac")
    mdFile.new_line(f"dataset = mlstac.load('...')")
    mdFile.new_line("```")

    # Add data raw repository --------------------------------
    if ml_collection.ml_spectral is not None:
        mdFile.new_paragraph(
            "Sensor: " + ml_collection.ml_spectral.sensor, bold_italics_code="b"
        )

        mdFile.new_paragraph(
            "ML-STAC Task: " + ", ".join(ml_collection.ml_task), bold_italics_code="b"
        )

    if ml_collection.ml_raw_data_url is not None:
        mdFile.new_paragraph(
            f"Data raw repository:  "
            + mdFile.new_inline_link(link=ml_collection.ml_raw_data_url),
            bold_italics_code="b",
        )

    if ml_collection.ml_discussion_url is not None:
        mdFile.new_paragraph(
            "Dataset discussion:  "
            + mdFile.new_inline_link(link=ml_collection.ml_discussion_url),
            bold_italics_code="b",
        )

    if ml_collection.ml_reviewers is not None:
        mdFile.new_paragraph(
            f"Review mean score:  {ml_collection.get_review_mean_score()}",
            bold_italics_code="b",
        )

    if ml_collection.ml_split_strategy is not None:
        mdFile.new_paragraph(
            f"Split_strategy:  " + ml_collection.ml_split_strategy,
            bold_italics_code="b",
        )

    if ml_collection.ml_paper is not None:
        mdFile.new_paragraph(
            f"Paper:  " + mdFile.new_inline_link(link=ml_collection.ml_paper),
            bold_italics_code="b",
        )

    # Add Provider --------------------------------------------
    mdFile.new_header(level=2, title=f"Data Providers")
    list_of_strings = ["Name", "Role", "URL"]
    for p in ml_collection.providers.field:
        list_of_strings.extend([p.name, p.roles, p.url])
    mdFile.new_table(
        columns=3,
        rows=len(ml_collection.providers.field) + 1,
        text=list_of_strings,
        text_align="center",
    )

    # Add Authors ---------------------------------------------
    # if len(self.ml_authors.authors) > 0:
    #    mdFile.new_header(level=2, title=f"Authors")
    #    list_of_strings = ["Name", "Organization"]
    #    for p in self.ml_authors:
    #        list_of_strings.extend([p['name'], p['organization']])
    # mdFile.new_table(columns=2, rows=len(self.ml_authors.authors)+1, text=list_of_strings, text_align='center')

    # Add Curators --------------------------------------------
    if ml_collection.ml_curators is not None:
        mdFile.new_header(level=2, title=f"Curators")
        list_of_strings = ["Name", "Organization", "URL"]
        for p in ml_collection.ml_curators.curators:
            list_of_strings.extend([p.name, p.organization, p.links[0].href])
        mdFile.new_table(
            columns=3,
            rows=len(ml_collection.ml_curators.curators) + 1,
            text=list_of_strings,
            text_align="center",
        )

    # Add Reviewers --------------------------------------------
    if ml_collection.ml_reviewers is not None:
        mdFile.new_header(level=2, title=f"Reviewers")
        list_of_strings = ["Name", "Organization", "URL", "Score"]
        for reviewer in ml_collection.ml_reviewers.reviewers:
            p = reviewer.reviewer
            s = reviewer.score
            list_of_strings.extend([p.name, p.organization, p.links[0].href, s])
        mdFile.new_table(
            columns=4,
            rows=len(ml_collection.ml_reviewers.reviewers) + 1,
            text=list_of_strings,
            text_align="center",
        )

    # Add Labels ----------------------------------------------
    if ml_collection.ml_target is not None:
        mdFile.new_header(level=2, title="Labels")
        list_of_strings = ["Name", "Value"]
        for k, v in ml_collection.ml_target.labels.items():
            list_of_strings.extend([k, v])
        mdFile.new_table(
            columns=2,
            rows=len(ml_collection.ml_target.labels) + 1,
            text=list_of_strings,
            text_align="center",
        )

        # Add Dimensions ------------------------------------------
        if ml_collection.ml_dimensions is not None:
            mdFile.new_header(level=2, title=f"Dimensions")
            for k, v in ml_collection.ml_dimensions.model_dump().items():
                if len(v) > 0:
                    mdFile.new_header(level=3, title=f"{k}")
                    list_of_strings = ["Axis", "Name", "Description"]
                    for p in v:
                        list_of_strings.extend([p["axis"], p["name"], p["description"]])
                    mdFile.new_table(
                        columns=3,
                        rows=len(v) + 1,
                        text=list_of_strings,
                        text_align="center",
                    )

        # Add Spectral Bands --------------------------------------
        if ml_collection.ml_spectral is not None:
            mdFile.new_header(level=2, title=f"Spectral Bands")
            list_of_strings = [
                "Name",
                "Common Name",
                "Description",
                "Center Wavelength",
                "Full Width Half Max",
                "Index",
            ]
            for p in ml_collection.ml_spectral.bands:
                list_of_strings.extend(
                    [
                        p.name,
                        p.common_name,
                        p.description,
                        p.center_wavelength,
                        p.full_width_half_max,
                        p.index,
                    ]
                )
            mdFile.new_table(
                columns=6,
                rows=len(ml_collection.ml_spectral.bands) + 1,
                text=list_of_strings,
                text_align="center",
            )

        file = mdFile.get_md_text().replace("\n\n\n  \n", "").replace("  \n", "\n")
        with open(outfile, "w") as f:
            f.write(file)
