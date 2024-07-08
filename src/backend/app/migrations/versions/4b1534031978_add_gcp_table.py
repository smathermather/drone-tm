"""Add GCP table

Revision ID: 4b1534031978
Revises: d2b9d45d3ede
Create Date: 2024-07-03 05:10:56.759505

"""
from typing import Sequence, Union
import geoalchemy2
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4b1534031978"
down_revision: Union[str, None] = "d2b9d45d3ede"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ground_control_points",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("image_relative_path", sa.String(), nullable=True),
        sa.Column("pixel_x", sa.SmallInteger(), nullable=True),
        sa.Column("pixel_y", sa.SmallInteger(), nullable=True),
        sa.Column(
            "reference_point",
            geoalchemy2.types.Geometry(
                geometry_type="POLYGON",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # op.create_index('idx_ground_control_points_reference_point', 'ground_control_points', ['reference_point'], unique=False, postgresql_using='gist')
    op.drop_column("drone_flights", "imagery_data_url")
    op.add_column("projects", sa.Column("output_raw_url", sa.String(), nullable=True))
    op.add_column("task_events", sa.Column("comment", sa.String(), nullable=True))
    op.drop_column("task_events", "detail")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "task_events",
        sa.Column("detail", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_column("task_events", "comment")
    op.drop_column("projects", "output_raw_url")
    op.add_column(
        "drone_flights",
        sa.Column("imagery_data_url", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    # op.drop_index('idx_ground_control_points_reference_point', table_name='ground_control_points', postgresql_using='gist')
    op.drop_table("ground_control_points")
    # ### end Alembic commands ###