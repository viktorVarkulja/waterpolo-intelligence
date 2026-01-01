"""init

Revision ID: 20240920_0001
Revises: 
Create Date: 2024-09-20 00:01:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "20240920_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False, unique=True),
        sa.Column("slug", sa.String(length=200), nullable=False, unique=True),
    )

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season", sa.String(length=50), nullable=True),
        sa.Column("stage", sa.String(length=50), nullable=True),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("home_team_id", sa.Integer(), nullable=False),
        sa.Column("away_team_id", sa.Integer(), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("match_key", sa.String(length=200), nullable=False, unique=True),
        sa.Column("import_batch", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["home_team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["away_team_id"], ["teams.id"]),
    )

    op.create_table(
        "team_match_stats",
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("to_g", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("to_sh", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("a_g", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("a_sh", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ce_g", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ce_sh", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ex_g", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ex_sh", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("six_m_g", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("six_m_sh", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("p_g", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("p_sh", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("co_g", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("co_sh", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pso_g", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pso_sh", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assists", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("turnovers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("steals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blocks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sprints_won", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sprints", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exclusions_drawn", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exclusions_fouls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("double_exclusions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("penalties", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exclusions_finished", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exclusions_4min", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("match_id", "team_id"),
        sa.UniqueConstraint("match_id", "team_id", name="uq_team_match"),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
    )

    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("number", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=50), nullable=True),
        sa.Column("dob", sa.Date(), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
    )

    op.create_table(
        "player_match_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("goals", sa.Integer(), nullable=True),
        sa.Column("shots", sa.Integer(), nullable=True),
        sa.Column("assists", sa.Integer(), nullable=True),
        sa.Column("steals", sa.Integer(), nullable=True),
        sa.Column("blocks", sa.Integer(), nullable=True),
        sa.Column("exclusions", sa.Integer(), nullable=True),
        sa.Column("turnovers", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"]),
    )


def downgrade() -> None:
    op.drop_table("player_match_stats")
    op.drop_table("players")
    op.drop_table("team_match_stats")
    op.drop_table("matches")
    op.drop_table("teams")
