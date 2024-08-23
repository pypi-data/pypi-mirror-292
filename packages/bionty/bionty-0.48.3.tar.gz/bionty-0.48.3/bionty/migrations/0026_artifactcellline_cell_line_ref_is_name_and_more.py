# Generated by Django 5.0.6 on 2024-05-18 14:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bionty", "0025_artifactcellline_alter_cellline_artifacts_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="artifactcellline",
            name="cell_line_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactcellline",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactcellmarker",
            name="cell_marker_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactcellmarker",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactcelltype",
            name="cell_type_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactcelltype",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactdevelopmentalstage",
            name="developmental_stage_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactdevelopmentalstage",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactdisease",
            name="disease_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactdisease",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactethnicity",
            name="ethnicity_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactethnicity",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactexperimentalfactor",
            name="experimental_factor_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactexperimentalfactor",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactgene",
            name="feature_ref_is_symbol",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactgene",
            name="gene_ref_is_symbol",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactorganism",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactorganism",
            name="organism_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactpathway",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactpathway",
            name="pathway_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactphenotype",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactphenotype",
            name="phenotype_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactprotein",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifactprotein",
            name="protein_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifacttissue",
            name="feature_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="artifacttissue",
            name="tissue_ref_is_name",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="artifactcellline",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cell_line_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcellline",
            name="cell_line",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.cellline",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcellline",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactcellline_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcellmarker",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cell_marker_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcellmarker",
            name="cell_marker",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.cellmarker",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcellmarker",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactcellmarker_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcelltype",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cell_type_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcelltype",
            name="cell_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.celltype",
            ),
        ),
        migrations.AlterField(
            model_name="artifactcelltype",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactcelltype_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactdevelopmentalstage",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="developmental_stage_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactdevelopmentalstage",
            name="developmental_stage",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.developmentalstage",
            ),
        ),
        migrations.AlterField(
            model_name="artifactdevelopmentalstage",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactdevelopmentalstage_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactdisease",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="disease_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactdisease",
            name="disease",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.disease",
            ),
        ),
        migrations.AlterField(
            model_name="artifactdisease",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactdisease_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactethnicity",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ethnicity_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactethnicity",
            name="ethnicity",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.ethnicity",
            ),
        ),
        migrations.AlterField(
            model_name="artifactethnicity",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactethnicity_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactexperimentalfactor",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="experimental_factor_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactexperimentalfactor",
            name="experimental_factor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.experimentalfactor",
            ),
        ),
        migrations.AlterField(
            model_name="artifactexperimentalfactor",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactexperimentalfactor_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactgene",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="gene_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactgene",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactgene_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactgene",
            name="gene",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.gene",
            ),
        ),
        migrations.AlterField(
            model_name="artifactorganism",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organism_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactorganism",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactorganism_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactorganism",
            name="organism",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.organism",
            ),
        ),
        migrations.AlterField(
            model_name="artifactpathway",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pathway_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactpathway",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactpathway_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactpathway",
            name="pathway",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.pathway",
            ),
        ),
        migrations.AlterField(
            model_name="artifactphenotype",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="phenotype_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactphenotype",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactphenotype_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactphenotype",
            name="phenotype",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.phenotype",
            ),
        ),
        migrations.AlterField(
            model_name="artifactprotein",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="protein_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifactprotein",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifactprotein_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifactprotein",
            name="protein",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.protein",
            ),
        ),
        migrations.AlterField(
            model_name="artifacttissue",
            name="artifact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tissue_links",
                to="lnschema_core.artifact",
            ),
        ),
        migrations.AlterField(
            model_name="artifacttissue",
            name="feature",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifacttissue_links",
                to="lnschema_core.feature",
            ),
        ),
        migrations.AlterField(
            model_name="artifacttissue",
            name="tissue",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="artifact_links",
                to="bionty.tissue",
            ),
        ),
    ]
