"""add_multitenant_support_organizations_and_relationships

Revision ID: 6c9f69f2b32f
Revises: 14765318ba03
Create Date: 2025-11-02 12:42:44.816135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c9f69f2b32f'
down_revision: Union[str, None] = '14765318ba03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. organizationsテーブル作成
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('subdomain', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_subdomain'), 'organizations', ['subdomain'], unique=True)

    # 2. デフォルト組織を作成（既存データ用）
    op.execute("""
        INSERT INTO organizations (name, subdomain, is_active, created_at, updated_at)
        VALUES ('Default Organization', 'default', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """)

    # 3. photosテーブルにorganization_idを追加
    op.add_column('photos', sa.Column('organization_id', sa.Integer(), nullable=True))

    # 既存データをデフォルト組織に紐付け
    op.execute("UPDATE photos SET organization_id = 1 WHERE organization_id IS NULL")

    # NOT NULL制約を追加
    op.alter_column('photos', 'organization_id', nullable=False)

    # 外部キー制約とインデックスを追加
    op.create_foreign_key('fk_photos_organization', 'photos', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_photos_organization_id'), 'photos', ['organization_id'], unique=False)

    # 複合インデックス追加
    op.create_index('ix_photos_org_created', 'photos', ['organization_id', 'created_at'])
    op.create_index('ix_photos_org_shooting_date', 'photos', ['organization_id', 'shooting_date'])

    # 4. usersテーブルにorganization_idを追加
    op.add_column('users', sa.Column('organization_id', sa.Integer(), nullable=True))

    # 既存データをデフォルト組織に紐付け
    op.execute("UPDATE users SET organization_id = 1 WHERE organization_id IS NULL")

    # NOT NULL制約を追加
    op.alter_column('users', 'organization_id', nullable=False)

    # 外部キー制約とインデックスを追加
    op.create_foreign_key('fk_users_organization', 'users', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)

    # 5. projectsテーブルにorganization_idを追加
    op.add_column('projects', sa.Column('organization_id', sa.Integer(), nullable=True))

    # 既存データをデフォルト組織に紐付け
    op.execute("UPDATE projects SET organization_id = 1 WHERE organization_id IS NULL")

    # NOT NULL制約を追加
    op.alter_column('projects', 'organization_id', nullable=False)

    # 外部キー制約とインデックスを追加
    op.create_foreign_key('fk_projects_organization', 'projects', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_projects_organization_id'), 'projects', ['organization_id'], unique=False)

    # 6. photo_duplicatesテーブルにorganization_idを追加
    op.add_column('photo_duplicates', sa.Column('organization_id', sa.Integer(), nullable=True))

    # 既存データをデフォルト組織に紐付け
    op.execute("UPDATE photo_duplicates SET organization_id = 1 WHERE organization_id IS NULL")

    # NOT NULL制約を追加
    op.alter_column('photo_duplicates', 'organization_id', nullable=False)

    # 外部キー制約とインデックスを追加
    op.create_foreign_key('fk_photo_duplicates_organization', 'photo_duplicates', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_photo_duplicates_organization_id'), 'photo_duplicates', ['organization_id'], unique=False)


def downgrade() -> None:
    # photo_duplicatesテーブルのorganization_id削除
    op.drop_index(op.f('ix_photo_duplicates_organization_id'), table_name='photo_duplicates')
    op.drop_constraint('fk_photo_duplicates_organization', 'photo_duplicates', type_='foreignkey')
    op.drop_column('photo_duplicates', 'organization_id')

    # projectsテーブルのorganization_id削除
    op.drop_index(op.f('ix_projects_organization_id'), table_name='projects')
    op.drop_constraint('fk_projects_organization', 'projects', type_='foreignkey')
    op.drop_column('projects', 'organization_id')

    # usersテーブルのorganization_id削除
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_constraint('fk_users_organization', 'users', type_='foreignkey')
    op.drop_column('users', 'organization_id')

    # photosテーブルのorganization_id削除
    op.drop_index('ix_photos_org_shooting_date', table_name='photos')
    op.drop_index('ix_photos_org_created', table_name='photos')
    op.drop_index(op.f('ix_photos_organization_id'), table_name='photos')
    op.drop_constraint('fk_photos_organization', 'photos', type_='foreignkey')
    op.drop_column('photos', 'organization_id')

    # organizationsテーブル削除
    op.drop_index(op.f('ix_organizations_subdomain'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')
